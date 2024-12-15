from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from company_profile.models import LkpState

class LoggingModel(models.Model):
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))
    
    class Meta:
        abstract = True

class LkpSoag(models.Model):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    name = models.CharField(_("name"),max_length=100)
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = _("Soag")
        verbose_name_plural = _("Soag")

class LkpJihatAlaisdar(models.Model):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    name = models.CharField(_("name"),max_length=100)
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = _("jihat_alaisdar")
        verbose_name_plural = _("jihat_alaisdar")

class GoldTravelTraditionalUser(LoggingModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="gold_travel_traditional",verbose_name=_("user"))
    name = models.CharField(_("name"),max_length=100)
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))

    def __str__(self):
        return f'{self.user} ({self.name})'

    class Meta:
        verbose_name = _("gold_travel_user")
        verbose_name_plural = _("gold_travel_users")

class GoldTravelTraditionalUserDetail(models.Model):
    master = models.ForeignKey(GoldTravelTraditionalUser, on_delete=models.PROTECT)    
    soug  = models.ForeignKey(LkpSoag, on_delete=models.PROTECT,verbose_name=_("Soag"))

    def __str__(self):
        return f'{self.master} ({self.soug})'

    class Meta:
        verbose_name = _("gold_travel_user_detail")
        verbose_name_plural = _("gold_travel_user_details")

class AppMoveGoldTraditional(LoggingModel):
    STATE_NEW = 1
    STATE_SOLD = 2
    STATE_EXPIRED = 3
    STATE_RENEW = 4
    STATE_CANCLED = 5

    STATE_CHOICES = {
        STATE_NEW: _('state_new'),
        STATE_SOLD: _('state_sold'),
        STATE_EXPIRED: _('state_expired'),
        STATE_RENEW: _('state_renew'),
        STATE_CANCLED: _('state_cancled'),
    }

    # IDENTITY_PASSPORT = 1
    # IDENTITY_PERSONAL = 2
    # IDENTITY_NATIONAL_ID = 3
    # IDENTITY_DRIVING_LICENSE = 4

    # IDENTITY_CHOICES = {
    #     IDENTITY_PASSPORT: _('identity_passport'),
    #     IDENTITY_PERSONAL: _('identity_personal'),
    #     IDENTITY_NATIONAL_ID: _('identity_national_id'),
    #     IDENTITY_DRIVING_LICENSE: _('identity_driving_license'),
    # }

    # def attachement_path(self, filename):
    #     code = self.code
    #     date = self.created_at.date()
    #     return "company_{0}/travel_traditional/travel/{1}/{2}".format(code,date, filename)    
    
    code = models.CharField(_("code"),max_length=20)
    issue_date = models.DateField(_("issue_date"))
    muharir_alaistimara = models.CharField(_("muharir_alaistimara"),max_length=150)
    almustafid_name = models.CharField(_("almustafid_name"),max_length=150)
    almustafid_phone = models.CharField(_("almustafid_phone"),max_length=30)
    # almustafid_identity_type = models.IntegerField(_("almustafid_identity_type"), choices=IDENTITY_CHOICES, default=IDENTITY_PASSPORT)
    # almustafid_identity = models.CharField(_("almustafid_identity"),max_length=50)
    # almustafid_identity_issue_date = models.DateField(_("almustafid_identity_issue_date"))
    
    jihat_alaisdar = models.ForeignKey(LkpJihatAlaisdar, on_delete=models.PROTECT,verbose_name=_("jihat_alaisdar"))
    wijhat_altarhil = models.ForeignKey(LkpSoag, on_delete=models.PROTECT,verbose_name=_("wijhat altarhil"))

    gold_weight_in_gram = models.FloatField(_("gold_weight_in_gram"))

    almushtari_name = models.CharField(_("almushtari_name"),max_length=150,null=True,blank=True)

    parent = models.OneToOneField('self', on_delete=models.PROTECT,related_name="child",verbose_name=_("parent"),null=True,blank=True)

    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_NEW)
    # attachement_file = models.FileField(_("attachement_file"),upload_to=attachement_path,null=True,blank=True)
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))

    def __str__(self):
        return f'{self.almustafid_name} ({self.code})'

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Move Gold Traditional")
        verbose_name_plural = _("Move Gold Traditional")
        indexes = [
            models.Index(fields=["code","almustafid_phone"]),
        ]
