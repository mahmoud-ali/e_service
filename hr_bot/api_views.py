from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.utils.translation import gettext as _
from django.utils import timezone
import json

from hr_bot.models import (
    EmployeeTelegram, EmployeeTelegramFamily, EmployeeTelegramMoahil,
    EmployeeTelegramBankAccount, STATE_DRAFT, STATE_ACCEPTED, STATE_REJECTED
)
from hr.models import EmployeeBasic


@login_required
@require_http_methods(["GET"])
def get_employee_data(request):
    """Get employee basic data"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        data = {
            'code': employee.code,
            'name': employee.name,
            'draja_wazifia': employee.draja_wazifia,
            'alawa_sanawia': employee.alawa_sanawia,
            'hikal_wazifi': employee.hikal_wazifi,
            'mosama_wazifi': employee.mosama_wazifi,
            'sex': employee.sex,
            'tarikh_milad': employee.tarikh_milad.isoformat() if employee.tarikh_milad else None,
            'tarikh_ta3in': employee.tarikh_ta3in.isoformat() if employee.tarikh_ta3in else None,
            'tarikh_akhir_targia': employee.tarikh_akhir_targia.isoformat() if employee.tarikh_akhir_targia else None,
            'gasima': employee.gasima,
            'atfal': employee.atfal,
            'moahil': employee.moahil,
            'phone': employee.phone,
            'email': employee.email,
            'no3_2lertibat': employee.no3_2lertibat,
            'sanoat_2lkhibra': employee.sanoat_2lkhibra,
            'aadoa': employee.aadoa,
            'm3ash': employee.m3ash,
            'status': employee.status,
        }
        return JsonResponse({'success': True, 'data': data})
    except EmployeeBasic.DoesNotExist:
        return JsonResponse({'success': False, 'error': _('Employee not found')}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_family_list(request):
    """Get employee family members"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        families = EmployeeTelegramFamily.objects.filter(employee=employee)
        
        data = [{
            'id': f.id,
            'relation': f.relation,
            'name': f.name,
            'tarikh_el2dafa': f.tarikh_el2dafa.isoformat() if f.tarikh_el2dafa else None,
            'attachement_file': f.attachement_file.url if f.attachement_file else None,
            'state': f.state,
            'created_at': f.created_at.isoformat() if f.created_at else None,
        } for f in families]
        
        return JsonResponse({'success': True, 'data': data})
    except EmployeeBasic.DoesNotExist:
        return JsonResponse({'success': False, 'error': _('Employee not found')}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def create_family(request):
    """Create new family member"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        
        relation = request.POST.get('relation')
        name = request.POST.get('name')
        tarikh_el2dafa = request.POST.get('tarikh_el2dafa')
        attachement_file = request.FILES.get('attachement_file')
        
        family = EmployeeTelegramFamily.objects.create(
            employee=employee,
            relation=relation,
            name=name,
            tarikh_el2dafa=tarikh_el2dafa if tarikh_el2dafa else None,
            attachement_file=attachement_file,
            state=STATE_DRAFT,
            created_by=request.user,
            updated_by=request.user,
        )
        
        return JsonResponse({
            'success': True,
            'message': _('Family member added successfully'),
            'data': {
                'id': family.id,
                'relation': family.relation,
                'name': family.name,
                'state': family.state,
            }
        })
    except EmployeeBasic.DoesNotExist:
        return JsonResponse({'success': False, 'error': _('Employee not found')}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def delete_family(request, family_id):
    """Delete family member (only if in draft state)"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        family = EmployeeTelegramFamily.objects.get(id=family_id, employee=employee)
        
        if family.state != STATE_DRAFT:
            return JsonResponse({
                'success': False,
                'error': _('Cannot delete non-draft records')
            }, status=400)
        
        family.delete()
        return JsonResponse({'success': True, 'message': _('Family member deleted successfully')})
    except EmployeeTelegramFamily.DoesNotExist:
        return JsonResponse({'success': False, 'error': _('Family member not found')}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_moahil_list(request):
    """Get employee qualifications"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        moahils = EmployeeTelegramMoahil.objects.filter(employee=employee)
        
        data = [{
            'id': m.id,
            'moahil': m.moahil,
            'university': m.university,
            'takhasos': m.takhasos,
            'graduate_dt': m.graduate_dt.isoformat() if m.graduate_dt else None,
            'attachement_file': m.attachement_file.url if m.attachement_file else None,
            'state': m.state,
            'created_at': m.created_at.isoformat() if m.created_at else None,
        } for m in moahils]
        
        return JsonResponse({'success': True, 'data': data})
    except EmployeeBasic.DoesNotExist:
        return JsonResponse({'success': False, 'error': _('Employee not found')}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def create_moahil(request):
    """Create new qualification"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        
        moahil = request.POST.get('moahil')
        university = request.POST.get('university')
        takhasos = request.POST.get('takhasos')
        graduate_dt = request.POST.get('graduate_dt')
        attachement_file = request.FILES.get('attachement_file')
        
        moahil_obj = EmployeeTelegramMoahil.objects.create(
            employee=employee,
            moahil=moahil,
            university=university,
            takhasos=takhasos,
            graduate_dt=graduate_dt if graduate_dt else None,
            attachement_file=attachement_file,
            state=STATE_DRAFT,
            created_by=request.user,
            updated_by=request.user,
        )
        
        return JsonResponse({
            'success': True,
            'message': _('Qualification added successfully'),
            'data': {
                'id': moahil_obj.id,
                'moahil': moahil_obj.moahil,
                'university': moahil_obj.university,
                'state': moahil_obj.state,
            }
        })
    except EmployeeBasic.DoesNotExist:
        return JsonResponse({'success': False, 'error': _('Employee not found')}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def delete_moahil(request, moahil_id):
    """Delete qualification (only if in draft state)"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        moahil = EmployeeTelegramMoahil.objects.get(id=moahil_id, employee=employee)
        
        if moahil.state != STATE_DRAFT:
            return JsonResponse({
                'success': False,
                'error': _('Cannot delete non-draft records')
            }, status=400)
        
        moahil.delete()
        return JsonResponse({'success': True, 'message': _('Qualification deleted successfully')})
    except EmployeeTelegramMoahil.DoesNotExist:
        return JsonResponse({'success': False, 'error': _('Qualification not found')}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_bank_account_list(request):
    """Get employee bank accounts"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        accounts = EmployeeTelegramBankAccount.objects.filter(employee=employee)
        
        data = [{
            'id': a.id,
            'bank': a.bank,
            'account_no': a.account_no,
            'active': a.active,
            'state': a.state,
            'created_at': a.created_at.isoformat() if a.created_at else None,
        } for a in accounts]
        
        return JsonResponse({'success': True, 'data': data})
    except EmployeeBasic.DoesNotExist:
        return JsonResponse({'success': False, 'error': _('Employee not found')}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def create_bank_account(request):
    """Create new bank account"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        
        bank = request.POST.get('bank')
        account_no = request.POST.get('account_no')
        active = request.POST.get('active') == 'true'
        
        account = EmployeeTelegramBankAccount.objects.create(
            employee=employee,
            bank=bank,
            account_no=account_no,
            active=active,
            state=STATE_DRAFT,
            created_by=request.user,
            updated_by=request.user,
        )
        
        return JsonResponse({
            'success': True,
            'message': _('Bank account added successfully'),
            'data': {
                'id': account.id,
                'bank': account.bank,
                'account_no': account.account_no,
                'state': account.state,
            }
        })
    except EmployeeBasic.DoesNotExist:
        return JsonResponse({'success': False, 'error': _('Employee not found')}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def delete_bank_account(request, account_id):
    """Delete bank account (only if in draft state)"""
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        account = EmployeeTelegramBankAccount.objects.get(id=account_id, employee=employee)
        
        if account.state != STATE_DRAFT:
            return JsonResponse({
                'success': False,
                'error': _('Cannot delete non-draft records')
            }, status=400)
        
        account.delete()
        return JsonResponse({'success': True, 'message': _('Bank account deleted successfully')})
    except EmployeeTelegramBankAccount.DoesNotExist:
        return JsonResponse({'success': False, 'error': _('Bank account not found')}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
