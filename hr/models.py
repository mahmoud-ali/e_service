from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.forms import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator,MinLengthValidator

MONTH_JAN = 1
MONTH_FEB = 2
MONTH_MAR = 3
MONTH_APR = 4
MONTH_MAY = 5
MONTH_JUN = 6
MONTH_JLY = 7
MONTH_AUG = 8
MONTH_SEP = 9
MONTH_OCT = 10
MONTH_NOV = 11
MONTH_DEC = 12

MONTH_CHOICES = {
    MONTH_JAN: _('MONTH_JAN'),
    MONTH_FEB: _('MONTH_FEB'),
    MONTH_MAR: _('MONTH_MAR'),
    MONTH_APR: _('MONTH_APR'),
    MONTH_MAY: _('MONTH_MAY'),
    MONTH_JUN: _('MONTH_JUN'),
    MONTH_JLY: _('MONTH_JLY'),
    MONTH_AUG: _('MONTH_AUG'),
    MONTH_SEP: _('MONTH_SEP'),
    MONTH_OCT: _('MONTH_OCT'),
    MONTH_NOV: _('MONTH_NOV'),
    MONTH_DEC: _('MONTH_DEC'),
}

MOAHIL_THANOI = 'thanoi'
MOAHIL_DEPLOM_TEGANI = 'deplom_tegani'
MOAHIL_DEPLOM_WASEET = 'deplom_waseet'
MOAHIL_BAKLARIOS = 'baklarios'
MOAHIL_BAKLARIOS_SHARAF = 'baklarios_sharaf'
MOAHIL_DAPLOM_3ALI = 'daplom_3ali'
MOAHIL_MAJSTEAR = 'majstear'
MOAHIL_DECTORA = 'dectora'

MOAHIL_CHOICES = {
    MOAHIL_THANOI: _('MOAHIL_THANOI'),
    MOAHIL_DEPLOM_TEGANI: _('MOAHIL_DEPLOM_TEGANI'),
    MOAHIL_DEPLOM_WASEET: _('MOAHIL_DEPLOM_WASEET'),
    MOAHIL_BAKLARIOS: _('MOAHIL_BAKLARIOS'),
    MOAHIL_BAKLARIOS_SHARAF: _('MOAHIL_BAKLARIOS_SHARAF'),
    MOAHIL_DAPLOM_3ALI: _('MOAHIL_DAPLOM_3ALI'),
    MOAHIL_MAJSTEAR: _('MOAHIL_MAJSTEAR'),
    MOAHIL_DECTORA: _('MOAHIL_DECTORA'),
}

MOAHIL_WEIGHT = {
    MOAHIL_THANOI: 1,
    MOAHIL_DEPLOM_WASEET: 2,
    MOAHIL_DEPLOM_TEGANI: 3,
    MOAHIL_BAKLARIOS: 4,
    MOAHIL_BAKLARIOS_SHARAF: 5,
    MOAHIL_DAPLOM_3ALI: 6,
    MOAHIL_MAJSTEAR: 7,
    MOAHIL_DECTORA: 8,
}

MOSAMA_CATEGORY_2LMODIR_2L3AM = 'modir_2l3am'
MOSAMA_CATEGORY_2LMOSA3DEEN = 'mosa3deen'
MOSAMA_CATEGORY_MODRA2_2L2DARAT_2L3AMA = 'modra2_3ameen'
MOSAMA_CATEGORY_MODRA2_2L2DARAT_2LFAR3IA = 'modra2_far3ia'
MOSAMA_CATEGORY_RO2SA2_2L2GSAM = 'ro2sa2_2gsam'
MOSAMA_CATEGORY_2LMOZAFEEN = 'mozafeen'
MOSAMA_CATEGORY_2L3MAL_SAGEEN = '3mal_sageen'

MOSAMA_CATEGORY_CHOICES = {
    MOSAMA_CATEGORY_2LMODIR_2L3AM:_('CATEGORY_2LMODIR_2L3AM'),
    MOSAMA_CATEGORY_2LMOSA3DEEN:_('CATEGORY_2LMOSA3DEEN'),
    MOSAMA_CATEGORY_MODRA2_2L2DARAT_2L3AMA:_('CATEGORY_MODRA2_2L2DARAT_2L3AMA'),
    MOSAMA_CATEGORY_MODRA2_2L2DARAT_2LFAR3IA:_('CATEGORY_MODRA2_2L2DARAT_2LFAR3IA'),
    MOSAMA_CATEGORY_RO2SA2_2L2GSAM:_('CATEGORY_RO2SA2_2L2GSAM'),
    MOSAMA_CATEGORY_2LMOZAFEEN:_('CATEGORY_2LMOZAFEEN'),
    MOSAMA_CATEGORY_2L3MAL_SAGEEN:_('CATEGORY_2L3MAL_SAGEEN'),
}


class LoggingModel(models.Model):
    """
    An abstract base class model that provides self-
    updating ``created_at`` and ``updated_at`` fields for responsable user.
    """
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))
    
    class Meta:
        abstract = True

class Settings(LoggingModel):
    MOAHIL_PREFIX = 'moahil_'
    MOSAMA_PREFIX = 'mosama_'

    SETTINGS_ZAKA_KAFAF = 'zaka_kafaf'
    SETTINGS_ZAKA_NISAB = 'zaka_nisab'
    SETTINGS_GASIMA = 'gasima'
    SETTINGS_ATFAL = 'atfal'
    SETTINGS_DAMGA = 'damga'
    SETTINGS_SANDOG = 'sandog'
    SETTINGS_AADOA = 'aadoa'
    SETTINGS_ENABLE_SANDOG_KAHRABA = 'enable_kahraba' #enable_sandog_kahraba
    SETTINGS_ENABLE_YOUM_ALGOAT_ALMOSALAHA = 'enable_algoat' #enable_youm_algoat_almosalaha

    SETTINGS_CHOICES = {
        SETTINGS_ZAKA_KAFAF: _('SETTINGS_ZAKAT_KAFAF'),
        SETTINGS_ZAKA_NISAB: _('SETTINGS_ZAKAT_NISAB'),
        SETTINGS_GASIMA: _('SETTINGS_GASIMA'),
        SETTINGS_ATFAL: _('SETTINGS_ATFAL'),
        SETTINGS_DAMGA: _('SETTINGS_DAMGA'),
        SETTINGS_SANDOG: _('SETTINGS_SANDOG'),
        SETTINGS_AADOA: _('SETTINGS_AADOA'),
        SETTINGS_ENABLE_SANDOG_KAHRABA: _('SETTINGS_ENABLE_SANDOG_KAHRABA'),
        SETTINGS_ENABLE_YOUM_ALGOAT_ALMOSALAHA: _('SETTINGS_ENABLE_YOUM_ALGOAT_ALMOSALAHA'),
    }

    for moahil in MOAHIL_CHOICES:
        key = MOAHIL_PREFIX + moahil
        SETTINGS_CHOICES[key] = _('moahil')+' '+MOAHIL_CHOICES[moahil]

    for mosama in MOSAMA_CATEGORY_CHOICES:
        key = MOSAMA_PREFIX + mosama
        SETTINGS_CHOICES[key] = _('2sti7gag 2lmobashara')+' '+MOSAMA_CATEGORY_CHOICES[mosama]

    code = models.CharField(_("code"), choices=SETTINGS_CHOICES,max_length=30)
    value = models.CharField(_("value"),max_length=255)

    def __str__(self) -> str:
        return f'{self.code}: {self.value}'
    
    def clean(self) -> None:
        if self.code in [self.SETTINGS_ENABLE_SANDOG_KAHRABA,self.SETTINGS_ENABLE_YOUM_ALGOAT_ALMOSALAHA]:
            if not self.value.isdigit() or not int(self.value) in [0,1]:
                raise ValidationError(
                    {"value":_("value should be 0 or 1")}
                )
        else:
            if not self.value.isdigit() or float(self.value) < 0:
                raise ValidationError(
                    {"value":_("value should be positive number")}
                )
        return super().clean()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['code'],name="unique_setting_code")
        ]
        indexes = [
            models.Index(fields=["code"]),
        ]
        verbose_name = _("HR Setting")
        verbose_name_plural = _("HR Settings")

class Drajat3lawat(LoggingModel):
    DRAJAT_TALTA_KHASA = -3
    DRAJAT_TANIA_KHASA = -2
    DRAJAT_AWLA_KHASA = -1
    DRAJAT_AWLA = 1
    DRAJAT_TANIA = 2
    DRAJAT_TALTA = 3
    DRAJAT_RAB3A = 4
    DRAJAT_KHAMSA = 5
    DRAJAT_SAB3A = 7
    DRAJAT_TAMNA = 8
    DRAJAT_TAS3A = 9
    DRAJAT_3ASHRA = 10
    DRAJAT_ATNASHAR = 12
    DRAJAT_KHAMSTASHR = 15
    DRAJAT_TA3AKOD = 17

    DRAJAT_CHOICES = {
        DRAJAT_TALTA_KHASA: _('DRAJAT_TALTA_KHASA'),
        DRAJAT_TANIA_KHASA: _('DRAJAT_TANIA_KHASA'),
        DRAJAT_AWLA_KHASA: _('DRAJAT_AWLA_KHASA'),
        DRAJAT_AWLA: _('DRAJAT_AWLA'),
        DRAJAT_TANIA: _('DRAJAT_TANIA'),
        DRAJAT_TALTA: _('DRAJAT_TALTA'),
        DRAJAT_RAB3A: _('DRAJAT_RAB3A'),
        DRAJAT_KHAMSA: _('DRAJAT_KHAMSA'),
        DRAJAT_SAB3A: _('DRAJAT_SAB3A'),
        DRAJAT_TAMNA: _('DRAJAT_TAMNA'),
        DRAJAT_TAS3A: _('DRAJAT_TAS3A'),
        DRAJAT_3ASHRA: _('DRAJAT_3ASHRA'),
        DRAJAT_ATNASHAR: _('DRAJAT_ATNASHAR'),
        DRAJAT_KHAMSTASHR: _('DRAJAT_KHAMSTASHR'),
        DRAJAT_TA3AKOD: _('DRAJAT_TA3AKOD'),
    }

    ALAWAT_AWALA = 1
    ALAWAT_TANIA = 2
    ALAWAT_TALTA = 3
    ALAWAT_RAB3A = 4
    ALAWAT_KHAMSA = 5
    ALAWAT_TA3AKOD = 7
    
    ALAWAT_CHOICES = {
        ALAWAT_AWALA: _('ALAWAT_AWALA'),
        ALAWAT_TANIA: _('ALAWAT_TANIA'),
        ALAWAT_TALTA: _('ALAWAT_TALTA'),
        ALAWAT_RAB3A: _('ALAWAT_RAB3A'),
        ALAWAT_KHAMSA: _('ALAWAT_KHAMSA'),
        ALAWAT_TA3AKOD: _('ALAWAT_TA3AKOD'),
    }

    draja_wazifia = models.IntegerField(_("draja_wazifia"), choices=DRAJAT_CHOICES)
    alawa_sanawia = models.IntegerField(_("alawa_sanawia"), choices=ALAWAT_CHOICES)
    abtdai = models.FloatField(_("abtdai"),default=0)
    galaa_m3isha = models.FloatField(_("galaa_m3isha"),default=0)
    shakhsia = models.FloatField(_("shakhsia"),default=0)
    ma3adin = models.FloatField(_("ma3adin"),default=0)
    # aadoa = models.FloatField(_("aadoa"),default=0)

    def __str__(self) -> str:
        return self.DRAJAT_CHOICES[self.draja_wazifia]+'/'+self.ALAWAT_CHOICES[self.alawa_sanawia]

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['draja_wazifia','alawa_sanawia'],name="unique_draja_3lawa")
        ]

        indexes = [
            models.Index(fields=["draja_wazifia", "alawa_sanawia"]),
        ]
        ordering = ["draja_wazifia","-alawa_sanawia"]
        verbose_name = _("Drajat & 3lawat")
        verbose_name_plural = _("Drajat & 3lawat")

class MosamaWazifi(models.Model):
    name = models.CharField(_("mosama_wazifi"),max_length=100)
    category = models.CharField(_("mosama_category"),choices=MOSAMA_CATEGORY_CHOICES,max_length=20)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'],name="unique_mosama_wazifi")
        ]
        indexes = [
            models.Index(fields=["category"]),
        ]
        ordering = ["name"]
        verbose_name = _("Mosama Wazifi")
        verbose_name_plural = _("Mosama Wazifi")

class Edara3ama(models.Model):
    name = models.CharField(_("edara_3ama"),max_length=150)

    def __str__(self) -> str:
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'],name="unique_edara_3ama")
        ]
        indexes = [
            models.Index(fields=["name"]),
        ]
        ordering = ["name"]
        verbose_name = _("Edara 3ama")
        verbose_name_plural = _("Edara 3ama")

class Edarafar3ia(models.Model):
    name = models.CharField(_("edara_far3ia"),max_length=150)
    edara_3ama = models.ForeignKey(Edara3ama, on_delete=models.PROTECT,verbose_name=_("edara_3ama"))

    def __str__(self) -> str:
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name','edara_3ama'],name="unique_edara_far3ia")
        ]
        ordering = ["name"]
        verbose_name = _("Edara far3ia")
        verbose_name_plural = _("Edara far3ia")

class EmployeeBasic(LoggingModel):
    SEX_MALE = 'male'
    SEX_FEMALE = 'female'

    SEX_CHOICES = {
        SEX_MALE: _('SEX_MALE'),
        SEX_FEMALE: _('SEX_FEMALE'),
    }

    NO3_2LERTIBAT_TA3EEN = 'ta3een'
    NO3_2LERTIBAT_NAGL = 'nagl'
    NO3_2LERTIBAT_2L7ag = '2l7ag'
    NO3_2LERTIBAT_2NTEDAB = '2ntedab'
    NO3_2LERTIBAT_TAKLEEF = 'takleef'
    NO3_2LERTIBAT_TA3AGOD = 'ta3agod'
    NO3_2LERTIBAT_MASHRO3 = 'mashro3'

    NO3_2LERTIBAT_CHOICES = {
        NO3_2LERTIBAT_TA3EEN: _("NO3_2LERTIBAT_TA3EEN"),
        NO3_2LERTIBAT_NAGL: _("NO3_2LERTIBAT_NAGL"),
        NO3_2LERTIBAT_2L7ag: _("NO3_2LERTIBAT_2L7ag"),
        NO3_2LERTIBAT_2NTEDAB: _("NO3_2LERTIBAT_2NTEDAB"),
        NO3_2LERTIBAT_TAKLEEF: _("NO3_2LERTIBAT_TAKLEEF"),
        NO3_2LERTIBAT_TA3AGOD: _("NO3_2LERTIBAT_TA3AGOD"),
        NO3_2LERTIBAT_MASHRO3: _("NO3_2LERTIBAT_MASHRO3"),
    }

    code = models.IntegerField(_("employee_code"))
    name = models.CharField(_("employee_name"),max_length=150,validators=[MinLengthValidator(12,_("2dkhil al2sm roba3i"))])
    mosama_wazifi = models.ForeignKey(MosamaWazifi, on_delete=models.PROTECT,verbose_name=_("mosama_wazifi"))
    edara_3ama = models.ForeignKey(Edara3ama, on_delete=models.PROTECT,verbose_name=_("edara_3ama"))
    edara_far3ia = models.ForeignKey(Edarafar3ia, on_delete=models.PROTECT,verbose_name=_("edara_far3ia"))
    draja_wazifia = models.IntegerField(_("draja_wazifia"), choices=Drajat3lawat.DRAJAT_CHOICES)
    alawa_sanawia = models.IntegerField(_("alawa_sanawia"), choices=Drajat3lawat.ALAWAT_CHOICES)
    tarikh_milad = models.DateField(_("tarikh_milad"))
    tarikh_ta3in = models.DateField(_("tarikh_ta3in"))
    sex = models.CharField(_("sex"),max_length=7, choices=SEX_CHOICES)
    phone = models.CharField(_("phone"),max_length=30)
    no3_2lertibat = models.CharField(_("no3_2lertibat"),max_length=10, choices=NO3_2LERTIBAT_CHOICES)
    sanoat_2lkhibra = models.FloatField(_("sanoat_2lkhibra"),default=0)
    gasima = models.BooleanField(_("gasima"),default=False)
    atfal = models.IntegerField(_("3dad_atfal"),default=0)
    moahil = models.CharField(_("moahil"),max_length=30, choices=MOAHIL_CHOICES,default=MOAHIL_BAKLARIOS)
    m3ash = models.FloatField(_("m3ash"),default=0)
    aadoa = models.BooleanField(_("aadoa"),default=False)

    def __str__(self) -> str:
        return f'{self.name}'# / {self.edara_3ama.name}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name','tarikh_ta3in'],name="unique_employee")
        ]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["edara_3ama"]),
            models.Index(fields=["draja_wazifia"]),
            models.Index(fields=["alawa_sanawia"]),
            models.Index(fields=["tarikh_milad"]),
            models.Index(fields=["tarikh_ta3in"]),
            models.Index(fields=["sex"]),
            models.Index(fields=["no3_2lertibat"]),
            models.Index(fields=["moahil"]),
            models.Index(fields=["aadoa"]),
        ]

        ordering = ["code"]
        verbose_name = _("Employee data")
        verbose_name_plural = _("Employee data")

    def clean(self):
        if hasattr(self.edara_far3ia,'edara_3ama'):
            if self.edara_far3ia.edara_3ama != self.edara_3ama:
                raise ValidationError(
                    {"edara_far3ia":_("al2dara alfr3ia la tatba3 lil al2dara al3ama")}
                )
            
        if self.draja_wazifia == Drajat3lawat.DRAJAT_TA3AKOD:
            if self.alawa_sanawia != Drajat3lawat.ALAWAT_TA3AKOD:
                raise ValidationError(
                    {"alawa_sanawia":_("akhtar 3lawat t3akod")}
                )
        else:
            if self.alawa_sanawia == Drajat3lawat.ALAWAT_TA3AKOD:
                raise ValidationError(
                    {"alawa_sanawia":_("akhtar 3lawat gair t3akod")}
                )

class EmployeeBankAccount(LoggingModel):
    BANK_KHARTOUM = 'bok'
    BANK_OMDURMAN = 'onb'

    BANK_CHOICES = {
        BANK_KHARTOUM: _('BANK_KHARTOUM'),
        BANK_OMDURMAN: _('BANK_OMDURMAN'),
    }

    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    bank = models.CharField(_("bank"), choices=BANK_CHOICES,max_length=10)
    account_no = models.CharField(_("account_no"),max_length=20)
    active = models.BooleanField(_("active"),default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['bank','account_no'],name="unique_bank_account")
        ]
        indexes = [
            models.Index(fields=["bank"]),
            models.Index(fields=["account_no"]),
        ]
        verbose_name = _("Bank Account")
        verbose_name_plural = _("Bank Accounts")

    def __str__(self) -> str:
        return f'{self.employee.name} ({self.BANK_CHOICES[self.bank]})'# / {self.edara_3ama.name}'

    def deactivate_other_accounts(self):
        if self.active:
            self.employee.employeebankaccount_set.exclude(id=self.id).update(active=False)

class EmployeeFamily(LoggingModel):
    FAMILY_RELATION_PARENT = 'parent'
    FAMILY_RELATION_CHILD = 'child'
    FAMILY_RELATION_CONSORT = 'consort'

    FAMILY_RELATION_CHOICES = {
        FAMILY_RELATION_PARENT: _('FAMILY_RELATION_PARENT'),
        FAMILY_RELATION_CHILD: _('FAMILY_RELATION_CHILD'),
        FAMILY_RELATION_CONSORT: _('FAMILY_RELATION_CONSORT'),
    }

    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    relation = models.CharField(_("relation"), choices=FAMILY_RELATION_CHOICES,max_length=10)
    name = models.CharField(_("name"),max_length=100,validators=[MinLengthValidator(12,_("2dkhil al2sm roba3i"))])

    class Meta:
        verbose_name = _("Employee Family")
        verbose_name_plural = _("Employee Family")

    def __str__(self) -> str:
        return f'{self.employee.name} ({self.get_relation_display()})'

    def update_number_of_children(self):
        count = self.employee.employeefamily_set.filter(relation=self.FAMILY_RELATION_CHILD).count()
        if count > self.employee.atfal:
            self.employee.atfal = count
            self.employee.save()

    def update_gasima_status(self):
        count = self.employee.employeefamily_set.filter(relation=self.FAMILY_RELATION_CONSORT).count()
        if count > 0:
            self.employee.gasima = True
            self.employee.save()

class EmployeeMoahil(LoggingModel):
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    moahil = models.CharField(_("moahil"), choices=MOAHIL_CHOICES,max_length=20)
    university = models.CharField(_("university"),max_length=150)
    takhasos = models.CharField(_("takhasos"),max_length=100)
    graduate_dt = models.DateField(_("graduate_dt"))

    class Meta:
        verbose_name = _("Employee Moahil")
        verbose_name_plural = _("Employee Moahil")

    def __str__(self) -> str:
        return f'{self.employee.name} ({self.get_moahil_display()})'

    def update_moahil(self):
        qs = EmployeeMoahil.objects.filter(employee=self.employee)

        tmp_moahil = MOAHIL_THANOI
        for emp in qs:
            if MOAHIL_WEIGHT[emp.moahil] > MOAHIL_WEIGHT[tmp_moahil]:
                tmp_moahil = emp.moahil

        if MOAHIL_WEIGHT[tmp_moahil] > MOAHIL_WEIGHT[self.employee.moahil]:
            self.employee.moahil = tmp_moahil
            self.employee.save()

class Salafiat(LoggingModel):
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    year = models.IntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    month = models.IntegerField(_("month"), choices=MONTH_CHOICES)
    note = models.CharField(_("note"),max_length=150)
    amount = models.FloatField(_("amount"))
    deducted = models.BooleanField(_("deducted"),default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee','year','month'],name="unique_salafiat_employee_year_month")
        ]
        indexes = [
            models.Index(fields=["employee", "year","month"]),
        ]
        ordering = ["-id"]
        verbose_name = _("Salafiat")
        verbose_name_plural = _("Salafiat")

class Jazaat(LoggingModel):
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    year = models.IntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    month = models.IntegerField(_("month"), choices=MONTH_CHOICES)
    note = models.CharField(_("note"),max_length=150)
    amount = models.FloatField(_("amount"))
    deducted = models.BooleanField(_("deducted"),default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee','year','month'],name="unique_jazaat_employee_year_month")
        ]
        indexes = [
            models.Index(fields=["employee", "year","month"]),
        ]
        ordering = ["-id"]
        verbose_name = _("Jazaat")
        verbose_name_plural = _("Jazaat")

class EmployeeMobashra(LoggingModel):
    STATE_ACTIVE = 'active'
    STATE_VACATION = 'vaction'
    STATE_INACTIVE = 'in_active'

    STATE_CHOICES = {
        STATE_ACTIVE: _('STATE_ACTIVE'),
        STATE_VACATION: _('STATE_VACATION'),
        STATE_INACTIVE: _('STATE_INACTIVE'),
    }

    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    start_dt = models.DateField(_('start_dt'))
    end_dt = models.DateField(_('end_dt'),blank=True)
    state = models.CharField(_("state"), choices=STATE_CHOICES,max_length=10)

    class Meta:
        indexes = [
            models.Index(fields=["employee","state"]),
            models.Index(fields=["state"]),
        ]
        ordering = ["-id"]
        verbose_name = _("Mobashra")
        verbose_name_plural = _("Mobashra")

class EmployeeMobashraMonthly(LoggingModel):
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    year = models.IntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    month = models.IntegerField(_("month"), choices=MONTH_CHOICES)
    no_days = models.IntegerField(_("no_days"))
    note = models.CharField(_("note"),max_length=150,blank=True)
    confirmed = models.BooleanField(_("confirmed"),default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee','year','month'],name="unique_mobashraemployee_year_month")
        ]

class PayrollMaster(LoggingModel):
    year = models.IntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    month = models.IntegerField(_("month"), choices=MONTH_CHOICES)
    zaka_kafaf = models.FloatField(_("zaka_kafaf"),default=0)
    zaka_nisab = models.FloatField(_("zaka_nisab"),default=0)
    enable_sandog_kahraba = models.BooleanField(_("enable_sandog_kahraba"),default=False)
    enable_youm_algoat_almosalaha = models.BooleanField(_("enable_youm_algoat_almosalaha"),default=False)
    confirmed = models.BooleanField(_("confirmed"),default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['year','month'],name="unique_payroll_year_month")
        ]
        verbose_name = _("Payroll")
        verbose_name_plural = _("Payroll")

    def __str__(self) -> str:
        return f'{_("Payroll")} {self.get_month_display()} {self.year}'

class PayrollDetail(models.Model):
    payroll_master = models.ForeignKey(PayrollMaster, on_delete=models.CASCADE)
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    abtdai = models.FloatField(_("abtdai"),default=0)
    galaa_m3isha = models.FloatField(_("galaa_m3isha"),default=0)
    shakhsia = models.FloatField(_("shakhsia"),default=0)
    aadoa = models.FloatField(_("aadoa"),default=0)
    gasima = models.FloatField(_("gasima"),default=0)
    atfal = models.FloatField(_("atfal"),default=0)
    moahil = models.FloatField(_("moahil"),default=0)
    ma3adin = models.FloatField(_("ma3adin"),default=0)
    m3ash = models.FloatField(_("m3ash"),default=0)
    salafiat = models.FloatField(_("salafiat"),default=0)
    jazaat = models.FloatField(_("jazaat"),default=0)
    damga = models.FloatField(_("damga"),default=0)
    sandog = models.FloatField(_("sandog"),default=0)
    sandog_kahraba = models.FloatField(_("sandog_kahraba"),default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['payroll_master','employee'],name="unique_employee_payroll")
        ]
        ordering = ["employee__code"]

    def __str__(self) -> str:
        return f'{self.employee.name} ({self.employee.edara_3ama.name})'
