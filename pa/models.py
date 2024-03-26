from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_fsm import FSMField, transition

from company_profile.models import TblCompanyProduction

CURRENCY_TYPE_SDG = "sdg"
CURRENCY_TYPE_EURO = "euro"

CURRENCY_TYPE_CHOICES = {
    CURRENCY_TYPE_SDG: _("entaj"),
    CURRENCY_TYPE_EURO: _("mokhalfat"),
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
        
class LkpItem(models.Model):
    name = models.CharField(_("item_name"),max_length=50)

    def __str__(self):
        return _("Item") +" ("+str(self.id)+")"
        
class TblCompanyCommitment(LoggingModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    item  = models.ForeignKey(LkpItem, on_delete=models.PROTECT,verbose_name=_("item"))    
    amount = models.FloatField(_("amount"))
    currency = models.CharField(_("currency"),max_length=10, choices=CURRENCY_TYPE_CHOICES, default=CURRENCY_TYPE_EURO)

    def __str__(self):
        return _("Financial commitment") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('pa:commitment_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Financial commitment")
        verbose_name_plural = _("Financial commitments")

class TblCompanyRequest(LoggingModel):
    REQUEST_PAYMENT_NO_PAYMENT = "no"
    REQUEST_PAYMENT_PARTIAL_PAYMENT = "partial"
    REQUEST_PAYMENT_FULL_PAYMENT = "full"

    REQUEST_PAYMENT_CHOICES = {
        REQUEST_PAYMENT_NO_PAYMENT: _("no_payment"),
        REQUEST_PAYMENT_PARTIAL_PAYMENT: _("partial_payment"),
        REQUEST_PAYMENT_FULL_PAYMENT: _("full_payment"),
    }

    commitement  = models.ForeignKey(TblCompanyCommitment, on_delete=models.PROTECT,verbose_name=_("commitement"))    
    from_dt = models.DateField(_("from_dt"))
    to_dt = models.DateField(_("to_dt"))
    amount = models.FloatField(_("amount"))
    currency = models.CharField(_("currency"),max_length=10, choices=CURRENCY_TYPE_CHOICES, default=CURRENCY_TYPE_EURO)
    payment_state = models.CharField(_("payment_state"),max_length=10, choices=REQUEST_PAYMENT_CHOICES, default=REQUEST_PAYMENT_NO_PAYMENT)

    def __str__(self):
        return _("Financial request") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('pa:request_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Financial request")
        verbose_name_plural = _("Financial requests")

class TblCompanyPayment(LoggingModel):
    request  = models.ForeignKey(TblCompanyRequest, on_delete=models.PROTECT,verbose_name=_("commitement"))    
    payment_dt = models.DateField(_("payment_dt"))
    amount = models.FloatField(_("amount"))
    currency = models.CharField(_("currency"),max_length=10, choices=CURRENCY_TYPE_CHOICES, default=CURRENCY_TYPE_EURO)
    excange_rate = models.FloatField(_("excange_rate"))

    def __str__(self):
        return _("Financial payment") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('pa:payment_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Financial payment")
        verbose_name_plural = _("Financial payments")
