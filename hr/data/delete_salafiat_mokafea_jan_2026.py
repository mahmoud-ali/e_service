#!/usr/bin/env python
import os
import sys
import django

# إضافة المجلد الرئيسي للمشروع إلى مسار النظام
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_service.settings')
django.setup()

from hr.models import EmployeeSalafiat


def delete_jan_2026_mokafea_salafiat():
    YEAR = 2026
    MONTH = 1
    SALAFIA_TYPE = EmployeeSalafiat.NO3_2LSALAFIA_3LA_2LMOKAF2  

    salafiat_qs = EmployeeSalafiat.objects.filter(
        year=YEAR,
        month=MONTH,
        no3_2lsalafia=SALAFIA_TYPE
    )

    count = salafiat_qs.count()
    print(f"جاري إيجاد السلفيات (سلفية على المكافأة) لشهر {MONTH}/{YEAR}...")
    print(f"عدد السلفيات المطابقة للشروط: {count}")

    if count == 0:
        print("لا توجد سلفيات مطابقة للمواصفات لحذفها.")
        return

    deleted_count, _ = salafiat_qs.delete()
    print(f"تم حذف {deleted_count} سجل (EmployeeSalafiat) بنجاح.")


if __name__ == '__main__':
    delete_jan_2026_mokafea_salafiat()
