import datetime
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.db.models import Q, Sum
from django.contrib.auth import get_user_model

from hr.calculations import Badalat_3lawat, Khosomat, M2moria, Mobashara, Mokaf2

from .models import EmployeeM2moria, EmployeeM2moriaMonthly, EmployeeMobashra, EmployeeJazaat,EmployeeBasic,Drajat3lawat, EmployeeMobashraMonthly, PayrollDetail, PayrollMaster,Settings,EmployeeSalafiat

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
    
    def get_code_as_boolean(self,code):
        return (float(self.values.get(code,0)) > 0)

class Payroll():
    def __init__(self,year,month) -> None:
        self.year = year
        self.month = month

        self.hr_settings = HrSettings()
        self.salafiat_qs = EmployeeSalafiat.objects.filter(year=self.year,month=self.month)
        self.jazaat_qs = EmployeeJazaat.objects.filter(year=self.year,month=self.month)
        self.employees = EmployeeBasic.objects.filter(status=EmployeeBasic.STATUS_ACTIVE) #exclude(hikal_wazifi=self.hr_settings.get_code_as_float(Settings.SETTINGS_KHARJ_ELSHARIKA)) #all() #filter(id=1794)

        self.admin_user = get_user_model().objects.get(id=1)

        try:
            self.payroll_master = PayrollMaster.objects.get(year=self.year,month=self.month)
            self.payroll_details = PayrollDetail.objects \
                .filter(payroll_master=self.payroll_master).prefetch_related("payroll_master","employee") \
                .exclude(employee__hikal_wazifi=self.hr_settings.get_code_as_float(Settings.SETTINGS_KHARJ_ELSHARIKA))
        except PayrollMaster.DoesNotExist:
            self.payroll_master = None
            self.payroll_details = []

    def employee_payroll_calculated(self,employee:EmployeeBasic):
        moahil = Settings.MOAHIL_PREFIX + employee.moahil
        salafiat_total = self.salafiat_qs.filter(employee=employee,no3_2lsalafia=EmployeeSalafiat.NO3_2LSALAFIA_SHARIKA).aggregate(total=Sum("amount"))['total'] or 0
        salafiat_sandog_total = self.salafiat_qs.filter(employee=employee,no3_2lsalafia=EmployeeSalafiat.NO3_2LSALAFIA_SANDOG).aggregate(total=Sum("amount"))['total'] or 0
        jazaat_total = self.jazaat_qs.filter(employee=employee).aggregate(total=Sum("amount"))['total'] or 0
        gasima = 0
        if(employee.gasima):
            gasima = self.hr_settings.get_code_as_float(Settings.SETTINGS_GASIMA)

        aadoa = 0
        if(employee.aadoa):
            aadoa = self.hr_settings.get_code_as_float(Settings.SETTINGS_AADOA)

        enable_sandog = self.hr_settings.get_code_as_boolean(Settings.SETTINGS_ENABLE_SANDOG_KAHRABA)

        enable_youm_algoat = self.hr_settings.get_code_as_boolean(Settings.SETTINGS_ENABLE_YOUM_ALGOAT_ALMOSALAHA)

        khasm_salafiat_elsandog_min_elomoratab = self.hr_settings.get_code_as_boolean(Settings.SETTINGS_KHASM_ELSANDOG_MIN_ELOMORATAB)

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
                ma3adin=draj_obj.ma3adin,
                month = self.month,
                year = self.month,
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
                tarikh_2lmilad=employee.tarikh_milad,
                m3ash_age=self.hr_settings.get_code_as_float(Settings.SETTINGS_OMER_2LMA3ASH),
                salafiat_sandog=salafiat_sandog_total,
                khasm_salafiat_elsandog_min_elomoratab=khasm_salafiat_elsandog_min_elomoratab,
                dariba_mokaf2=self.hr_settings.get_code_as_float(Settings.SETTINGS_DARIBAT_2LMOKAFA),
            )

            return (employee,badal,khosomat)
        except Drajat3lawat.DoesNotExist as e:
            pass
    
    def all_employees_payroll_calculated(self):
        for emp in self.employees:
            x = self.employee_payroll_calculated(emp)
            if x:
                yield(x)

    def employee_payroll_from_db(self,emp_payroll:PayrollDetail):
        badal = Badalat_3lawat(
            emp_payroll.abtdai,
            emp_payroll.galaa_m3isha,
            shakhsia=emp_payroll.shakhsia,
            aadoa=emp_payroll.aadoa,
            gasima=emp_payroll.gasima,
            atfal=emp_payroll.atfal,
            moahil=emp_payroll.moahil,
            ma3adin=emp_payroll.ma3adin,
            month = emp_payroll.payroll_master.month,
            year = emp_payroll.payroll_master.year,
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
            tarikh_2lmilad=emp_payroll.tarikh_milad,
            m3ash_age=self.payroll_master.m3ash_age,
            salafiat_sandog=emp_payroll.salafiat_sandog,
            khasm_salafiat_elsandog_min_elomoratab=self.payroll_master.khasm_salafiat_elsandog_min_elomoratab,
            dariba_mokaf2=self.hr_settings.get_code_as_float(Settings.SETTINGS_DARIBAT_2LMOKAFA),
        )

        return (emp_payroll.employee,badal,khosomat,emp_payroll.draja_wazifia,emp_payroll.alawa_sanawia)
    
    def all_employees_payroll_from_db(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db(emp_payroll))

    def employee_payroll_from_db_with_bank_account(self,emp_payroll:PayrollDetail):
        tmp_lst = list(self.employee_payroll_from_db(emp_payroll))
        tmp_lst.append(emp_payroll.bank)
        tmp_lst.append(emp_payroll.account_no)
        return tuple(tmp_lst)
    
    def all_employees_payroll_from_db_with_bank_account(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db_with_bank_account(emp_payroll))


    def employee_payroll_from_employee(self,emp:EmployeeBasic):
        emp_payroll = PayrollDetail.objects.filter(payroll_master=self.payroll_master,employee=emp).prefetch_related("employee").first()
        if emp_payroll:
            return self.employee_payroll_from_db(emp_payroll)
        
        return (None,None,None,None,None,)

    def calculate(self):
        if self.is_confirmed():
            return False
        
        emp = None

        try:
            with transaction.atomic():        
                if not self.payroll_master:
                    enable_sandog = self.hr_settings.get_code_as_boolean(Settings.SETTINGS_ENABLE_SANDOG_KAHRABA)

                    enable_youm_algoat = self.hr_settings.get_code_as_boolean(Settings.SETTINGS_ENABLE_YOUM_ALGOAT_ALMOSALAHA)

                    khasm_salafiat_elsandog_min_elomoratab = self.hr_settings.get_code_as_boolean(Settings.SETTINGS_KHASM_ELSANDOG_MIN_ELOMORATAB)


                    self.payroll_master = PayrollMaster.objects.create(
                        year = self.year,
                        month = self.month,
                        zaka_kafaf = self.hr_settings.get_code_as_float(Settings.SETTINGS_ZAKA_KAFAF),
                        zaka_nisab = self.hr_settings.get_code_as_float(Settings.SETTINGS_ZAKA_NISAB),
                        daribat_2lmokafa = self.hr_settings.get_code_as_float(Settings.SETTINGS_DARIBAT_2LMOKAFA),
                        enable_sandog_kahraba=enable_sandog,
                        enable_youm_algoat_almosalaha=enable_youm_algoat,
                        m3ash_age=self.hr_settings.get_code_as_float(Settings.SETTINGS_OMER_2LMA3ASH),
                        khasm_salafiat_elsandog_min_elomoratab = khasm_salafiat_elsandog_min_elomoratab,
                        created_by = self.admin_user,
                        updated_by = self.admin_user,
                    )
                else:
                    PayrollDetail.objects.filter(payroll_master = self.payroll_master).delete()
                    
                for emp_payroll in self.all_employees_payroll_calculated():
                    emp,badalat,khosomat = emp_payroll
                    bank = ''
                    account_no = ''
                    try:
                        bank_account = emp.employeebankaccount_set.get(active=True)
                        bank = bank_account.bank
                        account_no = bank_account.account_no
                    except:
                        pass

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
                        tarikh_milad = emp.tarikh_milad,
                        salafiat_sandog = khosomat.salafiat_sandog,
                        draja_wazifia = emp.draja_wazifia,
                        alawa_sanawia = emp.alawa_sanawia,
                        bank = bank,
                        account_no = account_no,
                    )
        except Exception as e:
            print(f'Payroll not calculated: {e}')
            return False
        
        self.payroll_details = PayrollDetail.objects \
            .filter(payroll_master=self.payroll_master).prefetch_related("employee") \
            .exclude(employee__hikal_wazifi=self.hr_settings.get_code_as_float(Settings.SETTINGS_KHARJ_ELSHARIKA))

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
    
class MobasharaSheet():
    def __init__(self,year,month) -> None:
        self.year = year
        self.month = month

        self.hr_settings = HrSettings()
        self.employees = EmployeeMobashra.objects.filter(state=EmployeeMobashra.STATE_ACTIVE).prefetch_related("employee").filter(employee__status=EmployeeBasic.STATUS_ACTIVE)

        self.admin_user = get_user_model().objects.get(id=1)

    def employee_mobashara_calculated(self,emp_mobashara:EmployeeMobashra):
        first_day_in_month = datetime.date(self.year,self.month,1)

        mobashara = Mobashara(
            self.year,
            self.month,
            emp_mobashara,
            emp_mobashara.employee.employeevacation_set.filter(
                Q(end_dt_actual__gte=first_day_in_month) |
                Q(end_dt_actual__isnull=True)
            ),
            emp_mobashara.employee.mokalafvacation_set.filter(
                Q(end_dt_actual__gte=first_day_in_month) |
                Q(end_dt_actual__isnull=True)
            )
        )
        return mobashara
    
    def all_employees_mobashara_calculated(self):
        for emp in self.employees:
            x = self.employee_mobashara_calculated(emp)
            if x:
                yield(x)

    def calculate(self):
        if EmployeeMobashraMonthly.objects.filter(year = self.year,month = self.month,confirmed=True).exists():
            return False

        try:
            with transaction.atomic():        
                EmployeeMobashraMonthly.objects.filter(year = self.year,month = self.month).delete()

                for emp_mobashara in self.all_employees_mobashara_calculated():

                    x1 = _("ayam_2lmobashara_2lsafi")
                    x2 = _("ayam_2l2jazaa")
                    x3 = _("ayam_2ltaklif")
                    mobashara_amount = 0
                    if emp_mobashara._mobashara.toari2_enabled:
                        mobashara_amount = emp_mobashara.safi_2l2sti7gag

                    mamoria_amount = 0
                    if emp_mobashara._mobashara.m2moria_enabled:
                        emp_payroll = emp_mobashara.employee.payrolldetail_set.get(payroll_master__year=self.year,payroll_master__month=self.month)
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
                        m2moria_rate = self.hr_settings.get_code_as_float(Settings.SETTINGS_M2MORIA_RATE)
                        mamoria_amount = (badal.ajmali_almoratab/emp_mobashara.ayam_2lshahar)*m2moria_rate*emp_mobashara.ayam_2lmobashara_2lsafi

                    e3asha_amount = 0
                    if emp_mobashara._mobashara.e3ash_enabled:    
                        e3asha_amount = self.hr_settings.get_code_as_float(Settings.SETTINGS_E3ASHA_RATE) * emp_mobashara.ayam_2lmobashara_2lsafi

                    EmployeeMobashraMonthly.objects.create(
                        employee = emp_mobashara.employee,
                        year = self.year,
                        month = self.month,
                        amount = mobashara_amount,
                        amount_m2moria = mamoria_amount,
                        amount_e3asha = e3asha_amount,
                        rate = emp_mobashara.employee.mobashara_rate,
                        no_days_month = emp_mobashara.ayam_2lshahar,
                        no_days_mobashara = emp_mobashara.ayam_2lmobashara_2lsafi,
                        no_days_2jazaa = emp_mobashara.ayam_2l2jazaa,
                        no_days_taklif = emp_mobashara.ayam_2ltaklif,
                        created_by = self.admin_user,
                        updated_by = self.admin_user,
                    )

        except Exception as e:
            print(f'Mobashara not calculated: {e}')
            return False
        
    def all_employees_mobashara_from_db(self):
        return EmployeeMobashraMonthly.objects.filter(year = self.year,month = self.month).prefetch_related("employee")
    
    def confirm(self):
        with transaction.atomic():
            for p in self.all_employees_mobashara_from_db():
                p.confirmed = True
                p.save(update_fields=['confirmed'])

            return True

class Mokaf2Sheet():
    def __init__(self,year,month) -> None:
        self.year = year
        self.month = month

        self.hr_settings = HrSettings()
        self.employees = PayrollDetail.objects.filter(payroll_master__year = self.year,payroll_master__month = self.month).prefetch_related("payroll_master","employee").filter(employee__status=EmployeeBasic.STATUS_ACTIVE)

    def employee_mokaf2_from_db(self,emp_payroll:PayrollDetail):
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

        return Mokaf2(badal,emp_payroll.payroll_master.daribat_2lmokafa,emp_payroll.damga,khasm_salafiat_elsandog_min_elmokaf2=(not emp_payroll.payroll_master.khasm_salafiat_elsandog_min_elomoratab),salafiat_sandog=emp_payroll.salafiat_sandog)

    def all_employees_mokaf2_from_db(self):
        for emp in self.employees:
            x = self.employee_mokaf2_from_db(emp)
            if x:
                yield(emp.employee,x)
    

class M2moriaSheet():
    def __init__(self,year,month) -> None:
        self.year = int(year)
        self.month = int(month)

        first_day_in_month = datetime.date(self.year,self.month,1)

        self.hr_settings = HrSettings()
        self.employees = EmployeeM2moria.objects.filter(
            Q(end_dt_actual__gte=first_day_in_month) |
            Q(end_dt_actual__isnull=True)
        ).prefetch_related("employee").filter(employee__status=EmployeeBasic.STATUS_ACTIVE)

        self.admin_user = get_user_model().objects.get(id=1)

    def employee_m2moria_calculated(self,emp_m2moria:EmployeeM2moria):
        employee = emp_m2moria.employee
        moahil = Settings.MOAHIL_PREFIX + employee.moahil
        gasima = 0
        if(employee.gasima):
            gasima = self.hr_settings.get_code_as_float(Settings.SETTINGS_GASIMA)

        aadoa = 0
        if(employee.aadoa):
            aadoa = self.hr_settings.get_code_as_float(Settings.SETTINGS_AADOA)

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

            return M2moria(badal,self.year,self.month,emp_m2moria,self.hr_settings.get_code_as_float(Settings.SETTINGS_DAMGA))
        except Drajat3lawat.DoesNotExist as e:
            return None

    
    def all_employees_m2moria_calculated(self):
        for emp in self.employees:
            x = self.employee_m2moria_calculated(emp)
            if x:
                yield(x)

    def calculate(self):
        if EmployeeM2moriaMonthly.objects.filter(year = self.year,month = self.month,confirmed=True).exists():
            return False

        try:
            with transaction.atomic():        
                EmployeeM2moriaMonthly.objects.filter(year = self.year,month = self.month).delete()

                for emp_m2moria in self.all_employees_m2moria_calculated():
                    EmployeeM2moriaMonthly.objects.create(
                        employee = emp_m2moria.employee,
                        year = self.year,
                        month = self.month,
                        ajmali_2lmoratab = emp_m2moria.ajmali_2lmoratab,
                        no_days = emp_m2moria.ayam_2l3mal,
                        damga = emp_m2moria.damga,
                        safi_2l2sti7gag = emp_m2moria.safi_2l2sti7gag,
                        created_by = self.admin_user,
                        updated_by = self.admin_user,
                    )

        except Exception as e:
            print(f'M2moria not calculated: {e}')
            return False
        
    def all_employees_m2moria_from_db(self):
        return EmployeeM2moriaMonthly.objects.filter(year = self.year,month = self.month).prefetch_related("employee")
    
    def confirm(self):
        with transaction.atomic():
            for p in self.all_employees_m2moria_from_db():
                p.confirmed = True
                p.save(update_fields=['confirmed'])

            return True
