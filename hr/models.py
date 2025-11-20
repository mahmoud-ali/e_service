from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.forms import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator,MinLengthValidator
from django.contrib import admin
from mptt.models import MPTTModel, TreeForeignKey
from django.db.models import Sum
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

def is_float(element: any) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False

def attachement_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/company_<id>/contract_<id>/<filename>
    return "employee_{0}/{1}".format(instance.employee.code, filename)    

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
    SETTINGS_DARIBAT_2LMOKAFA = 'daribat_2lmokafa'
    SETTINGS_ENABLE_SANDOG_KAHRABA = 'enable_kahraba' #enable_sandog_kahraba
    SETTINGS_ENABLE_YOUM_ALGOAT_ALMOSALAHA = 'enable_algoat' #enable_youm_algoat_almosalaha

    SETTINGS_M2MORIA_RATE = 'm2moria_rate'
    SETTINGS_E3ASHA_RATE = 'e3asha_rate'

    SETTINGS_KHARJ_ELSHARIKA = 'kharj_elsharika'

    SETTINGS_OMER_2LMA3ASH = 'omer_2lma3ash'

    SETTINGS_KHASM_ELSANDOG_MIN_ELOMORATAB = 'khasm_elsandog_min_elomoratab'

    SETTINGS_TA3AGODMOSIMI_MOZAF = 'ta3agod_mosimi_mozaf'
    SETTINGS_TA3AGODMOSIMI_3AMIL = 'ta3agod_mosimi_3amil'
    SETTINGS_TA3AGODMOSIMI_MOKAF2 = 'ta3agod_mosimi_mokaf2'

    SETTINGS_MAJLIS_EL2DARA_R2IS_2LMAJLIS = 'majlis_el2dara_r2is'
    SETTINGS_MAJLIS_EL2DARA_3ODO = 'majlis_el2dara_3odo'

    SETTINGS_MODIR_3AM_ASAI = 'modir_3am_asai'

    SETTINGS_MOKAF2T_ADA2 = 'mokaf2t_ada2'

    SETTINGS_MOKAF2T_ADA2_FI_MOKAF2 = 'mokaf2t_ada2_fi_mokaf2'

    SETTINGS_CHOICES = {
        SETTINGS_ZAKA_KAFAF: _('SETTINGS_ZAKAT_KAFAF'),
        SETTINGS_ZAKA_NISAB: _('SETTINGS_ZAKAT_NISAB'),
        SETTINGS_GASIMA: _('SETTINGS_GASIMA'),
        SETTINGS_ATFAL: _('SETTINGS_ATFAL'),
        SETTINGS_DAMGA: _('SETTINGS_DAMGA'),
        SETTINGS_SANDOG: _('SETTINGS_SANDOG'),
        # SETTINGS_AADOA: _('SETTINGS_AADOA'),
        SETTINGS_DARIBAT_2LMOKAFA: _('SETTINGS_DARIBAT_2LMOKAFA'),
        SETTINGS_ENABLE_SANDOG_KAHRABA: _('SETTINGS_ENABLE_SANDOG_KAHRABA'),
        SETTINGS_ENABLE_YOUM_ALGOAT_ALMOSALAHA: _('SETTINGS_ENABLE_YOUM_ALGOAT_ALMOSALAHA'),
        SETTINGS_M2MORIA_RATE: _('SETTINGS_M2MORIA_RATE'),
        SETTINGS_E3ASHA_RATE: _('SETTINGS_E3ASHA_RATE'),
        SETTINGS_KHARJ_ELSHARIKA: _('SETTINGS_KHARJ_ELSHARIKA'),
        SETTINGS_OMER_2LMA3ASH: _('SETTINGS_OMER_2LMA3ASH'),
        SETTINGS_KHASM_ELSANDOG_MIN_ELOMORATAB: _('SETTINGS_KHASM_ELSANDOG_MIN_ELOMORATAB'),
        SETTINGS_TA3AGODMOSIMI_MOZAF: _('SETTINGS_TA3AGODMOSIMI_MOZAF'),
        SETTINGS_TA3AGODMOSIMI_3AMIL: _('SETTINGS_TA3AGODMOSIMI_3AMIL'),
        SETTINGS_TA3AGODMOSIMI_MOKAF2: _('SETTINGS_TA3AGODMOSIMI_MOKAF2'),

        SETTINGS_MAJLIS_EL2DARA_R2IS_2LMAJLIS: _('SETTINGS_MAJLIS_EL2DARA_R2IS_2LMAJLIS'),
        SETTINGS_MAJLIS_EL2DARA_3ODO: _('SETTINGS_MAJLIS_EL2DARA_3ODO'),

        SETTINGS_MODIR_3AM_ASAI: _('SETTINGS_MODIR_3AM_ASAI'),
        SETTINGS_MOKAF2T_ADA2_FI_MOKAF2: 'حساب مكافئة الاداء في المرتب',
    }

    for moahil in MOAHIL_CHOICES:
        key = MOAHIL_PREFIX + moahil
        SETTINGS_CHOICES[key] = _('moahil')+' '+MOAHIL_CHOICES[moahil]

    for mosama in MOSAMA_CATEGORY_CHOICES:
        key = MOSAMA_PREFIX + mosama
        SETTINGS_CHOICES[key] = _('2sti7gag 2lmobashara')+' '+MOSAMA_CATEGORY_CHOICES[mosama]

    for draja in Drajat3lawat.DRAJAT_CHOICES:
        key_aadoa = SETTINGS_AADOA+'_daraja_' + str(draja)
        key_mokaf2t_ada2 = SETTINGS_MOKAF2T_ADA2+'_daraja_' + str(draja)
        SETTINGS_CHOICES[key_aadoa] = _('SETTINGS_AADOA')+' '+Drajat3lawat.DRAJAT_CHOICES[draja]
        SETTINGS_CHOICES[key_mokaf2t_ada2] = _('SETTINGS_MOKAF2T_2DA2')+' '+Drajat3lawat.DRAJAT_CHOICES[draja]

    code = models.CharField(_("code"), choices=SETTINGS_CHOICES,max_length=30)
    value = models.CharField(_("value"),max_length=255)

    def __str__(self) -> str:
        return f'{self.get_code_display()}: {self.value}'
    
    def clean(self) -> None:
        if self.code in [self.SETTINGS_ENABLE_SANDOG_KAHRABA,self.SETTINGS_ENABLE_YOUM_ALGOAT_ALMOSALAHA,self.SETTINGS_MOKAF2T_ADA2_FI_MOKAF2]:
            if not self.value or not is_float(self.value) or not int(self.value) in [0,1]:
                raise ValidationError(
                    {"value":_("value should be 0 or 1")}
                )
        else:
            if not self.value or not is_float(self.value) or float(self.value) < 0:
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
    edara_3ama = TreeForeignKey("HikalWazifi", on_delete=models.PROTECT,verbose_name=_("edara_3ama"),related_name="+",blank=True,null=True,editable=False)
    edara_far3ia = TreeForeignKey("HikalWazifi", on_delete=models.PROTECT,verbose_name=_("edara_far3ia"),related_name="+",blank=True,null=True,editable=False)
    gisim = TreeForeignKey("HikalWazifi", on_delete=models.PROTECT,verbose_name=_("gasima"),related_name="+",blank=True,null=True,editable=False)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _("HikalWazifi")
        verbose_name_plural = _("HikalWazifi")

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.edara_3ama = self.edara_3ama_calc
        self.edara_far3ia = self.edara_far3ia_calc
        self.gisim = self.gisim_calc

        super().save(*args, **kwargs)

    def traverse_hikal_wazifi(self,level):
        job = None
        try:
            job = self.get_ancestors(include_self=True).get(elmostoa_eltanzimi=level)
        except:
            pass
        return job
    
    @property
    @admin.display(description=_("edara_3ama"))
    def edara_3ama_calc(self):
        job = self.traverse_hikal_wazifi(HikalWazifi.ELMOSTOA_ELTANZIMI_2DARA_3AMA)
        if not job:
            job = self.traverse_hikal_wazifi(HikalWazifi.ELMOSTOA_ELTANZIMI_MOSA3ID_MODIR_3AM)
            if not job:
                job = self.get_root()

        return job

    @property
    @admin.display(description=_("edara_far3ia"))
    def edara_far3ia_calc(self):
        return self.traverse_hikal_wazifi(HikalWazifi.ELMOSTOA_ELTANZIMI_2DARA_FAR3IA)

    @property
    @admin.display(description=_("gisim"))
    def gisim_calc(self):
        return self.traverse_hikal_wazifi(HikalWazifi.ELMOSTOA_ELTANZIMI_GISIM)
    
class Edara3ama(models.Model):
    TAB3IA_EDARIA_MODIR3AM = 1
    TAB3IA_EDARIA_FANI = 2
    TAB3IA_EDARIA_MALI = 3
    
    TAB3IA_EDARIA = {
        TAB3IA_EDARIA_MODIR3AM: _('TAB3IA_EDARIA_MODIR3AM'),
        TAB3IA_EDARIA_FANI: _('TAB3IA_EDARIA_FANI'),
        TAB3IA_EDARIA_MALI: _('TAB3IA_EDARIA_MALI'),
    }

    name = models.CharField(_("edara_3ama"),max_length=150)
    tab3ia_edaria = models.IntegerField(_("tab3ia_edaria"), choices=TAB3IA_EDARIA,default=TAB3IA_EDARIA_MODIR3AM)

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
    hikal_wazifi = TreeForeignKey(HikalWazifi, on_delete=models.PROTECT,verbose_name=_("hikal_wazifi"),blank=True,null=True)
    
    def __str__(self) -> str:
        return self.name

    def update_emp_hikal(self):
        EmployeeBasic.objects.filter(edara_far3ia_tmp__id=self.id).update(hikal_wazifi=self.hikal_wazifi)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name','edara_3ama'],name="unique_edara_far3ia")
        ]
        ordering = ["name"]
        verbose_name = _("Edara far3ia")
        verbose_name_plural = _("Edara far3ia")

class Gisim(models.Model):
    name = models.CharField(_("gisim"),max_length=150)
    edara_far3ia = models.ForeignKey(Edarafar3ia, on_delete=models.PROTECT,verbose_name=_("edara_far3ia"))

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = _("Gisim")
        verbose_name_plural = _("Gisim")

class Wi7da(models.Model):
    name = models.CharField(_("Wi7da"),max_length=150)
    gisim = models.ForeignKey(Gisim, on_delete=models.PROTECT,verbose_name=_("gisim"))

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = _("Wi7da")
        verbose_name_plural = _("Wi7da")

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
    NO3_2LERTIBAT_TA3AGOD_MOSIMI =  'ta3agod_mosimi'
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
    STATUS_EIGAF_MO2KAT = 15

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
        STATUS_EIGAF_MO2KAT: _("STATUS_EIGAF_MO2KAT"),
    }

    code = models.IntegerField(_("employee_code"))
    name = models.CharField(_("employee_name"),max_length=150,validators=[MinLengthValidator(12,_("2dkhil al2sm roba3i"))])
    mosama_wazifi = models.ForeignKey(MosamaWazifi, on_delete=models.PROTECT,verbose_name=_("mosama_wazifi"))
    # edara_3ama_tmp = models.ForeignKey(Edara3ama, on_delete=models.PROTECT,verbose_name=_("edara_3ama"),blank=True,null=True)
    # edara_far3ia_tmp = models.ForeignKey(Edarafar3ia, on_delete=models.PROTECT,verbose_name=_("edara_far3ia"),blank=True,null=True)
    #gisim_tmp = models.ForeignKey(Gisim, on_delete=models.PROTECT,verbose_name=_("gisim"),blank=True,null=True)
    #wi7da_tmp = models.ForeignKey(Wi7da, on_delete=models.PROTECT,verbose_name=_("wi7da"),blank=True,null=True)
    draja_wazifia = models.IntegerField(_("draja_wazifia"), choices=Drajat3lawat.DRAJAT_CHOICES)
    alawa_sanawia = models.IntegerField(_("alawa_sanawia"), choices=Drajat3lawat.ALAWAT_CHOICES)
    tarikh_milad = models.DateField(_("tarikh_milad"))
    tarikh_ta3in = models.DateField(_("tarikh_ta3in"))
    tarikh_akhir_targia = models.DateField(_("tarikh_akhir_targia"),blank=True,null=True)
    sex = models.CharField(_("sex"),max_length=7, choices=SEX_CHOICES)
    phone = models.CharField(_("phone"),max_length=30,blank=True,null=True)
    email = models.EmailField(_("email"),max_length=30,blank=True,null=True)
    no3_2lertibat = models.CharField(_("no3_2lertibat"),max_length=15, choices=NO3_2LERTIBAT_CHOICES)
    sanoat_2lkhibra = models.FloatField(_("sanoat_2lkhibra"),default=0)
    gasima = models.BooleanField(_("gasima"),default=False)
    atfal = models.IntegerField(_("3dad_atfal"),default=0)
    moahil = models.CharField(_("moahil"),max_length=30, choices=MOAHIL_CHOICES,default=MOAHIL_BAKLARIOS)
    m3ash = models.FloatField(_("m3ash"),default=0)
    aadoa = models.BooleanField(_("aadoa"),default=False)
    status = models.IntegerField(_("status"), choices=STATUS_CHOICES,default=STATUS_ACTIVE)
    hikal_wazifi = TreeForeignKey(HikalWazifi, on_delete=models.PROTECT,verbose_name=_("hikal_wazifi"),blank=True,null=True)

    def __str__(self) -> str:
        return f'{self.name}'# / {self.edara_3ama.name}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name','tarikh_ta3in'],name="unique_employee"),
            models.UniqueConstraint(fields=['code',],name="unique_employee_code"),
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
    
    @property
    @admin.display(description=_("edara_3ama"))
    def edara_3ama(self):
        return self.hikal_wazifi.edara_3ama if self.hikal_wazifi else None



    @property
    @admin.display(description=_("edara_far3ia"))
    def edara_far3ia(self):
        return self.hikal_wazifi.edara_far3ia if self.hikal_wazifi else None

    @property
    @admin.display(description=_("gisim"))
    def gisim(self):
        return self.hikal_wazifi.gisim if self.hikal_wazifi else None

    @property
    @admin.display(description=_("wi7da"))
    def wi7da(self):
        return self.traverse_hikal_wazifi(HikalWazifi.ELMOSTOA_ELTANZIMI_WI7DA)

    @property
    def mobashara_rate(self):
        key = Settings.MOSAMA_PREFIX + self.mosama_wazifi.category
        try:
            val = float(Settings.objects.get(code=key).value)
            return val
        except Exception as e:
            return 0

    def clean(self):            
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

class EmployeeWi7datMosa3da(LoggingModel):
    employee = models.OneToOneField(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"),related_name="wi7dat_mosa3da")
    has_diff = models.BooleanField(_("has_diff"),default=False)
    payroll_2ljiha_2l2om = models.FloatField(_("payroll_2ljiha_2l2om"))
    
    class Meta:
        verbose_name = _("2lwi7dat 2lmosa3da")
        verbose_name_plural = _("2lwi7dat 2lmosa3da")

    def __str__(self) -> str:
        return f'{self.employee.name}'
    
class EmployeeMajlisEl2dara(LoggingModel):
    POSITION_R2IS_2LMAJLIS = 1
    POSITION_MODIR_3AM = 2
    POSITION_3ODO = 3

    POSITION_CHOICES = {
        POSITION_R2IS_2LMAJLIS: _('POSITION_R2IS_2LMAJLIS'),
        POSITION_MODIR_3AM: _('POSITION_MODIR_3AM'),
        POSITION_3ODO: _('POSITION_3ODO'),
    }

    employee = models.OneToOneField(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"),related_name="majlis_el2dara")
    position = models.IntegerField(_("position"), choices=POSITION_CHOICES,default=POSITION_3ODO)
    
    class Meta:
        verbose_name = _("majlis el2dara")
        verbose_name_plural = _("majlis el2dara")

    def __str__(self) -> str:
        return f'{self.employee.name}'

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
    name = models.CharField(_("name"),max_length=100)
    tarikh_el2dafa = models.DateField(_("tarikh_el2dafa"),blank=True,null=True)
    attachement_file = models.FileField(_("attachement"),upload_to=attachement_path,blank=True,null=True)

    class Meta:
        verbose_name = _("Employee Family")
        verbose_name_plural = _("Employee Family")

    def __str__(self) -> str:
        return f'{self.employee.name} ({self.get_relation_display()})'

    def update_number_of_children(self):
        count = self.employee.employeefamily_set.filter(relation=self.FAMILY_RELATION_CHILD).count()
        #if count > self.employee.atfal:
        self.employee.atfal = count
        self.employee.save()

    def update_gasima_status(self):
        count = self.employee.employeefamily_set.filter(relation=self.FAMILY_RELATION_CONSORT).count()
        if count > 0:
            self.employee.gasima = True
        else:
            self.employee.gasima = False
        
        self.employee.save()

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

    def update_moahil(self):
        qs = EmployeeMoahil.objects.filter(employee=self.employee)

        tmp_moahil = MOAHIL_THANOI
        for emp in qs:
            if MOAHIL_WEIGHT[emp.moahil] > MOAHIL_WEIGHT[tmp_moahil]:
                tmp_moahil = emp.moahil

        if MOAHIL_WEIGHT[tmp_moahil] > MOAHIL_WEIGHT[self.employee.moahil]:
            self.employee.moahil = tmp_moahil
            self.employee.save()

class EmployeeSalafiatMaster(LoggingModel):
    NO3_2LSALAFIA_SHARIKA = 1
    NO3_2LSALAFIA_SANDOG = 2
    NO3_2LSALAFIA_3LA_2LMORATAB = 3
    NO3_2LSALAFIA_3LA_2LMOKAF2 = 4

    NO3_2LSALAFIA_CHOICES = {
        NO3_2LSALAFIA_SHARIKA: _('NO3_2LSALAFIA_SHARIKA'),
        NO3_2LSALAFIA_SANDOG: _('NO3_2LSALAFIA_SANDOG'),
        NO3_2LSALAFIA_3LA_2LMORATAB: _('NO3_2LSALAFIA_3LA_2LMORATAB'),
        NO3_2LSALAFIA_3LA_2LMOKAF2: _('NO3_2LSALAFIA_3LA_2LMOKAF2'),
    }

    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    no3_2lsalafia = models.IntegerField(_("no3_2lsalafia"), choices=NO3_2LSALAFIA_CHOICES,default=NO3_2LSALAFIA_SANDOG)
    amount = models.FloatField(_("amount"))
    start_year = models.IntegerField(_("تاريخ البداية - السنة"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    start_month = models.IntegerField(_("تاريخ البداية - الشهر"), choices=MONTH_CHOICES)
    no_month = models.IntegerField(_("عدد الشهور"), default=1)

    def __str__(self):
        return f"{self.employee.name} {self.amount} ({self.get_no3_2lsalafia_display()})"
    
    def remaining(self, exclude=None):
        qs = EmployeeSalafiat.objects.filter(salafiat_master__id=self.id)
        paid = qs.aggregate(paid =Sum('amount'))['paid'] or 0
        
        return self.amount - paid

    class Meta:
        verbose_name = _("سجل سلفية")
        verbose_name_plural = _("سجل السلفيات")


class EmployeeSalafiat(LoggingModel):
    NO3_2LSALAFIA_SHARIKA = EmployeeSalafiatMaster.NO3_2LSALAFIA_SHARIKA
    NO3_2LSALAFIA_SANDOG = EmployeeSalafiatMaster.NO3_2LSALAFIA_SANDOG
    NO3_2LSALAFIA_3LA_2LMORATAB = EmployeeSalafiatMaster.NO3_2LSALAFIA_3LA_2LMORATAB
    NO3_2LSALAFIA_3LA_2LMOKAF2 = EmployeeSalafiatMaster.NO3_2LSALAFIA_3LA_2LMOKAF2

    NO3_2LSALAFIA_CHOICES = EmployeeSalafiatMaster.NO3_2LSALAFIA_CHOICES

    salafiat_master = models.ForeignKey(EmployeeSalafiatMaster, on_delete=models.PROTECT,verbose_name=_("مرجع السلفية"), null=True, default=None)
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    year = models.IntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    month = models.IntegerField(_("month"), choices=MONTH_CHOICES)
    no3_2lsalafia = models.IntegerField(_("no3_2lsalafia"), choices=NO3_2LSALAFIA_CHOICES,default=NO3_2LSALAFIA_SANDOG)
    note = models.CharField(_("note"),max_length=150)
    amount = models.FloatField(_("amount"))
    deducted = models.BooleanField(_("deducted"),default=False)

    def __str__(self) -> str:
        return f'{self.amount}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee','year','month','no3_2lsalafia'],name="unique_salafiat_employee_year_month")
        ]
        indexes = [
            models.Index(fields=["employee", "year","month"]),
        ]
        ordering = ["year","month","no3_2lsalafia"]
        verbose_name = _("تفاصيل سلفية")
        verbose_name_plural = _("تفاصيل السلفيات")

    def validate_unique(self, exclude=None):
        qs = EmployeeSalafiat.objects.filter(no3_2lsalafia=EmployeeSalafiat.NO3_2LSALAFIA_SANDOG,employee=self.employee,year=self.year,month=self.month)
        count = qs.count()

        if not (count==0 or (count==1 and self.pk)):
            raise ValidationError(_('Duplicated: Record already exists!'))
        
        return super().validate_unique(exclude=exclude)

    def clean(self):
        if self.salafiat_master and self.salafiat_master.employee != self.employee:
            raise ValidationError({
                'employee': 'لايمكن استقطاع سلفية موظف من موظف اخر!',
            })
        
        if self.salafiat_master and self.salafiat_master.no3_2lsalafia != self.no3_2lsalafia:
            raise ValidationError({
                'no3_2lsalafia': 'يجب ان تكون نوع السلفية من نفس نوع السلفية الاساسية',
            })
        
        return super().clean()
    
class EmployeeSalafiatSandogManager(models.Manager):
    def get_queryset(self):
       return super().get_queryset().filter(no3_2lsalafia=EmployeeSalafiat.NO3_2LSALAFIA_SANDOG)

class EmployeeSalafiatSandog(EmployeeSalafiat):
    objects = EmployeeSalafiatSandogManager()
    default_manager = objects

    class Meta:
        proxy = True
        verbose_name = _("سلفية صندوق")
        verbose_name_plural = _("سلفيات الصندوق")

class EmployeeJazaat(LoggingModel):
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    year = models.IntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    month = models.IntegerField(_("month"), choices=MONTH_CHOICES)
    note = models.CharField(_("note"),max_length=150)
    amount = models.FloatField(_("amount"))
    deducted = models.BooleanField(_("deducted"),default=False)
    attachement_file = models.FileField(_("attachement"),upload_to=attachement_path,blank=True,null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee','year','month'],name="unique_jazaat_employee_year_month")
        ]
        indexes = [
            models.Index(fields=["year","month"]),
            models.Index(fields=["employee", "year","month"]),
        ]
        ordering = ["-id"]
        verbose_name = _("Jazaat")
        verbose_name_plural = _("Jazaat")

class EmployeeMobashra(LoggingModel):
    STATE_ACTIVE = 'active'
    STATE_INACTIVE = 'in_active'

    STATE_CHOICES = {
        STATE_ACTIVE: _('STATE_ACTIVE'),
        STATE_INACTIVE: _('STATE_INACTIVE'),
    }

    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    start_dt = models.DateField(_('start_dt'))
    end_dt = models.DateField(_('end_dt'),null=True,blank=True)
    toari2_enabled = models.BooleanField(_("toari2_enabled"),default=False)
    m2moria_enabled = models.BooleanField(_("m2moria_enabled"),default=False)
    e3ash_enabled = models.BooleanField(_("e3ash_enabled"),default=False)

    state = models.CharField(_("mobashara state"), choices=STATE_CHOICES,default=STATE_ACTIVE,max_length=10)

    @property
    def employee_rate(self):
        return self.employee.mobashara_rate

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
    amount = models.FloatField(_("amount"))
    amount_m2moria = models.FloatField(_("amount_m2moria"),default=0)
    amount_e3asha = models.FloatField(_("amount_e3asha"),default=0)
    rate = models.FloatField(_("rate"))
    no_days_month = models.IntegerField(_("no_days_month"))
    no_days_mobashara = models.IntegerField(_("no_days_mobashara"))
    no_days_2jazaa = models.IntegerField(_("no_days_2jazaa"))
    no_days_taklif = models.IntegerField(_("no_days_taklif"))
    confirmed = models.BooleanField(_("confirmed"),default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee','year','month'],name="unique_mobashraemployee_year_month")
        ]
        indexes = [
            models.Index(fields=["year","month"]),
            models.Index(fields=["employee", "year","month"]),
        ]

def validate_not_in_future_dt(value):
    now = timezone.now().date()
    if value > now:
        raise ValidationError(_("value should be in the past!"))


class EmployeeVacation(LoggingModel):
    VACATION_SANAWIA = 'sanawia'
    VACATION_3ARDAH = '3ardah'
    VACATION_MARADIAH = 'maradiah'
    VACATION_29ABAT_3MAL = '29abat_3mal'
    VACATION_WDO3 = 'wdo3'
    VACATION_OMOMA = 'omoma'
    VACATION_3DA = '3da'
    VACATION_MORAFAGAT_MARID = 'morafagat_marid'
    VACATION_MIN7_DRASIA = 'min7_drasia'
    VACATION_ZOAJ = 'zoaj'
    VACATION_7AJ = '7aj'
    VACATION_OMRA = 'omra'
    VACATION_YOUM_97I = 'youm_97i'
    VACATION_ZARF_KAHIR = 'zarf_kahir'
    VACATION_BDON_MORATAB = 'bdon_moratab'
    VACATION_WAFAH = 'wafah'

    VACATION_CHOICES = {
        VACATION_SANAWIA: _('VACATION_SANAWIA'),
        VACATION_3ARDAH: _('VACATION_3ARDAH'),
        VACATION_MARADIAH: _('VACATION_MARADIAH'),
        VACATION_29ABAT_3MAL: _('VACATION_29ABAT_3MAL'),
        VACATION_WDO3: _('VACATION_WDO3'),
        VACATION_OMOMA: _('VACATION_OMOMA'),
        VACATION_3DA: _('VACATION_3DA'),
        VACATION_MORAFAGAT_MARID: _('VACATION_MORAFAGAT_MARID'),
        VACATION_MIN7_DRASIA: _('VACATION_MIN7_DRASIA'),
        VACATION_ZOAJ: _('VACATION_ZOAJ'),
        VACATION_7AJ: _('VACATION_7AJ'),
        VACATION_OMRA: _('VACATION_OMRA'),
        VACATION_YOUM_97I: _('VACATION_YOUM_97I'),
        VACATION_ZARF_KAHIR: _('VACATION_ZARF_KAHIR'),
        VACATION_BDON_MORATAB: _('VACATION_BDON_MORATAB'),
        VACATION_WAFAH: _('VACATION_WAFAH'),
    }

    vacation_type = models.CharField(_("vacation_type"), choices=VACATION_CHOICES,max_length=30)
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    start_dt = models.DateField(_('start_dt'))
    end_dt_excpected = models.DateField(_('end_dt_excpected'))
    end_dt_actual = models.DateField(_('end_dt_actual'),validators=[validate_not_in_future_dt],null=True,blank=True)
    mokalaf = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,related_name="mokalafvacation_set",verbose_name=_("mokalaf_name"),null=True,blank=True)
    attachement_file = models.FileField(_("attachement"),upload_to=attachement_path,blank=True,null=True)

    @property
    def employee_rate(self):
        return self.employee.mobashara_rate

    @property
    def mokalaf_rate(self):
        return self.mokalaf.mobashara_rate
    
    class Meta:
        indexes = [
            models.Index(fields=["employee","vacation_type"]),
            models.Index(fields=["vacation_type"]),
        ]
        ordering = ["-id"]
        verbose_name = _("Vacation")
        verbose_name_plural = _("Vacation")

class EmployeeM2moria(LoggingModel):
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    start_dt = models.DateField(_('start_dt'))
    end_dt_excpected = models.DateField(_('end_dt_excpected'))
    end_dt_actual = models.DateField(_('end_dt_actual'),null=True,blank=True)
    attachement_file = models.FileField(_("attachement"),upload_to=attachement_path,blank=True,null=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = _("M2moria")
        verbose_name_plural = _("M2moria")

class PayrollMaster(LoggingModel):
    year = models.IntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    month = models.IntegerField(_("month"), choices=MONTH_CHOICES)
    zaka_kafaf = models.FloatField(_("zaka_kafaf"),default=0)
    zaka_nisab = models.FloatField(_("zaka_nisab"),default=0)
    enable_sandog_kahraba = models.BooleanField(_("enable_sandog_kahraba"),default=False)
    enable_youm_algoat_almosalaha = models.BooleanField(_("enable_youm_algoat_almosalaha"),default=False)
    daribat_2lmokafa = models.FloatField(_("daribat_2lmokafa"),default=0)
    m3ash_age = models.FloatField(_("m3ash_age"),default=0)
    khasm_salafiat_elsandog_min_elomoratab = models.BooleanField(_("khasm_elsandog_min_elomoratab"),default=False)
    confirmed = models.BooleanField(_("confirmed"),default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['year','month'],name="unique_payroll_year_month")
        ]
        indexes = [
            models.Index(fields=["year","month"]),
        ]
        verbose_name = _("Payroll")
        verbose_name_plural = _("Payroll")

    def __str__(self) -> str:
        return f'{_("Payroll")} {self.get_month_display()} {self.year}'

class EmployeeM2moriaMonthly(LoggingModel):
    payroll_master = models.ForeignKey(PayrollMaster, on_delete=models.CASCADE)
    m2moria_master = models.ForeignKey(EmployeeM2moria, on_delete=models.CASCADE)
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    ajmali_2lmoratab = models.FloatField(_("amount"))
    no_days = models.IntegerField(_("no_days"))
    damga = models.FloatField(_("damga"))
    safi_2l2sti7gag = models.FloatField(_("safi_2l2sti7gag"))

    class Meta:
        verbose_name = _("M2moria detail")
        verbose_name_plural = _("M2moria details")

class PayrollDetailAbstract(models.Model):
    payroll_master = models.ForeignKey(PayrollMaster, on_delete=models.CASCADE)
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    salafiat = models.FloatField(_("salafiat"),default=0)
    jazaat = models.FloatField(_("jazaat"),default=0)
    damga = models.FloatField(_("damga"),default=0)
    sandog = models.FloatField(_("sandog"),default=0)
    sandog_kahraba = models.FloatField(_("sandog_kahraba"),default=0)
    tarikh_milad = models.DateField(_("tarikh_milad"),blank=True,null=True)
    salafiat_sandog = models.FloatField(_("salafiat_sandog"),default=0)
    salafiat_3la_2lmoratab = models.FloatField(_("salafiat_3la_2lmoratab"),default=0)
    salafiat_3la_2lmokaf2 = models.FloatField(_("salafiat_3la_2lmokaf2"),default=0)
    draja_wazifia = models.IntegerField(_("draja_wazifia"), choices=Drajat3lawat.DRAJAT_CHOICES,blank=True,null=True)
    alawa_sanawia = models.IntegerField(_("alawa_sanawia"), choices=Drajat3lawat.ALAWAT_CHOICES,blank=True,null=True)
    bank = models.CharField(_("bank"), choices=EmployeeBankAccount.BANK_CHOICES,max_length=10,blank=True,null=True)
    account_no = models.CharField(_("account_no"),max_length=20,blank=True,null=True)

    def __str__(self) -> str:
        return f'{self.employee.name} ({self.employee.edara_3ama})'

    class Meta:
        abstract = True

class PayrollDetailHikalRatibiAbstract(PayrollDetailAbstract):
    abtdai = models.FloatField(_("abtdai"),default=0)
    galaa_m3isha = models.FloatField(_("galaa_m3isha"),default=0)
    shakhsia = models.FloatField(_("shakhsia"),default=0)
    ma3adin = models.FloatField(_("ma3adin"),default=0)

    def __str__(self) -> str:
        return f'{self.employee.name} ({self.employee.edara_3ama})'

    class Meta:
        abstract = True

class PayrollDetail(PayrollDetailHikalRatibiAbstract):
    aadoa = models.FloatField(_("aadoa"),default=0)
    mokaf2at_2da2 = models.FloatField(_("mokaf2at_2da2"),default=0)
    mokaf2at_2da2_fi_mokaf2 = models.BooleanField("حساب بدل المكافئة في كشف المكافئة",default=True)
    gasima = models.FloatField(_("gasima"),default=0)
    atfal = models.FloatField(_("atfal"),default=0)
    moahil = models.FloatField(_("moahil"),default=0)
    m3ash = models.FloatField(_("m3ash"),default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['payroll_master','employee'],name="unique_employee_payroll")
        ]
        ordering = ["employee__code"]

        verbose_name = _("Payroll detail")
        verbose_name_plural = _("Payroll details")

class PayrollDetailWi7datMosa3ida(PayrollDetailHikalRatibiAbstract):
    payroll_2ljiha_2l2om = models.FloatField(_("payroll_2ljiha_2l2om"),default=0)
    payroll_2lsharika = models.FloatField(_("payroll_2lsharika"),default=0)
    has_diff = models.BooleanField(_("has_diff"),default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['payroll_master','employee'],name="unique_employee_payroll_wi7dat_mosa3da")
        ]
        ordering = ["employee__code"]

        verbose_name = _("Payroll detail (wi7dat mosa3da)")
        verbose_name_plural = _("Payroll details (wi7dat mosa3da)")

class PayrollDetailTa3agodMosimi(PayrollDetailAbstract):
    payroll_ajmali = models.FloatField(_("payroll_ajmali"),default=0)
    payroll_mokaf2 = models.FloatField(_("payroll_mokaf2"),default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['payroll_master','employee'],name="unique_employee_payroll_ta3agod_mosimi")
        ]
        ordering = ["employee__code"]

        verbose_name = _("Payroll detail (ta3agod mosimi)")
        verbose_name_plural = _("Payroll details (ta3agod mosimi)")

class PayrollDetailMajlisEl2dara(PayrollDetailAbstract):
    payroll_mokaf2 = models.FloatField(_("payroll_mokaf2"),default=0)
    payroll_asasi = models.FloatField(_("payroll_asasi"),default=0)
    gasima = models.FloatField(_("gasima"),default=0)
    atfal = models.FloatField(_("atfal"),default=0)
    moahil = models.FloatField(_("moahil"),default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['payroll_master','employee'],name="unique_employee_payroll_majlis_el2dara")
        ]
        ordering = ["employee__code"]

        verbose_name = _("Payroll detail (majlis el2dara)")
        verbose_name_plural = _("Payroll details (majlis el2dara)")

class PayrollTasoia(models.Model):
    payroll_master = models.OneToOneField(PayrollMaster, on_delete=models.CASCADE)
    total_abtdai = models.FloatField(_("abtdai"),default=0)
    total_galaa_m3isha = models.FloatField(_("galaa_m3isha"),default=0)
    total_tabi3at_3mal = models.FloatField(_("tabi3at_3mal"),default=0)
    total_tamtheel = models.FloatField(_("tamtheel"),default=0)
    total_mihna = models.FloatField(_("mihna"),default=0)
    total_ma3adin = models.FloatField(_("ma3adin"),default=0)
    total_aadoa = models.FloatField(_("aadoa"),default=0)
    total_mokaf2at_2da2 = models.FloatField(_("aadoa"),default=0)
    total_ajtima3ia = models.FloatField(_("ajtima3ia"),default=0)
    total_moahil = models.FloatField(_("moahil"),default=0)
    total_shakhsia = models.FloatField(_("shakhsia"),default=0)
    total_makhatir = models.FloatField(_("makhatir"),default=0)
    total_salafiat = models.FloatField(_("salafiat"),default=0)
    total_dariba = models.FloatField(_("dariba"),default=0)
    total_damga = models.FloatField(_("damga"),default=0)
    total_m3ash = models.FloatField(_("m3ash"),default=0)
    total_tameen_ajtima3i = models.FloatField(_("tameen_ajtima3i"),default=0)
    total_sandog = models.FloatField(_("sandog"),default=0)
    total_zakat = models.FloatField(_("zakat"),default=0)
    total_youm_algoat_almosalaha = models.FloatField(_("youm_algoat_almosalaha"),default=0)
    total_jazaat = models.FloatField(_("jazaat"),default=0)
    total_salafiat_sandog = models.FloatField(_("salafiat_sandog"),default=0)
    total_safi_alisti7gag = models.FloatField(_("total_safi_alisti7gag"),default=0)

    class Meta:
        verbose_name = _("Payroll tasoia")
        verbose_name_plural = _("Payroll tasoia")

class PayrollSummary(models.Model):
    payroll_master = models.ForeignKey(PayrollMaster, on_delete=models.CASCADE)
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    total_salary = models.FloatField(_("اجمالي المرتب"),default=0)
    net_salary = models.FloatField(_("صافي الإستحقاق"),default=0)
