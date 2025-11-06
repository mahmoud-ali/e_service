from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import NeedsRequest, SuggestedItem, Department
from django.core.paginator import Paginator
from .forms import (
    NeedsRequestForm, 
    ItemFormSet, 
    # ApprovedItemFormSet,
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
from django.contrib.auth.decorators import login_required

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
    if status:
        if status == 'approved':
            requests_qs = requests_qs.filter(approval_status='gm_approval')
        elif status == 'rejected':
            requests_qs = requests_qs.filter(approval_status__in=['dga_rejection', 'agmfa_rejection', 'gm_rejection'])
        elif status == 'pending':
            requests_qs = requests_qs.exclude(approval_status__in=['gm_approval', 'dga_rejection', 'agmfa_rejection', 'gm_rejection'])


    if not is_operational_employee(request.user):
        if request.user.groups.filter(name='eom_pub').exists(): 
            department = request.user.executive_manager_of.first()
            requests_qs = requests_qs.filter(department=department)
        elif request.user.groups.filter(name='dga_pub').exists(): 
            department = request.user.department_manager_of.first()
            requests_qs = requests_qs.filter(department=department)
    
    # Filter requests based on read permissions
    allowed_requests = [req for req in requests_qs if has_read_permission(request.user, req)]
    
    paginator = Paginator(allowed_requests, 50) # Show 50 requests per page
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
                    # Handle case where user is not an executive manager of any department
                    return render(request, '403.html', status=403)
            except AttributeError:
                # Handle case where user is not an executive manager of any department
                return render(request, '403.html', status=403)

            formset = ItemFormSet(request.POST, request.FILES, instance=needs_request, prefix='items')
            if formset.is_valid():
                needs_request.save()
                formset.save()
                return redirect('needs_request_list')
            else:
                # Add formset errors to the context
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
    form = None
    formset = None

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
                return redirect('needs_request_list')
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

    # Initialize all possible forms
    comment_form = CommentForm(request.POST or None, instance=needs_request)
    doa_comment_form = DOACommentForm(request.POST or None, instance=needs_request)
    it_comment_form = ITCommentForm(request.POST or None, instance=needs_request)
    dgdhra_form = DGDHRARecommendationForm(request.POST or None, instance=needs_request)
    dgfa_form = DGFARecommendationForm(request.POST or None, instance=needs_request)
    rejection_form = RejectionForm(request.POST or None)
    
    # approved_item_formset = ApprovedItemFormSet(request.POST or None, instance=needs_request)

    if request.method == 'POST':
        action = request.POST.get('action')

        if not has_action_permission(request.user, needs_request, action):
            return render(request, '403.html', status=403)

        # if action == 'approve_items':
        #     if approved_item_formset.is_valid():
        #         approved_item_formset.save()
        #         return redirect('needs_request_detail', pk=pk)

        if action == 'dga_approval':
            needs_request.approval_status = 'dga_approval'
            needs_request.rejection_cause = None
            needs_request.save()
            return redirect('needs_request_detail', pk=pk)
            
        elif action == 'sd_comment':
            if comment_form.is_valid():
                comment_form.save()
                needs_request.approval_status = 'sd_comment'
                needs_request.save()
                return redirect('needs_request_detail', pk=pk)
                
        elif action == 'doa_comment':
            if doa_comment_form.is_valid():
                doa_comment_form.save()
                needs_request.approval_status = 'doa_comment'
                needs_request.save()
                return redirect('needs_request_detail', pk=pk)
                
        elif action == 'it_comment':
            if it_comment_form.is_valid():
                it_comment_form.save()
                needs_request.approval_status = 'it_comment'
                needs_request.save()
                return redirect('needs_request_detail', pk=pk)
                
        elif action == 'dgdhra_recommendation':
            if dgdhra_form.is_valid():
                dgdhra_form.save()
                needs_request.approval_status = 'dgdhra_recommendation'
                needs_request.save()
                return redirect('needs_request_detail', pk=pk)
                
        elif action == 'dgfa_recommendation':
            if dgfa_form.is_valid():
                dgfa_form.save()
                needs_request.approval_status = 'dgfa_recommendation'
                needs_request.save()
                return redirect('needs_request_detail', pk=pk)
                
        elif action == 'agmfa_approval':
            needs_request.approval_status = 'agmfa_approval'
            needs_request.rejection_cause = None
            needs_request.save()
            return redirect('needs_request_detail', pk=pk)
            
        elif action == 'gm_approval':
            needs_request.approval_status = 'gm_approval'
            needs_request.rejection_cause = None
            needs_request.save()
            return redirect('needs_request_detail', pk=pk)
                     
        elif action == 'dga_rejection':
            if rejection_form.is_valid():
                needs_request.approval_status = 'dga_rejection'
                needs_request.rejection_cause = rejection_form.cleaned_data['rejection_cause']
                needs_request.save()
                return redirect('needs_request_detail', pk=pk)
                
        elif action == 'agmfa_rejection':
            if rejection_form.is_valid():
                needs_request.approval_status = 'agmfa_rejection'
                needs_request.rejection_cause = rejection_form.cleaned_data['rejection_cause']
                needs_request.save()
                return redirect('needs_request_detail', pk=pk)
                
        elif action == 'gm_rejection':
            if rejection_form.is_valid():
                needs_request.approval_status = 'gm_rejection'
                needs_request.rejection_cause = rejection_form.cleaned_data['rejection_cause']
                needs_request.save()
                return redirect('needs_request_detail', pk=pk)
                    
    return render(request, 'needs_request/needs_request_detail.html', {
        'needs_request': needs_request, 
        # 'approved_item_formset': approved_item_formset,
        'comment_form': comment_form,
        'doa_comment_form': doa_comment_form,
        'it_comment_form': it_comment_form,
        'dgdhra_form': dgdhra_form,
        'dgfa_form': dgfa_form,
        'rejection_form': rejection_form,
        'user_can_update': has_update_permission(request.user, needs_request),
        'user_can_delete': has_delete_permission(request.user, needs_request),
    })

