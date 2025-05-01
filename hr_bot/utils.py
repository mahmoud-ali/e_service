from django.contrib.auth import get_user_model
from django.contrib.auth.models import  Group

import requests

User = get_user_model()

def create_user(username, email, password):
    user = User.objects.create_user(username=username, email=email, password=password, is_staff=True)

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
