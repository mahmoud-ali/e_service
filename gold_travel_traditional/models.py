import io

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from PIL import Image

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
    JIHAT_ALAISDAR = 1
    JIHAT_TARHIL = 2
    BOTH = 3
    STATE_MANAGER = 4
    STATE_VIEWER = 5

    USER_TYPE_CHOICES = {
        JIHAT_ALAISDAR: _('جهة الإصدار'),
        JIHAT_TARHIL: _('جهة الوصول'),
        BOTH: _('جهة الإصدار والوصول'),
        STATE_MANAGER: _('مدير الولاية'),
        STATE_VIEWER: _('مشاهد الولاية'),
    }

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="gold_travel_traditional",verbose_name=_("user"))
    name = models.CharField(_("name"),max_length=100)
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    user_type = models.IntegerField(_('user_type'), choices=USER_TYPE_CHOICES, default=JIHAT_ALAISDAR)

    def __str__(self):
        return f'{self.user} ({self.name})'

    @property
    def is_alaisdar_user(self):
        return self.user_type in [self.JIHAT_ALAISDAR, self.BOTH]

    @property
    def is_tarhil_user(self):
        return self.user_type in [self.JIHAT_TARHIL, self.BOTH]

    @property
    def is_state_manager(self):
        return self.user_type == self.STATE_MANAGER

    @property
    def is_state_viewer(self):
        return self.user_type == self.STATE_VIEWER

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
    STATE_EXPIRED = 3
    STATE_RENEW = 4
    STATE_CANCLED = 5
    STATE_ARRIVED = 6

    STATE_CHOICES = {
        STATE_NEW: _('state_new'),
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
    almustafid_identity_attachement = models.ImageField(_("مرفق الإثبات"),upload_to=attachement_path)
    # almustafid_identity_issue_date = models.DateField(_("تاريخ إصدار الإثبات"))
    
    jihat_alaisdar = models.ForeignKey(LkpJihatAlaisdar, on_delete=models.PROTECT,verbose_name=_("جهة الإصدار"))
    wijhat_altarhil = models.ForeignKey(LkpJihatAltarhil, on_delete=models.PROTECT,verbose_name=_("جهة الوصول"))

    # gold_weight_in_gram = models.FloatField(_("gold_weight_in_gram"))

    almushtari_name = models.CharField(_("almushtari_name"),max_length=150,null=True,blank=True)

    melt_workshop = models.CharField(_("ورشة الصهر"), max_length=150, null=True, blank=True)
    standardization_lab = models.CharField(_("مختبر المعايرة"), max_length=150, null=True, blank=True)
    melt_date = models.DateField(_("تاريخ الصهر"), null=True, blank=True)
    melt_batch = models.ForeignKey('MeltBatch', on_delete=models.SET_NULL, null=True, blank=True, related_name='records', verbose_name=_('دفعة الصهر'))
    sale = models.ForeignKey('Sale', on_delete=models.SET_NULL, null=True, blank=True, related_name='records', verbose_name=_('فاتورة البيع'))

    parent = models.OneToOneField('self', on_delete=models.PROTECT,related_name="child",verbose_name=_("parent"),null=True,blank=True)

    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_NEW)
    attachement_file = models.ImageField(_("صورة الذهب المرحل"),upload_to=attachement_path)
    renew_date = models.DateField(_("renew_date"), null=True, blank=True, editable=False)
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))

    MAX_IMAGE_DIMENSION = 1200
    JPEG_QUALITY = 85

    def clean(self):
        super().clean()
        if self.pk:
            original = AppMoveGoldTraditional.objects.get(pk=self.pk)
            if original.state not in [self.STATE_NEW, self.STATE_ARRIVED]:
                from django.core.exceptions import ValidationError
                raise ValidationError(_("Record cannot be modified in its current state."))

    def _optimize_image(self, image_field):
        """Resize and compress an uploaded image to reduce file size."""
        img_file = getattr(self, image_field)
        if not img_file:
            return

        img = Image.open(img_file)

        # Convert RGBA to RGB for JPEG compatibility
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Resize if larger than max dimension, preserving aspect ratio
        w, h = img.size
        if w > self.MAX_IMAGE_DIMENSION or h > self.MAX_IMAGE_DIMENSION:
            img.thumbnail((self.MAX_IMAGE_DIMENSION, self.MAX_IMAGE_DIMENSION), Image.LANCZOS)

        # Save optimized image to an in-memory buffer
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=self.JPEG_QUALITY, optimize=True)
        output.seek(0)

        # Replace the file content
        img_file.file = output
        img_file.name = img_file.name.rsplit('.', 1)[0] + '.jpg'

    def save(self, *args, **kwargs):
        self._optimize_image('attachement_file')
        self._optimize_image('almustafid_identity_attachement')

        if not self.code:
            import datetime
            from django.db import transaction, IntegrityError
            
            # Get user state code if possible
            prefix = "G"
            try:
                # We expect created_by to be set before save or via current request
                # However, since save() doesn't always have access to request, 
                # we rely on source_state being set in admin's save_model
                if self.source_state and self.source_state.code:
                    prefix = self.source_state.code
            except:
                pass

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

    @property
    def alloy_count(self):
        return self.details.count()

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
    SHAPE_OTHER = 3
    
    SHAPE_CHOICES = {
        SHAPE_CIRCULAR: _('دائري'),
        SHAPE_RECTANGULAR: _('مستطيل'),
        SHAPE_OTHER: _('أخرى'),
    }

    master = models.ForeignKey(AppMoveGoldTraditional, on_delete=models.CASCADE, related_name="details", verbose_name=_("master"))
    alloy_weight_gram = models.FloatField(_("وزن السبيكة بالجرام"))
    alloy_shape = models.IntegerField(_("شكل السبيكة"), choices=SHAPE_CHOICES)

    def __str__(self):
        return f'{self.master} - {self.alloy_weight_gram}g'

    class Meta:
        verbose_name = _("تفاصيل السبيكة")
        verbose_name_plural = _("تفاصيل السبائك")

class MeltBatch(LoggingModel):
    STATE_PENDING = 1
    STATE_COMPLETE = 2

    STATE_CHOICES = {
        STATE_PENDING: _('قيد الصهر'),
        STATE_COMPLETE: _('مكتمل'),
    }

    code = models.CharField(_('code'), max_length=20, unique=True)
    melt_date = models.DateField(_('تاريخ الصهر'))
    melt_workshop = models.CharField(_('ورشة الصهر'), max_length=150)
    standardization_lab = models.CharField(_('مختبر المعايرة'), max_length=150)
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_('state'))
    state = models.IntegerField(_('record_state'), choices=STATE_CHOICES, default=STATE_PENDING)

    @property
    def total_weight(self):
        return self.records.aggregate(
            total=models.Sum('details__alloy_weight_gram')
        )['total'] or 0.0

    @property
    def total_alloy_count(self):
        return sum(r.details.count() for r in self.records.all())

    @property
    def record_count(self):
        return self.records.count()

    def save(self, *args, **kwargs):
        if not self.code:
            import datetime
            from django.db import transaction, IntegrityError
            prefix = "MB"
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            for attempt in range(5):
                try:
                    with transaction.atomic():
                        last = MeltBatch.objects.select_for_update().filter(
                            code__startswith=f"{prefix}-{date_str}-"
                        ).order_by('code').last()
                        if last:
                            new_num = int(last.code.split('-')[-1]) + 1
                        else:
                            new_num = 1
                        new_num += attempt
                        self.code = f"{prefix}-{date_str}-{new_num:04d}"
                        super().save(*args, **kwargs)
                        return
                except IntegrityError:
                    if attempt == 4:
                        raise
                    continue
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.code} - {self.melt_workshop}'

    class Meta:
        ordering = ["-id"]
        verbose_name = _('استمارة تسييح ومعاييرة')
        verbose_name_plural = _('استمارات تسييح ومعاييرة')

class Sale(LoggingModel):
    STATE_PENDING = 1
    STATE_COMPLETE = 2

    STATE_CHOICES = {
        STATE_PENDING: _('قيد البيع'),
        STATE_COMPLETE: _('مكتمل'),
    }

    code = models.CharField(_('code'), max_length=20, unique=True)
    sale_date = models.DateField(_('تاريخ البيع'))
    buyer = models.ForeignKey('gold_travel.LkpOwner', on_delete=models.PROTECT, verbose_name=_('المشتري'))
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_('state'))
    state = models.IntegerField(_('state'), choices=STATE_CHOICES, default=STATE_PENDING)

    @property
    def total_weight(self):
        return self.records.aggregate(
            total=models.Sum('details__alloy_weight_gram')
        )['total'] or 0.0

    @property
    def total_alloy_count(self):
        return sum(r.details.count() for r in self.records.all())

    @property
    def record_count(self):
        return self.records.count()

    def save(self, *args, **kwargs):
        if not self.code:
            import datetime
            from django.db import transaction, IntegrityError
            prefix = "S"
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            for attempt in range(5):
                try:
                    with transaction.atomic():
                        last = Sale.objects.select_for_update().filter(
                            code__startswith=f"{prefix}-{date_str}-"
                        ).order_by('code').last()
                        if last:
                            new_num = int(last.code.split('-')[-1]) + 1
                        else:
                            new_num = 1
                        new_num += attempt
                        self.code = f"{prefix}-{date_str}-{new_num:04d}"
                        super().save(*args, **kwargs)
                        return
                except IntegrityError:
                    if attempt == 4:
                        raise
                    continue
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.code} - {self.buyer}'

    class Meta:
        ordering = ["-id"]
        verbose_name = _('استمارة بيع')
        verbose_name_plural = _('استمارات البيع')
