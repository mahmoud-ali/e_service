from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.forms import ValidationError

from company_profile.models import TblCompany, TblCompanyProduction

STATE_DRAFT = 1
STATE_CONFIRMED = 2
STATE_EXPIRED = 3

STATE_CHOICES = {
    STATE_DRAFT: _('state_draft'),
    STATE_CONFIRMED: _('state_confirmed'),
    STATE_EXPIRED: _('state_expired'),
}

class LoggingModel(models.Model):
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))
    
    class Meta:
        abstract = True
        
def company_applications_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/company_<id>/applications/<filename>
    return "company_{0}/applications/{1}".format(instance.company.id, filename)    

class LkpMoragib(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="moragib_list",verbose_name=_("user"))
    name = models.CharField(_("name"),max_length=100)
    emp_code = models.CharField(_("name"),max_length=20,default='',null=True)
    company_type = models.CharField(_("company_type"),max_length=15, choices=TblCompany.COMPANY_TYPE_CHOICES)

    def __str__(self):
        return f'{self.name} ({self.user})'

    class Meta:
        verbose_name = _("moragib_list")
        verbose_name_plural = _("moragib_list")

class GoldProductionUser(LoggingModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="gold_production_user",verbose_name=_("user"))
    name = models.CharField(_("name"),max_length=100)
    moragib = models.OneToOneField(LkpMoragib, on_delete=models.PROTECT,related_name="moragib_distribution",verbose_name=_("moragib"),default=None,null=True)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

    def __str__(self):
        return f'{self.user} ({self.name})'

    class Meta:
        verbose_name = _("moragib_distribution")
        verbose_name_plural = _("moragib_distribution")

class GoldProductionUserDetail(models.Model):
    master = models.ForeignKey(GoldProductionUser, on_delete=models.PROTECT)    
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))

    def __str__(self):
        return f'{self.master} ({self.company})'

    class Meta:
        verbose_name = _("gold_production_user_detail")
        verbose_name_plural = _("gold_production_user_details")

class GoldProductionForm(LoggingModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    date = models.DateField(_("date"))

    form_no = models.CharField(_("form_no"),max_length=20)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)
    alloy_jaf = models.FloatField(_("alloy_jaf"),default=0)
    alloy_khabath = models.FloatField(_("alloy_khabath"),default=0)
    alloy_remaind = models.FloatField(_("alloy_remaind"),blank=True,null=True,default=0)
    gold_production_form_file = models.FileField(_("gold_production_form_file"),upload_to=company_applications_path,blank=True,null=True)
    gold_production_3hda_file = models.FileField(_("gold_production_3hda_file"),upload_to=company_applications_path,blank=True,null=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Gold Production Form")
        verbose_name_plural = _("Gold Production Form")

    def __str__(self):
        return f'{self.company} ({self.form_no})' 
        
    def total_weight(self):
        total = self.goldproductionformalloy_set.aggregate(total=models.Sum('alloy_weight'))['total'] or 0
        return round(total,2)

class GoldProductionFormAlloy(models.Model):
    master = models.ForeignKey(GoldProductionForm, on_delete=models.CASCADE)    
    alloy_serial_no = models.CharField(_("alloy_serial_no"),max_length=30)
    alloy_weight = models.FloatField(_("alloy_weight"))
    # alloy_jaf = models.FloatField(_("alloy_jaf"))
    # alloy_khabath = models.FloatField(_("alloy_khabath"))
    alloy_added_gold = models.FloatField(_("alloy_added_gold"),blank=True,null=True)
    # alloy_remaind = models.FloatField(_("alloy_remaind"),blank=True,null=True)
    alloy_shipped = models.BooleanField(_("alloy_shipped"),default=False)

    def __str__(self):
        return f'{self.master.form_no} ({self.alloy_serial_no})'

    class Meta:
        verbose_name = _("Gold Production Form - Alloy")
        verbose_name_plural = _("Gold Production Form - Alloy")

class GoldShippingForm(LoggingModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    date = models.DateField(_("date"))

    form_no = models.CharField(_("form_no"),max_length=20)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)
    attachement_file = models.FileField(_("gold_shipping_form_file"),upload_to=company_applications_path,blank=True,null=True)

    def __str__(self):
        return f'{self.company} ({self.form_no})' 
        
    def get_absolute_url(self): 
        return reverse('profile:app_gold_shipping_show',args=[str(self.id)])                
    
    def alloy_shipped(self):
        if self.state == STATE_CONFIRMED:
            for obj in self.goldshippingformalloy_set.all():
                obj.alloy_serial_no.alloy_shipped = True
                obj.alloy_serial_no.save()
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Gold Shipping Form")
        verbose_name_plural = _("Gold Shipping Form")

class GoldShippingFormAlloy(models.Model):
    master = models.ForeignKey(GoldShippingForm, on_delete=models.CASCADE)    
    alloy_serial_no = models.ForeignKey(GoldProductionFormAlloy, on_delete=models.PROTECT,verbose_name=_('alloy_serial_no'))
    # alloy_weight = models.FloatField(_("alloy_weight"))

    def __str__(self):
        return f'{self.master.form_no} ({self.alloy_serial_no})'

    class Meta:
        verbose_name = _("Gold Shipping Form - Alloy")
        verbose_name_plural = _("Gold Shipping Form - Alloy")

    def clean(self) -> None:
        if self.master.company != self.alloy_serial_no.master.company:
            raise ValidationError(
                {"alloy_serial_no":_("alloy should belong to same company!")}
            )

        return super().clean()