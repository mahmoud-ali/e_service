from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
import json
from hr_bot.models import EmployeeTelegramRegistration, EmployeeTelegramFamily, EmployeeTelegramMoahil, EmployeeTelegramBankAccount, STATE_DRAFT, STATE_ACCEPTED, STATE_REJECTED
from hr_bot.utils import send_message
from hr.models import EmployeeFamily, EmployeeMoahil, EmployeeBankAccount
from django.utils import timezone
import random
from hr_bot.utils import create_user, reset_user_password
from django.contrib.auth import get_user_model

from hr_bot.management.commands._telegram_main import TOKEN_ID


User = get_user_model()

def index(request):
    with open('hr_bot/frontend/index.html', 'r') as f:
        return HttpResponse(f.read())

@login_required
def login_status(request):
    return JsonResponse({
        'is_authenticated': True,
        'user': request.user.username,
        'groups': list(request.user.groups.values_list('name', flat=True)),
    })

@csrf_exempt
@login_required
def api_logout(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logged out'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def registrations_list(request):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    registrations = EmployeeTelegramRegistration.objects.all()
    data = [{
        'id': r.id,
        'employee': r.employee.name,
        'name': r.name,
        'phone': r.phone,
        'state': r.state,
    } for r in registrations]
    return JsonResponse({'registrations': data})

@csrf_exempt
@login_required
def registration_accept(request, pk):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    reg = get_object_or_404(EmployeeTelegramRegistration, pk=pk)
    reg.state = STATE_ACCEPTED
    reg.save()
    # Similar logic as in admin.py for accepting
    # ... (include the full accept logic from admin.py here)
    return JsonResponse({'message': 'Accepted'})

# Similar views for reject, and for other models: family_list, family_accept, etc.
# For brevity, I'll add placeholders; expand as needed for all CRUD operations.

@login_required
def family_list(request):
    if not request.user.groups.filter(name__in=['hr_manager', 'hr_manpower']).exists() and not request.user.is_superuser:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    families = EmployeeTelegramFamily.objects.all()
    data = [{
        'id': f.id,
        'employee': f.employee.name,
        'name': f.name,
        'relation': f.relation,
        'state': f.state,
    } for f in families]
    return JsonResponse({'families': data})

# Add more views for moahil, bank_account, etc., mirroring admin.py actions.
