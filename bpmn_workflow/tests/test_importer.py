from bpmn_workflow.models import WorkflowDefinition
from bpmn_workflow.importer import WorkflowSyncService
from .base import BPMNTestBase

class WorkflowImporterTest(BPMNTestBase):
    def test_importer_detailed(self):
        """Test detailed attribute synchronization in WorkflowSyncService"""
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
        <bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" 
            xmlns:camunda="http://camunda.org/schema/1.0/bpmn" targetNamespace="http://bpmn.io/schema/bpmn">
          <bpmn:process id="sync_test" isExecutable="true">
            <bpmn:startEvent id="start" />
            <bpmn:userTask id="user_task" name="User Task" camunda:formKey="test_form" />
            <bpmn:serviceTask id="service_task" name="Service Task" camunda:class="com.test.Handler" />
            <bpmn:endEvent id="end" />
          </bpmn:process>
        </bpmn:definitions>"""
        
        workflow = WorkflowDefinition.objects.create(key='sync_test', bpmn_xml=xml, name='Sync Test')
        WorkflowSyncService.sync(workflow)
        
        user_node = workflow.nodes.get(bpmn_id='user_task')
        self.assertEqual(user_node.form_key, 'test_form')
        
        service_node = workflow.nodes.get(bpmn_id='service_task')
        self.assertEqual(service_node.implementation, 'com.test.Handler')

    def test_importer_empty_xml(self):
        """Test importer error with empty XML (Line 23)"""
        workflow = WorkflowDefinition.objects.create(key='empty_xml', bpmn_xml='')
        with self.assertRaises(ValueError) as cm:
            WorkflowSyncService.sync(workflow)
        self.assertIn("has no BPMN XML content", str(cm.exception))

    def test_importer_name_autofill(self):
        """Test importer auto-fills name from XML (Line 31)"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL">
          <bpmn:process id="named_proc" name="Auto Name">
            <bpmn:startEvent id="start" />
          </bpmn:process>
        </bpmn:definitions>"""
        workflow = WorkflowDefinition.objects.create(key='name_test', bpmn_xml=xml)
        self.assertEqual(workflow.name, '')
        WorkflowSyncService.sync(workflow)
        workflow.refresh_from_db()
        self.assertEqual(workflow.name, 'Auto Name')

    def test_importer_orphan_flows(self):
        """Test importer handles flows with missing nodes (Lines 66-70)"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL">
          <bpmn:process id="orphan_test">
            <bpmn:startEvent id="start" />
            <bpmn:sequenceFlow id="orphan_flow" sourceRef="start" targetRef="ghost_node" />
          </bpmn:process>
        </bpmn:definitions>"""
        workflow = WorkflowDefinition.objects.create(key='orphan_test', bpmn_xml=xml)
        
        with self.assertLogs('bpmn_workflow.importer', level='WARNING') as cm:
            WorkflowSyncService.sync(workflow)
        
        self.assertTrue(any("Skipping flow orphan_flow" in output for output in cm.output))
        self.assertEqual(workflow.flows.count(), 0)
        self.assertEqual(workflow.nodes.count(), 1)
