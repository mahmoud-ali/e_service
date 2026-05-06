from bpmn_workflow.models import WorkflowDefinition, BPMNNode, SequenceFlow
from bpmn_workflow.generator import WorkflowHandlerGenerator
from .base import BPMNTestBase

class HandlerGeneratorTest(BPMNTestBase):
    def test_generator(self):
        """Test that the handler generator produces valid python code"""
        wf = WorkflowDefinition.objects.create(key='test_workflow_gen', name='Test Workflow Gen', is_active=True)
        BPMNNode.objects.create(workflow=wf, bpmn_id='UserTask_1', node_type='user_task', name='User Task')
        BPMNNode.objects.create(workflow=wf, bpmn_id='ServiceTask_1', node_type='service_task', name='Service')
        gate = BPMNNode.objects.create(workflow=wf, bpmn_id='Gateway_1', node_type='exclusive_gateway', name='My Gateway')
        
        # Add a flow to trigger more code generation
        target = BPMNNode.objects.create(workflow=wf, bpmn_id='End', node_type='end_event')
        SequenceFlow.objects.create(workflow=wf, bpmn_id='flow1', source=gate, target=target, condition_expression="True")
        
        generator = WorkflowHandlerGenerator(wf)
        code = generator.generate()
        
        self.assertIn('class TestWorkflowGenHandler', code)
        self.assertIn('def evaluate_1', code)
        self.assertIn('def handle_user1', code)
        self.assertIn('def handle_service1', code)
