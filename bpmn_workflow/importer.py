from django.db import transaction
from .models import WorkflowDefinition, BPMNNode, SequenceFlow
from .parser import BPMNParser
import logging

logger = logging.getLogger(__name__)

class WorkflowSyncService:
    """
    Service to synchronize BPMN XML with the database models.
    """
    
    @staticmethod
    @transaction.atomic
    def sync(workflow: WorkflowDefinition):
        """
        Takes a WorkflowDefinition object, uses the parser to get structured data,
        and atomically updates its nodes and flows.
        """
        logger.info(f"Synchronizing workflow: {workflow.key} (ID: {workflow.id})")
        
        if not workflow.bpmn_xml:
            raise ValueError(f"Workflow {workflow.key} has no BPMN XML content.")
            
        parser = BPMNParser(workflow.bpmn_xml)
        data = parser.parse()
        
        # Update workflow attributes from XML if possible
        workflow.bpmn_process_id = data.get('process_id', workflow.bpmn_process_id)
        if not workflow.name and data.get('process_name'):
            workflow.name = data['process_name']
        workflow.save()
        
        # Atomic clear and recreate
        # We delete flows first due to foreign key constraints on BPMNNode
        SequenceFlow.objects.filter(workflow=workflow).delete()
        BPMNNode.objects.filter(workflow=workflow).delete()
        
        node_map = {}
        nodes_created = 0
        
        # Map standard BPMN tags to node_type choices
        # The parser already does some mapping, we ensure it matches models.py
        for node_data in data.get('nodes', []):
            node = BPMNNode.objects.create(
                workflow=workflow,
                bpmn_id=node_data['bpmn_id'],
                node_type=node_data['node_type'],
                name=node_data['name'],
                assignee_expression=node_data.get('assignee_expression', ''),
                candidate_groups=node_data.get('candidate_groups', []),
                form_key=node_data.get('form_key', ''),
                implementation=node_data.get('implementation', ''),
                default_flow=node_data.get('default_flow'),
                properties=node_data.get('properties', {})
            )
            node_map[node.bpmn_id] = node
            nodes_created += 1
            
        flows_created = 0
        for flow_data in data.get('flows', []):
            source_node = node_map.get(flow_data['source'])
            target_node = node_map.get(flow_data['target'])
            
            if not source_node or not target_node:
                logger.warning(
                    f"Skipping flow {flow_data['bpmn_id']}: "
                    f"source({flow_data['source']}) or target({flow_data['target']}) not found."
                )
                continue
                
            SequenceFlow.objects.create(
                workflow=workflow,
                bpmn_id=flow_data['bpmn_id'],
                name=flow_data.get('name', ''),
                source=source_node,
                target=target_node,
                condition_expression=flow_data.get('condition_expression')
            )
            flows_created += 1
            
        logger.info(f"Sync complete: {nodes_created} nodes, {flows_created} flows created for workflow {workflow.key}.")
        return workflow
