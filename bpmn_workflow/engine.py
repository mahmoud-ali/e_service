"""
BPMN Process Engine

Core engine for executing BPMN workflows.
"""

from django.db import transaction
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from typing import Dict, Any, Optional
import importlib
import logging

from .models import (
    WorkflowDefinition, BPMNNode, SequenceFlow,
    ProcessInstance, Token, TaskInstance, ActivityLog
)

logger = logging.getLogger(__name__)


class BaseWorkflowHandler:
    """Base class for custom workflow handlers"""
    
    workflow_key = None
    
    def get_variable(self, process_instance: ProcessInstance, key: str, default=None):
        """Get process variable"""
        return process_instance.variables.get(key, default)
    
    def set_variable(self, process_instance: ProcessInstance, key: str, value):
        """Set process variable"""
        process_instance.variables[key] = value
        process_instance.save(update_fields=['variables', 'updated_at'])
        
        # Log variable set
        # ActivityLog.objects.create(
        #     process_instance=process_instance,
        #     event_type='variable_set',
        #     details={'key': key, 'value': str(value)[:200]}
        # )


class BPMNEngine:
    """BPMN Process Engine - executes workflows"""
    
    @staticmethod
    @transaction.atomic
    def start_process(workflow_key: str, business_object, user, initial_variables: Dict = None):
        """
        Start a new process instance
        
        Args:
            workflow_key: The workflow definition key
            business_object: The Django model instance this workflow operates on
            user: The user starting the process
            initial_variables: Optional dict of initial process variables
            
        Returns:
            ProcessInstance object
        """
        workflow = WorkflowDefinition.objects.get(key=workflow_key, is_active=True)
        content_type = ContentType.objects.get_for_model(business_object)
        
        # Create process instance
        process = ProcessInstance.objects.create(
            workflow=workflow,
            content_type=content_type,
            object_id=business_object.pk,
            status='active',
            started_by=user,
            variables=initial_variables or {}
        )
        
        # Log start
        ActivityLog.objects.create(
            process_instance=process,
            event_type='process_started',
            actor=user,
            details={'variables': initial_variables or {}}
        )
        
        # Find start event
        start_node = workflow.nodes.filter(node_type='start_event').first()
        if not start_node:
            raise ValueError(f"Workflow '{workflow_key}' has no start event")
        
        # Create initial token
        token = Token.objects.create(
            process_instance=process,
            current_node=start_node
        )
        
        # Move token forward
        BPMNEngine._move_token(token, user)
        
        logger.info(f"Started process {process.id} for workflow '{workflow_key}'")
        
        return process
    
    @staticmethod
    @transaction.atomic
    def complete_task(task_instance: TaskInstance, user, data: Dict[str, Any]):
        """
        Complete a user task
        
        Args:
            task_instance: The TaskInstance to complete
            user: The user completing the task
            data: Form data or task output
        """
        if task_instance.status not in ['ready', 'in_progress']:
            raise ValueError(f"Task is not in a completable state: {task_instance.status}")
        
        if not task_instance.can_be_completed_by(user):
            raise PermissionError(f"User {user} cannot complete this task")
        
        # Load handler
        handler = BPMNEngine._get_handler(task_instance.process_instance.workflow)
        
        # Execute handler method
        method_name = f"handle_{BPMNEngine._to_method_name(task_instance.node.bpmn_id)}"

        if hasattr(handler, method_name):
            try:
                output = getattr(handler, method_name)(task_instance, user, data)
                
                # Store output variables
                if output and isinstance(output, dict):
                    process = task_instance.process_instance
                    for key, value in output.items():
                        handler.set_variable(process, key, value)
            except Exception as e:
                logger.error(f"Error executing handler {method_name}: {e}")
                task_instance.status = 'failed'
                task_instance.save()
                raise
        else:
            logger.error(f"Invalid handler: {method_name}")
            task_instance.status = 'failed'
            task_instance.save()

            raise Exception(f'Invalid handler: {method_name}')
        
        # Complete task
        task_instance.status = 'completed'
        task_instance.output_data = data
        task_instance.completed_at = timezone.now()
        task_instance.save()
        
        # Log completion
        ActivityLog.objects.create(
            process_instance=task_instance.process_instance,
            task_instance=task_instance,
            event_type='task_completed',
            node=task_instance.node,
            actor=user,
            details={'data': data}
        )
        
        logger.info(f"Completed task {task_instance.node}({task_instance.id}) by user {user.username}")
        
        # Move token
        BPMNEngine._move_token(task_instance.token, user)
    
    @staticmethod
    def _move_token(token: Token, user):
        """Move token to next node(s) based on current node type"""
        
        current_node = token.current_node
        logger.debug(f"Moving token from {current_node.name} ({current_node.node_type})")
        
        # Handle different node types
        if current_node.node_type == 'start_event':
            BPMNEngine._handle_start_event(token, user)
        
        elif current_node.node_type in ['user_task', 'service_task', 'script_task']:
            # These require completion before moving
            if current_node.node_type == 'user_task':
                # User task already completed by complete_task
                BPMNEngine._advance_from_task(token, user)
            else:
                # Service/Script tasks execute automatically
                BPMNEngine._handle_service_task(token, user)
        
        elif current_node.node_type == 'exclusive_gateway':
            BPMNEngine._handle_exclusive_gateway(token, user)
        
        elif current_node.node_type == 'parallel_gateway':
            BPMNEngine._handle_parallel_gateway(token, user)
        
        elif current_node.node_type == 'end_event':
            BPMNEngine._handle_end_event(token, user)
        
        else:
            logger.warning(f"Unhandled node type: {current_node.node_type}")
    
    @staticmethod
    def _handle_start_event(token: Token, user):
        """Move from start event to next node"""
        outgoing = token.current_node.outgoing_flows.first()
        if outgoing:
            BPMNEngine._create_token_at(outgoing.target, token.process_instance, user, parent=token)
        else:
            logger.warning(f"Start event {token.current_node.name} has no outgoing flows")
        
        token.is_active = False
        token.completed_at = timezone.now()
        token.save()
    
    @staticmethod
    def _advance_from_task(token: Token, user):
        """Move after task completes"""        
        token.is_active = False
        token.completed_at = timezone.now()
        token.save()

        outgoing = token.current_node.outgoing_flows.first()
        if outgoing:
            BPMNEngine._create_token_at(outgoing.target, token.process_instance, user, parent=token)

    @staticmethod
    def _handle_service_task(token: Token, user):
        """Execute service task automatically"""
        handler = BPMNEngine._get_handler(token.process_instance.workflow)
        method_name = f"handle_{BPMNEngine._to_method_name(token.current_node.bpmn_id)}"
        
        if hasattr(handler, method_name):
            try:
                logger.info(f"Run service handler: {handler.__class__.__name__}.{method_name}")
                output = getattr(handler, method_name)(token.process_instance)
                if output and isinstance(output, dict):
                    for key, value in output.items():
                        handler.set_variable(token.process_instance, key, value)
                logger.info(f"Executed service task: {token.current_node.name}")
            except Exception as e:
                logger.error(f"Service task failed: {e}")
                raise
        
        # Auto-advance
        BPMNEngine._advance_from_task(token, user)
    
    @staticmethod
    def _handle_exclusive_gateway(token: Token, user):
        """Evaluate gateway conditions and route to one path"""
        handler = BPMNEngine._get_handler(token.process_instance.workflow)
        method_name = f"evaluate_{BPMNEngine._to_method_name(token.current_node.bpmn_id)}"
        
        selected_flow_id = None
        
        # Try custom evaluator
        if hasattr(handler, method_name):
            logger.info(f"Run exclusive_gateway handler: {handler.__class__.__name__}.{method_name}")
            selected_flow_id = getattr(handler, method_name)(token.process_instance)
        else:
            # Evaluate conditions on flows
            logger.info(f"{token.current_node.name} has no handler. run conditions on flows if exists")
            for flow in token.current_node.outgoing_flows.all():
                if flow.condition_expression:
                    if BPMNEngine._evaluate_condition(flow.condition_expression, token.process_instance):
                        selected_flow_id = flow.bpmn_id                        
                        break
            
            # No condition matched - use default flow
            if not selected_flow_id:
                selected_flow_id = token.current_node.default_flow

            
            # Still no flow - take first
            if not selected_flow_id:
                first_flow = token.current_node.outgoing_flows.first()
                selected_flow_id = first_flow.bpmn_id if first_flow else None
        
        logger.info(f"selected flow is: {selected_flow_id}")

        token.is_active = False
        token.completed_at = timezone.now()
        token.save()

        if selected_flow_id:
            flow = token.current_node.outgoing_flows.get(bpmn_id=selected_flow_id)
            BPMNEngine._create_token_at(flow.target, token.process_instance, user, parent=token)
            
            ActivityLog.objects.create(
                process_instance=token.process_instance,
                event_type='gateway_evaluated',
                node=token.current_node,
                actor=user,
                details={'selected_flow': selected_flow_id}
            )
        else:
            logger.error(f"No outgoing flow selected for gateway {token.current_node.name}")
            
    @staticmethod
    def _handle_parallel_gateway(token: Token, user):
        """Handle parallel split/join"""
        outgoing_count = token.current_node.outgoing_flows.count()
        incoming_count = token.current_node.incoming_flows.count()
        
        # Split: create token for each outgoing flow
        if outgoing_count > 1:
            token.is_active = False
            token.completed_at = timezone.now()
            token.save()

            for flow in token.current_node.outgoing_flows.all():
                BPMNEngine._create_token_at(flow.target, token.process_instance, user, parent=token)
                    
        # Join: wait for all incoming tokens
        elif incoming_count > 1:
            # Count active tokens at this node
            active_tokens = Token.objects.filter(
                process_instance=token.process_instance,
                current_node=token.current_node,
                is_active=True
            ).count()
            
            # If this is the last token, proceed
            if active_tokens >= incoming_count:
                # Deactivate all tokens at this node
                Token.objects.filter(
                    process_instance=token.process_instance,
                    current_node=token.current_node,
                    is_active=True
                ).update(is_active=False, completed_at=timezone.now())
                
                # Create new token after join
                outgoing = token.current_node.outgoing_flows.first()
                if outgoing:
                    BPMNEngine._create_token_at(outgoing.target, token.process_instance, user)
        
        else:
            token.is_active = False
            token.completed_at = timezone.now()
            token.save()

            # Simple pass-through
            outgoing = token.current_node.outgoing_flows.first()
            if outgoing:
                BPMNEngine._create_token_at(outgoing.target, token.process_instance, user, parent=token)
                
    @staticmethod
    def _handle_end_event(token: Token, user):
        """End process"""
        process = token.process_instance
        
        # Check if there are other active tokens
        other_active = process.tokens.filter(is_active=True).exclude(id=token.id).exists()
        
        if not other_active:
            # No other active tokens - process is complete
            is_approved = process.variables.get('approved', False)
            if is_approved:
                process.status = 'completed'
            else:
                process.status = 'terminated'

            process.ended_at = timezone.now()
            process.save()
            
            ActivityLog.objects.create(
                process_instance=process,
                event_type='process_completed',
                node=token.current_node,
                actor=user
            )
            
            logger.info(f"Process {process.id} completed")
        
        token.is_active = False
        token.completed_at = timezone.now()
        token.save()
    
    @staticmethod
    def _create_token_at(node: BPMNNode, process: ProcessInstance, user, parent=None):
        """Create token at node and handle it"""
        new_token = Token.objects.create(
            process_instance=process,
            current_node=node,
            parent_token=parent
        )
        
        ActivityLog.objects.create(
            process_instance=process,
            event_type='token_moved',
            node=node,
            actor=user,
            details={'from_node': parent.current_node.name if parent else 'start'}
        )
        
        # If it's a user task, create task instance and wait
        if node.node_type == 'user_task':
            task = TaskInstance.objects.create(
                process_instance=process,
                node=node,
                token=new_token,
                status='ready'
            )
            
            ActivityLog.objects.create(
                process_instance=process,
                task_instance=task,
                event_type='task_created',
                node=node,
                actor=user
            )
            
            logger.info(f"Created user task: {node.name}")
        else:
            # Auto-execute non-user tasks
            BPMNEngine._move_token(new_token, user)
    
    @staticmethod
    def _evaluate_condition(expression: str, process: ProcessInstance) -> bool:
        """Evaluate a condition expression"""
        try:
            # Simple evaluation - you can enhance this
            # Variables available: process.variables
            context = {'variables': process.variables, 'process': process}
            result = eval(expression, {"__builtins__": {}}, context)
            return bool(result)
        except Exception as e:
            logger.error(f"Error evaluating condition '{expression}': {e}")
            return False
    
    @staticmethod
    def _get_handler(workflow: WorkflowDefinition) -> BaseWorkflowHandler:
        """Load workflow handler class"""
        if workflow.handler_class:
            try:
                module_path, class_name = workflow.handler_class.rsplit('.', 1)
                module = importlib.import_module(module_path)
                handler_class = getattr(module, class_name)
                return handler_class()
            except Exception as e:
                logger.error(f"Failed to load handler '{workflow.handler_class}': {e}")
        
        return BaseWorkflowHandler()
    
    @staticmethod
    def _to_method_name(bpmn_id: str) -> str:
        """Convert BPMN ID to method name"""
        # Remove common prefixes and convert to lowercase
        name = bpmn_id.replace('Activity_', '').replace('Gateway_', '').replace('Task_', '')
        return name.lower().replace('-', '_')
    
    @staticmethod
    def get_timeline(process_instance: ProcessInstance):
        """Get complete timeline of process activities"""
        return process_instance.activity_logs.select_related('actor', 'node', 'task_instance').all()
