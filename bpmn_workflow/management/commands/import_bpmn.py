"""
Management command to import BPMN workflows from XML files.
"""

import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from bpmn_workflow.parser import BPMNParser
from bpmn_workflow.models import WorkflowDefinition, BPMNNode, SequenceFlow
from bpmn_workflow.generator import WorkflowHandlerGenerator

def ensure_trailing_slash(output_dir: str) -> str:
    """Ensure the given folder path always ends with a slash (/)"""
    if not output_dir.endswith('/'):
        output_dir += '/'
    return output_dir

class Command(BaseCommand):
    help = 'Import BPMN workflow definition and optionally generate handler class'

    def add_arguments(self, parser):
        parser.add_argument(
            'bpmn_file', 
            type=str, 
            help='Path to BPMN XML file'
        )
        parser.add_argument(
            '--key', 
            type=str, 
            required=True, 
            help='Workflow key (slug identifier, e.g., "needs_request_approval")'
        )
        parser.add_argument(
            '--generate-handler',
            action='store_true',
            help='Generate Python handler class'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='bpmn_workflow/handlers/',
            help='Output directory for generated handler (default: bpmn_workflow/handlers/)'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing workflow (increments version)'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        bpmn_file = options['bpmn_file']
        workflow_key = options['key']
        
        # Validate file exists
        if not os.path.exists(bpmn_file):
            raise CommandError(f"BPMN file not found: {bpmn_file}")
        
        # Read BPMN file
        self.stdout.write(f"Reading BPMN file: {bpmn_file}")
        try:
            with open(bpmn_file, 'r', encoding='utf-8') as f:
                bpmn_xml = f.read()
        except Exception as e:
            raise CommandError(f"Error reading file: {e}")
        
        # Parse BPMN
        self.stdout.write("Parsing BPMN XML...")
        try:
            parser = BPMNParser(bpmn_xml)
            parsed_data = parser.parse()
        except Exception as e:
            raise CommandError(f"Error parsing BPMN: {e}")
        
        self.stdout.write(self.style.SUCCESS(f"✓ Parsed process: {parsed_data['process_name']}"))
        self.stdout.write(f"  - Process ID: {parsed_data['process_id']}")
        self.stdout.write(f"  - Nodes: {len(parsed_data['nodes'])}")
        self.stdout.write(f"  - Flows: {len(parsed_data['flows'])}")
        
        # Create or update WorkflowDefinition
        if options['update']:
            # Get latest version and increment
            latest = WorkflowDefinition.objects.filter(key=workflow_key).order_by('-version').first()
            next_version = (latest.version + 1) if latest else 1
            
            workflow = WorkflowDefinition.objects.create(
                key=workflow_key,
                name=parsed_data['process_name'],
                bpmn_xml=bpmn_xml,
                bpmn_process_id=parsed_data['process_id'],
                version=next_version,
                is_active=True
            )
            
            # Deactivate old versions
            if latest:
                WorkflowDefinition.objects.filter(
                    key=workflow_key
                ).exclude(id=workflow.id).update(is_active=False)
            
            self.stdout.write(self.style.SUCCESS(f"✓ Created new version {next_version} of workflow: {workflow.name}"))
        else:
            # Create new or replace existing
            workflow, created = WorkflowDefinition.objects.update_or_create(
                key=workflow_key,
                defaults={
                    'name': parsed_data['process_name'],
                    'bpmn_xml': bpmn_xml,
                    'bpmn_process_id': parsed_data['process_id'],
                }
            )
            
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"✓ {action} workflow: {workflow.name}"))
        
        # Clear existing nodes and flows
        self.stdout.write("Clearing existing nodes and flows...")
        workflow.nodes.all().delete()
        workflow.flows.all().delete()
        
        # Create nodes
        self.stdout.write(f"Creating {len(parsed_data['nodes'])} nodes...")
        node_map = {}  # bpmn_id -> BPMNNode instance
        
        for node_data in parsed_data['nodes']:
            node = BPMNNode.objects.create(
                workflow=workflow,
                **node_data
            )
            node_map[node_data['bpmn_id']] = node
            
            icon = self._get_node_icon(node.node_type)
            self.stdout.write(f"  {icon} {node.name} ({node.node_type})")
        
        # Create flows
        self.stdout.write(f"Creating {len(parsed_data['flows'])} sequence flows...")
        for flow_data in parsed_data['flows']:
            source_id = flow_data.pop('source')
            target_id = flow_data.pop('target')
            
            if source_id not in node_map or target_id not in node_map:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠ Skipping flow {flow_data['bpmn_id']}: missing node"
                    )
                )
                continue
            
            SequenceFlow.objects.create(
                workflow=workflow,
                source=node_map[source_id],
                target=node_map[target_id],
                **flow_data
            )
            
            flow_name = flow_data.get('name', '')
            condition = f" [if {flow_data.get('condition_expression', '')}]" if flow_data.get('condition_expression') else ''
            self.stdout.write(f"  → {node_map[source_id].name} → {node_map[target_id].name}{condition}")
        
        # Generate handler class
        if options['generate_handler'] or options['output_dir']:
            self.stdout.write("\nGenerating handler class...")
            
            generator = WorkflowHandlerGenerator(workflow)
            handler_code = generator.generate()
            class_name = generator._to_class_name(workflow.key)
            
            output_dir = ensure_trailing_slash(options['output_dir'])
            os.makedirs(output_dir, exist_ok=True)
            
            handler_file = os.path.join(output_dir, f'{workflow_key}_handler.py')
            with open(handler_file, 'w', encoding='utf-8') as f:
                f.write(handler_code)

            workflow.handler_class = output_dir.replace('/', '.')+'.'+f'{workflow_key}_handler.'+class_name
            workflow.save()

            self.stdout.write(self.style.SUCCESS(f"✓ Generated handler: {handler_file}"))
            self.stdout.write(self.style.WARNING("\nIMPORTANT: Remember to customize the handler methods!"))
            self.stdout.write(f"  1. Edit {handler_file}")
            self.stdout.write(f"  2. Implement business logic in each method")
            self.stdout.write(f"  3. Update workflow with handler path:")
            self.stdout.write(f"     handler_class = 'bpmn_workflow.handlers.{workflow_key}_handler.{generator._to_class_name(workflow_key)}'")
        
        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"✓ Successfully imported workflow: {workflow.key}"))
        self.stdout.write("="*60)
        self.stdout.write(f"Workflow ID: {workflow.id}")
        self.stdout.write(f"Version: {workflow.version}")
        self.stdout.write(f"Nodes: {workflow.nodes.count()}")
        self.stdout.write(f"Flows: {workflow.flows.count()}")
        
        # Next steps
        self.stdout.write("\nNext steps:")
        self.stdout.write("1. Implement handler methods (if generated)")
        self.stdout.write("2. Test workflow:")
        self.stdout.write(f"   from bpmn_workflow.engine import BPMNEngine")
        self.stdout.write(f"   process = BPMNEngine.start_process('{workflow_key}', your_object, user)")
        self.stdout.write("3. View workflow in Django admin")
    
    def _get_node_icon(self, node_type):
        """Get icon for node type"""
        icons = {
            'start_event': '▶',
            'end_event': '⏹',
            'user_task': '👤',
            'service_task': '⚙',
            'script_task': '📝',
            'exclusive_gateway': '◆',
            'parallel_gateway': '⊕',
            'inclusive_gateway': '⬡',
            'intermediate_event': '⏸',
        }
        return icons.get(node_type, '•')
