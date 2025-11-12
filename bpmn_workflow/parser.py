"""
BPMN Parser

Parses BPMN 2.0 XML files and extracts workflow structure.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional


class BPMNParser:
    """Parse BPMN 2.0 XML files"""
    
    BPMN_NS = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}
    BPMNDI_NS = {'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI'}
    
    def __init__(self, bpmn_xml: str):
        """Initialize parser with BPMN XML content"""
        self.root = ET.fromstring(bpmn_xml)
        self.process = self.root.find('.//bpmn:process', self.BPMN_NS)
        
        if self.process is None:
            raise ValueError("No BPMN process found in XML")
    
    def parse(self) -> Dict:
        """Parse BPMN and return structured data"""
        return {
            'process_id': self.process.get('id'),
            'process_name': self.process.get('name', 'Unnamed Process'),
            'nodes': self._parse_nodes(),
            'flows': self._parse_flows(),
        }
    
    def _parse_nodes(self) -> List[Dict]:
        """Parse all BPMN elements"""
        nodes = []
        
        # Start Events
        for elem in self.process.findall('.//bpmn:startEvent', self.BPMN_NS):
            nodes.append({
                'bpmn_id': elem.get('id'),
                'node_type': 'start_event',
                'name': elem.get('name', 'Start'),
                'properties': self._parse_extension_elements(elem),
            })
        
        # User Tasks
        for elem in self.process.findall('.//bpmn:userTask', self.BPMN_NS)+self.process.findall('.//bpmn:task', self.BPMN_NS):
            candidate_groups = elem.get('{http://task_details}candidateGroups', '').split(',') if elem.get('{http://task_details}candidateGroups') else []
            candidate_groups = [g.strip() for g in candidate_groups if g.strip()]
            
            nodes.append({
                'bpmn_id': elem.get('id'),
                'node_type': 'user_task',
                'name': elem.get('name', 'User Task'),
                'assignee_expression': elem.get('assignee', ''),
                'candidate_groups': candidate_groups,
                'form_key': elem.get('{http://task_details}viewURL', ''),
                'properties': self._parse_extension_elements(elem),
            })
        
        # Service Tasks
        for elem in self.process.findall('.//bpmn:serviceTask', self.BPMN_NS):
            nodes.append({
                'bpmn_id': elem.get('id'),
                'node_type': 'service_task',
                'name': elem.get('name', 'Service Task'),
                'implementation': elem.get('implementation', ''),
                'properties': self._parse_extension_elements(elem),
            })
        
        # Script Tasks
        for elem in self.process.findall('.//bpmn:scriptTask', self.BPMN_NS):
            nodes.append({
                'bpmn_id': elem.get('id'),
                'node_type': 'script_task',
                'name': elem.get('name', 'Script Task'),
                'implementation': elem.get('implementation', 'python'),
                'properties': self._parse_extension_elements(elem),
            })
        
        # Exclusive Gateways
        for elem in self.process.findall('.//bpmn:exclusiveGateway', self.BPMN_NS):
            nodes.append({
                'bpmn_id': elem.get('id'),
                'node_type': 'exclusive_gateway',
                'name': elem.get('name', 'Gateway'),
                'default_flow': elem.get('default'),
                'properties': self._parse_extension_elements(elem),
            })
        
        # Parallel Gateways
        for elem in self.process.findall('.//bpmn:parallelGateway', self.BPMN_NS):
            nodes.append({
                'bpmn_id': elem.get('id'),
                'node_type': 'parallel_gateway',
                'name': elem.get('name', 'Parallel Gateway'),
                'properties': self._parse_extension_elements(elem),
            })
        
        # Inclusive Gateways
        for elem in self.process.findall('.//bpmn:inclusiveGateway', self.BPMN_NS):
            nodes.append({
                'bpmn_id': elem.get('id'),
                'node_type': 'inclusive_gateway',
                'name': elem.get('name', 'Inclusive Gateway'),
                'default_flow': elem.get('default'),
                'properties': self._parse_extension_elements(elem),
            })
        
        # End Events
        for elem in self.process.findall('.//bpmn:endEvent', self.BPMN_NS):
            nodes.append({
                'bpmn_id': elem.get('id'),
                'node_type': 'end_event',
                'name': elem.get('name', 'End'),
                'properties': self._parse_extension_elements(elem),
            })
        
        # Intermediate Events
        for elem in self.process.findall('.//bpmn:intermediateThrowEvent', self.BPMN_NS):
            nodes.append({
                'bpmn_id': elem.get('id'),
                'node_type': 'intermediate_event',
                'name': elem.get('name', 'Intermediate Event'),
                'properties': self._parse_extension_elements(elem),
            })
        
        return nodes
    
    def _parse_flows(self) -> List[Dict]:
        """Parse sequence flows"""
        flows = []
        
        for elem in self.process.findall('.//bpmn:sequenceFlow', self.BPMN_NS):
            condition = None
            condition_elem = elem.find('.//bpmn:conditionExpression', self.BPMN_NS)
            if condition_elem is not None:
                condition = condition_elem.text
            
            flows.append({
                'bpmn_id': elem.get('id'),
                'name': elem.get('name', ''),
                'source': elem.get('sourceRef'),
                'target': elem.get('targetRef'),
                'condition_expression': condition,
            })
        
        return flows
    
    def _parse_extension_elements(self, elem) -> Dict:
        """Parse custom extension properties from BPMN"""
        properties = {}
        
        # Try to find extensionElements
        ext_elem = elem.find('.//bpmn:extensionElements', self.BPMN_NS)
        if ext_elem is not None:
            # Parse all child elements as properties
            for child in ext_elem:
                # Remove namespace from tag
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                
                # Get text content or attributes
                if child.text and child.text.strip():
                    properties[tag] = child.text.strip()
                elif child.attrib:
                    properties[tag] = dict(child.attrib)
        
        return properties
