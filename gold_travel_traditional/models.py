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

class LkpJihatAltarhil(models.Model):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    name = models.CharField(_("name"),max_length=100)
    
    def __str__(self):
        return f"{self.name} ({self.state})"
        
    class Meta:
        verbose_name = _("جهة الوصول")
        verbose_name_plural = _("جهات الوصول")

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

class GoldTravelTraditionalUserJihatAlaisdar(models.Model):
    master = models.ForeignKey(GoldTravelTraditionalUser, on_delete=models.CASCADE)    
    jihat_alaisdar  = models.ForeignKey(LkpJihatAlaisdar, on_delete=models.PROTECT,verbose_name=_("جهة الإصدار"))

    def __str__(self):
        return f'{self.master.user.username} - {self.jihat_alaisdar.name}'

    class Meta:
        verbose_name = _("جهة الإصدار المعتمدة للمستخدم")
        verbose_name_plural = _("جهات الإصدار المعتمدة للمستخدمين")

class GoldTravelTraditionalUserJihatTarhil(models.Model):
    master = models.ForeignKey(GoldTravelTraditionalUser, on_delete=models.CASCADE)    
    wijhat_altarhil  = models.ForeignKey(LkpJihatAltarhil, on_delete=models.PROTECT,verbose_name=_("جهة الوصول"))

    def __str__(self):
        return f'{self.master.user.username} - {self.wijhat_altarhil.name}'

    class Meta:
        verbose_name = _("جهة الوصول المعتمدة للمستخدم")
        verbose_name_plural = _("جهات الوصول المعتمدة للمستخدمين")


class AppMoveGoldTraditional(LoggingModel):
    STATE_NEW = 1
    STATE_SOLD = 2
    STATE_EXPIRED = 3
    STATE_RENEW = 4
    STATE_CANCLED = 5
    STATE_ARRIVED = 6

    STATE_CHOICES = {
        STATE_NEW: _('state_new'),
        STATE_SOLD: _('state_sold'),
        STATE_EXPIRED: _('state_expired'),
        STATE_RENEW: _('state_renew'),
        STATE_CANCLED: _('state_cancled'),
        STATE_ARRIVED: _('وصل للوجهة'),
    }

    IDENTITY_PASSPORT = 1
    IDENTITY_PERSONAL = 2
    IDENTITY_NATIONAL_ID = 3
    IDENTITY_DRIVING_LICENSE = 4

    IDENTITY_CHOICES = {
        IDENTITY_PASSPORT: _('identity_passport'),
        IDENTITY_PERSONAL: _('identity_personal'),
        IDENTITY_NATIONAL_ID: _('identity_national_id'),
        IDENTITY_DRIVING_LICENSE: _('identity_driving_license'),
    }

    def attachement_path(self, filename):
        code = self.code
        date = self.created_at.date()
        return "company_{0}/travel_traditional/travel/{1}/{2}".format(code,date, filename)    
    
    code = models.CharField(_("code"),max_length=20, unique=True)
    issue_date = models.DateField(_("issue_date"))
    # muharir_alaistimara = models.CharField(_("muharir_alaistimara"),max_length=150)
    almustafid_name = models.CharField(_("almustafid_name"),max_length=150)
    almustafid_phone = models.CharField(_("almustafid_phone"),max_length=30)
    almustafid_identity_type = models.IntegerField(_("نوع الإثبات"), choices=IDENTITY_CHOICES, default=IDENTITY_PASSPORT)
    almustafid_identity = models.CharField(_("رقم الإثبات"),max_length=50)
    # almustafid_identity_issue_date = models.DateField(_("تاريخ إصدار الإثبات"))
    
    jihat_alaisdar = models.ForeignKey(LkpJihatAlaisdar, on_delete=models.PROTECT,verbose_name=_("جهة الإصدار"))
    wijhat_altarhil = models.ForeignKey(LkpJihatAltarhil, on_delete=models.PROTECT,verbose_name=_("جهة الوصول"))

    # gold_weight_in_gram = models.FloatField(_("gold_weight_in_gram"))

    almushtari_name = models.CharField(_("almushtari_name"),max_length=150,null=True,blank=True)

    parent = models.OneToOneField('self', on_delete=models.PROTECT,related_name="child",verbose_name=_("parent"),null=True,blank=True)

    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_NEW)
    attachement_file = models.FileField(_("attachement_file"),upload_to=attachement_path,null=True,blank=True)
    # attachement_file = models.ImageField(_("attachement_file"),upload_to ='gold_travel_traditional/',null=True,blank=True) 
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))

    def clean(self):
        super().clean()
        if self.pk:
            # Re-fetch the original object from DB to check current state
            original = AppMoveGoldTraditional.objects.get(pk=self.pk)
            if original.state != self.STATE_NEW:
                from django.core.exceptions import ValidationError
                raise ValidationError(_("Record cannot be modified unless its state is 'New'."))

    def save(self, *args, **kwargs):
        if not self.code:
            import datetime
            from django.db import transaction, IntegrityError
            
            prefix = "G"
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            
            for attempt in range(5):
                try:
                    with transaction.atomic():
                        # Lock the table for today's records
                        last_instance = AppMoveGoldTraditional.objects.select_for_update().filter(
                            code__startswith=f"{prefix}-{date_str}-"
                        ).order_by('code').last()
                        
                        if last_instance:
                            try:
                                last_num = int(last_instance.code.split('-')[-1])
                                new_num = last_num + 1
                            except (ValueError, IndexError):
                                new_num = 1
                        else:
                            new_num = 1
                        
                        # Apply offset based on attempt to find a free slot
                        new_num += attempt
                            
                        self.code = f"{prefix}-{date_str}-{new_num:04d}"
                        super().save(*args, **kwargs)
                        return # Success
                except IntegrityError:
                    if attempt == 4:
                        raise
                    continue
        else:
            super().save(*args, **kwargs)

    @property
    def gold_weight_in_gram(self):
        return self.details.aggregate(total=models.Sum('alloy_weight_gram'))['total'] or 0.0

    def __str__(self):
        return f'{self.almustafid_name} ({self.code})'

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Move Gold Traditional")
        verbose_name_plural = _("Move Gold Traditional")
        indexes = [
            models.Index(fields=["code","almustafid_phone"]),
        ]

class AppMoveGoldTraditionalDetail(models.Model):
    SHAPE_CIRCULAR = 1
    SHAPE_RECTANGULAR = 2
    
    SHAPE_CHOICES = {
        SHAPE_CIRCULAR: _('دائري'),
        SHAPE_RECTANGULAR: _('مستطيل'),
    }

    master = models.ForeignKey(AppMoveGoldTraditional, on_delete=models.CASCADE, related_name="details", verbose_name=_("master"))
    alloy_weight_gram = models.FloatField(_("وزن السبيكة بالجرام"))
    alloy_shape = models.IntegerField(_("شكل السبيكة"), choices=SHAPE_CHOICES)

    def __str__(self):
        return f'{self.master} - {self.alloy_weight_gram}g'

    class Meta:
        verbose_name = _("تفاصيل السبيكة")
        verbose_name_plural = _("تفاصيل السبائك")
