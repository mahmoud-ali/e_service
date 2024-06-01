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

    def get_code_as_float(self,code):
        return float(self.values.get(code,0))

    def get_code_as_str(self,code):
        return self.values.get(code,'')

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
            self.payroll_details = PayrollDetail.objects.filter(payroll_master=self.payroll_master).prefetch_related("employee")
        except PayrollMaster.DoesNotExist:
            self.payroll_master = None
            self.payroll_details = []

    def employee_payroll_calculated(self,employee):
        moahil = Settings.MOAHIL_PREFIX + employee.moahil
        salafiat_total = self.salafiat_qs.filter(employee=employee).aggregate(total=Sum("amount"))['total'] or 0
        jazaat_total = self.jazaat_qs.filter(employee=employee).aggregate(total=Sum("amount"))['total'] or 0
        gasima = 0
        if(employee.gasima):
            gasima = self.hr_settings.get_code_as_float(Settings.SETTINGS_GASIMA)

        aadoa = 0
        if(employee.aadoa):
            aadoa = self.hr_settings.get_code_as_float(Settings.SETTINGS_AADOA)

        enable_sandog = self.hr_settings.get_code_as_float(Settings.SETTINGS_ENABLE_SANDOG_KAHRABA)
        if enable_sandog > 0:
            enable_sandog = True
        else:
            enable_sandog = False

        enable_youm_algoat = self.hr_settings.get_code_as_float(Settings.SETTINGS_ENABLE_YOUM_ALGOAT_ALMOSALAHA)
        if enable_youm_algoat > 0:
            enable_youm_algoat = True
        else:
            enable_youm_algoat = False

        try:
            draj_obj = Drajat3lawat.objects.get(draja_wazifia=employee.draja_wazifia,alawa_sanawia=employee.alawa_sanawia)
            badal = Badalat_3lawat(
                draj_obj.abtdai,
                draj_obj.galaa_m3isha,
                shakhsia=draj_obj.shakhsia,
                aadoa=aadoa,
                gasima=gasima,
                atfal=(employee.atfal *self.hr_settings.get_code_as_float(Settings.SETTINGS_ATFAL)),
                moahil=self.hr_settings.get_code_as_float(moahil),
                ma3adin=draj_obj.ma3adin
            )
            khosomat = Khosomat(
                badal,self.hr_settings.get_code_as_float(Settings.SETTINGS_ZAKA_KAFAF),
                self.hr_settings.get_code_as_float(Settings.SETTINGS_ZAKA_NISAB),
                damga=self.hr_settings.get_code_as_float(Settings.SETTINGS_DAMGA),
                m3ash=employee.m3ash,
                salafiat=salafiat_total,
                jazaat=jazaat_total,
                sandog=self.hr_settings.get_code_as_float(Settings.SETTINGS_SANDOG),
                enable_sandog_kahraba=enable_sandog,
                enable_youm_algoat_almosalaha=enable_youm_algoat,
            )

            return (employee,badal,khosomat)
        except Drajat3lawat.DoesNotExist as e:
            pass
    
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
            enable_sandog_kahraba=self.payroll_master.enable_sandog_kahraba,
            enable_youm_algoat_almosalaha=self.payroll_master.enable_youm_algoat_almosalaha,
        )

        return (emp_payroll.employee,badal,khosomat)

    def all_employees_payroll_from_db(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db(emp_payroll))

    def calculate(self):
        if self.is_confirmed():
            return False
        
        emp = None

        try:
            with transaction.atomic():        
                if not self.payroll_master:
                    enable_sandog = self.hr_settings.get_code_as_float(Settings.SETTINGS_ENABLE_SANDOG_KAHRABA)
                    if enable_sandog > 0:
                        enable_sandog = True
                    else:
                        enable_sandog = False

                    enable_youm_algoat = self.hr_settings.get_code_as_float(Settings.SETTINGS_ENABLE_YOUM_ALGOAT_ALMOSALAHA)
                    if enable_youm_algoat > 0:
                        enable_youm_algoat = True
                    else:
                        enable_youm_algoat = False

                    self.payroll_master = PayrollMaster.objects.create(
                        year = self.year,
                        month = self.month,
                        zaka_kafaf = self.hr_settings.get_code_as_float(Settings.SETTINGS_ZAKA_KAFAF),
                        zaka_nisab = self.hr_settings.get_code_as_float(Settings.SETTINGS_ZAKA_NISAB),
                        enable_sandog_kahraba=enable_sandog,
                        enable_youm_algoat_almosalaha=enable_youm_algoat,
                        created_by = self.admin_user,
                        updated_by = self.admin_user,
                    )
                else:
                    PayrollDetail.objects.filter(payroll_master = self.payroll_master).delete()
                    
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
        
        self.payroll_details = PayrollDetail.objects.filter(payroll_master=self.payroll_master).prefetch_related("employee")

    def confirm(self):
        if not self.payroll_master:
            return False
        
        with transaction.atomic():
            self.payroll_master.confirmed = True
            self.payroll_master.save(update_fields=['confirmed'])

            self.salafiat_qs.update(deducted = True)
            self.jazaat_qs.update(deducted = True)

            return True
        
    def is_confirmed(self):
        if not hasattr(self.payroll_master,'confirmed'):
            return False
        
        return self.payroll_master.confirmed