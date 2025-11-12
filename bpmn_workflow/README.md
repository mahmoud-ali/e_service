# BPMN Workflow Engine for Django

A powerful, BPMN 2.0-compliant workflow engine for Django that allows you to design workflows visually using [bpmn.io](https://bpmn.io) and execute them with full audit logging.

## Features

- **Visual Workflow Design**: Design workflows using the industry-standard BPMN 2.0 notation with bpmn.io
- **Auto-Generated Handlers**: Automatically generate Python handler classes from BPMN XML
- **Customizable Logic**: Easy-to-customize handler methods for your business logic
- **Complete Audit Trail**: Every action is logged with timestamp and responsible user
- **Generic & Reusable**: Works with any Django model - attach workflows to any business object
- **Django Admin Integration**: Full admin interface for managing workflows and viewing process instances
- **Multi-tenancy Support**: Multiple versions of workflows can coexist
- **BPMN 2.0 Compliant**: Supports user tasks, service tasks, exclusive/parallel gateways, and more

## Supported BPMN Elements

### Events
- ✅ Start Event
- ✅ End Event
- ⏳ Intermediate Events (partial support)

### Tasks
- ✅ User Task (manual tasks requiring user interaction)
- ✅ Service Task (automated tasks)
- ✅ Script Task
- ⏳ Send/Receive Tasks (planned)

### Gateways
- ✅ Exclusive Gateway (XOR - choose one path)
- ✅ Parallel Gateway (AND - all paths)
- ⏳ Inclusive Gateway (OR - one or more paths)

### Other
- ✅ Sequence Flows (with conditions)
- ✅ Process Variables
- ✅ Candidate Groups

## Installation

### 1. Add to Django Project

Add `'bpmn_workflow'` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'bpmn_workflow',
]
```

### 2. Run Migrations

```bash
python manage.py makemigrations bpmn_workflow
python manage.py migrate bpmn_workflow
```

### 3. Create Handlers Directory

```bash
mkdir -p bpmn_workflow/handlers
touch bpmn_workflow/handlers/__init__.py
```

## Quick Start

### Step 1: Design Your Workflow in bpmn.io

1. Go to [https://bpmn.io/demo/modeler](https://demo.bpmn.io/new)
2. Design your workflow using the visual editor
3. Configure tasks:
   - **User Tasks**: Set `candidateGroups` property (e.g., `dga_pub,sd_pub`)
   - **Gateways**: Add condition expressions on outgoing flows
4. Download the BPMN XML file

Example simple workflow:
```
[Start] → [DGA Approval] → <Gateway> → [Approved End]
                              ↓
                          [Rejected End]
```

### Step 2: Import the BPMN Workflow

```bash
python manage.py import_bpmn path/to/your/workflow.bpmn \
    --key=needs_request_approval \
    --generate-handler \
    --output-dir=bpmn_workflow/handlers/
```

This command will:
- Parse the BPMN XML
- Create WorkflowDefinition and BPMNNode records in the database
- Generate a Python handler class at `bpmn_workflow/handlers/needs_request_approval_handler.py`

### Step 3: Customize the Generated Handler

Edit the generated handler file:

```python
# bpmn_workflow/handlers/needs_request_approval_handler.py

from django.db import transaction
from django.utils import timezone
from typing import Dict, Any
from bpmn_workflow.engine import BaseWorkflowHandler
from bpmn_workflow.models import ProcessInstance, TaskInstance


class NeedsRequestApprovalHandler(BaseWorkflowHandler):
    """Handler for Needs Request Approval Process"""
    
    workflow_key = 'needs_request_approval'
    
    @transaction.atomic
    def handle_dga_approval(
        self, 
        task_instance: TaskInstance, 
        user, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle DGA (Director of General Administration) approval
        """
        # Get the business object (e.g., NeedsRequest)
        needs_request = task_instance.process_instance.content_object
        
        # Your business logic here
        approved = data.get('approved', False)
        comment = data.get('comment', '')
        
        # Update the business object
        needs_request.dga_comment = comment
        needs_request.save()
        
        # Return variables that can be used in gateway conditions
        return {
            'approved': approved,
            'comment': comment,
            'approved_by': user.username,
            'approved_at': timezone.now().isoformat(),
        }
    
    def evaluate_gateway_dga(self, process_instance: ProcessInstance) -> str:
        """
        Evaluate DGA decision gateway
        
        Returns the BPMN ID of the sequence flow to take
        """
        # Get the 'approved' variable set by the previous task
        approved = self.get_variable(process_instance, 'approved')
        
        if approved:
            return 'flow_to_approval'  # BPMN ID of approval flow
        else:
            return 'flow_to_rejection'  # BPMN ID of rejection flow
```

### Step 4: Register the Handler

Update the workflow definition with the handler class path:

```python
from bpmn_workflow.models import WorkflowDefinition

workflow = WorkflowDefinition.objects.get(key='needs_request_approval')
workflow.handler_class = 'bpmn_workflow.handlers.needs_request_approval_handler.NeedsRequestApprovalHandler'
workflow.save()
```

Or via Django admin interface.

### Step 5: Use the Workflow in Your Views

```python
# views.py
from django.shortcuts import render, redirect
from bpmn_workflow.engine import BPMNEngine
from bpmn_workflow.models import ProcessInstance, TaskInstance
from .models import NeedsRequest


def create_needs_request(request):
    """Create a new needs request and start the workflow"""
    if request.method == 'POST':
        # Create your business object
        needs_request = NeedsRequest.objects.create(
            department=request.user.department,
            date=timezone.now().date()
        )
        
        # Start the workflow
        process = BPMNEngine.start_process(
            workflow_key='needs_request_approval',
            business_object=needs_request,
            user=request.user,
            initial_variables={'status': 'pending'}
        )
        
        return redirect('needs_request_detail', pk=needs_request.pk)
    
    return render(request, 'create_form.html')


def needs_request_detail(request, pk):
    """View and act on a needs request"""
    needs_request = NeedsRequest.objects.get(pk=pk)
    
    # Get the workflow process
    process = ProcessInstance.objects.filter(
        content_type__model='needsrequest',
        object_id=needs_request.pk
    ).first()
    
    # Get current active tasks for this user
    current_tasks = process.get_current_tasks().filter(
        node__candidate_groups__contains=[request.user.groups.first().name]
    ) if process else []
    
    # Get activity timeline
    timeline = BPMNEngine.get_timeline(process) if process else []
    
    if request.method == 'POST':
        action = request.POST.get('action')
        task_id = request.POST.get('task_id')
        
        if action == 'complete_task' and task_id:
            task = TaskInstance.objects.get(pk=task_id)
            
            # Complete the task
            BPMNEngine.complete_task(
                task_instance=task,
                user=request.user,
                data={
                    'approved': request.POST.get('approved') == 'true',
                    'comment': request.POST.get('comment', ''),
                }
            )
            
            return redirect('needs_request_detail', pk=pk)
    
    return render(request, 'needs_request_detail.html', {
        'needs_request': needs_request,
        'process': process,
        'current_tasks': current_tasks,
        'timeline': timeline,
    })
```

### Step 6: Create Templates

```django
{# templates/needs_request_detail.html #}
<h1>Needs Request #{{ needs_request.id }}</h1>

<h2>Workflow Status: {{ process.status }}</h2>

{% if current_tasks %}
<div class="current-tasks">
    <h3>Action Required</h3>
    {% for task in current_tasks %}
    <div class="task">
        <h4>{{ task.node.name }}</h4>
        <form method="post">
            {% csrf_token %}
            <input type="hidden" name="action" value="complete_task">
            <input type="hidden" name="task_id" value="{{ task.id }}">
            
            <textarea name="comment" placeholder="Add your comment..."></textarea>
            
            <button type="submit" name="approved" value="true">Approve</button>
            <button type="submit" name="approved" value="false">Reject</button>
        </form>
    </div>
    {% endfor %}
</div>
{% endif %}

<div class="timeline">
    <h3>Approval Timeline</h3>
    <ul>
        {% for log in timeline %}
        <li>
            <strong>{{ log.timestamp|date:"Y-m-d H:i" }}</strong> -
            {{ log.actor.get_full_name|default:log.actor.username }}
            <strong>{{ log.event_type|upper }}</strong>
            {% if log.node %}
            at {{ log.node.name }}
            {% endif %}
            {% if log.details.comment %}
            <p>{{ log.details.comment }}</p>
            {% endif %}
        </li>
        {% endfor %}
    </ul>
</div>
```

## Advanced Usage

### Custom Service Tasks

Service tasks execute automatically without user interaction:

```python
@transaction.atomic
def handle_send_notification(self, process_instance: ProcessInstance) -> Dict[str, Any]:
    """Automatically send email notification"""
    business_object = process_instance.content_object
    approved_by = self.get_variable(process_instance, 'approved_by')
    
    # Send email
    send_mail(
        'Request Approved',
        f'Your request has been approved by {approved_by}',
        'noreply@example.com',
        [business_object.requester.email],
    )
    
    return {
        'notification_sent': True,
        'sent_at': timezone.now().isoformat(),
    }
```

### Conditional Flows (Gateway Expressions)

In bpmn.io, add conditions to sequence flows:

```xml
<sequenceFlow id="Flow_Approved" sourceRef="Gateway_1" targetRef="Task_2">
  <conditionExpression>variables['approved'] == True</conditionExpression>
</sequenceFlow>
```

Or evaluate in the handler:

```python
def evaluate_gateway_amount_check(self, process_instance: ProcessInstance) -> str:
    """Route based on amount"""
    amount = self.get_variable(process_instance, 'total_amount')
    
    if amount > 10000:
        return 'flow_to_gm_approval'  # Requires GM approval
    else:
        return 'flow_to_auto_approve'  # Auto-approve
```

### Parallel Workflows

Use Parallel Gateways for concurrent approvals:

```
         ┌─→ [Finance Approval]  ─┐
[Split] ─┼─→ [Legal Approval]    ─┼─→ [Join] → [Complete]
         └─→ [IT Approval]       ─┘
```

All three approvals happen in parallel and the workflow waits at the join gateway until all are complete.

### Process Variables

Store and retrieve data throughout the workflow:

```python
# Set variable
self.set_variable(process_instance, 'total_cost', 15000)

# Get variable
total = self.get_variable(process_instance, 'total_cost', default=0)
```

### Querying Workflows

```python
# Get all active processes
active_processes = ProcessInstance.objects.filter(status='active')

# Get processes for a specific business object
from django.contenttypes.models import ContentType

ct = ContentType.objects.get_for_model(NeedsRequest)
process = ProcessInstance.objects.get(
    content_type=ct,
    object_id=my_request.id
)

# Get user's pending tasks
my_tasks = TaskInstance.objects.filter(
    status__in=['ready', 'in_progress'],
    node__candidate_groups__contains=[user.groups.first().name]
)

# Get workflow timeline
timeline = process.activity_logs.all()
```

## API Reference

### BPMNEngine

Main engine for executing workflows.

#### `BPMNEngine.start_process(workflow_key, business_object, user, initial_variables=None)`
Start a new workflow instance.

**Parameters:**
- `workflow_key` (str): The workflow definition key
- `business_object` (Model): Django model instance to attach workflow to
- `user` (User): User starting the process
- `initial_variables` (dict, optional): Initial process variables

**Returns:** `ProcessInstance`

#### `BPMNEngine.complete_task(task_instance, user, data)`
Complete a user task.

**Parameters:**
- `task_instance` (TaskInstance): The task to complete
- `user` (User): User completing the task
- `data` (dict): Form data/output

#### `BPMNEngine.get_timeline(process_instance)`
Get complete audit trail.

**Returns:** QuerySet of `ActivityLog`

### BaseWorkflowHandler

Base class for custom handlers.

#### `get_variable(process_instance, key, default=None)`
Get a process variable.

#### `set_variable(process_instance, key, value)`
Set a process variable (automatically logged).

## Management Commands

### import_bpmn

Import a BPMN workflow from XML file.

```bash
python manage.py import_bpmn <bpmn_file> --key=<workflow_key> [options]
```

**Options:**
- `--key`: Required. Workflow key (slug)
- `--generate-handler`: Generate Python handler class
- `--output-dir`: Output directory for handler (default: `bpmn_workflow/handlers/`)
- `--update`: Create new version instead of replacing

**Examples:**

```bash
# Import and generate handler
python manage.py import_bpmn workflows/approval.bpmn \
    --key=approval_process \
    --generate-handler

# Import new version
python manage.py import_bpmn workflows/approval_v2.bpmn \
    --key=approval_process \
    --update
```

## Admin Interface

The app provides a comprehensive Django admin interface:

- **Workflow Definitions**: View and manage workflows
- **Process Instances**: Monitor running processes
- **Task Instances**: View all tasks
- **Activity Logs**: Complete audit trail
- **Tokens**: Debug workflow execution (shows current position)

Access at: `/admin/bpmn_workflow/`

## Best Practices

### 1. Keep Handlers Simple
Handlers should focus on workflow logic. Keep complex business logic in model methods or services.

### 2. Use Process Variables for Gateway Decisions
Store decision data as process variables so gateways can evaluate them:

```python
return {
    'approved': True,
    'amount': 5000,
    'priority': 'high',
}
```

### 3. Test Workflows
Create unit tests for your handlers:

```python
def test_approval_handler():
    handler = NeedsRequestApprovalHandler()
    process = ProcessInstance.objects.create(...)
    task = TaskInstance.objects.create(...)
    
    result = handler.handle_dga_approval(task, user, {'approved': True})
    
    assert result['approved'] == True
    assert handler.get_variable(process, 'approved') == True
```

### 4. Version Control BPMN Files
Store your `.bpmn` files in version control alongside your code.

### 5. Use Descriptive Names
Use clear, descriptive names in bpmn.io for tasks and gateways - these become method names.

### 6. Document Gateway Logic
Add comments explaining routing logic in gateway evaluators.

## Troubleshooting

### Workflow doesn't start
- Check that `is_active=True` on WorkflowDefinition
- Ensure workflow has a start event
- Check logs for errors

### Task doesn't appear for user
- Verify user is in the correct group (candidate_groups)
- Check task status is 'ready' or 'in_progress'
- Ensure process is 'active'

### Gateway doesn't route correctly
- Check gateway evaluator returns valid BPMN flow ID
- Verify process variables are set correctly
- Check condition expressions if using auto-evaluation

### Handler not found
- Verify `handler_class` path is correct
- Ensure handler file is in Python path
- Check for import errors

## Examples

See `bpmn_workflow/examples/` for complete examples:
- Simple approval workflow
- Multi-step review process
- Parallel approval workflow
- Conditional routing

## Contributing

Contributions are welcome! Please ensure:
1. Code follows Django best practices
2. Tests are included
3. Documentation is updated
4. BPMN 2.0 compliance is maintained

## License

MIT License - see LICENSE file

## Credits

- Built with Django
- BPMN 2.0 standard by OMG
- Visual editor: [bpmn.io](https://bpmn.io)

## Support

For issues, questions, or contributions:
- GitHub Issues: [your-repo/issues]
- Documentation: [your-docs-url]
