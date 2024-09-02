from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

from django.conf import settings

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

class TblRevenu(LoggingModel):
    date = models.DateField(_("date"))
    name = models.CharField(_("name"),max_length=100)
    revenu_type  = models.ForeignKey(LkpRevenuType, on_delete=models.PROTECT)    
    amount = models.FloatField(_("amount"))
    currency = models.IntegerField(_("currency"), choices=CURRENCY_TYPE_CHOICES, default=CURRENCY_TYPE_SDG)
    source = models.CharField(_("source"),max_length=100)

    def __str__(self):
        return f'{self.name} ({self.amount} {self.get_currency_display()})'

    class Meta:
        verbose_name = _("Revenu")
        verbose_name_plural = _("Revenu")

    def checkDetailsTotalEqualAmount(self):
        qs = self.tblrevenudist_set.all()
        result = qs.aggregate(total=Sum("amount",default=0))
        diff = (result['total']-self.amount)
        print('----',diff)
        return (abs(diff) <=  ALLOWED_ERROR)

    def calculatePartnerShare(self,partner):
        master_amount = self.amount
        revenu_type = self.revenu_type
        try:
            share_percent = LkpRevenuTypeDetail.objects.get(master=revenu_type,partner=partner).percent
            return (master_amount*share_percent)/100
        except LkpRevenuTypeDetail.DoesNotExist:
            return 0
        
    def distributeAmount(self):
        for d in LkpRevenuTypeDetail.objects.filter(master=self.revenu_type):
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
        verbose_name = _("Revenu distribution")
        verbose_name_plural = _("Revenu distribution")

