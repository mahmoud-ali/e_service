from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.forms import ValidationError

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
MOAHIL_BAKLARIOS = 'baklarios'
MOAHIL_MAJSTEAR = 'majstear'
MOAHIL_DECTORA = 'dectora'

MOAHIL_CHOICES = {
    MOAHIL_THANOI: _('MOAHIL_THANOI'),
    MOAHIL_BAKLARIOS: _('MOAHIL_BAKLARIOS'),
    MOAHIL_MAJSTEAR: _('MOAHIL_MAJSTEAR'),
    MOAHIL_DECTORA: _('MOAHIL_DECTORA'),
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

    SETTINGS_ZAKA_KAFAF = 'zaka_kafaf'
    SETTINGS_ZAKA_NISAB = 'zaka_nisab'
    SETTINGS_GASIMA = 'gasima'
    SETTINGS_ATFAL = 'atfal'
    SETTINGS_DAMGA = 'damga'
    SETTINGS_SANDOG = 'sandog'

    SETTINGS_CHOICES = {
        SETTINGS_ZAKA_KAFAF: _('SETTINGS_ZAKAT_KAFAF'),
        SETTINGS_ZAKA_NISAB: _('SETTINGS_ZAKAT_NISAB'),
        SETTINGS_GASIMA: _('SETTINGS_GASIMA'),
        SETTINGS_ATFAL: _('SETTINGS_ATFAL'),
        SETTINGS_DAMGA: _('SETTINGS_DAMGA'),
        SETTINGS_SANDOG: _('SETTINGS_SANDOG'),
    }

    for moahil in MOAHIL_CHOICES:
        key = MOAHIL_PREFIX + moahil
        SETTINGS_CHOICES[key] = MOAHIL_CHOICES[moahil]

    code = models.CharField(_("code"), choices=SETTINGS_CHOICES,max_length=20)
    value = models.FloatField(_("value"))

    def __str__(self) -> str:
        return f'{self.code}: {self.value}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['code'],name="unique_setting_code")
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
    aadoa = models.FloatField(_("aadoa"),default=0)

    def __str__(self) -> str:
        return self.DRAJAT_CHOICES[self.draja_wazifia]+'/'+self.ALAWAT_CHOICES[self.alawa_sanawia]

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['draja_wazifia','alawa_sanawia'],name="unique_draja_3lawa")
        ]

        indexes = [
            models.Index(fields=["draja_wazifia", "alawa_sanawia"]),
        ]
        verbose_name = _("Drajat & 3lawat")
        verbose_name_plural = _("Drajat & 3lawat")

class MosamaWazifi(models.Model):
    name = models.CharField(_("mosama_wazifi"),max_length=100)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name'],name="unique_mosama_wazifi")
        ]
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
        verbose_name = _("Edara 3ama")
        verbose_name_plural = _("Edara 3ama")

class Edarafar3ia(models.Model):
    name = models.CharField(_("edara_far3ia"),max_length=150)
    edara_3ama = models.ForeignKey(Edara3ama, on_delete=models.PROTECT,verbose_name=_("edara_3ama"))

    def __str__(self) -> str:
        return self.edara_3ama.name+'/'+self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name','edara_3ama'],name="unique_edara_far3ia")
        ]
        verbose_name = _("Edara far3ia")
        verbose_name_plural = _("Edara far3ia")

class EmployeeBasic(LoggingModel):
    name = models.CharField(_("employee_name"),max_length=150)
    mosama_wazifi = models.ForeignKey(MosamaWazifi, on_delete=models.PROTECT,verbose_name=_("mosama_wazifi"))
    edara_3ama = models.ForeignKey(Edara3ama, on_delete=models.PROTECT,verbose_name=_("edara_3ama"))
    edara_far3ia = models.ForeignKey(Edarafar3ia, on_delete=models.PROTECT,verbose_name=_("edara_far3ia"))
    draja_wazifia = models.IntegerField(_("draja_wazifia"), choices=Drajat3lawat.DRAJAT_CHOICES)
    alawa_sanawia = models.IntegerField(_("alawa_sanawia"), choices=Drajat3lawat.ALAWAT_CHOICES)
    tarikh_ta3in = models.DateField(_("tarikh_ta3in"))
    gasima = models.BooleanField(_("gasima"),default=False)
    atfal = models.IntegerField(_("3dad_atfal"),default=0)
    moahil = models.CharField(_("moahil"),max_length=20, choices=MOAHIL_CHOICES,default=MOAHIL_BAKLARIOS)
    m3ash = models.FloatField(_("m3ash"),default=0)

    def __str__(self) -> str:
        return f'{self.name} / {self.edara_3ama.name}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name','tarikh_ta3in'],name="unique_employee")
        ]
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

class Salafiat(LoggingModel):
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    year = models.IntegerField(_("year"))
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
        verbose_name = _("Salafiat")
        verbose_name_plural = _("Salafiat")

class Jazaat(LoggingModel):
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    year = models.IntegerField(_("year"))
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
        verbose_name = _("Jazaat")
        verbose_name_plural = _("Jazaat")

class PayrollMaster(LoggingModel):
    year = models.IntegerField(_("year"))
    month = models.IntegerField(_("month"), choices=MONTH_CHOICES)
    zaka_kafaf = models.FloatField(_("zaka_kafaf"),default=0)
    zaka_nisab = models.FloatField(_("zaka_nisab"),default=0)
    confirmed = models.BooleanField(_("confirmed"),default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['year','month'],name="unique_payroll_year_month")
        ]
        verbose_name = _("Payroll")
        verbose_name_plural = _("Payroll")

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
