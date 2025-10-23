from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.utils.translation import gettext as _

from hr.models import EmployeeBasic, EmployeeFamily, EmployeeMoahil, EmployeeBankAccount
from hr_bot.models import EmployeeTelegramFamily, EmployeeTelegramMoahil, EmployeeTelegramBankAccount


@login_required
def portal_home(request):
    """Employee portal home page"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        
        family_count = EmployeeFamily.objects.filter(employee=employee).count()
        moahil_count = EmployeeMoahil.objects.filter(employee=employee).count()
        bank_account_count = EmployeeBankAccount.objects.filter(employee=employee).count()
        
        pending_family = EmployeeTelegramFamily.objects.filter(employee=employee, state=1).count()
        pending_moahil = EmployeeTelegramMoahil.objects.filter(employee=employee, state=1).count()
        pending_bank = EmployeeTelegramBankAccount.objects.filter(employee=employee, state=1).count()
        
        context = {
            'employee': employee,
            'family_count': family_count,
            'moahil_count': moahil_count,
            'bank_account_count': bank_account_count,
            'pending_family': pending_family,
            'pending_moahil': pending_moahil,
            'pending_bank': pending_bank,
        }
        
        return render(request, 'hr_bot/portal/home.html', context)
    except EmployeeBasic.DoesNotExist:
        return render(request, 'hr_bot/portal/error.html', {
            'error': _('Employee record not found. Please contact HR.')
        })


@login_required
def portal_profile(request):
    """Employee profile page"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        context = {'employee': employee}
        return render(request, 'hr_bot/portal/profile.html', context)
    except EmployeeBasic.DoesNotExist:
        return render(request, 'hr_bot/portal/error.html', {
            'error': _('Employee record not found. Please contact HR.')
        })


@login_required
def portal_family(request):
    """Employee family management page"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        
        approved_families = EmployeeFamily.objects.filter(employee=employee)
        
        pending_families = EmployeeTelegramFamily.objects.filter(employee=employee)
        
        context = {
            'employee': employee,
            'approved_families': approved_families,
            'pending_families': pending_families,
        }
        
        return render(request, 'hr_bot/portal/family.html', context)
    except EmployeeBasic.DoesNotExist:
        return render(request, 'hr_bot/portal/error.html', {
            'error': _('Employee record not found. Please contact HR.')
        })


@login_required
def portal_moahil(request):
    """Employee qualifications management page"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        
        approved_moahils = EmployeeMoahil.objects.filter(employee=employee)
        
        pending_moahils = EmployeeTelegramMoahil.objects.filter(employee=employee)
        
        context = {
            'employee': employee,
            'approved_moahils': approved_moahils,
            'pending_moahils': pending_moahils,
        }
        
        return render(request, 'hr_bot/portal/moahil.html', context)
    except EmployeeBasic.DoesNotExist:
        return render(request, 'hr_bot/portal/error.html', {
            'error': _('Employee record not found. Please contact HR.')
        })


@login_required
def portal_bank_account(request):
    """Employee bank account management page"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        
        approved_accounts = EmployeeBankAccount.objects.filter(employee=employee)
        
        pending_accounts = EmployeeTelegramBankAccount.objects.filter(employee=employee)
        
        context = {
            'employee': employee,
            'approved_accounts': approved_accounts,
            'pending_accounts': pending_accounts,
        }
        
        return render(request, 'hr_bot/portal/bank_account.html', context)
    except EmployeeBasic.DoesNotExist:
        return render(request, 'hr_bot/portal/error.html', {
            'error': _('Employee record not found. Please contact HR.')
        })


def portal_logout(request):
    """Logout view"""
    auth_logout(request)
    return redirect('portal_login')
