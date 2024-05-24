from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

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

    draja_wazifia = models.IntegerField(_("draja_wazifia"),max_length=2, choices=DRAJAT_CHOICES)
    alawa_sanawia = models.IntegerField(_("alawa_sanawia"),max_length=2, choices=ALAWAT_CHOICES)
    abtdai = models.FloatField(_("abtdai"))
    galaa_m3isha = models.FloatField(_("galaa_m3isha"))
    shakhsia = models.FloatField(_("shakhsia"))
    ma3adin = models.FloatField(_("ma3adin"))
    aadoa = models.FloatField(_("aadoa"))

class MosamaWazifi(models.Model):
    name = models.CharField(_("mosama_wazifi"),max_length=100)

class Edara3ama(models.Model):
    name = models.CharField(_("edara3ama"),max_length=150)

class Edarafar3ia(models.Model):
    name = models.CharField(_("edarafar3ia"),max_length=150)
    edara_3ama = models.ForeignKey(Edara3ama, on_delete=models.PROTECT,verbose_name=_("edara3ama"))

class EmployeeBasic(LoggingModel):
    name = models.CharField(_("employee_name"),max_length=150)
    mosama_wazifi = models.ForeignKey(MosamaWazifi, on_delete=models.PROTECT,verbose_name=_("mosama_wazifi"))
    edara_3ama = models.ForeignKey(Edara3ama, on_delete=models.PROTECT,verbose_name=_("edara_3ama"))
    edara_far3ia = models.ForeignKey(Edarafar3ia, on_delete=models.PROTECT,verbose_name=_("edara_far3ia"))
    draja_wazifia = models.IntegerField(_("draja_wazifia"),max_length=2, choices=Drajat3lawat.DRAJAT_CHOICES)
    alawa_sanawia = models.IntegerField(_("alawa_sanawia"),max_length=2, choices=Drajat3lawat.ALAWAT_CHOICES)
    tarikh_ta3in = models.DateField(_("tarikh_ta3in"))
    