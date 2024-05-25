import csv

from django.contrib.auth import get_user_model

from hr.calculations import Badalat_3lawat, Khosomat
from django.db.models import Sum

from ..models import Jazaat, MosamaWazifi,Edara3ama,Edarafar3ia,EmployeeBasic,Drajat3lawat,Settings,Salafiat

class HrSettings():
    def __init__(self) -> None:
        self.values = {}
        
        for val in Settings.objects.values('code','value'):
            code = val.get('code')
            self.values[code] = val.get('value')

    def get_by_code(self,code):            
        return self.values.get(code,0)

def show_data():
    with open('./hr/data/employee.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            print(', '.join(row[1:8]))

def import_employees():
    admin_user = get_user_model().objects.get(id=1)

    # EmployeeBasic.objects.delete()

    with open('./hr/data/employee.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            id = row[0].strip()
            name = row[1].strip()
            mosama_wazifi = row[2].strip()
            edara_3ama = row[3].strip()
            edara_far3ia = row[4].strip()
            draja_wazifia = int(row[5])
            alawa_sanawia = int(row[6])
            tarikh_ta3in = row[7].strip()

            mosama_wazifi_obj, created = MosamaWazifi.objects.get_or_create(name=mosama_wazifi)
            edara_3ama_obj, created = Edara3ama.objects.get_or_create(name=edara_3ama)
            edara_far3ia_obj, created = Edarafar3ia.objects.get_or_create(name=edara_far3ia,edara_3ama=edara_3ama_obj)

            try:
                EmployeeBasic.objects.create(
                    name=name,mosama_wazifi=mosama_wazifi_obj,edara_3ama=edara_3ama_obj,edara_far3ia=edara_far3ia_obj,\
                    draja_wazifia=draja_wazifia,alawa_sanawia=alawa_sanawia,tarikh_ta3in=tarikh_ta3in,\
                    created_by=admin_user,updated_by=admin_user
                )
            except Exception as e:
                print(f'Id: {id}, Exception: {e}')

def payroll_summary(year,month):
    hr_settings = HrSettings()
    for emp in EmployeeBasic.objects.filter(id=1794): #.all():
        moahil = Settings.MOAHIL_PREFIX + emp.moahil
        salafiat_total = Salafiat.objects.filter(year=year,month=month).aggregate(total=Sum("amount"))['total'] or 0
        jazaat_total = Jazaat.objects.filter(year=year,month=month).aggregate(total=Sum("amount"))['total'] or 0
        gasima = 0
        if(emp.gasima):
            gasima = hr_settings.get_by_code(Settings.SETTINGS_GASIMA)

        try:
            draj_obj = Drajat3lawat.objects.get(draja_wazifia=emp.draja_wazifia,alawa_sanawia=emp.alawa_sanawia)
            badal = Badalat_3lawat(
                draj_obj.abtdai,
                draj_obj.galaa_m3isha,
                shakhsia=draj_obj.shakhsia,
                aadoa=draj_obj.aadoa,
                gasima=gasima,
                atfal=(emp.atfal *hr_settings.get_by_code(Settings.SETTINGS_ATFAL)),
                moahil=hr_settings.get_by_code(moahil),
                ma3adin=draj_obj.ma3adin
            )
            khosomat = Khosomat(
                badal,hr_settings.get_by_code(Settings.SETTINGS_ZAKA_KAFAF),
                hr_settings.get_by_code(Settings.SETTINGS_ZAKA_NISAB),
                damga=hr_settings.get_by_code(Settings.SETTINGS_DAMGA),
                m3ash=emp.m3ash,
                salafiat=salafiat_total,
                jazaat=jazaat_total,
                sandog_kahraba=0,
                sandog=hr_settings.get_by_code(Settings.SETTINGS_SANDOG),
            )

            print(f'Name: {emp.name}')
            print(badal)
            print(khosomat)
            print("\n")
        except Drajat3lawat.DoesNotExist as e:
            pass
            # print(e)
            # print(f'draja_wazifia: {Drajat3lawat.DRAJAT_CHOICES.get(emp.draja_wazifia)}, alawa_sanawia: {Drajat3lawat.DRAJAT_CHOICES.get(emp.alawa_sanawia)}')
