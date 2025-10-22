from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.conf import settings
import json
from hr_bot.models import EmployeeTelegramRegistration, EmployeeTelegramFamily, EmployeeTelegramMoahil, EmployeeTelegramBankAccount, STATE_DRAFT, STATE_ACCEPTED, STATE_REJECTED, EmployeeTelegram
from hr_bot.utils import send_message, reject_cause, create_user, reset_user_password
from hr.models import EmployeeFamily, EmployeeMoahil, EmployeeBankAccount, EmployeeBasic
from django.utils import timezone
import random
from django.contrib.auth import get_user_model

from hr_bot.management.commands._telegram_main import TOKEN_ID


User = get_user_model()

# Custom login_required decorator that redirects to admin login
def admin_login_required(view_func):
    decorated_view_func = login_required(view_func, login_url='/admin/login/')
    return decorated_view_func

def index(request):
    template_name = 'hr_bot/index.html'
    extra_context = {}
    return render(request, template_name, extra_context)

@admin_login_required
def login_status(request):
    return JsonResponse({
        'is_authenticated': True,
        'user': request.user.username,
        'groups': list(request.user.groups.values_list('name', flat=True)),
        'is_superuser': request.user.is_superuser,
    })

@csrf_exempt
@admin_login_required
def api_logout(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logged out'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@admin_login_required
def registrations_list(request):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    registrations = EmployeeTelegramRegistration.objects.filter(state=STATE_DRAFT)
    data = [{
        'id': r.id,
        'employee': r.employee.name,
        'employee_code': r.employee.code,
        'name': r.name,
        'phone': r.phone,
        'state': r.state,
        'created_at': r.created_at.strftime('%Y-%m-%d %H:%M') if r.created_at else '',
    } for r in registrations]
    return JsonResponse({'registrations': data})

@csrf_exempt
@admin_login_required
def registration_accept(request, pk):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    obj = get_object_or_404(EmployeeTelegramRegistration, pk=pk)
    obj.state = STATE_ACCEPTED
    obj.save()

    try:
        emp, created = EmployeeTelegram.objects.update_or_create(
            employee=obj.employee,
            defaults={
                'user_id': obj.user_id,
                'phone': obj.phone,
                'created_by': request.user,
                'updated_by': request.user,
            }
        )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

    username = obj.employee.email

    if not username:
        message = "لاتمتلك بريداً إلكترونياً. الرجاء مراجعة إدارة الموارد البشرية لتخصيص بريد إلكتروني لك."
        send_message(TOKEN_ID, obj.user_id, message)
        return JsonResponse({'message': 'Accepted but no email'})

    obj.employee.phone = obj.phone
    obj.employee.save()

    portal_url = "https://hr1.mineralsgate.com/app/managers/"

    if User.objects.filter(username=username).exists():
        message = f"الآن يمكنك الدخول لبوابة الموارد البشرية عبر الرابط التالي\n {portal_url} \n باسم المستخدم {username}"
    else:
        password = f"{int(random.random()*1000000)}"
        user = create_user(username, username, password)
        message = f"الآن يمكنك الدخول لبوابة الموارد البشرية عبر الرابط التالي\n {portal_url} \n باسم المستخدم {username} \n وكلمة المرور {password}"

    send_message(TOKEN_ID, obj.user_id, message)
    
    return JsonResponse({'message': 'Accepted'})

@csrf_exempt
@admin_login_required
def registration_reject(request, pk):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    obj = get_object_or_404(EmployeeTelegramRegistration, pk=pk)
    if obj.state == STATE_DRAFT:
        obj.state = STATE_REJECTED
        obj.save()
        
        message = f"تم رفض طلبك: {obj}. الرجاء مراجعة البيانات.\n\n{reject_cause(EmployeeTelegramRegistration, obj)}"
        
        try:
            user_id = obj.employee.employeetelegramregistration_set.first().user_id
            send_message(TOKEN_ID, user_id, message)
            obj.delete()
        except:
            pass
    
    return JsonResponse({'message': 'Rejected'})

@csrf_exempt
@admin_login_required
def registration_reset_password(request, pk):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    obj = get_object_or_404(EmployeeTelegramRegistration, pk=pk)
    password = f"{int(random.random()*1000000)}"
    portal_url = "https://hr1.mineralsgate.com/app/managers/"
    message = f"تم إعادة تعيين كلمة المرور الخاصة بك.\nالآن يمكنك الدخول لبوابة الموارد البشرية عبر الرابط التالي {portal_url} \n باسم المستخدم {obj.employee.email} \n وكلمة المرور {password}"
    reset_user_password(obj.employee.email, password)
    send_message(TOKEN_ID, obj.user_id, message)
    
    return JsonResponse({'message': 'Password reset'})

@admin_login_required
def family_list(request):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower', 'hr_employee']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    families = EmployeeTelegramFamily.objects.all()
    
    if request.user.groups.filter(name__in=['hr_employee']).exists() and not request.user.is_superuser:
        families = families.filter(employee__email=request.user.email)
    
    data = [{
        'id': f.id,
        'employee': f.employee.name,
        'employee_code': f.employee.code,
        'name': f.name,
        'relation': f.relation,
        'tarikh_el2dafa': f.tarikh_el2dafa.strftime('%Y-%m-%d') if f.tarikh_el2dafa else '',
        'attachement_file': f.attachement_file.url if f.attachement_file else None,
        'state': f.state,
        'created_at': f.created_at.strftime('%Y-%m-%d %H:%M') if f.created_at else '',
    } for f in families]
    return JsonResponse({'families': data})

@csrf_exempt
@admin_login_required
def family_create(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.user.groups.filter(name__in=['hr_employee']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        employee = EmployeeTelegram.objects.get(employee__email=request.user.email).employee
    except:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    
    relation = request.POST.get('relation')
    name = request.POST.get('name')
    tarikh_el2dafa = request.POST.get('tarikh_el2dafa')
    attachement_file = request.FILES.get('attachement_file')
    
    family = EmployeeTelegramFamily.objects.create(
        employee=employee,
        relation=relation,
        name=name,
        tarikh_el2dafa=tarikh_el2dafa,
        attachement_file=attachement_file,
        state=STATE_DRAFT,
        created_by=request.user,
        updated_by=request.user,
    )
    
    return JsonResponse({'message': 'Created', 'id': family.id})

@csrf_exempt
@admin_login_required
def family_accept(request, pk):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    obj = get_object_or_404(EmployeeTelegramFamily, pk=pk)
    if obj.state == STATE_DRAFT:
        obj.state = STATE_ACCEPTED
        obj.save()
        
        EmployeeFamily.objects.create(
            employee=obj.employee,
            relation=obj.relation,
            name=obj.name,
            tarikh_el2dafa=obj.tarikh_el2dafa,
            attachement_file=obj.attachement_file,
            created_by=request.user,
            updated_by=request.user,
        )
        
        message = f"تم قبول طلبك: {obj}."
        
        try:
            user_id = obj.employee.employeetelegramregistration_set.first().user_id
            send_message(TOKEN_ID, user_id, message)
        except:
            pass
    
    return JsonResponse({'message': 'Accepted'})

@csrf_exempt
@admin_login_required
def family_reject(request, pk):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    obj = get_object_or_404(EmployeeTelegramFamily, pk=pk)
    if obj.state == STATE_DRAFT:
        obj.state = STATE_REJECTED
        obj.save()
        
        message = f"تم رفض طلبك: {obj}. الرجاء مراجعة البيانات.\n\n{reject_cause(EmployeeTelegramFamily, obj)}"
        
        try:
            user_id = obj.employee.employeetelegramregistration_set.first().user_id
            send_message(TOKEN_ID, user_id, message)
            obj.delete()
        except:
            pass
    
    return JsonResponse({'message': 'Rejected'})

@admin_login_required
def moahil_list(request):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower', 'hr_employee']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    moahil = EmployeeTelegramMoahil.objects.all()
    
    if request.user.groups.filter(name__in=['hr_employee']).exists() and not request.user.is_superuser:
        moahil = moahil.filter(employee__email=request.user.email)
    
    data = [{
        'id': m.id,
        'employee': m.employee.name,
        'employee_code': m.employee.code,
        'moahil': m.moahil,
        'university': m.university,
        'takhasos': m.takhasos,
        'graduate_dt': m.graduate_dt.strftime('%Y-%m-%d') if m.graduate_dt else '',
        'attachement_file': m.attachement_file.url if m.attachement_file else None,
        'state': m.state,
        'created_at': m.created_at.strftime('%Y-%m-%d %H:%M') if m.created_at else '',
    } for m in moahil]
    return JsonResponse({'moahil': data})

@csrf_exempt
@admin_login_required
def moahil_create(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.user.groups.filter(name__in=['hr_employee']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        employee = EmployeeTelegram.objects.get(employee__email=request.user.email).employee
    except:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    
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
        graduate_dt=graduate_dt,
        attachement_file=attachement_file,
        state=STATE_DRAFT,
        created_by=request.user,
        updated_by=request.user,
    )
    
    return JsonResponse({'message': 'Created', 'id': moahil_obj.id})

@csrf_exempt
@admin_login_required
def moahil_accept(request, pk):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    obj = get_object_or_404(EmployeeTelegramMoahil, pk=pk)
    if obj.state == STATE_DRAFT:
        obj.state = STATE_ACCEPTED
        obj.save()
        
        EmployeeMoahil.objects.create(
            employee=obj.employee,
            moahil=obj.moahil,
            university=obj.university,
            takhasos=obj.takhasos,
            graduate_dt=obj.graduate_dt,
            tarikh_el2dafa=timezone.now(),
            attachement_file=obj.attachement_file,
            created_by=request.user,
            updated_by=request.user,
        )
        
        message = f"تم قبول طلبك: {obj}."
        
        try:
            user_id = obj.employee.employeetelegramregistration_set.first().user_id
            send_message(TOKEN_ID, user_id, message)
        except:
            pass
    
    return JsonResponse({'message': 'Accepted'})

@csrf_exempt
@admin_login_required
def moahil_reject(request, pk):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    obj = get_object_or_404(EmployeeTelegramMoahil, pk=pk)
    if obj.state == STATE_DRAFT:
        obj.state = STATE_REJECTED
        obj.save()
        
        message = f"تم رفض طلبك: {obj}. الرجاء مراجعة البيانات.\n\n{reject_cause(EmployeeTelegramMoahil, obj)}"
        
        try:
            user_id = obj.employee.employeetelegramregistration_set.first().user_id
            send_message(TOKEN_ID, user_id, message)
            obj.delete()
        except:
            pass
    
    return JsonResponse({'message': 'Rejected'})

@admin_login_required
def bank_account_list(request):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower', 'hr_employee']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    bank_accounts = EmployeeTelegramBankAccount.objects.all()
    
    if request.user.groups.filter(name__in=['hr_employee']).exists() and not request.user.is_superuser:
        bank_accounts = bank_accounts.filter(employee__email=request.user.email)
    
    data = [{
        'id': b.id,
        'employee': b.employee.name,
        'employee_code': b.employee.code,
        'bank': b.bank,
        'account_no': b.account_no,
        'active': b.active,
        'state': b.state,
        'created_at': b.created_at.strftime('%Y-%m-%d %H:%M') if b.created_at else '',
    } for b in bank_accounts]
    return JsonResponse({'bank_accounts': data})

@csrf_exempt
@admin_login_required
def bank_account_create(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not request.user.groups.filter(name__in=['hr_employee']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        employee = EmployeeTelegram.objects.get(employee__email=request.user.email).employee
    except:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    
    bank = request.POST.get('bank')
    account_no = request.POST.get('account_no')
    active = request.POST.get('active') == 'true'
    
    bank_account = EmployeeTelegramBankAccount.objects.create(
        employee=employee,
        bank=bank,
        account_no=account_no,
        active=active,
        state=STATE_DRAFT,
        created_by=request.user,
        updated_by=request.user,
    )
    
    return JsonResponse({'message': 'Created', 'id': bank_account.id})

@csrf_exempt
@admin_login_required
def bank_account_accept(request, pk):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    obj = get_object_or_404(EmployeeTelegramBankAccount, pk=pk)
    if obj.state == STATE_DRAFT:
        obj.state = STATE_ACCEPTED
        obj.save()
        
        EmployeeBankAccount.objects.create(
            employee=obj.employee,
            bank=obj.bank,
            account_no=obj.account_no,
            active=obj.active,
            created_by=request.user,
            updated_by=request.user,
        )
        
        message = f"تم قبول طلبك: {obj}."
        
        try:
            user_id = obj.employee.employeetelegramregistration_set.first().user_id
            send_message(TOKEN_ID, user_id, message)
        except:
            pass
    
    return JsonResponse({'message': 'Accepted'})

@csrf_exempt
@admin_login_required
def bank_account_reject(request, pk):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    obj = get_object_or_404(EmployeeTelegramBankAccount, pk=pk)
    if obj.state == STATE_DRAFT:
        obj.state = STATE_REJECTED
        obj.save()
        
        message = f"تم رفض طلبك: {obj}. الرجاء مراجعة البيانات.\n\n{reject_cause(EmployeeTelegramBankAccount, obj)}"
        
        try:
            user_id = obj.employee.employeetelegramregistration_set.first().user_id
            send_message(TOKEN_ID, user_id, message)
            obj.delete()
        except:
            pass
    
    return JsonResponse({'message': 'Rejected'})

@admin_login_required
def employee_data(request):
    try:
        employee = EmployeeBasic.objects.get(email=request.user.email)
        
        families = EmployeeFamily.objects.filter(employee=employee)
        moahil = EmployeeMoahil.objects.filter(employee=employee)
        bank_accounts = EmployeeBankAccount.objects.filter(employee=employee)
        
        data = {
            'employee': {
                'code': employee.code,
                'name': employee.name,
                'draja_wazifia': str(employee.draja_wazifia) if employee.draja_wazifia else '',
                'alawa_sanawia': str(employee.alawa_sanawia) if employee.alawa_sanawia else '',
                'hikal_wazifi': str(employee.hikal_wazifi) if employee.hikal_wazifi else '',
                'mosama_wazifi': str(employee.mosama_wazifi) if employee.mosama_wazifi else '',
                'sex': employee.sex,
                'tarikh_milad': employee.tarikh_milad.strftime('%Y-%m-%d') if employee.tarikh_milad else '',
                'tarikh_ta3in': employee.tarikh_ta3in.strftime('%Y-%m-%d') if employee.tarikh_ta3in else '',
                'tarikh_akhir_targia': employee.tarikh_akhir_targia.strftime('%Y-%m-%d') if employee.tarikh_akhir_targia else '',
                'gasima': employee.gasima,
                'atfal': employee.atfal,
                'moahil': employee.moahil,
                'phone': employee.phone,
                'email': employee.email,
                'no3_2lertibat': employee.no3_2lertibat,
                'sanoat_2lkhibra': str(employee.sanoat_2lkhibra) if employee.sanoat_2lkhibra else '',
                'aadoa': employee.aadoa,
                'm3ash': str(employee.m3ash) if employee.m3ash else '',
                'status': employee.status,
            },
            'families': [{
                'relation': f.relation,
                'name': f.name,
                'tarikh_el2dafa': f.tarikh_el2dafa.strftime('%Y-%m-%d') if f.tarikh_el2dafa else '',
            } for f in families],
            'moahil': [{
                'moahil': m.moahil,
                'university': m.university,
                'takhasos': m.takhasos,
                'graduate_dt': m.graduate_dt.strftime('%Y-%m-%d') if m.graduate_dt else '',
            } for m in moahil],
            'bank_accounts': [{
                'bank': b.bank,
                'account_no': b.account_no,
                'active': b.active,
            } for b in bank_accounts],
        }
        
        return JsonResponse(data)
    except EmployeeBasic.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
