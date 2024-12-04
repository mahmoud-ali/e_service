from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.contrib import admin
from mptt.models import MPTTModel, TreeForeignKey

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

def attachement_path(instance, filename):
    return "employee_{0}/{1}".format(instance.employee.code, filename)    

class LoggingModel(models.Model):
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))
    
    class Meta:
        abstract = True

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

class HikalWazifi(MPTTModel):
    ELMOSTOA_ELTANZIMI_MODIR_3AM = 1
    ELMOSTOA_ELTANZIMI_MOSA3ID_MODIR_3AM = 2
    ELMOSTOA_ELTANZIMI_2DARA_3AMA = 3
    ELMOSTOA_ELTANZIMI_2DARA_FAR3IA = 4
    ELMOSTOA_ELTANZIMI_GISIM = 5
    ELMOSTOA_ELTANZIMI_WI7DA = 6
    
    ELMOSTOA_ELTANZIMI_CHOICES = {
        ELMOSTOA_ELTANZIMI_MODIR_3AM: _('ELMOSTOA_ELTANZIMI_MODIR_3AM'),
        ELMOSTOA_ELTANZIMI_MOSA3ID_MODIR_3AM: _('ELMOSTOA_ELTANZIMI_MOSA3ID_MODIR_3AM'),
        ELMOSTOA_ELTANZIMI_2DARA_3AMA: _('ELMOSTOA_ELTANZIMI_2DARA_3AMA'),
        ELMOSTOA_ELTANZIMI_2DARA_FAR3IA: _('ELMOSTOA_ELTANZIMI_2DARA_FAR3IA'),
        ELMOSTOA_ELTANZIMI_GISIM: _('ELMOSTOA_ELTANZIMI_GISIM'),
        ELMOSTOA_ELTANZIMI_WI7DA: _('ELMOSTOA_ELTANZIMI_WI7DA'),
    }

    name = models.CharField(max_length=150, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    elmostoa_eltanzimi = models.IntegerField(_("elmostoa_eltanzimi"), choices=ELMOSTOA_ELTANZIMI_CHOICES,default=ELMOSTOA_ELTANZIMI_WI7DA)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _("HikalWazifi")
        verbose_name_plural = _("HikalWazifi")

    def __str__(self) -> str:
        return self.name

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
    NO3_2LERTIBAT_TA3AGOD = 'ta3agod_mosimi'
    NO3_2LERTIBAT_TA3AGOD_MOSIMI = 'ta3agod'
    NO3_2LERTIBAT_MASHRO3 = 'mashro3'
    NO3_2LERTIBAT_MAJLIS_EL2DARA = 'majlis_el2dara'

    NO3_2LERTIBAT_CHOICES = {
        NO3_2LERTIBAT_TA3EEN: _("NO3_2LERTIBAT_TA3EEN"),
        NO3_2LERTIBAT_NAGL: _("NO3_2LERTIBAT_NAGL"),
        NO3_2LERTIBAT_2NTEDAB: _("NO3_2LERTIBAT_2NTEDAB"),
        NO3_2LERTIBAT_TAKLEEF: _("NO3_2LERTIBAT_TAKLEEF"),
        NO3_2LERTIBAT_2L7ag: _("NO3_2LERTIBAT_2L7ag"), #wi7dat mosa3da
        NO3_2LERTIBAT_TA3AGOD: _("NO3_2LERTIBAT_TA3AGOD"),
        NO3_2LERTIBAT_TA3AGOD_MOSIMI: _("NO3_2LERTIBAT_TA3AGOD_MOSIMI"),
        NO3_2LERTIBAT_MASHRO3: _("NO3_2LERTIBAT_MASHRO3"),
        NO3_2LERTIBAT_MAJLIS_EL2DARA: _("NO3_2LERTIBAT_MAJLIS_EL2DARA"),
    }

    STATUS_ACTIVE = 1
    STATUS_MA3ASH = 2
    STATUS_TAGA3D_EKHTIARI = 3
    STATUS_ESTIKALA = 4
    STATUS_3DAM_ELIAGA_ELTIBIA = 5
    STATUS_ELFASL = 6
    STATUS_ENTIHA2_2L3AGD = 7
    STATUS_SHAGL_MANSAB_DASTORY = 8
    STATUS_ELWAFAH = 9
    STATUS_FOGDAN_ELJENSIA_ELSODANIA = 10
    STATUS_ENHA2_ENTIDAB = 11
    STATUS_NAGL = 12
    STATUS_2L7AG = 13
    STATUS_EJAZA_MIN_GAIR_MORATAB = 14

    STATUS_CHOICES = {
        STATUS_ACTIVE: _("STATUS_ACTIVE"),
        STATUS_MA3ASH: _("STATUS_MA3ASH"),
        STATUS_TAGA3D_EKHTIARI: _("STATUS_TAGA3D_EKHTIARI"),
        STATUS_ESTIKALA: _("STATUS_ESTIKALA"),
        STATUS_3DAM_ELIAGA_ELTIBIA: _("STATUS_3DAM_ELIAGA_ELTIBIA"),
        STATUS_ELFASL: _("STATUS_ELFASL"),
        STATUS_ENTIHA2_2L3AGD: _("STATUS_ENTIHA2_2L3AGD"),
        STATUS_SHAGL_MANSAB_DASTORY: _("STATUS_SHAGL_MANSAB_DASTORY"),
        STATUS_ELWAFAH: _("STATUS_ELWAFAH"),
        STATUS_FOGDAN_ELJENSIA_ELSODANIA: _("STATUS_FOGDAN_ELJENSIA_ELSODANIA"),
        STATUS_ENHA2_ENTIDAB: _("STATUS_ENHA2_ENTIDAB"),
        STATUS_NAGL: _("STATUS_NAGL"),
        STATUS_2L7AG: _("STATUS_2L7AG"),
        STATUS_EJAZA_MIN_GAIR_MORATAB: _("STATUS_EJAZA_MIN_GAIR_MORATAB"),
    }

    code = models.IntegerField(_("employee_code"))
    name = models.CharField(_("employee_name"),max_length=150,validators=[MinLengthValidator(12,_("2dkhil al2sm roba3i"))])
    mosama_wazifi = models.ForeignKey(MosamaWazifi, on_delete=models.PROTECT,verbose_name=_("mosama_wazifi"))
    draja_wazifia = models.IntegerField(_("draja_wazifia"), choices=Drajat3lawat.DRAJAT_CHOICES)
    alawa_sanawia = models.IntegerField(_("alawa_sanawia"), choices=Drajat3lawat.ALAWAT_CHOICES)
    tarikh_milad = models.DateField(_("tarikh_milad"))
    tarikh_ta3in = models.DateField(_("tarikh_ta3in"))
    tarikh_akhir_targia = models.DateField(_("tarikh_akhir_targia"),blank=True,null=True)
    sex = models.CharField(_("sex"),max_length=7, choices=SEX_CHOICES)
    phone = models.CharField(_("phone"),max_length=30,blank=True,null=True)
    no3_2lertibat = models.CharField(_("no3_2lertibat"),max_length=15, choices=NO3_2LERTIBAT_CHOICES)
    sanoat_2lkhibra = models.FloatField(_("sanoat_2lkhibra"),default=0)
    m3ash = models.FloatField(_("m3ash"),default=0)
    aadoa = models.BooleanField(_("aadoa"),default=False)
    status = models.IntegerField(_("status"), choices=STATUS_CHOICES,default=STATUS_ACTIVE)
    hikal_wazifi = TreeForeignKey(HikalWazifi, on_delete=models.PROTECT,verbose_name=_("hikal_wazifi"),blank=True,null=True)

    def __str__(self) -> str:
        return f'{self.name}'# / {self.edara_3ama.name}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name','tarikh_ta3in'],name="unique_employee")
        ]
        indexes = [
            models.Index(fields=["code"]),
            # models.Index(fields=["edara_3ama"]),
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

    def traverse_hikal_wazifi(self,level):
        job = None
        try:
            job = self.hikal_wazifi.get_ancestors(include_self=True).get(elmostoa_eltanzimi=level)
        except:
            pass
        return job
    
    @property
    @admin.display(description=_("edara_3ama"))
    def edara_3ama(self):
        job = self.traverse_hikal_wazifi(HikalWazifi.ELMOSTOA_ELTANZIMI_2DARA_3AMA)
        if self.hikal_wazifi and not job:
            job = self.traverse_hikal_wazifi(HikalWazifi.ELMOSTOA_ELTANZIMI_MOSA3ID_MODIR_3AM)
            if not job:
                job = self.hikal_wazifi.get_root()

        return job

    @property
    @admin.display(description=_("edara_far3ia"))
    def edara_far3ia(self):
        return self.traverse_hikal_wazifi(HikalWazifi.ELMOSTOA_ELTANZIMI_2DARA_FAR3IA)

    @property
    @admin.display(description=_("gisim"))
    def gisim(self):
        return self.traverse_hikal_wazifi(HikalWazifi.ELMOSTOA_ELTANZIMI_GISIM)

    @property
    @admin.display(description=_("wi7da"))
    def wi7da(self):
        return self.traverse_hikal_wazifi(HikalWazifi.ELMOSTOA_ELTANZIMI_WI7DA)


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
    name = models.CharField(_("name"),max_length=100,validators=[MinLengthValidator(4,_("2dkhil al2sm roba3i"))])
    tarikh_el2dafa = models.DateField(_("tarikh_el2dafa"),blank=True,null=True)
    attachement_file = models.FileField(_("attachement"),upload_to=attachement_path,blank=True,null=True)

    class Meta:
        verbose_name = _("Employee Family")
        verbose_name_plural = _("Employee Family")

    def __str__(self) -> str:
        return f'{self.employee.name} ({self.get_relation_display()})'

class EmployeeMoahil(LoggingModel):
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    moahil = models.CharField(_("moahil"), choices=MOAHIL_CHOICES,max_length=20)
    university = models.CharField(_("university"),max_length=150)
    takhasos = models.CharField(_("takhasos"),max_length=100)
    graduate_dt = models.DateField(_("graduate_dt"))
    tarikh_el2dafa = models.DateField(_("tarikh_el2dafa"),blank=True,null=True)
    attachement_file = models.FileField(_("attachement"),upload_to=attachement_path,blank=True,null=True)

    class Meta:
        verbose_name = _("Employee Moahil")
        verbose_name_plural = _("Employee Moahil")

    def __str__(self) -> str:
        return f'{self.employee.name} ({self.get_moahil_display()})'
