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

class LkpState(models.Model):
    name = models.CharField(_("name"),max_length=100)
    
    def __str__(self):
        return self.name    
        
    class Meta:
        verbose_name = _("State")
        verbose_name_plural = _("States")

class LkpSoag(models.Model):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    name = models.CharField(_("name"),max_length=100)
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = _("Soag")
        verbose_name_plural = _("Soag")

class TblCollector(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="collector")
    name = models.CharField(_("name"),max_length=100)
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    soag = models.ForeignKey(LkpSoag, on_delete=models.PROTECT,verbose_name=_("Soag"))

    def __str__(self):
        return f'{self.name} ({self.user.email})'

    class Meta:
        verbose_name = _("Collector")
        verbose_name_plural = _("Collectors")

class TblInvoice(LoggingModel):
    collector = models.ForeignKey(TblCollector, on_delete=models.PROTECT,verbose_name=_("Collector"))
    mo3adin_name = models.CharField(_("mo3adin_name"),max_length=100)
    quantity_in_shoal = models.IntegerField(_("quantity_per_shoal"))
    amount = models.FloatField(_("amount"))

    def __str__(self):
        return f'{self.collector.name} ({self.collector.soag})'

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
