import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO
import csv

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q, Sum

from fleet.models import FuelMonthlyStatement, FuelDistributionItem, FuelBeneficiarySetting
from hr.models import EmployeeBasic


@login_required
def fuel_statement_list(request):
    """عرض قائمة كشوفات الوقود الشهرية"""
    statements = FuelMonthlyStatement.objects.all()
    return redirect('/managers/fleet/fuelmonthlystatement/')


@login_required
def fuel_statement_detail(request, statement_id):
    """عرض تفاصيل كشف الوقود الشهري"""
    return redirect(f'/managers/fleet/fuelmonthlystatement/{statement_id}/change/')


@login_required
def generate_fuel_statement_items(request, statement_id):
    """توليد بنود الكشف الشهري"""
    return redirect(f'/managers/fleet/fuelmonthlystatement/{statement_id}/change/')


@login_required
@require_POST
def fuel_item_save(request, statement_id):
    """حفظ بند وقود"""
    return redirect(f'/managers/fleet/fuelmonthlystatement/{statement_id}/change/')


@login_required
@require_POST
def fuel_item_delete(request, statement_id, item_id):
    """حذف بند وقود"""
    item = get_object_or_404(FuelDistributionItem, pk=item_id, statement_id=statement_id)
    item.delete()
    return redirect(f'/managers/fleet/fuelmonthlystatement/{statement_id}/change/')


@login_required
def import_fuel_excel(request, statement_id):
    """استيراد ملف إكسل الكشف"""
    return redirect(f'/managers/fleet/fuelmonthlystatement/{statement_id}/change/')


@login_required
def export_fuel_excel(request, statement_id):
    """تصدير الكشف لإكسل"""
    return redirect(f'/managers/fleet/fuelmonthlystatement/{statement_id}/export-csv/')


def api_hr_employees(request):
    """API للبحث عن موظفي الموارد البشرية"""
    query = request.GET.get('q', '').strip()
    employees_qs = EmployeeBasic.objects.filter(status=EmployeeBasic.STATUS_ACTIVE)

    if query:
        q_filter = Q(name__icontains=query) | Q(email__icontains=query)
        if query.isdigit():
            q_filter |= Q(code=int(query))
        employees_qs = employees_qs.filter(q_filter)

    employees_qs = employees_qs.select_related('mosama_wazifi', 'hikal_wazifi')[:50]

    results = []
    for emp in employees_qs:
        dept_name = emp.hikal_wazifi.name if emp.hikal_wazifi else ""
        results.append({
            'id': emp.id,
            'code': emp.code,
            'name': emp.name,
            'email': emp.email or '',
            'job_title': emp.mosama_wazifi.name if emp.mosama_wazifi else '',
            'department': dept_name
        })

    return JsonResponse({'results': results})


@login_required
def fuel_beneficiaries_setting(request):
    """صفحة مستفيدي الوقود"""
    return redirect('/managers/fleet/fuelbeneficiarysetting/')


@login_required
@require_POST
def fuel_beneficiary_setting_save(request):
    """حفظ مستفيد وقود"""
    return redirect('/managers/fleet/fuelbeneficiarysetting/')


@login_required
@require_POST
def fuel_beneficiary_setting_toggle(request, setting_id):
    """تفعيل/إلغاء تفعيل مستفيد"""
    setting = get_object_or_404(FuelBeneficiarySetting, pk=setting_id)
    setting.is_active_for_fuel = not setting.is_active_for_fuel
    setting.save()
    return redirect('/managers/fleet/fuelbeneficiarysetting/')