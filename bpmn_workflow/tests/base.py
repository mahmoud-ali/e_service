from rest_framework.test import APIClient
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from bpmn_workflow.models import WorkflowDefinition, BPMNNode, SequenceFlow
from bpmn_workflow.engine import BaseWorkflowHandler

User = get_user_model()

class TestHandler(BaseWorkflowHandler):
    def handle_servicetask_1(self, process_instance):
        raise Exception("Custom Service Error")
    
    def handle_fail_task(self, task_instance, user, data):
        raise Exception("Handler broken")
    
    def handle_usertask_1(self, task_instance, user, data):
        """Returns a dict to hit lines 164-167 in engine.py"""
        return {'processed': True, 'score': 100}
    
    def pre_end_event(self, process, user):
        return {'end_ran': True}
    
    def evaluate_gate(self, process):
        return 'f_target'

    def evaluate_gate_crash(self, process):
        raise Exception("Gate logic crash")

class BPMNTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='testuser', password='password', email='test@example.com')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Simple BPMN XML: Start -> UserTask -> ServiceTask -> End
        self.bpmn_xml = """
        <bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" id="Definitions_1">
          <bpmn:process id="Process_1" name="Test Process" isExecutable="true">
            <bpmn:startEvent id="StartEvent_1" name="Start">
                <bpmn:outgoing>Flow_1</bpmn:outgoing>
            </bpmn:startEvent>
            <bpmn:userTask id="UserTask_1" name="User Task">
                <bpmn:incoming>Flow_1</bpmn:incoming>
                <bpmn:outgoing>Flow_2</bpmn:outgoing>
            </bpmn:userTask>
            <bpmn:serviceTask id="ServiceTask_1" name="Service" implementation="">
                <bpmn:incoming>Flow_2</bpmn:incoming>
                <bpmn:outgoing>Flow_3</bpmn:outgoing>
            </bpmn:serviceTask>
            <bpmn:endEvent id="EndEvent_1" name="End">
                <bpmn:incoming>Flow_3</bpmn:incoming>
            </bpmn:endEvent>
            <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="UserTask_1" />
            <bpmn:sequenceFlow id="Flow_2" sourceRef="UserTask_1" targetRef="ServiceTask_1" />
            <bpmn:sequenceFlow id="Flow_3" sourceRef="ServiceTask_1" targetRef="EndEvent_1" />
          </bpmn:process>
        </bpmn:definitions>
        """
        
        self.workflow = WorkflowDefinition.objects.create(
            key='test_workflow',
            name='Test Workflow',
            bpmn_xml=self.bpmn_xml,
            is_active=True
        )
        
        # Manually create nodes
        self.start_node = BPMNNode.objects.create(workflow=self.workflow, bpmn_id='StartEvent_1', node_type='start_event', name='Start')
        self.user_node = BPMNNode.objects.create(workflow=self.workflow, bpmn_id='UserTask_1', node_type='user_task', name='User Task')
        self.service_node = BPMNNode.objects.create(workflow=self.workflow, bpmn_id='ServiceTask_1', node_type='service_task', name='Service', implementation='')
        self.end_node = BPMNNode.objects.create(workflow=self.workflow, bpmn_id='EndEvent_1', node_type='end_event', name='End')
        
        SequenceFlow.objects.create(workflow=self.workflow, bpmn_id='Flow_1', source=self.start_node, target=self.user_node)
        SequenceFlow.objects.create(workflow=self.workflow, bpmn_id='Flow_2', source=self.user_node, target=self.service_node)
        SequenceFlow.objects.create(workflow=self.workflow, bpmn_id='Flow_3', source=self.service_node, target=self.end_node)
        
        self.content_object = self.user

def dummy_function(process_instance):
    """Dummy function for service task testing"""
    return {"status": "success", "variables": {"dummy": "value"}}

def dummy_extra_keys(process):
    return {'status': 'success', 'extra_calc': 123}

def dummy_waiting(process):
    return {'status': 'waiting'}
