import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone




class MaintenanceUnit(models.Model):
    CODE_ELEC       = 'ELEC'
    CODE_AIR_COND   = 'AIR_COND'
    CODE_MECH       = 'MECH'
    CODE_CONST      = 'CONST'
    CODE_SAFETY     = 'SAFETY'

    CODE_CHOICES = [
        (CODE_ELEC,     _('وحدة الكهرباء')),
        (CODE_AIR_COND, _('وحدة التبريد والتكييف')),
        (CODE_MECH,     _('وحدة الميكانيكا')),
        (CODE_CONST,    _('وحدة الإنشاءات')),
        (CODE_SAFETY,   _('وحدة الأعمال الخطرة والسلامة')),
    ]

    code        = models.CharField(_('رمز الوحدة'), max_length=20, unique=True, choices=CODE_CHOICES)
    name        = models.CharField(_('اسم الوحدة'), max_length=100)
    group_name  = models.CharField(_('مجموعة المستخدمين'), max_length=100, help_text=_('اسم مجموعة Django المرتبطة'))
    icon        = models.CharField(_('أيقونة'), max_length=50, default='🔧', blank=True)
    requires_safety_permit = models.BooleanField(_('يتطلب تصريح سلامة مهنية'), default=False)

    class Meta:
        verbose_name        = _('وحدة الصيانة')
        verbose_name_plural = _('وحدات الصيانة')
        ordering            = ['code']

    def __str__(self):
        return self.name


class FaultCategory(models.Model):
    unit        = models.ForeignKey(MaintenanceUnit, on_delete=models.PROTECT,
                                    related_name='fault_categories', verbose_name=_('الوحدة'))
    sub_category = models.CharField(_('التصنيف الفرعي'), max_length=100, blank=True,
                                     help_text=_('مثال: سباكة، حدادة، نجارة...'))
    name        = models.CharField(_('اسم العطل'), max_length=150)
    is_active   = models.BooleanField(_('فعّال'), default=True)
    order       = models.PositiveIntegerField(_('الترتيب'), default=0)
    requires_safety_permit = models.BooleanField(_('يتطلب تصريح سلامة مهنية'), default=False)

    class Meta:
        verbose_name        = _('تصنيف العطل')
        verbose_name_plural = _('تصنيفات الأعطال')
        ordering            = ['unit', 'order', 'name']

    def __str__(self):
        return f"{self.unit.name} — {self.name}"

class Floor(models.Model):
    name  = models.CharField(_('اسم الطابق'), max_length=100)
    order = models.PositiveIntegerField(_('الترتيب'), default=0)

    class Meta:
        verbose_name        = _('الطابق')
        verbose_name_plural = _('الطوابق')
        ordering            = ['order', 'name']

    def __str__(self):
        return self.name


class Apartment(models.Model):
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='apartments', verbose_name=_('الطابق'))
    name  = models.CharField(_('اسم/رقم الشقة'), max_length=100)

    class Meta:
        verbose_name        = _('الشقة')
        verbose_name_plural = _('الشقق')
        ordering            = ['floor', 'name']

    def __str__(self):
        return f"{self.floor.name} — {self.name}"


class TechnicalTechnician(models.Model):
    name      = models.CharField(_('اسم الفني التقني'), max_length=150)
    phone     = models.CharField(_('رقم الهاتف'), max_length=30)
    unit      = models.ForeignKey(MaintenanceUnit, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='technical_technicians', verbose_name=_('الوحدة المختصة'))
    specialty = models.CharField(_('التخصص/الملاحظات'), max_length=150, blank=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإضافة'), auto_now_add=True)

    class Meta:
        verbose_name        = _('فني تقني')
        verbose_name_plural = _('الفنيون التقنيون')
        ordering            = ['unit', 'name']

    def __str__(self):
        unit_str = f" [{self.unit.name}]" if self.unit else ""
        return f"{self.name} ({self.phone}){unit_str}"


class MaintenanceRequest(models.Model):
    STATUS_PENDING        = 'pending'
    STATUS_RECEIVED       = 'received'
    STATUS_PENDING_SAFETY = 'pending_safety'
    STATUS_IN_PROGRESS    = 'in_progress'
    STATUS_COMPLETED      = 'completed'
    STATUS_CANCELLED      = 'cancelled'
    STATUS_REJECTED       = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING,        _('قيد الانتظار')),
        (STATUS_RECEIVED,       _('تم الاستلام')),
        (STATUS_PENDING_SAFETY, _('بانتظار تصريح السلامة')),
        (STATUS_IN_PROGRESS,    _('قيد التنفيذ')),
        (STATUS_COMPLETED,      _('مكتمل')),
        (STATUS_CANCELLED,      _('ملغى')),
        (STATUS_REJECTED,       _('مرفوض')),
    ]

    PRIORITY_LOW    = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH   = 'high'
    PRIORITY_URGENT = 'urgent'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW,    _('منخفضة')),
        (PRIORITY_MEDIUM, _('متوسطة')),
        (PRIORITY_HIGH,   _('عالية')),
        (PRIORITY_URGENT, _('عاجل')),
    ]

    request_number      = models.CharField(_('رقم الطلب'), max_length=20, unique=True, editable=False)

    requester           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                            related_name='maintenance_requests', verbose_name=_('المستخدم'))
    try:
        from hr.models import EmployeeBasic
        employee            = models.ForeignKey('hr.EmployeeBasic', on_delete=models.SET_NULL,
                                                null=True, blank=True, related_name='maintenance_requests',
                                                verbose_name=_('سجل الموظف'))
    except Exception:
        pass

    employee_name       = models.CharField(_('اسم الموظف'), max_length=150)
    general_dept        = models.CharField(_('الإدارة العامة'), max_length=150)
    department          = models.CharField(_('القسم'), max_length=150)

    floor               = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='requests', verbose_name=_('الطابق'))
    apartment           = models.ForeignKey(Apartment, on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='requests', verbose_name=_('الشقة'))
    location            = models.CharField(_('موقع العطل بالضبط'), max_length=250)

    fault_category      = models.ForeignKey(FaultCategory, on_delete=models.PROTECT,
                                            related_name='requests', verbose_name=_('نوع العطل'))
    fault_description   = models.TextField(_('وصف إضافي للمشكلة'), blank=False)

    assigned_unit       = models.ForeignKey(MaintenanceUnit, on_delete=models.PROTECT,
                                            related_name='assigned_requests',
                                            verbose_name=_('الوحدة المختصة'), null=True, blank=True)
    assigned_technician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                            null=True, blank=True, related_name='assigned_requests',
                                            verbose_name=_('الفني المختص'))

    assigned_technical_technicians = models.ManyToManyField(TechnicalTechnician, blank=True,
                                                             related_name='requests',
                                                             verbose_name=_('الفنيون التقنيون المشاركون'))

    requires_safety_permit = models.BooleanField(_('يتطلب تصريح سلامة مهنية'), default=False)

    status              = models.CharField(_('حالة الطلب'), max_length=20,
                                           choices=STATUS_CHOICES, default=STATUS_PENDING)
    priority            = models.CharField(_('الأولوية'), max_length=10,
                                           choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)

    delay_reason        = models.TextField(_('سبب التأخير'), blank=True)
    rejection_reason    = models.TextField(_('سبب الرفض/الاعتذار'), blank=True)
    admin_notes         = models.TextField(_('ملاحظات المدير'), blank=True)

    created_at          = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at          = models.DateTimeField(_('آخر تحديث'), auto_now=True)
    completed_at        = models.DateTimeField(_('تاريخ الإكمال'), null=True, blank=True)

    class Meta:
        verbose_name        = _('طلب صيانة')
        verbose_name_plural = _('طلبات الصيانة')
        ordering            = ['-created_at']
        permissions         = [
            ('can_manage_all_requests', _('يمكنه إدارة جميع الطلبات')),
            ('can_view_unit_requests',  _('يمكنه عرض طلبات الوحدة')),
            ('can_manage_safety_permits', _('يمكنه إدارة وتصديق تصاريح السلامة')),
        ]

    def __str__(self):
        return f"{self.request_number} — {self.employee_name}"

    def save(self, *args, **kwargs):
        if not self.request_number:
            year = timezone.now().year
            last = MaintenanceRequest.objects.filter(
                request_number__startswith=f'MR-{year}-'
            ).order_by('request_number').last()
            if last:
                last_num = int(last.request_number.split('-')[-1])
            else:
                last_num = 0
            self.request_number = f'MR-{year}-{last_num + 1:04d}'

        if self.fault_category_id and not self.assigned_unit_id:
            self.assigned_unit = self.fault_category.unit

        if not self.requires_safety_permit:
            if (self.fault_category_id and self.fault_category.requires_safety_permit) or \
               (self.assigned_unit_id and self.assigned_unit.requires_safety_permit):
                self.requires_safety_permit = True

        super().save(*args, **kwargs)

    def get_status_badge_class(self):
        mapping = {
            self.STATUS_PENDING:        'badge-warning',
            self.STATUS_RECEIVED:       'badge-info',
            self.STATUS_PENDING_SAFETY: 'badge-secondary',
            self.STATUS_IN_PROGRESS:    'badge-primary',
            self.STATUS_COMPLETED:      'badge-success',
            self.STATUS_CANCELLED:      'badge-error',
            self.STATUS_REJECTED:       'badge-error',
        }
        return mapping.get(self.status, 'badge-ghost')

class CompletionReport(models.Model):
    request             = models.OneToOneField(MaintenanceRequest, on_delete=models.CASCADE,
                                               related_name='completion_report',
                                               verbose_name=_('طلب الصيانة'))
    technician          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                            verbose_name=_('الفني'))
    work_done           = models.TextField(_('العمل المنجز'))
    root_cause          = models.TextField(_('السبب الجذري للعطل'), blank=True)
    recommendations     = models.TextField(_('التوصيات'), blank=True)
    completed_at        = models.DateTimeField(_('تاريخ الإنجاز'), auto_now_add=True)

    class Meta:
        verbose_name        = _('تقرير إنجاز')
        verbose_name_plural = _('تقارير الإنجاز')

    def __str__(self):
        return f"تقرير: {self.request.request_number}"

class SafetyPermit(models.Model):
    STATUS_DRAFT            = 'draft'
    STATUS_PENDING_SAFETY   = 'pending_safety'
    STATUS_APPROVED         = 'approved'
    STATUS_REJECTED         = 'rejected'
    STATUS_CLOSED           = 'closed'

    STATUS_CHOICES = [
        (STATUS_DRAFT,          _('مسودة')),
        (STATUS_PENDING_SAFETY, _('بانتظار موافقة السلامة')),
        (STATUS_APPROVED,       _('معتمد من السلامة')),
        (STATUS_REJECTED,       _('مرفوض')),
        (STATUS_CLOSED,         _('مغلق من السلامة')),
    ]

    request                 = models.OneToOneField(MaintenanceRequest, on_delete=models.CASCADE,
                                                   related_name='safety_permit',
                                                   verbose_name=_('طلب الصيانة المرتبط'))
    work_description        = models.TextField(_('وصف العمل'))
    start_time              = models.DateTimeField(_('زمن بداية العمل'))
    end_time                = models.DateTimeField(_('زمن انتهاء العمل'))
    permit_duration         = models.CharField(_('مدة التصريح'), max_length=100, blank=True,
                                               help_text=_('تُحدد وتُدخل من قبل موظف قسم السلامة'))
    responsible_person      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                                null=True, blank=True,
                                                related_name='safety_permits_responsible',
                                                verbose_name=_('الشخص المسؤول عن العمل'))
    responsible_person_name = models.CharField(_('اسم المسؤول عن العمل'), max_length=150)
    responsible_person_job  = models.CharField(_('الوظيفة'), max_length=150)
    assigned_technicians    = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                                     related_name='safety_permits_assigned',
                                                     verbose_name=_('الفنيون المكلفون/المشاركون بالعمل'))


    hazardous_activities    = models.JSONField(_('الأنشطة الخطرة'), default=list, blank=True)
    hazardous_activities_other = models.CharField(_('أنشطة خطرة أخرى'), max_length=250, blank=True)

    control_measures        = models.TextField(_('طرق التحكم والوقاية الموجودة'), blank=True)

    site_preparations       = models.JSONField(_('تجهيزات المكان'), default=list, blank=True)
    site_preparations_other = models.CharField(_('تجهيزات مكان أخرى'), max_length=250, blank=True)

    ppe_equipment           = models.JSONField(_('مهمات ومعدات الحماية الشخصية (PPE)'), default=list, blank=True)

    status                  = models.CharField(_('حالة التصريح'), max_length=20,
                                               choices=STATUS_CHOICES, default=STATUS_PENDING_SAFETY)
    safety_officer          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                                null=True, blank=True,
                                                related_name='approved_safety_permits',
                                                verbose_name=_('موظف السلامة المعتمد'))
    safety_notes            = models.TextField(_('توصيات وملاحظات السلامة'), blank=True)

    created_at              = models.DateTimeField(_('تاريخ إنشاء التصريح'), auto_now_add=True)
    approved_at             = models.DateTimeField(_('تاريخ موافقة السلامة'), null=True, blank=True)
    closed_at               = models.DateTimeField(_('تاريخ إغلاق التصريح'), null=True, blank=True)

    class Meta:
        verbose_name        = _('تصريح سلامة مهنية')
        verbose_name_plural = _('تصاريح السلامة المهنية')
        ordering            = ['-created_at']

    def __str__(self):
        return f"تصريح سلامة: {self.request.request_number} [{self.get_status_display()}]"



class ServiceRating(models.Model):
    RATING_CHOICES = [(i, '★' * i) for i in range(1, 6)]

    request             = models.OneToOneField(MaintenanceRequest, on_delete=models.CASCADE,
                                               related_name='rating', verbose_name=_('طلب الصيانة'))
    rating              = models.PositiveSmallIntegerField(_('التقييم'), choices=RATING_CHOICES)
    comment             = models.TextField(_('تعليق'), blank=True)
    created_at          = models.DateTimeField(_('تاريخ التقييم'), auto_now_add=True)

    class Meta:
        verbose_name        = _('تقييم الخدمة')
        verbose_name_plural = _('تقييمات الخدمة')

    def __str__(self):
        return f"تقييم {self.request.request_number}: {self.rating}★"

class SparePart(models.Model):
    sku                 = models.CharField(_('كود القطعة (SKU)'), max_length=50, unique=True)
    name                = models.CharField(_('اسم القطعة'), max_length=200)
    unit                = models.ForeignKey(MaintenanceUnit, on_delete=models.PROTECT,
                                            related_name='spare_parts', verbose_name=_('الوحدة المختصة'))
    description         = models.TextField(_('وصف القطعة'), blank=True)
    unit_of_measure     = models.CharField(_('وحدة القياس'), max_length=30,
                                           default='قطعة',
                                           help_text=_('مثال: قطعة، متر، لتر، كيلو'))
    quantity_in_stock   = models.IntegerField(_('الرصيد الحالي'), default=0)
    reorder_point       = models.IntegerField(_('حد إعادة الطلب (حد الأمان)'), default=5,
                                              help_text=_('يُرسل تنبيه عند الوصول لهذا الحد'))
    is_active           = models.BooleanField(_('فعّال'), default=True)
    created_at          = models.DateTimeField(_('تاريخ الإضافة'), auto_now_add=True)
    updated_at          = models.DateTimeField(_('آخر تحديث'), auto_now=True)

    class Meta:
        verbose_name        = _('قطعة غيار')
        verbose_name_plural = _('قطع الغيار')
        ordering            = ['unit', 'name']

    def __str__(self):
        return f"[{self.sku}] {self.name}"

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_point

    @property
    def stock_status_class(self):
        if self.quantity_in_stock <= 0:
            return 'badge-error'
        elif self.is_low_stock:
            return 'badge-warning'
        return 'badge-success'


class StockMovement(models.Model):
    MOVEMENT_IN     = 'in'
    MOVEMENT_OUT    = 'out'
    MOVEMENT_ADJUST = 'adjust'

    MOVEMENT_TYPE_CHOICES = [
        (MOVEMENT_IN,     _('وارد (شراء/استلام)')),
        (MOVEMENT_OUT,    _('صادر (استهلاك في صيانة)')),
        (MOVEMENT_ADJUST, _('تعديل جرد')),
    ]

    spare_part          = models.ForeignKey(SparePart, on_delete=models.PROTECT,
                                            related_name='movements', verbose_name=_('القطعة'))
    movement_type       = models.CharField(_('نوع الحركة'), max_length=10,
                                           choices=MOVEMENT_TYPE_CHOICES)
    quantity            = models.PositiveIntegerField(_('الكمية'))
    maintenance_request = models.ForeignKey(MaintenanceRequest, on_delete=models.SET_NULL,
                                            null=True, blank=True,
                                            related_name='spare_parts_used',
                                            verbose_name=_('طلب الصيانة المرتبط'))
    performed_by        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                            verbose_name=_('منفذ العملية'))
    notes               = models.TextField(_('ملاحظات'), blank=True)
    created_at          = models.DateTimeField(_('تاريخ الحركة'), auto_now_add=True)

    class Meta:
        verbose_name        = _('حركة مخزون')
        verbose_name_plural = _('حركات المخزون')
        ordering            = ['-created_at']

    def __str__(self):
        sign = '+' if self.movement_type == self.MOVEMENT_IN else '-'
        return f"{sign}{self.quantity} × {self.spare_part.name}"

class LowStockAlert(models.Model):
    spare_part          = models.ForeignKey(SparePart, on_delete=models.CASCADE,
                                            related_name='alerts', verbose_name=_('القطعة'))
    quantity_at_alert   = models.IntegerField(_('الرصيد وقت التنبيه'))
    is_resolved         = models.BooleanField(_('تمت معالجته'), default=False)
    resolved_at         = models.DateTimeField(_('تاريخ المعالجة'), null=True, blank=True)
    created_at          = models.DateTimeField(_('تاريخ التنبيه'), auto_now_add=True)

    class Meta:
        verbose_name        = _('تنبيه مخزون منخفض')
        verbose_name_plural = _('تنبيهات المخزون المنخفض')
        ordering            = ['-created_at']

    def __str__(self):
        return f"تنبيه: {self.spare_part.name} (رصيد: {self.quantity_at_alert})"


class Notification(models.Model):
    TYPE_REQUEST_CREATED    = 'request_created'
    TYPE_REQUEST_UPDATED    = 'request_updated'
    TYPE_REQUEST_COMPLETED  = 'request_completed'
    TYPE_LOW_STOCK          = 'low_stock'

    TYPE_CHOICES = [
        (TYPE_REQUEST_CREATED,   _('طلب صيانة جديد')),
        (TYPE_REQUEST_UPDATED,   _('تحديث طلب صيانة')),
        (TYPE_REQUEST_COMPLETED, _('إغلاق طلب صيانة')),
        (TYPE_LOW_STOCK,         _('تنبيه مخزون منخفض')),
    ]

    recipient           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                            related_name='maintenance_notifications',
                                            verbose_name=_('المستلم'))
    notification_type   = models.CharField(_('نوع الإشعار'), max_length=30, choices=TYPE_CHOICES)
    title               = models.CharField(_('العنوان'), max_length=200)
    message             = models.TextField(_('نص الإشعار'))
    is_read             = models.BooleanField(_('مقروء'), default=False)
    related_request     = models.ForeignKey(MaintenanceRequest, on_delete=models.SET_NULL,
                                            null=True, blank=True,
                                            related_name='notifications',
                                            verbose_name=_('الطلب المرتبط'))
    created_at          = models.DateTimeField(_('التاريخ'), auto_now_add=True)

    class Meta:
        verbose_name        = _('إشعار')
        verbose_name_plural = _('الإشعارات')
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.recipient} — {self.title}"
