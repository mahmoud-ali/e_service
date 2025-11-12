from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType

from .models import NeedsRequest, SuggestedItem, Department
from .forms import (
    NeedsRequestForm, 
    ItemFormSet, 
    ItemActionFormSet,
    CommentForm,
    DOACommentForm,
    ITCommentForm,
    DGDHRARecommendationForm,
    DGFARecommendationForm,
    RejectionForm
)
from .permissions import (
    has_read_permission, 
    has_update_permission, 
    has_delete_permission,
    has_action_permission,
    is_operational_employee
)

# BPMN Workflow imports
from bpmn_workflow.engine import BPMNEngine
from bpmn_workflow.models import ProcessInstance, TaskInstance


@login_required
def needs_request_list(request):
    requests_qs = NeedsRequest.objects.order_by('-id')

    # Filtering logic
    request_id = request.GET.get('id')
    date = request.GET.get('date')
    department_id = request.GET.get('department')
    status = request.GET.get('status')

    if request_id:
        requests_qs = requests_qs.filter(id=request_id)
    if date:
        requests_qs = requests_qs.filter(date=date)
    if department_id:
        requests_qs = requests_qs.filter(department_id=department_id)
    
    # Filter by workflow status
    if status:
        if status == 'approved':
            # Filter by workflow status = completed
            content_type = ContentType.objects.get_for_model(NeedsRequest)
            approved_ids = ProcessInstance.objects.filter(
                content_type=content_type,
                status='completed'
            ).values_list('object_id', flat=True)
            requests_qs = requests_qs.filter(id__in=approved_ids)
        elif status == 'rejected':
            # Filter by workflow status = terminated (rejected)
            content_type = ContentType.objects.get_for_model(NeedsRequest)
            rejected_ids = ProcessInstance.objects.filter(
                content_type=content_type,
                status='terminated'
            ).values_list('object_id', flat=True)
            requests_qs = requests_qs.filter(id__in=rejected_ids)
        elif status == 'pending':
            # Filter by workflow status = active
            content_type = ContentType.objects.get_for_model(NeedsRequest)
            pending_ids = ProcessInstance.objects.filter(
                content_type=content_type,
                status='active'
            ).values_list('object_id', flat=True)
            requests_qs = requests_qs.filter(id__in=pending_ids)

    if not is_operational_employee(request.user):
        if request.user.groups.filter(name='eom_pub').exists(): 
            department = request.user.executive_manager_of.first()
            requests_qs = requests_qs.filter(department=department)
        elif request.user.groups.filter(name='dga_pub').exists(): 
            department = request.user.department_manager_of.first()
            requests_qs = requests_qs.filter(department=department)
    
    # Filter requests based on read permissions
    allowed_requests = [req for req in requests_qs if has_read_permission(request.user, req)]
    
    paginator = Paginator(allowed_requests, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    departments = Department.objects.all()
    
    context = {
        'requests': page_obj,
        'departments': departments,
        'current_id': request_id,
        'current_date': date,
        'current_department': department_id,
        'current_status': status,
    }
    
    return render(request, 'needs_request/needs_request_list.html', context)


@login_required
def needs_request_create(request):
    if not request.user.groups.filter(name='eom_pub').exists() and not request.user.is_superuser:
        return render(request, '403.html', status=403)
        
    if request.method == 'POST':
        form = NeedsRequestForm(request.POST)
        if form.is_valid():
            needs_request = form.save(commit=False)
            
            # Set department based on user
            try:
                department = request.user.executive_manager_of.first()
                if department:
                    needs_request.department = department
                else:
                    return render(request, '403.html', status=403)
            except AttributeError:
                return render(request, '403.html', status=403)

            formset = ItemFormSet(request.POST, request.FILES, instance=needs_request, prefix='items')
            if formset.is_valid():
                needs_request.save()
                formset.save()
                
                # START BPMN WORKFLOW
                try:
                    process = BPMNEngine.start_process(
                        workflow_key='needs_request_v1',
                        business_object=needs_request,
                        user=request.user,
                        initial_variables={
                            'department': needs_request.department.name,
                            'date': needs_request.date.isoformat(),
                        }
                    )
                except Exception as e:
                    # Log error but don't fail - workflow can be started manually
                    print(f"Error starting workflow: {e}")
                    raise
                
                return redirect('needs:needs_request_list')
            else:
                return render(request, 'needs_request/needs_request_form.html', {'form': form, 'formset': formset})
        else:
            formset = ItemFormSet(request.POST, request.FILES, prefix='items')
            return render(request, 'needs_request/needs_request_form.html', {'form': form, 'formset': formset})
    else:
        form = NeedsRequestForm()
        formset = ItemFormSet(prefix='items')
    return render(request, 'needs_request/needs_request_form.html', {'form': form, 'formset': formset})


@login_required
def needs_request_update(request, pk):
    needs_request = get_object_or_404(NeedsRequest, pk=pk)
    
    if not has_update_permission(request.user, needs_request):
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        form = NeedsRequestForm(request.POST, instance=needs_request)
        if form.is_valid():
            needs_request = form.save(commit=False)
            formset = ItemFormSet(request.POST, request.FILES, instance=needs_request, prefix='items')
            if formset.is_valid():
                needs_request.save()
                formset.save()
                return redirect('needs:needs_request_list')
            else:
                return render(request, 'needs_request/needs_request_form.html', {'form': form, 'formset': formset})
        else:
            formset = ItemFormSet(request.POST, request.FILES, instance=needs_request, prefix='items')
            return render(request, 'needs_request/needs_request_form.html', {'form': form, 'formset': formset})
    else:
        form = NeedsRequestForm(instance=needs_request)
        formset = ItemFormSet(instance=needs_request, prefix='items')
    return render(request, 'needs_request/needs_request_form.html', {'form': form, 'formset': formset, 'needs_request': needs_request})


@login_required
def needs_request_detail(request, pk):
    needs_request = get_object_or_404(NeedsRequest, pk=pk)
    
    if not has_read_permission(request.user, needs_request):
        return render(request, '403.html', status=403)
    
    if not is_operational_employee(request.user):
        if request.user.groups.filter(name='eom_pub').exists(): 
            department = request.user.executive_manager_of.first()
            if needs_request.department != department:
                return render(request, '403.html', status=403)
        elif request.user.groups.filter(name='dga_pub').exists(): 
            department = request.user.department_manager_of.first()
            if needs_request.department != department:
                return render(request, '403.html', status=403)

    # Get workflow information
    workflow = needs_request.get_workflow()
    current_tasks = needs_request.get_current_tasks()
    timeline = needs_request.get_workflow_timeline()
    
    # Get the current task for this user (if any)
    user_current_task = None
    for task in current_tasks:
        if task.can_be_completed_by(request.user):
            user_current_task = task
            break
    
    # Initialize forms
    comment_form = CommentForm(request.POST or None, instance=needs_request)
    doa_comment_form = DOACommentForm(request.POST or None, instance=needs_request)
    it_comment_form = ITCommentForm(request.POST or None, instance=needs_request)
    dgdhra_form = DGDHRARecommendationForm(request.POST or None, instance=needs_request)
    dgfa_form = DGFARecommendationForm(request.POST or None, instance=needs_request)
    rejection_form = RejectionForm(request.POST or None)
    item_action_formset = ItemActionFormSet(request.POST or None, instance=needs_request)

    if request.method == 'POST':
        action = request.POST.get('action')

        # Handle workflow actions
        if action and user_current_task:
            try:
                task_data = {}
                
                if action == 'dga_approval':
                    task_data = {'approved': True}
                    
                elif action == 'dga_rejection':
                    if rejection_form.is_valid():
                        task_data = {
                            'approved': False,
                            'dga_rejection_cause': rejection_form.cleaned_data['rejection_cause']
                        }
                    
                elif action == 'sd_comment':
                    if comment_form.is_valid():
                        task_data = {'comment': comment_form.cleaned_data['sd_comment']}
                        
                elif action == 'doa_comment':
                    if doa_comment_form.is_valid():
                        task_data = {'comment': doa_comment_form.cleaned_data['doa_comment']}
                        
                elif action == 'it_comment':
                    if it_comment_form.is_valid():
                        task_data = {'comment': it_comment_form.cleaned_data['it_comment']}
                        
                elif action == 'dgdhra_recommendation':
                    if dgdhra_form.is_valid():
                        task_data = {'recommendation': dgdhra_form.cleaned_data['dgdhra_recommendation']}
                        
                elif action == 'dgfa_recommendation':
                    if dgfa_form.is_valid():
                        task_data = {'recommendation': dgfa_form.cleaned_data['dgfa_recommendation']}
                        
                elif action == 'agmfa_approval':
                    task_data = {'approved': True}
                    
                elif action == 'agmfa_rejection':
                    if rejection_form.is_valid():
                        task_data = {
                            'approved': False,
                            'rejection_cause': rejection_form.cleaned_data['rejection_cause']
                        }
                        
                elif action == 'gm_approval':
                    # Collect approved item quantities
                    task_data = {
                        'approved': True,
                    }
                    
                elif action == 'gm_rejection':
                    if rejection_form.is_valid():
                        task_data = {
                            'approved': False,
                            'rejection_cause': rejection_form.cleaned_data['rejection_cause']
                        }
                
                # Complete the workflow task
                if task_data:
                    BPMNEngine.complete_task(
                        task_instance=user_current_task,
                        user=request.user,
                        data=task_data
                    )
                    return redirect('needs:needs_request_detail', pk=pk)
                    
            except Exception as e:
                print(f"Error completing workflow task: {e}")
                raise
        
        # Handle item actions separately
        elif action == 'action_items':
            if item_action_formset.is_valid():
                item_action_formset.save()
                return redirect('needs:needs_request_detail', pk=pk)
                     
    
    return render(request, 'needs_request/needs_request_detail.html', {
        'needs_request': needs_request,
        'workflow': workflow,
        'current_tasks': current_tasks,
        'user_current_task': user_current_task,
        'timeline': timeline,
        'item_action_formset': item_action_formset,
        'comment_form': comment_form,
        'doa_comment_form': doa_comment_form,
        'it_comment_form': it_comment_form,
        'dgdhra_form': dgdhra_form,
        'dgfa_form': dgfa_form,
        'rejection_form': rejection_form,
        'user_can_update': has_update_permission(request.user, needs_request),
        'user_can_delete': has_delete_permission(request.user, needs_request),
    })
