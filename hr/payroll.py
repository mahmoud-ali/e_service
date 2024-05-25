from django.contrib.auth import get_user_model

from hr.calculations import Badalat_3lawat, Khosomat
from django.db import transaction
from django.db.models import Sum

from .models import Jazaat,EmployeeBasic,Drajat3lawat, PayrollDetail, PayrollMaster,Settings,Salafiat

class HrSettings():
    def __init__(self) -> None:
        self.values = {}
        
        for val in Settings.objects.values('code','value'):
            code = val.get('code')
            self.values[code] = val.get('value')

    def get_by_code(self,code):
        return self.values.get(code,0)

class Payroll():
    def __init__(self,year,month) -> None:
        self.year = year
        self.month = month

        self.hr_settings = HrSettings()
        self.salafiat_qs = Salafiat.objects.filter(year=self.year,month=self.month)
        self.jazaat_qs = Jazaat.objects.filter(year=self.year,month=self.month)
        self.employees = EmployeeBasic.objects.all() #filter(id=1794)

        self.admin_user = get_user_model().objects.get(id=1)

        try:
            self.payroll_master = PayrollMaster.objects.get(year=self.year,month=self.month)
            self.payroll_details = PayrollDetail.objects.filter(payroll_master=self.payroll_master)
        except PayrollMaster.DoesNotExist:
            self.payroll_master = None
            self.payroll_details = []

    def employee_payroll_calculated(self,employee):
        moahil = Settings.MOAHIL_PREFIX + employee.moahil
        salafiat_total = self.salafiat_qs.filter(employee=employee).aggregate(total=Sum("amount"))['total'] or 0
        jazaat_total = self.jazaat_qs.filter(employee=employee).aggregate(total=Sum("amount"))['total'] or 0
        gasima = 0
        if(employee.gasima):
            gasima = self.hr_settings.get_by_code(Settings.SETTINGS_GASIMA)

        try:
            draj_obj = Drajat3lawat.objects.get(draja_wazifia=employee.draja_wazifia,alawa_sanawia=employee.alawa_sanawia)
            badal = Badalat_3lawat(
                draj_obj.abtdai,
                draj_obj.galaa_m3isha,
                shakhsia=draj_obj.shakhsia,
                aadoa=draj_obj.aadoa,
                gasima=gasima,
                atfal=(employee.atfal *self.hr_settings.get_by_code(Settings.SETTINGS_ATFAL)),
                moahil=self.hr_settings.get_by_code(moahil),
                ma3adin=draj_obj.ma3adin
            )
            khosomat = Khosomat(
                badal,self.hr_settings.get_by_code(Settings.SETTINGS_ZAKA_KAFAF),
                self.hr_settings.get_by_code(Settings.SETTINGS_ZAKA_NISAB),
                damga=self.hr_settings.get_by_code(Settings.SETTINGS_DAMGA),
                m3ash=employee.m3ash,
                salafiat=salafiat_total,
                jazaat=jazaat_total,
                sandog_kahraba=0,
                sandog=self.hr_settings.get_by_code(Settings.SETTINGS_SANDOG),
            )

            return (employee,badal,khosomat)
            # print(f'Name: {employee.name}')
            # print(badal)
            # print(khosomat)
            # print("\n")
        except Drajat3lawat.DoesNotExist as e:
            pass
            # print(e)
            # print(f'draja_wazifia: {Drajat3lawat.DRAJAT_CHOICES.get(emp.draja_wazifia)}, alawa_sanawia: {Drajat3lawat.DRAJAT_CHOICES.get(emp.alawa_sanawia)}')

    # def __iter__(self):
    #     for emp in self.employees:
    #         yield(self.calculate_employee_payroll(emp))
    
    def all_employees_payroll_calculated(self):
        for emp in self.employees:
            x = self.employee_payroll_calculated(emp)
            if x:
                yield(x)

    def employee_payroll_from_db(self,emp_payroll):
        badal = Badalat_3lawat(
            emp_payroll.abtdai,
            emp_payroll.galaa_m3isha,
            shakhsia=emp_payroll.shakhsia,
            aadoa=emp_payroll.aadoa,
            gasima=emp_payroll.gasima,
            atfal=emp_payroll.atfal,
            moahil=emp_payroll.moahil,
            ma3adin=emp_payroll.ma3adin
        )
        khosomat = Khosomat(
            badal,self.payroll_master.zaka_kafaf,
            self.payroll_master.zaka_nisab,
            damga=emp_payroll.damga,
            m3ash=emp_payroll.m3ash,
            salafiat=emp_payroll.salafiat,
            jazaat=emp_payroll.jazaat,
            sandog_kahraba=emp_payroll.sandog_kahraba,
            sandog=emp_payroll.sandog,
        )

        return (emp_payroll.employee,badal,khosomat)

    def all_employees_payroll_from_db(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db(emp_payroll))

    def show_all(self):
        for emp_payroll in self.employees:
            print(*emp_payroll)
        

    def calculate(self):
        if self.payroll_master:
            return False
        
        emp = None

        try:
            with transaction.atomic():        
                self.payroll_master = PayrollMaster.objects.create(
                    year = self.year,
                    month = self.month,
                    zaka_kafaf = self.hr_settings.get_by_code(Settings.SETTINGS_ZAKA_KAFAF),
                    zaka_nisab = self.hr_settings.get_by_code(Settings.SETTINGS_ZAKA_NISAB),
                    created_by = self.admin_user,
                    updated_by = self.admin_user,
                )

                for emp_payroll in self.all_employees_payroll_calculated():
                    emp,badalat,khosomat = emp_payroll

                    PayrollDetail.objects.create(
                        payroll_master = self.payroll_master,
                        employee = emp,
                        abtdai = badalat.abtdai,
                        galaa_m3isha = badalat.galaa_m3isha,
                        shakhsia = badalat.shakhsia,
                        aadoa = badalat.aadoa,
                        gasima = badalat.ajtima3ia_gasima,
                        atfal = badalat.ajtima3ia_atfal,
                        moahil = badalat.moahil,
                        ma3adin = badalat.ma3adin,
                        m3ash = khosomat.m3ash,
                        salafiat = khosomat.salafiat,
                        jazaat = khosomat.jazaat,
                        damga = khosomat.damga,
                        sandog = khosomat.sandog,
                        sandog_kahraba = khosomat.sandog_kahraba,
                    )
        except Exception as e:
            print(f'Payroll not calculated: {e}')
            return False
        
        self.payroll_details = PayrollDetail.objects.filter(payroll_master=self.payroll_master)

    def confirm(self):
        if not self.payroll_master:
            return False
        
        with transaction.atomic():
            self.payroll_master.confirmed = True
            self.payroll_master.save(update_fields=['confirmed'])

            self.salafiat_qs.update(confirmed = True)
            self.jazaat_qs.update(confirmed = True)

            return True
        
    def is_confirmed(self):
        if not hasattr(self.payroll_master,'confirmed'):
            return False
        
        return self.payroll_master.confirmed