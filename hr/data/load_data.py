import csv

from django.contrib.auth import get_user_model

from ..models import MOAHIL_BAKLARIOS, MOAHIL_DAPLOM_3ALI, MOAHIL_DECTORA, MOAHIL_MAJSTEAR, MOAHIL_THANOI, MosamaWazifi,Edara3ama,Edarafar3ia,EmployeeBasic,Drajat3lawat, PayrollDetail, PayrollMaster, Jazaat, Salafiat

from ..payroll import Payroll

admin_user = get_user_model().objects.get(id=1)

def show_data():
    with open('./hr/data/employee.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            print(', '.join(row[1:8]))
def empty_database():
    PayrollMaster.objects.all().delete()
    Jazaat.objects.all().delete()
    Salafiat.objects.all().delete()
    EmployeeBasic.objects.all().delete()
    Edarafar3ia.objects.all().delete()
    Edara3ama.objects.all().delete()
    MosamaWazifi.objects.all().delete()
    Drajat3lawat.objects.all().delete()

def import_employees():
    # EmployeeBasic.objects.all().delete()

    with open('./hr/data/employee.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            id = row[0].strip()
            name = row[1].strip()
            mosama_wazifi = row[2].strip()
            edara_3ama = row[3].strip()
            edara_far3ia = row[4].strip()
            draja_wazifia = int(row[5])
            alawa_sanawia = int(row[6])
            tarikh_ta3in = row[7].strip()
            gasima = row[8]
            atfal = row[9]

            if not tarikh_ta3in:
                tarikh_ta3in = '2010-12-31'

            if not mosama_wazifi:
                mosama_wazifi = 'لايوجد'

            if not edara_3ama:
                edara_3ama = 'لايوجد'

            if not edara_far3ia:
                edara_far3ia = 'لايوجد'

            if gasima:
                gasima = True
            else:
                gasima = False

            if atfal:
                atfal = int(atfal)
            else:
                atfal = 0

            mosama_wazifi_obj, created = MosamaWazifi.objects.get_or_create(name=mosama_wazifi)
            edara_3ama_obj, created = Edara3ama.objects.get_or_create(name=edara_3ama)
            edara_far3ia_obj, created = Edarafar3ia.objects.get_or_create(name=edara_far3ia,edara_3ama=edara_3ama_obj)

            try:
                EmployeeBasic.objects.create(
                    code=id,name=name,mosama_wazifi=mosama_wazifi_obj,edara_3ama=edara_3ama_obj,edara_far3ia=edara_far3ia_obj,\
                    draja_wazifia=draja_wazifia,alawa_sanawia=alawa_sanawia,tarikh_ta3in=tarikh_ta3in,\
                    gasima=gasima,atfal=atfal,moahil=MOAHIL_BAKLARIOS,m3ash=0,created_by=admin_user,updated_by=admin_user
                )
            except Exception as e:
                print(f'Id: {id}, Exception: {e}')

def update_moahil():
    with open('./hr/data/moahil.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            code = int(row[0])
            moahil = row[2]

            if not moahil:
                moahil = 0
                
            if int(moahil) == 10000:
                moahil = MOAHIL_DAPLOM_3ALI
            elif int(moahil) == 20000:
                moahil = MOAHIL_MAJSTEAR
            elif int(moahil) == 30000:
                moahil = MOAHIL_DECTORA
            else:
                moahil = MOAHIL_BAKLARIOS

            # print(code,moahil)
            emp = EmployeeBasic.objects.get(code=code)
            emp.moahil = moahil
            emp.save(update_fields=['moahil'])

def update_3doa():
    with open('./hr/data/3doa.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            if row[0]:
                code = int(row[0])
                aadoa = row[2]

                if not aadoa:
                    aadoa = False
                else:
                    aadoa = True
                    
                # print(code,moahil)
                emp = EmployeeBasic.objects.get(code=code)
                emp.aadoa = aadoa
                emp.save(update_fields=['aadoa'])

def import_drajat_3lawat():
    Drajat3lawat.objects.all().delete()

    with open('./hr/data/drajat_3lawat2.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            try:
                Drajat3lawat.objects.create(
                    draja_wazifia=int(row[0]),alawa_sanawia=int(row[1]),abtdai=float(row[2]),galaa_m3isha=float(row[3]),\
                    ma3adin=float(row[4]),aadoa=0,shakhsia=float(row[6]),\
                    created_by=admin_user,updated_by=admin_user
                ) #aadoa=float(row[5])
            except Exception as e:
                print(f'Daraja: {row[0]}, 3lawa: {row[1]}, Error {e}')

def export_drajat_3lawat():    
    with open('./hr/data/drajat_3lawat.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['draja_wazifia','alawa_sanawia','abtdai','galaa_m3isha','shakhsia','ma3adin','aadoa'])

        for draja in Drajat3lawat.DRAJAT_CHOICES:
            for alawa in Drajat3lawat.ALAWAT_CHOICES:
                if (
                    (draja != Drajat3lawat.DRAJAT_TA3AKOD and alawa != Drajat3lawat.ALAWAT_TA3AKOD) 
                    or (draja == Drajat3lawat.DRAJAT_TA3AKOD and alawa == Drajat3lawat.ALAWAT_TA3AKOD)
                ):
                    writer.writerow([draja,alawa,0,0,0,0,0]) 

def export_badalat(year,month):    
    payroll = Payroll(year,month)

    with open(f'./hr/data/badalat_{year}_{month}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['الموظف','الدرجة الوظيفية','العلاوة','ابتدائي','غلاء معيشة','اساسي','طبيعة عمل','تمثيل','مهنة','معادن','مخاطر','عدوى','اجتماعية-قسيمة','اجتماعية اطفال','مؤهل','شخصية','اجمالي المرتب'])

        for (emp,badalat,khosomat) in payroll.all_employees_payroll_from_db():
            l = [emp.name,Drajat3lawat.DRAJAT_CHOICES[emp.draja_wazifia],Drajat3lawat.ALAWAT_CHOICES[emp.alawa_sanawia]] + [b[1] for b in badalat]
            writer.writerow(l) 
def export_khosomat(year,month):    
    payroll = Payroll(year,month)

    with open(f'./hr/data/khsomat_{year}_{month}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['الموظف','الدرجة الوظيفية','العلاوة','تأمين اجتماعي','معاش','الصندوق','الضريبة','دمغه','إجمالي الإستقطاعات الأساسية','صندوق كهربائيه','السلفيات','استقطاع يوم اجمالي لصالح دعم القوات المسلحه','الزكاة','إجمالي الإستقطاعات السنوية','خصومات - جزاءات','إجمالي الإستقطاع الكلي','صافي الإستحقاق'])

        for (emp,badalat,khosomat) in payroll.all_employees_payroll_from_db():
            l = [emp.name,Drajat3lawat.DRAJAT_CHOICES[emp.draja_wazifia],Drajat3lawat.ALAWAT_CHOICES[emp.alawa_sanawia]] + [k[1] for k in khosomat]
            writer.writerow(l) 
    