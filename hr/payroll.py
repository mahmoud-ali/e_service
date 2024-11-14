import datetime
from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError, transaction
from django.db.models import Q, Sum
from django.contrib.auth import get_user_model

from hr.calculations import Badalat_3lawat, BadalatModir3am, Khosomat, KhosomatModir3am, M2moria, MajlisEl2daraMokaf2, Mobashara, Mokaf2, Mokaf2Modir3am, Ta3agodMosimiMokaf2, Ta3agodMosimiMoratab, Wi7datMosa3idaMokaf2,Wi7datMosa3idaMokaf2tFarigMoratab

from .models import EmployeeM2moria, EmployeeM2moriaMonthly, EmployeeMajlisEl2dara, EmployeeMobashra, EmployeeJazaat,EmployeeBasic,Drajat3lawat, EmployeeMobashraMonthly, EmployeeWi7datMosa3da, PayrollDetail, PayrollDetailMajlisEl2dara, PayrollDetailTa3agodMosimi, PayrollDetailWi7datMosa3ida, PayrollMaster, PayrollTasoia,Settings,EmployeeSalafiat

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
        self.employees = EmployeeBasic.objects \
            .filter(status=EmployeeBasic.STATUS_ACTIVE) \
            .exclude(no3_2lertibat__in=[EmployeeBasic.NO3_2LERTIBAT_2L7ag, EmployeeBasic.NO3_2LERTIBAT_TA3AGOD, EmployeeBasic.NO3_2LERTIBAT_TA3AGOD_MOSIMI,EmployeeBasic.NO3_2LERTIBAT_MASHRO3,EmployeeBasic.NO3_2LERTIBAT_MAJLIS_EL2DARA])

        self.admin_user = get_user_model().objects.get(id=1)

        try:
            self.payroll_master = PayrollMaster.objects.get(year=self.year,month=self.month)
            self.payroll_details = PayrollDetail.objects \
                .filter(payroll_master=self.payroll_master).prefetch_related("payroll_master","employee") \
                .exclude(employee__no3_2lertibat__in=[EmployeeBasic.NO3_2LERTIBAT_2L7ag, EmployeeBasic.NO3_2LERTIBAT_TA3AGOD, EmployeeBasic.NO3_2LERTIBAT_TA3AGOD_MOSIMI,EmployeeBasic.NO3_2LERTIBAT_MASHRO3,EmployeeBasic.NO3_2LERTIBAT_MAJLIS_EL2DARA])
                # .exclude(employee__hikal_wazifi=self.hr_settings.get_code_as_float(Settings.SETTINGS_KHARJ_ELSHARIKA))
        except PayrollMaster.DoesNotExist:
            self.payroll_master = None
            self.payroll_details = []

    def employee_payroll_calculated(self,employee:EmployeeBasic):
        moahil = Settings.MOAHIL_PREFIX + employee.moahil
        salafiat_total = self.salafiat_qs.filter(employee=employee,no3_2lsalafia=EmployeeSalafiat.NO3_2LSALAFIA_SHARIKA).aggregate(total=Sum("amount"))['total'] or 0
        salafiat_sandog_total = self.salafiat_qs.filter(employee=employee,no3_2lsalafia=EmployeeSalafiat.NO3_2LSALAFIA_SANDOG).aggregate(total=Sum("amount"))['total'] or 0
        salafiat_moratab_total = self.salafiat_qs.filter(employee=employee,no3_2lsalafia=EmployeeSalafiat.NO3_2LSALAFIA_3LA_2LMORATAB).aggregate(total=Sum("amount"))['total'] or 0
        salafiat_mokaf2_total = self.salafiat_qs.filter(employee=employee,no3_2lsalafia=EmployeeSalafiat.NO3_2LSALAFIA_3LA_2LMOKAF2).aggregate(total=Sum("amount"))['total'] or 0
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
                salafiat_3la_2lmoratab=salafiat_moratab_total,
                salafiat_3la_2lmokaf2=salafiat_mokaf2_total,
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
            salafiat_3la_2lmoratab=emp_payroll.salafiat_3la_2lmoratab,
            salafiat_3la_2lmokaf2=emp_payroll.salafiat_3la_2lmokaf2,
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
                        salafiat_3la_2lmoratab = khosomat.salafiat_3la_2lmoratab,
                        salafiat_3la_2lmokaf2 = khosomat._salafiat_3la_2lmokaf2,
                        draja_wazifia = emp.draja_wazifia,
                        alawa_sanawia = emp.alawa_sanawia,
                        bank = bank,
                        account_no = account_no,
                    )
        except Exception as e:
            print(f'Payroll not calculated: {e}')
            return False
        
        # self.payroll_details = PayrollDetail.objects \
        #     .filter(payroll_master=self.payroll_master).prefetch_related("employee") \
        #     .exclude(employee__no3_2lertibat__in=[EmployeeBasic.NO3_2LERTIBAT_2L7ag, EmployeeBasic.NO3_2LERTIBAT_TA3AGOD, EmployeeBasic.NO3_2LERTIBAT_TA3AGOD_MOSIMI,EmployeeBasic.NO3_2LERTIBAT_MASHRO3])

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
    
    def is_calculated(self):
        if not self.payroll_master or (hasattr(self.payroll_master,'count') and self.payroll_master.count()==0):
            return False
        
        return True
    
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
        self.employees = PayrollDetail.objects \
            .exclude(employee__no3_2lertibat__in=[EmployeeBasic.NO3_2LERTIBAT_2L7ag, EmployeeBasic.NO3_2LERTIBAT_TA3AGOD, EmployeeBasic.NO3_2LERTIBAT_TA3AGOD_MOSIMI,EmployeeBasic.NO3_2LERTIBAT_MASHRO3]) \
            .filter(payroll_master__year = self.year,payroll_master__month = self.month).prefetch_related("payroll_master","employee").filter(employee__status=EmployeeBasic.STATUS_ACTIVE)
            # .exclude(employee__hikal_wazifi=self.hr_settings.get_code_as_float(Settings.SETTINGS_KHARJ_ELSHARIKA))\

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

        return Mokaf2(badal,emp_payroll.payroll_master.daribat_2lmokafa,emp_payroll.damga,khasm_salafiat_elsandog_min_elmokaf2=(not emp_payroll.payroll_master.khasm_salafiat_elsandog_min_elomoratab),salafiat_sandog=emp_payroll.salafiat_sandog,salafiat_3la_2lmokaf2=emp_payroll.salafiat_3la_2lmokaf2)

    def all_employees_mokaf2_from_db(self):
        for emp in self.employees:
            x = self.employee_mokaf2_from_db(emp)
            if x:
                yield(emp.employee,x)
    
class M2moriaSheet():
    def __init__(self,year,month) -> None:
        self.year = int(year)
        self.month = int(month)

        self.payroll_master = PayrollMaster.objects.get(
                year = self.year,
                month = self.month,
            )

        first_day_in_month = datetime.date(self.year,self.month,1)

        self.hr_settings = HrSettings()
        self.employees = EmployeeM2moria.objects.filter(
            Q(end_dt_actual__gte=first_day_in_month) 
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
        # if EmployeeM2moriaMonthly.objects.filter(year = self.year,month = self.month,confirmed=True).exists():
        #     return False

        if not self.payroll_master:
            self.payroll_master = PayrollMaster.objects.get(
                year = self.year,
                month = self.month,
            )
        else:
            EmployeeM2moriaMonthly.objects.filter(payroll_master = self.payroll_master).delete()

        try:
            with transaction.atomic():        

                for emp_m2moria in self.all_employees_m2moria_calculated():
                    EmployeeM2moriaMonthly.objects.create(
                        payroll_master = self.payroll_master,
                        m2moria_master = emp_m2moria._m2moria_model,
                        employee = emp_m2moria.employee,
                        # year = self.year,
                        # month = self.month,
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
        return EmployeeM2moriaMonthly.objects.filter(payroll_master = self.payroll_master).prefetch_related("employee")
    
    # def confirm(self):
    #     with transaction.atomic():
    #         for p in self.all_employees_m2moria_from_db():
    #             p.confirmed = True
    #             p.save(update_fields=['confirmed'])

    #         return True

###########
class Wi7datMosa3idaMokaf2tFarigMoratabPayroll():
    def __init__(self,year,month) -> None:
        self.year = year
        self.month = month

        self.hr_settings = HrSettings()
        self.employees = EmployeeBasic.objects \
            .filter(no3_2lertibat=EmployeeBasic.NO3_2LERTIBAT_2L7ag) \
            .filter(status=EmployeeBasic.STATUS_ACTIVE) \
            .order_by('hikal_wazifi')
        
        self.salafiat_qs = EmployeeSalafiat.objects.filter(year=self.year,month=self.month)

        self.admin_user = get_user_model().objects.get(id=1)

        try:
            self.payroll_master = PayrollMaster.objects.get(year=self.year,month=self.month)
            self.payroll_details = PayrollDetailWi7datMosa3ida.objects \
                .filter(payroll_master=self.payroll_master)\
                .filter(has_diff=True)\
                .prefetch_related("payroll_master","employee")
                
        except PayrollMaster.DoesNotExist:
            self.payroll_master = None
            self.payroll_details = []

    def employee_payroll_calculated(self,employee:EmployeeBasic):
        try:
            obj = employee.wi7dat_mosa3da
            obj_payroll_2ljiha_2l2om = obj.payroll_2ljiha_2l2om
            obj_has_diff = obj.has_diff
        except EmployeeWi7datMosa3da.DoesNotExist as e:
            obj_payroll_2ljiha_2l2om = 0
            obj_has_diff = False
            
        gasima = 0
        aadoa = 0
        atfal = 0
        moahil = 0

        try:
            draj_obj = Drajat3lawat.objects.get(draja_wazifia=employee.draja_wazifia,alawa_sanawia=employee.alawa_sanawia)
            badal = Badalat_3lawat(
                draj_obj.abtdai,
                draj_obj.galaa_m3isha,
                shakhsia=draj_obj.shakhsia,
                aadoa=aadoa,
                gasima=gasima,
                atfal=atfal,
                moahil=moahil,
                ma3adin=draj_obj.ma3adin,
                month = self.month,
                year = self.month,
            )

            mokaf2 = Wi7datMosa3idaMokaf2tFarigMoratab(
                payroll_2lsharika=badal.ajmali_almoratab,
                payroll_2ljiha_2l2om=obj_payroll_2ljiha_2l2om,
                has_diff=obj_has_diff,
                damga=self.hr_settings.get_code_as_float(Settings.SETTINGS_DAMGA),
                sandog=self.hr_settings.get_code_as_float(Settings.SETTINGS_SANDOG),
            )

            return (employee,badal,mokaf2)
        except Drajat3lawat.DoesNotExist as e:
            pass
    
    def all_employees_payroll_calculated(self):
        for emp in self.employees:
            x = self.employee_payroll_calculated(emp)
            if x:
                yield(x)

    def employee_payroll_from_db(self,emp_payroll:PayrollDetailWi7datMosa3ida):
        badal = Badalat_3lawat(
            emp_payroll.abtdai,
            emp_payroll.galaa_m3isha,
            shakhsia=emp_payroll.shakhsia,
            aadoa=0,
            gasima=0,
            atfal=0,
            moahil=0,
            ma3adin=emp_payroll.ma3adin,
            month = emp_payroll.payroll_master.month,
            year = emp_payroll.payroll_master.year,
        )

        mokaf2 = Wi7datMosa3idaMokaf2tFarigMoratab(
            payroll_2lsharika=badal.ajmali_almoratab,
            payroll_2ljiha_2l2om=emp_payroll.payroll_2ljiha_2l2om,
            has_diff=emp_payroll.has_diff,
            damga=emp_payroll.damga,
            sandog=emp_payroll.sandog,
        )

        return (emp_payroll.employee,badal,mokaf2,emp_payroll.draja_wazifia,emp_payroll.alawa_sanawia)
    
    def all_employees_payroll_from_db(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db(emp_payroll))

    def employee_payroll_from_db_with_bank_account(self,emp_payroll:PayrollDetailWi7datMosa3ida):
        tmp_lst = list(self.employee_payroll_from_db(emp_payroll))
        tmp_lst.append(emp_payroll.bank)
        tmp_lst.append(emp_payroll.account_no)
        return tuple(tmp_lst)
    
    def all_employees_payroll_from_db_with_bank_account(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db_with_bank_account(emp_payroll))


    def employee_payroll_from_employee(self,emp:EmployeeBasic):
        emp_payroll = PayrollDetailWi7datMosa3ida.objects.filter(payroll_master=self.payroll_master,employee=emp).prefetch_related("employee").first()
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


                    self.payroll_master = PayrollMaster.objects.get(
                        year = self.year,
                        month = self.month,
                    )
                else:
                    PayrollDetailWi7datMosa3ida.objects.filter(payroll_master = self.payroll_master).delete()
                    
                for emp_payroll in self.all_employees_payroll_calculated():
                    emp,badalat,mokaf2 = emp_payroll
                    bank = ''
                    account_no = ''
                    salafiat_sandog_total = self.salafiat_qs.filter(employee=emp,no3_2lsalafia=EmployeeSalafiat.NO3_2LSALAFIA_SANDOG).aggregate(total=Sum("amount"))['total'] or 0

                    try:
                        bank_account = emp.employeebankaccount_set.get(active=True)
                        bank = bank_account.bank
                        account_no = bank_account.account_no
                    except:
                        pass

                    PayrollDetailWi7datMosa3ida.objects.create(
                        payroll_master = self.payroll_master,
                        employee = emp,
                        abtdai = badalat.abtdai,
                        galaa_m3isha = badalat.galaa_m3isha,
                        shakhsia = badalat.shakhsia,
                        ma3adin = badalat.ma3adin,
                        damga = self.hr_settings.get_code_as_float(Settings.SETTINGS_DAMGA),
                        sandog = self.hr_settings.get_code_as_float(Settings.SETTINGS_SANDOG),
                        sandog_kahraba = 0,
                        # salafiat = 0,
                        # jazaat = 0,
                        # salafiat_sandog = khosomat.salafiat_sandog,
                        # salafiat_3la_2lmoratab = khosomat.salafiat_3la_2lmoratab,
                        # salafiat_3la_2lmokaf2 = khosomat._salafiat_3la_2lmokaf2,
                        salafiat_sandog=salafiat_sandog_total,
                        tarikh_milad = emp.tarikh_milad,
                        payroll_2ljiha_2l2om = mokaf2.payroll_2ljiha_2l2om,
                        payroll_2lsharika = mokaf2.payroll_2lsharika,
                        has_diff = mokaf2.has_diff,
                        draja_wazifia = emp.draja_wazifia,
                        alawa_sanawia = emp.alawa_sanawia,
                        bank = bank,
                        account_no = account_no,
                    )

        except Exception as e:
            print(f'Payroll not calculated: {e}')
            return False
        
        self.payroll_details = PayrollDetailWi7datMosa3ida.objects \
            .filter(payroll_master=self.payroll_master).prefetch_related("employee")

    def is_confirmed(self):
        if not hasattr(self.payroll_master,'confirmed'):
            return False
        
        return self.payroll_master.confirmed

###########
class Wi7datMosa3idaMokaf2tPayroll():
    def __init__(self,year,month) -> None:
        self.year = year
        self.month = month

        self.hr_settings = HrSettings()
        self.employees = EmployeeBasic.objects \
            .filter(no3_2lertibat=EmployeeBasic.NO3_2LERTIBAT_2L7ag) \
            .filter(status=EmployeeBasic.STATUS_ACTIVE)
        
        self.admin_user = get_user_model().objects.get(id=1)

        try:
            self.payroll_master = PayrollMaster.objects.get(year=self.year,month=self.month)
            self.payroll_details = PayrollDetailWi7datMosa3ida.objects \
                .filter(payroll_master=self.payroll_master)\
                .prefetch_related("payroll_master","employee")
                
        except PayrollMaster.DoesNotExist:
            self.payroll_master = None
            self.payroll_details = []
    
    def all_employees_payroll_calculated(self):
        for emp in self.employees:
            x = self.employee_payroll_calculated(emp)
            if x:
                yield(x)

    def employee_payroll_from_db(self,emp_payroll:PayrollDetailWi7datMosa3ida):
        badal = Badalat_3lawat(
            emp_payroll.abtdai,
            emp_payroll.galaa_m3isha,
            shakhsia=emp_payroll.shakhsia,
            aadoa=0,
            gasima=0,
            atfal=0,
            moahil=0,
            ma3adin=emp_payroll.ma3adin,
            month = emp_payroll.payroll_master.month,
            year = emp_payroll.payroll_master.year,
        )

        mokaf2 = Wi7datMosa3idaMokaf2(
                payroll_2lsharika=badal.ajmali_almoratab,
                damga=self.hr_settings.get_code_as_float(Settings.SETTINGS_DAMGA),
                salafiat_sandog=emp_payroll.salafiat_sandog,
        )

        return (emp_payroll.employee,badal,mokaf2,emp_payroll.draja_wazifia,emp_payroll.alawa_sanawia)
    
    def all_employees_payroll_from_db(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db(emp_payroll))

    def employee_payroll_from_db_with_bank_account(self,emp_payroll:PayrollDetailWi7datMosa3ida):
        tmp_lst = list(self.employee_payroll_from_db(emp_payroll))
        tmp_lst.append(emp_payroll.bank)
        tmp_lst.append(emp_payroll.account_no)
        return tuple(tmp_lst)
    
    def all_employees_payroll_from_db_with_bank_account(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db_with_bank_account(emp_payroll))


    def employee_payroll_from_employee(self,emp:EmployeeBasic):
        emp_payroll = PayrollDetailWi7datMosa3ida.objects.filter(payroll_master=self.payroll_master,employee=emp).prefetch_related("employee").first()
        if emp_payroll:
            return self.employee_payroll_from_db(emp_payroll)
        
        return (None,None,None,None,None,)
    
###########
class Ta3agodMosimiPayroll():
    def __init__(self,year,month) -> None:
        self.year = year
        self.month = month

        self.hr_settings = HrSettings()
        self.employees = EmployeeBasic.objects \
            .filter(no3_2lertibat=EmployeeBasic.NO3_2LERTIBAT_TA3AGOD_MOSIMI) \
            .filter(status=EmployeeBasic.STATUS_ACTIVE)
        
        self.admin_user = get_user_model().objects.get(id=1)

        try:
            self.payroll_master = PayrollMaster.objects.get(year=self.year,month=self.month)
            self.payroll_details = PayrollDetailTa3agodMosimi.objects \
                .filter(payroll_master=self.payroll_master).prefetch_related("payroll_master","employee")
                
        except PayrollMaster.DoesNotExist:
            self.payroll_master = None
            self.payroll_details = []

    def employee_payroll_calculated(self,employee:EmployeeBasic):
        try:
            draj_obj = Drajat3lawat.objects.get(draja_wazifia=employee.draja_wazifia,alawa_sanawia=employee.alawa_sanawia)

            if draj_obj.draja_wazifia <= 9:
                ajmali = self.hr_settings.get_code_as_float(Settings.SETTINGS_TA3AGODMOSIMI_MOZAF)
            else:
                ajmali = self.hr_settings.get_code_as_float(Settings.SETTINGS_TA3AGODMOSIMI_3AMIL)

            moratab = Ta3agodMosimiMoratab(
                ajmali=ajmali,
                damga=self.hr_settings.get_code_as_float(Settings.SETTINGS_DAMGA),
            )

            return (employee,moratab)
        except Drajat3lawat.DoesNotExist as e:
            pass
    
    def all_employees_payroll_calculated(self):
        for emp in self.employees:
            x = self.employee_payroll_calculated(emp)
            if x:
                yield(x)

    def employee_payroll_from_db(self,emp_payroll:PayrollDetailTa3agodMosimi):
        moratab = Ta3agodMosimiMoratab(
            ajmali = emp_payroll.payroll_ajmali,
            damga=emp_payroll.damga,
        )

        return (emp_payroll.employee,moratab,emp_payroll.draja_wazifia,emp_payroll.alawa_sanawia)
    
    def all_employees_payroll_from_db(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db(emp_payroll))

    def employee_payroll_from_db_with_bank_account(self,emp_payroll:PayrollDetailTa3agodMosimi):
        tmp_lst = list(self.employee_payroll_from_db(emp_payroll))
        tmp_lst.append(emp_payroll.bank)
        tmp_lst.append(emp_payroll.account_no)
        return tuple(tmp_lst)
    
    def all_employees_payroll_from_db_with_bank_account(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db_with_bank_account(emp_payroll))


    def employee_payroll_from_employee(self,emp:EmployeeBasic):
        emp_payroll = PayrollDetailTa3agodMosimi.objects.filter(payroll_master=self.payroll_master,employee=emp).prefetch_related("employee").first()
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


                    self.payroll_master = PayrollMaster.objects.get(
                        year = self.year,
                        month = self.month,
                    )
                else:
                    PayrollDetailTa3agodMosimi.objects.filter(payroll_master = self.payroll_master).delete()
                    
                for emp_payroll in self.all_employees_payroll_calculated():
                    emp,moratab = emp_payroll
                    bank = ''
                    account_no = ''
                    try:
                        bank_account = emp.employeebankaccount_set.get(active=True)
                        bank = bank_account.bank
                        account_no = bank_account.account_no
                    except:
                        pass

                    PayrollDetailTa3agodMosimi.objects.create(
                        payroll_master = self.payroll_master,
                        employee = emp,
                        damga = self.hr_settings.get_code_as_float(Settings.SETTINGS_DAMGA),
                        # sandog = self.hr_settings.get_code_as_float(Settings.SETTINGS_SANDOG),
                        # sandog_kahraba = 0,
                        # salafiat = 0,
                        # jazaat = 0,
                        # salafiat_sandog = khosomat.salafiat_sandog,
                        # salafiat_3la_2lmoratab = khosomat.salafiat_3la_2lmoratab,
                        # salafiat_3la_2lmokaf2 = khosomat._salafiat_3la_2lmokaf2,
                        tarikh_milad = emp.tarikh_milad,
                        payroll_ajmali = moratab.ajmali,
                        payroll_mokaf2 = self.hr_settings.get_code_as_float(Settings.SETTINGS_TA3AGODMOSIMI_MOKAF2),
                        draja_wazifia = emp.draja_wazifia,
                        alawa_sanawia = emp.alawa_sanawia,
                        bank = bank,
                        account_no = account_no,
                    )

        except Exception as e:
            print(f'Payroll not calculated: {e}')
            return False
        
        self.payroll_details = PayrollDetailTa3agodMosimi.objects \
            .filter(payroll_master=self.payroll_master).prefetch_related("employee")

    def is_confirmed(self):
        if not hasattr(self.payroll_master,'confirmed'):
            return False
        
        return self.payroll_master.confirmed

###########
class Ta3agodMosimiMokaf2Payroll():
    def __init__(self,year,month) -> None:
        self.year = year
        self.month = month

        self.hr_settings = HrSettings()
        self.employees = EmployeeBasic.objects \
            .filter(no3_2lertibat=EmployeeBasic.NO3_2LERTIBAT_TA3AGOD_MOSIMI) \
            .filter(status=EmployeeBasic.STATUS_ACTIVE)
        
        self.admin_user = get_user_model().objects.get(id=1)

        try:
            self.payroll_master = PayrollMaster.objects.get(year=self.year,month=self.month)
            self.payroll_details = PayrollDetailTa3agodMosimi.objects \
                .filter(payroll_master=self.payroll_master).prefetch_related("payroll_master","employee")
                
        except PayrollMaster.DoesNotExist:
            self.payroll_master = None
            self.payroll_details = []

    def employee_payroll_from_db(self,emp_payroll:PayrollDetailTa3agodMosimi):
        moratab = Ta3agodMosimiMokaf2(
            mokaf2 = emp_payroll.payroll_mokaf2,
            damga=emp_payroll.damga,
        )

        return (emp_payroll.employee,moratab,emp_payroll.draja_wazifia,emp_payroll.alawa_sanawia)
    
    def all_employees_payroll_from_db(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db(emp_payroll))

    def employee_payroll_from_db_with_bank_account(self,emp_payroll:PayrollDetailTa3agodMosimi):
        tmp_lst = list(self.employee_payroll_from_db(emp_payroll))
        tmp_lst.append(emp_payroll.bank)
        tmp_lst.append(emp_payroll.account_no)
        return tuple(tmp_lst)
    
    def all_employees_payroll_from_db_with_bank_account(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db_with_bank_account(emp_payroll))


    def employee_payroll_from_employee(self,emp:EmployeeBasic):
        emp_payroll = PayrollDetailTa3agodMosimi.objects.filter(payroll_master=self.payroll_master,employee=emp).prefetch_related("employee").first()
        if emp_payroll:
            return self.employee_payroll_from_db(emp_payroll)
        
        return (None,None,None,None,None,)

###########################
class MajlisEl2daraMokaf2Payroll():
    def __init__(self,year,month) -> None:
        self.year = year
        self.month = month

        self.hr_settings = HrSettings()
        self.employees = EmployeeBasic.objects \
            .filter(no3_2lertibat=EmployeeBasic.NO3_2LERTIBAT_MAJLIS_EL2DARA) \
            .filter(status=EmployeeBasic.STATUS_ACTIVE)
        
        self.admin_user = get_user_model().objects.get(id=1)

        try:
            self.payroll_master = PayrollMaster.objects.get(year=self.year,month=self.month)
            self.payroll_details = PayrollDetailMajlisEl2dara.objects \
                .filter(payroll_master=self.payroll_master).prefetch_related("payroll_master","employee")\
                .order_by('-payroll_mokaf2')
                
        except PayrollMaster.DoesNotExist:
            self.payroll_master = None
            self.payroll_details = []

    def employee_payroll_calculated(self,employee:EmployeeBasic):
        try:
# payroll_asasi
            emp_majlis_position = EmployeeMajlisEl2dara.POSITION_3ODO
            try:
                emp_majlis = employee.majlis_el2dara
                emp_majlis_position = emp_majlis.position
            except:
                pass

            mokaf2 = self.hr_settings.get_code_as_float(Settings.SETTINGS_MAJLIS_EL2DARA_3ODO)

            asasi = 0
            gasima = 0
            atfal = 0
            moahil = 0
            sandog = 0

            if emp_majlis_position == EmployeeMajlisEl2dara.POSITION_R2IS_2LMAJLIS:
                mokaf2 = self.hr_settings.get_code_as_float(Settings.SETTINGS_MAJLIS_EL2DARA_R2IS_2LMAJLIS)
            elif emp_majlis_position == EmployeeMajlisEl2dara.POSITION_MODIR_3AM:
                asasi = self.hr_settings.get_code_as_float(Settings.SETTINGS_MODIR_3AM_ASAI)
                moahil_str = Settings.MOAHIL_PREFIX + employee.moahil
                moahil=self.hr_settings.get_code_as_float(moahil_str)
                atfal=(employee.atfal *self.hr_settings.get_code_as_float(Settings.SETTINGS_ATFAL))
                sandog=self.hr_settings.get_code_as_float(Settings.SETTINGS_SANDOG)
                if(employee.gasima):
                    gasima = self.hr_settings.get_code_as_float(Settings.SETTINGS_GASIMA)

            moratab = MajlisEl2daraMokaf2(
                mokaf2=mokaf2,
                asasi=asasi,
                damga=self.hr_settings.get_code_as_float(Settings.SETTINGS_DAMGA),
                gasima=gasima,
                atfal=atfal,
                moahil=moahil,
                sandog=sandog,
            )

            return (employee,moratab)
        except Exception as e:
            print(f"not calcuted {e}")
    
    def all_employees_payroll_calculated(self):
        for emp in self.employees:
            x = self.employee_payroll_calculated(emp)
            if x:
                yield(x)

    def employee_payroll_from_db(self,emp_payroll:PayrollDetailMajlisEl2dara):
        moratab = MajlisEl2daraMokaf2(
            mokaf2 = emp_payroll.payroll_mokaf2,
            asasi = emp_payroll.payroll_asasi,
            damga=emp_payroll.damga,
            gasima=emp_payroll.gasima,
            atfal=emp_payroll.atfal,
            moahil=emp_payroll.moahil,
            sandog=emp_payroll.sandog,
        )

        return (emp_payroll.employee,moratab,emp_payroll.draja_wazifia,emp_payroll.alawa_sanawia)
    
    def all_employees_payroll_from_db(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db(emp_payroll))

    def employee_payroll_from_db_with_bank_account(self,emp_payroll:PayrollDetailMajlisEl2dara):
        tmp_lst = list(self.employee_payroll_from_db(emp_payroll))
        tmp_lst.append(emp_payroll.bank)
        tmp_lst.append(emp_payroll.account_no)
        return tuple(tmp_lst)
    
    def all_employees_payroll_from_db_with_bank_account(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db_with_bank_account(emp_payroll))


    def employee_payroll_from_employee(self,emp:EmployeeBasic):
        emp_payroll = PayrollDetailMajlisEl2dara.objects.filter(payroll_master=self.payroll_master,employee=emp).prefetch_related("employee").first()
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
                    self.payroll_master = PayrollMaster.objects.get(
                        year = self.year,
                        month = self.month,
                    )
                else:
                    PayrollDetailMajlisEl2dara.objects.filter(payroll_master = self.payroll_master).delete()
                    
                for emp_payroll in self.all_employees_payroll_calculated():
                    emp,moratab = emp_payroll
                    bank = ''
                    account_no = ''
                    try:
                        bank_account = emp.employeebankaccount_set.get(active=True)
                        bank = bank_account.bank
                        account_no = bank_account.account_no
                    except:
                        pass


                    PayrollDetailMajlisEl2dara.objects.create(
                        payroll_master = self.payroll_master,
                        employee = emp,
                        damga = self.hr_settings.get_code_as_float(Settings.SETTINGS_DAMGA),
                        # sandog = self.hr_settings.get_code_as_float(Settings.SETTINGS_SANDOG),
                        # sandog_kahraba = 0,
                        # salafiat = 0,
                        # jazaat = 0,
                        # salafiat_sandog = khosomat.salafiat_sandog,
                        # salafiat_3la_2lmoratab = khosomat.salafiat_3la_2lmoratab,
                        # salafiat_3la_2lmokaf2 = khosomat._salafiat_3la_2lmokaf2,
                        tarikh_milad = emp.tarikh_milad,
                        payroll_mokaf2 = moratab.mokaf2,
                        payroll_asasi = moratab.asasi,
                        gasima = moratab.ajtima3ia_gasima,
                        atfal = moratab.ajtima3ia_atfal,
                        moahil = moratab.moahil,
                        sandog = moratab.sandog,
                        draja_wazifia = emp.draja_wazifia,
                        alawa_sanawia = emp.alawa_sanawia,
                        bank = bank,
                        account_no = account_no,
                    )

        except Exception as e:
            print(f'Payroll not calculated: {e} {emp}')
            # return False
        
    def is_confirmed(self):
        if not hasattr(self.payroll_master,'confirmed'):
            return False
        
        return self.payroll_master.confirmed

###########################
class Modir3amPayroll():
    def __init__(self,year,month) -> None:
        self.year = year
        self.month = month

        self.hr_settings = HrSettings()
        self.employees = EmployeeBasic.objects \
            .filter(id__in=EmployeeMajlisEl2dara.objects.filter(position=EmployeeMajlisEl2dara.POSITION_MODIR_3AM).values_list("id")) \
            .filter(status=EmployeeBasic.STATUS_ACTIVE)
        
        self.admin_user = get_user_model().objects.get(id=1)

        try:
            self.payroll_master = PayrollMaster.objects.get(year=self.year,month=self.month)
            self.payroll_details = PayrollDetailMajlisEl2dara.objects \
                .filter(payroll_master=self.payroll_master).filter(payroll_asasi__gt=0).prefetch_related("payroll_master","employee")
                
        except PayrollMaster.DoesNotExist:
            self.payroll_master = None
            self.payroll_details = []

    def employee_payroll_from_db(self,emp_payroll:PayrollDetailMajlisEl2dara):
        badalat = BadalatModir3am(
            abtdai = emp_payroll.payroll_asasi,
            gasima = emp_payroll.gasima,
            atfal=emp_payroll.atfal,
            moahil=emp_payroll.moahil,
        )

        khosomat = KhosomatModir3am(
            badalat,
            zaka_kafaf=self.payroll_master.zaka_kafaf,
            zaka_nisab=self.payroll_master.zaka_nisab,
            salafiat=emp_payroll.salafiat,
            damga=emp_payroll.damga,
            sandog=emp_payroll.sandog,
        )

        mokaf2 = Mokaf2Modir3am(
            badalat,
            damga=emp_payroll.damga,
        )

        return (emp_payroll.employee,badalat,khosomat,mokaf2,emp_payroll.draja_wazifia,emp_payroll.alawa_sanawia)
    
    def all_employees_payroll_from_db(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db(emp_payroll))

    def employee_payroll_from_db_with_bank_account(self,emp_payroll:PayrollDetailMajlisEl2dara):
        tmp_lst = list(self.employee_payroll_from_db(emp_payroll))
        tmp_lst.append(emp_payroll.bank)
        tmp_lst.append(emp_payroll.account_no)
        return tuple(tmp_lst)
    
    def all_employees_payroll_from_db_with_bank_account(self):
        for emp_payroll in self.payroll_details:
            yield(self.employee_payroll_from_db_with_bank_account(emp_payroll))

    def employee_payroll_from_employee(self,emp:EmployeeBasic):
        emp_payroll = PayrollDetailMajlisEl2dara.objects.filter(payroll_master=self.payroll_master,employee=emp).prefetch_related("employee").first()
        if emp_payroll:
            return self.employee_payroll_from_db(emp_payroll)
        
        return (None,None,None,None,None,)

class TasoiaPayroll():
    def __init__(self,year,month) -> None:
        self.year = year
        self.month = month

        self.payroll = Payroll(self.year,self.month)

    def calculate(self):
        total_abtdai = 0
        total_galaa_m3isha = 0
        total_tabi3at_3mal = 0
        total_tamtheel = 0
        total_mihna = 0

        total_ma3adin = 0
        total_aadoa = 0
        total_gasima = 0
        total_atfal = 0
        total_moahil = 0
        total_shakhsia = 0
        total_makhatir = 0

        total_salafiat = 0
        total_damga = 0
        total_m3ash = 0

        total_dariba = 0 
        total_tameen_ajtima3i = 0 
        total_zakat = 0 
        total_youm_algoat_almosalaha = 0
        total_sandog = 0
        total_jazaat = 0
        total_salafiat_sandog = 0

        for (emp,badalat,khosomat,draja_wazifia,alawa_sanawia) in self.payroll.all_employees_payroll_from_db():
            total_abtdai += badalat.abtdai
            total_galaa_m3isha += badalat.galaa_m3isha
            total_tabi3at_3mal += badalat.tabi3at_3mal
            total_tamtheel += badalat.tamtheel
            total_mihna += badalat.mihna
            total_ma3adin += badalat.ma3adin
            total_aadoa += badalat.aadoa
            total_gasima += badalat.ajtima3ia_gasima
            total_atfal += badalat.ajtima3ia_atfal
            total_moahil += badalat.moahil
            total_shakhsia += badalat.shakhsia
            total_makhatir += badalat.makhatir

            total_salafiat += khosomat.salafiat
            total_dariba += khosomat.dariba
            total_damga += khosomat.damga
            total_tameen_ajtima3i += khosomat.tameen_ajtima3i
            total_m3ash += khosomat.m3ash
            total_sandog = khosomat.sandog            
            total_zakat += khosomat.zakat
            total_youm_algoat_almosalaha += khosomat.youm_algoat_almosalaha
            total_jazaat += khosomat.jazaat
            total_salafiat_sandog +=khosomat.salafiat_sandog

        total_band_2wal = (total_abtdai + total_galaa_m3isha)

        ajtima3ia = (total_gasima + total_atfal)
        total_band_tani = (total_tabi3at_3mal+total_tamtheel+total_mihna+total_ma3adin+total_aadoa+ajtima3ia+total_moahil+total_shakhsia+total_makhatir)

        total_band_2wal_tani = (total_band_2wal+total_band_tani)

        try:
            obj = PayrollTasoia.objects.create(
                payroll_master = self.payroll.payroll_master,
                total_abtdai = total_abtdai,
                total_galaa_m3isha = total_galaa_m3isha,
                total_tabi3at_3mal = total_tabi3at_3mal,
                total_tamtheel = total_tamtheel,
                total_mihna = total_mihna,
                total_ma3adin = total_ma3adin,
                total_aadoa = total_aadoa,
                total_ajtima3ia = ajtima3ia,
                total_moahil = total_moahil,
                total_shakhsia = total_shakhsia,
                total_makhatir = total_makhatir,
                total_salafiat = total_salafiat,
                total_dariba = total_dariba,
                total_damga = total_damga,
                total_m3ash = total_m3ash,
                total_tameen_ajtima3i = total_tameen_ajtima3i,
                total_sandog = total_sandog,
                total_zakat = total_zakat,
                total_youm_algoat_almosalaha = total_youm_algoat_almosalaha,
                total_jazaat = total_jazaat,
                total_salafiat_sandog = total_salafiat_sandog
            )

        except IntegrityError:
            pass

    def from_db(self):
        try:
            return PayrollTasoia.objects.get(payroll_master=self.payroll.payroll_master)
        except:
            return None
