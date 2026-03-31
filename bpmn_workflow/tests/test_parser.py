from bpmn_workflow.parser import BPMNParser
from .base import BPMNTestBase

class BPMNParserTest(BPMNTestBase):
    def test_parser_extensions(self):
        """Test parsing of extension elements"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" targetNamespace="http://bpmn.io/schema/bpmn">
          <bpmn:process id="ext_test">
            <bpmn:serviceTask id="task1" name="Task 1">
              <bpmn:extensionElements>
                <someProperty>Value</someProperty>
                <attrProperty key="val" />
              </bpmn:extensionElements>
            </bpmn:serviceTask>
          </bpmn:process>
        </bpmn:definitions>"""
        parser = BPMNParser(xml)
        nodes = parser.parse()['nodes']
        task1 = [n for n in nodes if n['bpmn_id'] == 'task1'][0]
        self.assertEqual(task1['properties'].get('someProperty'), 'Value')
        self.assertIn('attrProperty', task1['properties'])

    def test_parser_no_process(self):
        """Test parser error when no process is found (Line 24)"""
        xml = "<bpmn:definitions xmlns:bpmn=\"http://www.omg.org/spec/BPMN/20100524/MODEL\"></bpmn:definitions>"
        with self.assertRaises(ValueError) as cm:
            BPMNParser(xml)
        self.assertEqual(str(cm.exception), "No BPMN process found in XML")

    def test_parser_comprehensive(self):
        """Test parsing of various node types and condition text"""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" targetNamespace="http://bpmn.io/schema/bpmn">
          <bpmn:process id="comp_test" isExecutable="true">
            <bpmn:scriptTask id="script" name="Script" implementation="python" />
            <bpmn:exclusiveGateway id="exclusive" name="Exclusive" default="flow_default" />
            <bpmn:parallelGateway id="parallel" name="Parallel" />
            <bpmn:inclusiveGateway id="inclusive" name="Inclusive" default="flow_inc_default" />
            <bpmn:intermediateThrowEvent id="intermediate" name="Intermediate" />
            <bpmn:sequenceFlow id="flow1" sourceRef="start" targetRef="end">
              <bpmn:conditionExpression>score > 50</bpmn:conditionExpression>
            </bpmn:sequenceFlow>
          </bpmn:process>
        </bpmn:definitions>"""
        parser = BPMNParser(xml)
        data = parser.parse()
        nodes = data['nodes']
        flows = data['flows']
        
        # Verify node types
        node_types = {n['bpmn_id']: n['node_type'] for n in nodes}
        self.assertEqual(node_types['script'], 'script_task')
        self.assertEqual(node_types['exclusive'], 'exclusive_gateway')
        self.assertEqual(node_types['parallel'], 'parallel_gateway')
        self.assertEqual(node_types['inclusive'], 'inclusive_gateway')
        self.assertEqual(node_types['intermediate'], 'intermediate_event')
        
        # Verify condition text
        flow1 = [f for f in flows if f['bpmn_id'] == 'flow1'][0]
        self.assertEqual(flow1['condition_expression'], 'score > 50')
