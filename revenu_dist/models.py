from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

from django.conf import settings

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

ALLOWED_ERROR = 1

CURRENCY_TYPE_SDG = 1
CURRENCY_TYPE_EURO = 2
CURRENCY_TYPE_DOLLAR = 3

CURRENCY_TYPE_CHOICES = {
    CURRENCY_TYPE_SDG: _("sdg"),
    CURRENCY_TYPE_EURO: _("euro"),
    CURRENCY_TYPE_DOLLAR: _("dollar"),
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

class LkpPartner(models.Model):
    name = models.CharField(_("name"),max_length=100)
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = _("Partner")
        verbose_name_plural = _("Partners")

class LkpRevenuType(models.Model):
    name = models.CharField(_("name"),max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Revenu type")
        verbose_name_plural = _("Revenu types")

    def checkDetailsTotalEqual100(self):
        result = self.lkprevenutypedetail_set.aggregate(total=Sum("percent",default=0))
        return result['total']==100

class LkpRevenuTypeDetail(models.Model):
    master  = models.ForeignKey(LkpRevenuType, on_delete=models.PROTECT)    
    partner  = models.ForeignKey(LkpPartner, on_delete=models.PROTECT,verbose_name=_('Partner'))    
    percent = models.FloatField(_("percent"),validators=[MinValueValidator(limit_value=0),MaxValueValidator(limit_value=100)])

    class Meta:
        verbose_name = _("Revenu type detail")
        verbose_name_plural = _("Revenu type details")

class LkpRevenu(models.Model):
    name = models.CharField(_("name"),max_length=100)
    revenu_type  = models.ForeignKey(LkpRevenuType, on_delete=models.PROTECT,verbose_name=_('Revenu type'))    

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Revenu")
        verbose_name_plural = _("Revenu")


class TblRevenu(LoggingModel):
    date = models.DateField(_("date"))
    name = models.CharField(_("note"),max_length=100)
    revenu  = models.ForeignKey(LkpRevenu, on_delete=models.PROTECT,verbose_name=_('Revenu'))    
    amount = models.FloatField(_("amount"))
    currency = models.IntegerField(_("currency"), choices=CURRENCY_TYPE_CHOICES, default=CURRENCY_TYPE_SDG)
    source = models.CharField(_("source"),max_length=100)

    def __str__(self):
        return f'{self.revenu.name} - {MONTH_CHOICES[self.date.month]} {self.date.year} ({self.get_currency_display()})'

    class Meta:
        verbose_name = _("Revenu distribution")
        verbose_name_plural = _("Revenu distribution")

    def checkDetailsTotalEqualAmount(self):
        qs = self.tblrevenudist_set.all()
        result = qs.aggregate(total=Sum("amount",default=0))
        diff = (result['total']-self.amount)
        return (abs(diff) <=  ALLOWED_ERROR)

    def calculatePartnerShare(self,partner):
        master_amount = self.amount
        revenu_type = self.revenu.revenu_type
        try:
            share_percent = LkpRevenuTypeDetail.objects.get(master=revenu_type,partner=partner).percent
            return (master_amount*share_percent)/100
        except LkpRevenuTypeDetail.DoesNotExist:
            return 0
        
    def distributeAmount(self):
        for d in LkpRevenuTypeDetail.objects.filter(master=self.revenu.revenu_type):
            TblRevenuDist.objects.create(
                master=self,
                partner=d.partner,
                amount=self.calculatePartnerShare(d.partner)
            )

        
class TblRevenuDist(models.Model):
    master  = models.ForeignKey(TblRevenu, on_delete=models.PROTECT)    
    partner  = models.ForeignKey(LkpPartner, on_delete=models.PROTECT)    
    amount = models.FloatField(_("amount"),validators=[MinValueValidator(limit_value=0),])

    class Meta:
        verbose_name = _("Revenu distribution detail")
        verbose_name_plural = _("Revenu distribution details")

    def calculateShare(self,partner):
        master_amount = self.master.amount
        revenu_type = self.master.revenu.revenu_type
        try:
            share_percent = LkpRevenuTypeDetail.objects.get(master=revenu_type,partner=self.partner).percent
            return (master_amount*share_percent)/100
        except LkpRevenuTypeDetail.DoesNotExist:
            return 0
