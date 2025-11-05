import csv
from django.http import HttpResponse
from ..models import EmployeeTelegram

def save_employee_telegram_csv():
    qs = EmployeeTelegram.objects.all().prefetch_related('employee').values_list('user_id', 'employee__name', 'employee__email')
    with open('employee_telegram.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Id', 'Name', 'Email'])
        writer.writerows(qs)

    print("CSV file saved successfully!")