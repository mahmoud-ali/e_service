from traditional_app.hr_calculations import Badalat_3lawat, Khosomat
from traditional_app.models import Employee, PayrollDetail, PayrollMaster
from django.db import transaction
from django.contrib.auth import get_user_model

class T3agoodPayroll():
    def __init__(self,year,month) -> None:
        self.admin_user = get_user_model().objects.get(id=1)

        self.year = int(year)
        self.month = int(month)

        self.hr_settings = {
            'asasi': 54000,
            'galaa_m3isha': 22000,
            'badel_sakan': 28000,
            'badel_tar7il': 22000,
            'tabi3at_3amal': 40000,
            'badel_laban': 14000,
            'badel_3laj': 20000,
            'badel_3laj': 20000,
            'damga':1
        }

        try:
            self.payroll_master = PayrollMaster.objects.get(year=self.year,month=self.month)
            self.payroll_details = PayrollDetail.objects \
                .filter(payroll_master=self.payroll_master).prefetch_related("payroll_master","employee")
        except PayrollMaster.DoesNotExist:
            self.payroll_master = None
            self.payroll_details = []

        self.employees = Employee.objects \
            .filter(no3_elta3god=Employee.EMPLOYEE_TYPE_T3AGOOD)

    def is_confirmed(self):
        if not hasattr(self.payroll_master,'confirmed'):
            return False
        
        return self.payroll_master.confirmed

    def is_calculated(self):
        if not self.payroll_master or (hasattr(self.payroll_master,'count') and self.payroll_master.count()==0):
            return False
        
        return True
    
    def calculate(self):
        if self.is_confirmed():
            return False

        try:
            with transaction.atomic():        
                if not self.payroll_master:
                    self.payroll_master = PayrollMaster.objects.create(
                        year = self.year,
                        month = self.month,
                        asasi = self.hr_settings['asasi'],
                        galaa_m3isha = self.hr_settings['galaa_m3isha'],
                        badel_sakan = self.hr_settings['badel_sakan'],
                        badel_tar7il= self.hr_settings['badel_tar7il'],
                        tabi3at_3amal= self.hr_settings['tabi3at_3amal'],
                        badel_laban= self.hr_settings['badel_laban'],
                        badel_3laj = self.hr_settings['badel_3laj'],
                        damga= self.hr_settings['damga'],
                        created_by = self.admin_user,
                        updated_by = self.admin_user,
                    )

                    print("********",self.payroll_master.asasi)
                else:
                    PayrollDetail.objects.filter(payroll_master = self.payroll_master).delete()

                for employee in self.employees:
                    PayrollDetail.objects.create(
                        payroll_master = self.payroll_master,
                        employee = employee,
                    )

        except Exception as e:
            print(f'Payroll not calculated: {e}')
            return False
        
    def all_employees_payroll_from_db(self):
        if not self.is_calculated():
            return []
        
        for emp_payroll in self.payroll_details:
            badalat = Badalat_3lawat(
                emp_payroll.payroll_master.asasi,
                emp_payroll.payroll_master.galaa_m3isha,
                emp_payroll.payroll_master.badel_sakan,
                emp_payroll.payroll_master.badel_tar7il,
                emp_payroll.payroll_master.tabi3at_3amal,
                emp_payroll.payroll_master.badel_laban,
                emp_payroll.payroll_master.badel_3laj
            )

            khosomat = Khosomat(badalat,emp_payroll.payroll_master.damga)

            yield (emp_payroll,badalat,khosomat)

