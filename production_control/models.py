from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.forms import ValidationError

from workflow.model_utils import LoggingModel, WorkFlowModel

from company_profile.models import LkpSector,LkpState, TblCompany, TblCompanyProduction, TblCompanyProductionLicense

STATE_DRAFT = 1
STATE_CONFIRMED = 2

# class LoggingModel(models.Model):
#     created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    
#     updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
#     updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))
    
#     class Meta:
#         abstract = True
        
def company_applications_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/company_<id>/applications/<filename>
    return "company_{0}/applications/{1}".format(instance.license.company.id, filename)    

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
    STATE_EXPIRED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _('state_draft'),
        STATE_CONFIRMED: _('state_confirmed'),
        STATE_EXPIRED: _('state_expired'),
    }

    # user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="gold_production_user",verbose_name=_("user"))
    # name = models.CharField(_("name"),max_length=100)
    moragib = models.OneToOneField(LkpMoragib, on_delete=models.PROTECT,related_name="moragib_distribution",verbose_name=_("moragib"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

    def __str__(self):
        return f'{self.moragib}' # ({self.state})

    class Meta:
        verbose_name = _("moragib_distribution")
        verbose_name_plural = _("moragib_distribution")

class GoldProductionStateUser(LoggingModel):
    company_type = models.CharField(_("company_type"),max_length=15, choices=TblCompany.COMPANY_TYPE_CHOICES)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="gold_production_state_user",verbose_name=_("user"))
    name = models.CharField(_("name"),max_length=100)
    state = models.ManyToManyField(LkpState,verbose_name=_("state"))
    # state = models .ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))

    def __str__(self):
        return f'{self.name}({self.user})' # ({self.state})

    class Meta:
        verbose_name = _("رئيس القسم بالولاية")
        verbose_name_plural = _("رؤساء الاقسام بالولايات")

class GoldProductionSectorUser(LoggingModel):
    company_type = models.CharField(_("company_type"),max_length=15, choices=TblCompany.COMPANY_TYPE_CHOICES)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="gold_production_sector_user",verbose_name=_("user"))
    name = models.CharField(_("name"),max_length=100)
    sector = models.ForeignKey(LkpSector, on_delete=models.PROTECT,verbose_name=_("sector"))

    def __str__(self):
        return f'{self.name}({self.user})' # ({self.state})

    class Meta:
        verbose_name = _("مشرف القطاع")
        verbose_name_plural = _("مشرفي القطاعات")

class GoldProductionUserDetail(models.Model):
    master = models.ForeignKey(GoldProductionUser, on_delete=models.PROTECT)    
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))
    license  = models.ForeignKey(TblCompanyProductionLicense, on_delete=models.PROTECT,verbose_name=_("Production Company License"),blank=True,null=True)

    def __str__(self):
        return f'{self.master} ({self.company})'
    
    def clean(self):
        #raise error if licence.company not equal company
        if self.license and (self.license.company != self.company):
            print(self.license.company,self.company)
            raise ValidationError(
                {"license":_("licence should belong to same company!")}
            )


    class Meta:
        verbose_name = _("gold_production_user_detail")
        verbose_name_plural = _("gold_production_user_details")

class GoldProductionForm(WorkFlowModel):
    STATE_DRAFT = 1
    STATE_CONFIRMED1 = 2
    STATE_CONFIRMED2 = 3
    STATE_APPROVED = 4
    STATE_REVIEW_REQUIRED = 5

    STATE_CHOICES = {
        STATE_DRAFT: _('state_draft'),
        STATE_CONFIRMED1: _('تأكيد المراقب'),
        STATE_CONFIRMED2: _('تأكيد رئيس قسم الانتاج بالولاية'),
        STATE_APPROVED: _('إعتماد مشرف القطاع'),
        STATE_REVIEW_REQUIRED: _('مراجعة الإدخال'),
    }

    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"),blank=True,null=True)    
    license  = models.ForeignKey(TblCompanyProductionLicense, on_delete=models.PROTECT,verbose_name=_("Production Company License"),blank=True,null=True)

    date = models.DateField(_("date"))

    form_no = models.CharField(_("form_no"),max_length=20)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)
    alloy_jaf = models.FloatField(_("alloy_jaf"),default=0)
    alloy_khabath = models.FloatField(_("alloy_khabath"),default=0)
    alloy_remaind = models.FloatField(_("alloy_remaind"),blank=True,null=True,default=0)
    alloy_weight_expected = models.FloatField(_("alloy_weight_expected"),default=0,null=True)
    gold_production_form_file = models.FileField(_("gold_production_form_file"),upload_to=company_applications_path,blank=True,null=True)
    gold_production_3hda_file = models.FileField(_("gold_production_3hda_file"),upload_to=company_applications_path,blank=True,null=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Gold Production Form")
        verbose_name_plural = _("Gold Production Form")

    def __str__(self):
        return f'{self.license} ({self.form_no})' 

    def clean(self):
        if not self.license:
            raise ValidationError(
                {"license":_("Required field")}
            )

    def total_weight(self):
        total = self.goldproductionformalloy_set.aggregate(total=models.Sum('alloy_weight'))['total'] or 0
        return round(total,2)

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []
        if 'production_control_auditor' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_CONFIRMED1, self.STATE_CHOICES[self.STATE_CONFIRMED1]))

            if self.state == self.STATE_REVIEW_REQUIRED:
                states.append((self.STATE_CONFIRMED1, self.STATE_CHOICES[self.STATE_CONFIRMED1]))

        if 'production_control_state_mgr' in user_groups:
            if self.state == self.STATE_CONFIRMED1:
                states.append((self.STATE_CONFIRMED2, self.STATE_CHOICES[self.STATE_CONFIRMED2]))
                states.append((self.STATE_REVIEW_REQUIRED, self.STATE_CHOICES[self.STATE_REVIEW_REQUIRED]))

        if 'production_control_sector_mgr' in user_groups:
            if self.state == self.STATE_CONFIRMED2:
                states.append((self.STATE_APPROVED, self.STATE_CHOICES[self.STATE_APPROVED]))
                states.append((self.STATE_REVIEW_REQUIRED, self.STATE_CHOICES[self.STATE_REVIEW_REQUIRED]))

        return states

    def can_transition_to_next_state(self, user, state):
        """
        Check if the given user can transition to the specified state.
        """
        if state[0] in map(lambda x: x[0], self.get_next_states(user)):
            return True

        return False

    def transition_to_next_state(self, user, state):
        """
        Transitions the workflow to the given state, after checking user permissions.
        """
        if self.can_transition_to_next_state(user, state):
            self.state = state[0]
            self.updated_by = user
            self.save()
        else:
            raise Exception(f"User {user.username} cannot transition to state {state} from state {self.state}")

        return self

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

class GoldShippingForm(WorkFlowModel):
    STATE_DRAFT = 1
    STATE_CONFIRMED1 = 2
    STATE_CONFIRMED2 = 3
    STATE_APPROVED = 4
    STATE_REVIEW_REQUIRED = 5

    STATE_CHOICES = {
        STATE_DRAFT: _('state_draft'),
        STATE_CONFIRMED1: _('تأكيد المراقب'),
        STATE_CONFIRMED2: _('تأكيد رئيس قسم الانتاج بالولاية'),
        STATE_APPROVED: _('إعتماد مشرف القطاع'),
        STATE_REVIEW_REQUIRED: _('مراجعة الإدخال'),
    }

    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"),blank=True,null=True)    
    license  = models.ForeignKey(TblCompanyProductionLicense, on_delete=models.PROTECT,verbose_name=_("Production Company License"),blank=True,null=True)
    date = models.DateField(_("date"))

    form_no = models.CharField(_("form_no"),max_length=20)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)
    attachement_file = models.FileField(_("gold_shipping_form_file"),upload_to=company_applications_path,blank=True,null=True)

    def __str__(self):
        return f'{self.license} ({self.form_no})' 
        
    def get_absolute_url(self): 
        return reverse('profile:app_gold_shipping_show',args=[str(self.id)])           
         
    def clean(self):
        if not self.license:
            raise ValidationError(
                {"license":_("Required field")}
            )

    def total_weight(self):
        total = self.goldshippingformalloy_set.aggregate(total=models.Sum('alloy_serial_no__alloy_weight'))['total'] or 0
        return round(total,2)
    
    def alloy_shipped(self):
        if self.state == STATE_CONFIRMED:
            for obj in self.goldshippingformalloy_set.all():
                obj.alloy_serial_no.alloy_shipped = True
                obj.alloy_serial_no.save()

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []
        if 'production_control_auditor' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_CONFIRMED1, self.STATE_CHOICES[self.STATE_CONFIRMED1]))

            if self.state == self.STATE_REVIEW_REQUIRED:
                states.append((self.STATE_CONFIRMED1, self.STATE_CHOICES[self.STATE_CONFIRMED1]))

        if 'production_control_state_mgr' in user_groups:
            if self.state == self.STATE_CONFIRMED1:
                states.append((self.STATE_CONFIRMED2, self.STATE_CHOICES[self.STATE_CONFIRMED2]))
                states.append((self.STATE_REVIEW_REQUIRED, self.STATE_CHOICES[self.STATE_REVIEW_REQUIRED]))

        if 'production_control_sector_mgr' in user_groups:
            if self.state == self.STATE_CONFIRMED2:
                states.append((self.STATE_APPROVED, self.STATE_CHOICES[self.STATE_APPROVED]))
                states.append((self.STATE_REVIEW_REQUIRED, self.STATE_CHOICES[self.STATE_REVIEW_REQUIRED]))

        return states

    def can_transition_to_next_state(self, user, state):
        """
        Check if the given user can transition to the specified state.
        """
        if state[0] in map(lambda x: x[0], self.get_next_states(user)):
            return True

        return False

    def transition_to_next_state(self, user, state):
        """
        Transitions the workflow to the given state, after checking user permissions.
        """
        if self.can_transition_to_next_state(user, state):
            self.state = state[0]
            self.updated_by = user
            self.save()
        else:
            raise Exception(f"User {user.username} cannot transition to state {state} from state {self.state}")

        return self
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
        # try:
        #     if self.master and (self.master.company != self.alloy_serial_no.master.company):
        #         raise ValidationError(
        #             {"alloy_serial_no":_("alloy should belong to same company!")}
        #         )
        # except GoldShippingFormAlloy.alloy_serial_no.RelatedObjectDoesNotExist:
        #     raise ValidationError(
        #             {"alloy_serial_no":_("هذا الحقل مطلوب!")}
        #         )
        return super().clean()
    
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=GoldProductionForm)
def update_smrc_data(sender, instance, **kwargs):
    instance.company = instance.license.company

@receiver(pre_save, sender=GoldShippingForm)
def update_smrc_data(sender, instance, **kwargs):
    instance.company = instance.license.company
