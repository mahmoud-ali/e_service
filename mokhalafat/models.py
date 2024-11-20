from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class LoggingModel(models.Model):
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))
    
    class Meta:
        abstract = True

class AppMokhalafat(LoggingModel):
    code = models.IntegerField(_("code"))
    date = models.DateField(_("date"))
    aism_almukhalafa = models.CharField(_("aism_almukhalafa"),max_length=150)
    wasf_almukhalafa = models.CharField(_("wasf_almukhalafa"),max_length=1000)
    tahlil_almukhalafa = models.CharField(_("tahlil_almukhalafa"),max_length=150)

    class Meta:
        verbose_name = _("AppMokhalafat")
        verbose_name_plural = _("AppMokhalafat")

    def __str__(self):
        return f"{self.aism_almukhalafa}"

class AppMokhalafatProcedure(models.Model):
    master = models.ForeignKey(AppMokhalafat, on_delete=models.PROTECT)
    name = models.CharField(_("procedure_name"),max_length=150)

    class Meta:
        verbose_name = _("AppMokhalafatProcedure")
        verbose_name_plural = _("AppMokhalafatProcedure")

    def __str__(self):
        return f"{self.name}"

class AppMokhalafatRecommendation(models.Model):
    master = models.ForeignKey(AppMokhalafat, on_delete=models.PROTECT)
    name = models.CharField(_("recommendation_name"),max_length=150)
    jihat_altanfidh = models.CharField(_("jihat_altanfidh"),max_length=100)
    from_date = models.DateField(_("from_date"))
    to_date = models.DateField(_("to_date"))
    comments = models.CharField(_("comments"),max_length=255,null=True,blank=True) 

    class Meta:
        verbose_name = _("AppMokhalafatRecommendation")
        verbose_name_plural = _("AppMokhalafatRecommendation")
        
    def __str__(self):
        return f"{self.name}"
