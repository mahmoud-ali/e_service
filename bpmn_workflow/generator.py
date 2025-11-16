"""
BPMN Workflow Handler Generator

Generates Python handler classes from BPMN workflow definitions.
"""

from typing import List
from .models import WorkflowDefinition, BPMNNode


class WorkflowHandlerGenerator:
    """Generate Python handler class from BPMN workflow"""
    
    def __init__(self, workflow: WorkflowDefinition):
        self.workflow = workflow
    
    def generate(self) -> str:
        """Generate complete handler class code"""
        
        user_tasks = list(self.workflow.nodes.filter(node_type='user_task'))
        service_tasks = list(self.workflow.nodes.filter(node_type='service_task'))
        gateways = list(self.workflow.nodes.filter(node_type__icontains='gateway'))
        
        code = self._generate_header()
        code += self._generate_class_definition()
        code += self._generate_init_method()
        
        # Generate handler methods for user tasks
        for task in user_tasks:
            code += self._generate_user_task_handler(task)
        
        # Generate handler methods for service tasks
        for task in service_tasks:
            code += self._generate_service_task_handler(task)
        
        # Generate condition evaluators for gateways
        for gateway in gateways:
            code += self._generate_gateway_evaluator(gateway)
        
        code += self._generate_footer()
        
        return code
    
    def _generate_header(self) -> str:
        return f'''"""
Auto-generated workflow handler for: {self.workflow.name}

GENERATED CODE - Customize the implementation of each method as needed.

Generated from BPMN process: {self.workflow.bpmn_process_id}
Workflow key: {self.workflow.key}
Version: {self.workflow.version}
"""

from django.db import transaction
from django.utils import timezone
from typing import Dict, Any
from bpmn_workflow.engine import BaseWorkflowHandler
from bpmn_workflow.models import ProcessInstance, TaskInstance


'''
    
    def _generate_class_definition(self) -> str:
        class_name = self._to_class_name(self.workflow.key)
        return f'''class {class_name}(BaseWorkflowHandler):
    """
    Handler for {self.workflow.name}
    
    This class contains methods that are called when tasks and gateways
    are executed in the workflow. Customize the implementation to add
    your business logic.
    """
    
    workflow_key = '{self.workflow.key}'
    
'''
    
    def _generate_init_method(self) -> str:
        return '''    def __init__(self):
        super().__init__()
        # Add any initialization code here
    
'''
    
    def _generate_user_task_handler(self, task: BPMNNode) -> str:
        method_name = self._to_method_name(task.bpmn_id)
        
        # Extract candidate groups
        groups = task.candidate_groups if task.candidate_groups else []
        groups_str = ', '.join(groups) if groups else 'any authorized user'
        
        return f'''    @transaction.atomic
    def handle_{method_name}(
        self, 
        task_instance: TaskInstance, 
        user, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        User Task: {task.name}
        BPMN ID: {task.bpmn_id}
        Authorized groups: {groups_str}
        
        This method is called when the user completes this task.
        
        Args:
            task_instance: The task being executed
            user: The user performing the action
            data: Input data from the form/API (POST data)
            
        Returns:
            Dict with output variables to store in process.
            These variables can be accessed in gateway conditions.
            
        Example:
            return {{
                'approved': True,
                'comment': data.get('comment', ''),
                'approved_by': user.username,
                'approved_at': timezone.now().isoformat(),
            }}
        """
        # Access the business object
        business_object = task_instance.process_instance.content_object
        
        # Get process variables
        # status = self.get_variable(task_instance.process_instance, 'status')
        
        # Your custom logic here
        # Example: Update the business object with form data
        # business_object.comment = data.get('comment', '')
        # business_object.save()
        
        # Return variables to store in the process
        return {{
            'task_completed': True,
            'completed_by': user.username,
            'completed_at': timezone.now().isoformat(),
        }}

'''
    
    def _generate_service_task_handler(self, task: BPMNNode) -> str:
        method_name = self._to_method_name(task.bpmn_id)
        
        return f'''    @transaction.atomic
    def handle_{method_name}(self, process_instance: ProcessInstance) -> Dict[str, Any]:
        """
        Service Task: {task.name}
        BPMN ID: {task.bpmn_id}
        
        This is an automated task that executes without user interaction.
        
        Args:
            process_instance: The running process instance
            
        Returns:
            Dict with output variables
            
        Example:
            return {{
                'calculation_result': 42,
                'email_sent': True,
            }}
        """
        # Access the business object
        business_object = process_instance.content_object
        
        # Get process variables
        # total = self.get_variable(process_instance, 'total_amount')
        
        # Your automation logic here
        # Examples:
        # - Send email notifications
        # - Calculate totals
        # - Update external systems
        # - Generate documents
        
        return {{
            'service_executed_at': timezone.now().isoformat(),
        }}

'''
    
    def _generate_gateway_evaluator(self, gateway: BPMNNode) -> str:
        method_name = self._to_method_name(gateway.bpmn_id)
        flows = list(gateway.outgoing_flows.all())
        
        conditions_comment = "        # Available outgoing flows:\n"
        for i, flow in enumerate(flows, 1):
            flow_name = flow.name or f"Flow {i}"
            target_name = flow.target.name
            condition = flow.condition_expression or 'default'
            conditions_comment += f"        #   {i}. '{flow_name}'({flow.bpmn_id}) -> {target_name} (condition: {condition})\n"
        
        flow_returns = "\n".join([
            f"        # return '{flow.bpmn_id}'  # Route to: {flow.target.name}"
            for flow in flows
        ])
        
        default_return = f"'{flows[0].bpmn_id}'" if flows else "'default'"
        other_return = f"'{flows[-1].bpmn_id}'" if flows else "'default'"
        
        return f'''    def evaluate_{method_name}(self, process_instance: ProcessInstance) -> str:
        """
        Gateway: {gateway.name}
        BPMN ID: {gateway.bpmn_id}
        Type: {gateway.node_type}
        
        Evaluate this gateway to determine which path to take.
        
{conditions_comment}
        
        Returns:
            The BPMN ID of the sequence flow to take
            
        Example:
            approved = self.get_variable(process_instance, 'approved')
            if approved:
                return 'flow_to_approval'
            else:
                return 'flow_to_rejection'
        """
        # Access the business object
        business_object = process_instance.content_object
        
        # Get process variables
        # approved = self.get_variable(process_instance, 'approved')
        # amount = self.get_variable(process_instance, 'total_amount')
        
        # Example routing logic:
        if not approved:
            return {other_return}
        
        # Default flow
        return {default_return}

'''
    
    def _generate_footer(self) -> str:
        return '''
    @transaction.atomic
    def pre_end_event(self,process_instance: ProcessInstance, user):
        """
        This will be called before end event.
        
        process_instance: process instanse
        user: user object
        """
        pass
        
    # ==========================================
    # Add your custom helper methods below
    # ==========================================
    
    def _your_custom_helper(self, data):
        """
        Add any custom helper methods you need.
        
        These methods can be called from your task handlers
        to keep your code organized and reusable.
        """
        pass
'''
    
    @staticmethod
    def _to_class_name(key: str) -> str:
        """Convert workflow_key to ClassName"""
        return ''.join(word.capitalize() for word in key.split('_')) + 'Handler'
    
    @staticmethod
    def _to_method_name(bpmn_id: str) -> str:
        """Convert BPMN ID to method_name"""
        # Remove common prefixes and convert to snake_case
        name = bpmn_id.replace('Activity_', '').replace('Gateway_', '').replace('Task_', '')
        name = name.replace('-', '_')
        return name.lower()
