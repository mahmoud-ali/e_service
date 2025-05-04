from django.contrib.auth import get_user_model
from django.contrib.auth.models import  Group

from hr.models import EmployeeFamily
from hr_bot.models import EmployeeTelegramBankAccount, EmployeeTelegramFamily, EmployeeTelegramMoahil,ApplicationRequirement

import requests

User = get_user_model()

def create_user(username, email, password):
    user = User.objects.create_user(username=username.lower(), email=email.lower(), password=password, is_staff=True)

    # user = User.objects.create_user(username, username, password, is_staff=True)

    employee_group = Group.objects.get(name='hr_employee') 
    employee_group.user_set.add(user)

    return user

def reset_user_password(username, new_password):
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        return True
    except User.DoesNotExist:
        return False
    
def send_message(TOKEN_ID, user_id, message):
    telegram_url = f"https://api.telegram.org/bot{TOKEN_ID}/sendMessage?chat_id={int(user_id)}&text={message}"
    return requests.get(telegram_url)

def reject_cause(model, obj):
    msg = ""
    qs = ApplicationRequirement.objects.all()

    if model == EmployeeTelegramFamily:
        if obj.relation == EmployeeFamily.FAMILY_RELATION_CHILD:
            qs = qs.filter(app=ApplicationRequirement.ATFAL)
            if qs.exists():
                msg = "*** مطلوبات إضافة طفل ***\n - "
                msg += "\n - ".join(qs.values_list("requirement",flat=True))
        elif obj.relation == EmployeeFamily.FAMILY_RELATION_CONSORT:
            qs = qs.filter(app=ApplicationRequirement.GASIMA)
            if qs.exists():
                msg = "*** مطلوبات إضافة قسيمة ***\n - "
                msg += "\n - ".join(qs.values_list("requirement",flat=True))
    elif model == EmployeeTelegramMoahil:
        qs = qs.filter(app=ApplicationRequirement.MOAHIL)
        if qs.exists():
            msg = "*** مطلوبات إضافة مؤهل ***\n - "
            msg += "\n - ".join(qs.values_list("requirement",flat=True))
    elif model == EmployeeTelegramBankAccount:
        qs = qs.filter(app=ApplicationRequirement.BANK_ACCOUNT)
        if qs.exists():
            msg = "*** مطلوبات إضافة حساب بنكي ***\n - "
            msg += "\n - ".join(qs.values_list("requirement",flat=True))

    return msg