from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from .models import EmployeeSolarSystem, LkpSolarSystemCategory, LkpSolarSystemPaymentMethod

@login_required
def portal_home(request):
    """Manager portal home page with statistics"""
    if not request.user.groups.filter(name__in=["hr_manager", "hr_manpower"]).exists():
        messages.error(request, _("You don't have permission to access this page."))
        return redirect('admin:index')
    
    # Get statistics
    total_registrations = EmployeeSolarSystem.objects.count()
    registrations_by_category = EmployeeSolarSystem.objects.values(
        'category__name'
    ).annotate(count=Count('id')).order_by('-count')
    
    registrations_by_payment = EmployeeSolarSystem.objects.values(
        'payment_method__name'
    ).annotate(count=Count('id')).order_by('-count')
    
    recent_registrations = EmployeeSolarSystem.objects.select_related(
        'employee', 'category', 'payment_method'
    ).order_by('-created_at')[:10]
    
    context = {
        'total_registrations': total_registrations,
        'registrations_by_category': registrations_by_category,
        'registrations_by_payment': registrations_by_payment,
        'recent_registrations': recent_registrations,
    }
    
    return render(request, 'sandog/portal_home.html', context)

@login_required
def registration_list(request):
    """List all solar system registrations"""
    if not request.user.groups.filter(name__in=["hr_manager", "hr_manpower"]).exists():
        messages.error(request, _("You don't have permission to access this page."))
        return redirect('admin:index')
    
    # Get filter parameters
    category_id = request.GET.get('category')
    payment_method_id = request.GET.get('payment_method')
    search = request.GET.get('search', '')
    
    # Base queryset
    registrations = EmployeeSolarSystem.objects.select_related(
        'employee', 'category', 'payment_method', 'created_by'
    ).all()
    
    # Apply filters
    if category_id:
        registrations = registrations.filter(category_id=category_id)
    
    if payment_method_id:
        registrations = registrations.filter(payment_method_id=payment_method_id)
    
    if search:
        registrations = registrations.filter(employee__name__icontains=search)
    
    # Get filter options
    categories = LkpSolarSystemCategory.objects.all()
    payment_methods = LkpSolarSystemPaymentMethod.objects.all()
    
    context = {
        'registrations': registrations,
        'categories': categories,
        'payment_methods': payment_methods,
        'selected_category': category_id,
        'selected_payment_method': payment_method_id,
        'search': search,
    }
    
    return render(request, 'sandog/registration_list.html', context)

@login_required
def registration_detail(request, pk):
    """View details of a specific registration"""
    if not request.user.groups.filter(name__in=["hr_manager", "hr_manpower"]).exists():
        messages.error(request, _("You don't have permission to access this page."))
        return redirect('admin:index')
    
    registration = get_object_or_404(
        EmployeeSolarSystem.objects.select_related(
            'employee', 'category', 'payment_method', 'created_by', 'updated_by'
        ),
        pk=pk
    )
    
    context = {
        'registration': registration,
    }
    
    return render(request, 'sandog/registration_detail.html', context)

@login_required
def category_list(request):
    """List all solar system categories"""
    if not request.user.groups.filter(name__in=["hr_manager", "hr_manpower"]).exists():
        messages.error(request, _("You don't have permission to access this page."))
        return redirect('admin:index')
    
    categories = LkpSolarSystemCategory.objects.annotate(
        registration_count=Count('employeesolarsystem')
    ).order_by('id')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'sandog/category_list.html', context)

@login_required
def payment_method_list(request):
    """List all payment methods"""
    if not request.user.groups.filter(name__in=["hr_manager", "hr_manpower"]).exists():
        messages.error(request, _("You don't have permission to access this page."))
        return redirect('admin:index')
    
    payment_methods = LkpSolarSystemPaymentMethod.objects.annotate(
        registration_count=Count('employeesolarsystem')
    ).order_by('id')
    
    context = {
        'payment_methods': payment_methods,
    }
    
    return render(request, 'sandog/payment_method_list.html', context)
