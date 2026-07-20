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


class ChemicalViolationStateRepresentative(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="chemical_violation_representative",
        verbose_name=_("المستخدم")
    )
    name = models.CharField(_("الاسم"), max_length=100)
    state = models.ForeignKey(
        LkpState,
        on_delete=models.PROTECT,
        verbose_name=_("الولاية")
    )

    def __str__(self):
        return f'{self.name} ({self.state})'

    class Meta:
        verbose_name = _("ممثل ولاية - مخالفات كيميائية")
        verbose_name_plural = _("ممثلو الولايات - مخالفات كيميائية")


class AppChemicalMaterialsViolation(LoggingModel):

    STATE_DRAFT = 1
    STATE_SMRC = 2
    STATE_APPROVED = 3
    STATE_CANCELED = 8

    STATE_CHOICES = {
        STATE_DRAFT: _('state_draft'),
        STATE_SMRC: _('state_smrc'),
        STATE_APPROVED: _('state_approved'),
        STATE_CANCELED: _('state_canceled'),
    }

    record_state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)
    source_state = models.ForeignKey(
        LkpState,
        on_delete=models.PROTECT,
        related_name="chemical_violations",
        verbose_name=_("ولاية المصدر"),
        null=True,
        blank=True
    )

    # تفاصيل الواقعة / Incident Details
    date = models.DateField(_("التاريخ"))
    time = models.TimeField(_("الزمن"))
    city_or_village = models.CharField(_("المدينة أو القرية"), max_length=150)
    neighborhood = models.CharField(_("الحي"), max_length=150)
    house = models.CharField(_("المنزل"), max_length=150)
    location_details = models.TextField(_("احداثيات الموقع بالتفصيل"), max_length=1000)
    
    INCIDENT_TYPE_CHOICES = [
        ('inspection_tour', _('جولة تفتيش')),
        ('incoming_report', _('بلاغ وارد')),
        ('field_work', _('عمل ميداني')),
    ]
    incident_type = models.CharField(
        _("تفاصيل الواقعة"), 
        max_length=50, 
        choices=INCIDENT_TYPE_CHOICES
    )

    # بيانات القائم بالضبط / Seizing Officer Details
    officer_name = models.CharField(_("الاسم (القائم بالضبط)"), max_length=200)
    officer_job = models.CharField(_("الوظيفة (القائم بالضبط)"), max_length=150)
    officer_org = models.CharField(_("الجهة (القائم بالضبط)"), max_length=150)

    # حالة التخزين / Storage Condition
    YES_NO_CHOICES = [
        ('yes', _('نعم')),
        ('no', _('لا')),
    ]
    is_safely_stored = models.CharField(
        _("هل المواد محفوظة بطريقة آمنة؟"), 
        max_length=5, 
        choices=YES_NO_CHOICES
    )
    
    VENTILATION_CHOICES = [
        ('good', _('جيدة')),
        ('weak', _('ضعيفة')),
        ('none', _('معدومة')),
    ]
    ventilation = models.CharField(
        _("وجود تهوية"), 
        max_length=10, 
        choices=VENTILATION_CHOICES
    )
    
    has_warning_labels = models.CharField(
        _("وجود ملصقات تحذيرية"), 
        max_length=5, 
        choices=YES_NO_CHOICES
    )
    near_heat_or_flame = models.CharField(
        _("قرب المواد من مصادر حرارة أو لهب"), 
        max_length=5, 
        choices=YES_NO_CHOICES
    )

    # تقييم المخاطر / Risk Assessment
    RISK_LEVEL_CHOICES = [
        ('high', _('عالي')),
        ('medium', _('متوسط')),
        ('low', _('منخفض')),
    ]
    public_health_risk = models.CharField(
        _("خطر على الصحة العامة"), 
        max_length=10, 
        choices=RISK_LEVEL_CHOICES
    )
    fire_explosion_risk = models.CharField(
        _("خطر حريق أو انفجار"), 
        max_length=10, 
        choices=RISK_LEVEL_CHOICES
    )
    environmental_risk = models.CharField(
        _("خطر تلوث بيئي"), 
        max_length=10, 
        choices=RISK_LEVEL_CHOICES
    )

    # إجراءات أولية يجب اتباعها / Initial Procedures
    proc_secure_site = models.BooleanField(
        _("تأمين الموقع وإبعاد السكان بشريط عاكس او غيره"), 
        default=False
    )
    proc_notify_authorities = models.BooleanField(
        _("إبلاغ الجهات المختصة (الشرطة / المجلس الأعلى للبيئة / نيابة التعدين)"), 
        default=False
    )
    proc_prevent_handling = models.BooleanField(
        _("منع استخدام أو تداول المواد ووضعها تحت سيطرة شرطة التعدين"), 
        default=False
    )
    proc_notify_violations = models.BooleanField(
        _("إبلاغ إدارة المخالفات"), 
        default=False
    )
    proc_educate_owner = models.BooleanField(
        _("توعية صاحب الموقع بخطورة المواد"), 
        default=False
    )

    # أقوال صاحب الموقع / Owner Statements
    owner_statements = models.TextField(_("أقوال صاحب الموقع"), blank=True, null=True)

    # التوقيعات / Signatures
    officer_signature_name = models.CharField(_("توقيع القائم بالضبط (الاسم)"), max_length=200)
    owner_signature_name = models.CharField(_("توقيع صاحب الموقع (الاسم)"), max_length=200)

    class Meta:
        verbose_name = _("مخالفة المواد الكيميائية")
        verbose_name_plural = _("مخالفات المواد الكيميائية")

    def __str__(self):
        return f"مخالفة كيميائية - {self.date} - {self.officer_name}"


class AppChemicalMaterialsViolationItem(models.Model):
    violation = models.ForeignKey(
        AppChemicalMaterialsViolation, 
        on_delete=models.CASCADE, 
        related_name="items", 
        verbose_name=_("المخالفة")
    )
    material_name = models.CharField(_("اسم المادة"), max_length=200)
    quantity = models.CharField(_("الكمية"), max_length=100)
    condition = models.CharField(_("الحالة"), max_length=100)
    remarks = models.TextField(_("ملاحظات"), blank=True, null=True)

    class Meta:
        verbose_name = _("مادة مضبوطة")
        verbose_name_plural = _("المواد المضبوطة")

    def __str__(self):
        return self.material_name


class AppChemicalMaterialsViolationWitness(models.Model):
    violation = models.ForeignKey(
        AppChemicalMaterialsViolation, 
        on_delete=models.CASCADE, 
        related_name="witnesses", 
        verbose_name=_("المخالفة")
    )
    name = models.CharField(_("اسم الشاهد"), max_length=200)

    class Meta:
        verbose_name = _("شاهد")
        verbose_name_plural = _("الشهود")

    def __str__(self):
        return self.name


class AppChemicalMaterialsViolationAttachment(models.Model):
    ATTACHMENT_TYPE_CHOICES = [
        ('site_photo', _('صورة الموقع')),
        ('material_photo', _('صورة للمواد المضبوطة')),
        ('other_doc', _('أي مستندات أخرى')),
    ]
    violation = models.ForeignKey(
        AppChemicalMaterialsViolation,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name=_("المخالفة")
    )
    attachment_type = models.CharField(
        _("نوع المرفق"),
        max_length=50,
        choices=ATTACHMENT_TYPE_CHOICES
    )
    file = models.FileField(
        _("الملف المرفق"),
        upload_to="mokhalafat/chemical_violations/attachments/"
    )

    class Meta:
        verbose_name = _("مرفق")
        verbose_name_plural = _("المرفقات")

    def __str__(self):
        return f"{self.get_attachment_type_display()} - {self.file.name}"


