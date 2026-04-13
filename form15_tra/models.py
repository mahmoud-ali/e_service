from tabnanny import verbose
from django.conf import settings
from django.db import models
from django.db.models import Index
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from typing import Any
from django.db import transaction
from django.utils import timezone
import os

from cryptography.fernet import Fernet, InvalidToken

from company_profile.models import LkpState #, LkpLocality

PRICE_PER_SACK = getattr(settings, "PRICE_PER_SACK", 25000)

class Market(models.Model):
    """
    Represents a market where revenue is collected.
    """
    market_name = models.CharField(verbose_name="اسم السوق", max_length=255)
    location = models.CharField(verbose_name="الموقع", max_length=255)
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name="الولاية",null=True,blank=True)
    # locality = models.ForeignKey(LkpLocality, on_delete=models.PROTECT, verbose_name="المحلية",null=True,blank=True)

    def __str__(self) -> str:
        return self.market_name

    class Meta:
        verbose_name = "سوق"
        verbose_name_plural = "الأسواق"

class CollectorAssignment(models.Model):
    """
    Assigns a collector to a specific market.
    One collector belongs to one market. A market has many collectors.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="المستخدم",
        on_delete=models.CASCADE,
        related_name='assignment'
    )
    market = models.ForeignKey(
        Market,
        verbose_name="السوق",
        on_delete=models.CASCADE,
        related_name='collectors'
    )
    is_collector = models.BooleanField(
        verbose_name="متحصل",
        default=False,
        help_text="يسمح للمستخدم بإنشاء وتأكيد إيصالات التحصيل."
    )
    is_senior_collector = models.BooleanField(
        verbose_name="كبير متحصل",
        default=False,
        help_text="يسمح للمستخدم بإلغاء إيصالات التحصيل."
    )

    is_observer = models.BooleanField(
        verbose_name="مراقب",
        default=False,
        help_text="يسمح للمستخدم بإنشاء إيصالات مسودة فقط."
    )

    # Esali credentials (used by the TRA invoice daemon).
    # Stored encrypted at rest; the daemon will decrypt locally using ESALI_FERNET_KEY.
    esali_username = models.CharField(verbose_name="مستخدم ايصالي", max_length=128, blank=True, default="")
    esali_password_enc = models.TextField(verbose_name="كلمة المرور المشفرة لمستخدم ايصالي", blank=True, default="")
    esali_service_id = models.CharField(verbose_name="رقم الخدمة", max_length=64, blank=True, default="")

    class Meta:
        verbose_name = "تكليف متحصل"
        verbose_name_plural = "تكليف المتحصلين"

    def __str__(self) -> str:
        return f"{self.user.get_full_name() or self.user.username} -> {self.market.market_name}"

    @staticmethod
    def _get_fernet() -> Fernet:
        key = getattr(settings, "ESALI_FERNET_KEY", None) or os.getenv("ESALI_FERNET_KEY", "")
        key = str(key).strip()
        if key == "":
            raise ValidationError("ESALI_FERNET_KEY is not configured.")
        try:
            return Fernet(key.encode("utf-8"))
        except Exception as exc:
            raise ValidationError(f"Invalid ESALI_FERNET_KEY: {exc}")

    def set_esali_password_plain(self, password: str) -> None:
        password = str(password)
        token = self._get_fernet().encrypt(password.encode("utf-8")).decode("utf-8")
        self.esali_password_enc = token

    def get_esali_password_plain(self) -> str:
        token = (self.esali_password_enc or "").strip()
        if token == "":
            return ""
        try:
            return self._get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")
        except InvalidToken:
            raise ValidationError("Invalid encrypted Esali password.")

    def clean(self) -> None:
        if sum([self.is_collector, self.is_senior_collector, self.is_observer]) > 1:
            raise ValidationError("لا يمكن للمستخدم أن يمتلك أكثر من دور واحد (مراقب، محصل، كبير متحصلين) في نفس الوقت.")

        if self.is_collector:
            missing: list[str] = []
            if str(self.esali_username).strip() == "":
                missing.append("esali_username")
            if str(self.esali_password_enc).strip() == "":
                missing.append("esali_password_enc")
            if missing:
                raise ValidationError(
                    {"__all__": f"Missing required Esali credentials for collector: {', '.join(missing)}"}
                )

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

class CollectorOnlyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_collector=True)


class SeniorCollectorOnlyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_senior_collector=True)


class ObserverOnlyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_observer=True)


class CollectorAssignmentCollector(CollectorAssignment):
    objects = CollectorOnlyManager()

    class Meta:
        proxy = True
        verbose_name = "متحصل"
        verbose_name_plural = "المتحصلين"


class CollectorAssignmentSeniorCollector(CollectorAssignment):
    objects = SeniorCollectorOnlyManager()

    class Meta:
        proxy = True
        verbose_name = "كبير متحصل"
        verbose_name_plural = "كبار المتحصلين"


class CollectorAssignmentObserver(CollectorAssignment):
    objects = ObserverOnlyManager()

    class Meta:
        proxy = True
        verbose_name = "مراقب"
        verbose_name_plural = "المراقبين"



class CollectionForm(models.Model):
    """
    Electronic Collection Form for mining revenue.
    
    Includes business logic for state transitions and immutable fields.
    """
    
    class Status(models.TextChoices):
        DRAFT = 'Draft', 'مسودة'
        COLLECTOR_CONFIRMATION = 'Collector Confirmation', 'بانتظار تأكيد المتحصل'
        INVOICE_REQUESTED = 'Invoice Requested', 'تم طلب الفاتورة'
        INVOICE_QUEUED = 'Invoice Queued', 'تمت جدولة الفاتورة'
        PENDING_PAYMENT = 'Pending Payment', 'بانتظار الدفع'
        PAID = 'Paid', 'تم الدفع'
        CANCELLED = 'Cancelled', 'ملغي'

    receipt_number = models.CharField(verbose_name="رقم الإيصال",
        max_length=64,
        blank=True
    )
    rrn_number = models.CharField(verbose_name="رقم التحويل", max_length=64, blank=True, default="")
    miner_name = models.CharField(verbose_name="اسم العميل / المعدن", max_length=255)
    phone = models.CharField(
        verbose_name="رقم الهاتف",
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^\d{10}$",
                message="رقم الهاتف يجب أن يكون 10 أرقام بالضبط.",
            )
        ],
    )
    sacks_count = models.DecimalField(verbose_name="عدد الجوالات", max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(verbose_name="المبلغ الإجمالي", max_digits=12, decimal_places=2)
    invoice_id = models.CharField(verbose_name="رقم الفاتورة", max_length=64, null=True, blank=True, db_index=True)
    invoice_generated_at = models.DateTimeField(verbose_name="تاريخ إنشاء الفاتورة", null=True, blank=True, db_index=True)
    status = models.CharField(
        verbose_name="الحالة",
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT
    )
    pending_payment_check_now = models.BooleanField(
        verbose_name="التحقق من الدفع الآن",
        default=False,
        db_index=True,
        help_text="Set when a user opens this collection in Pending Payment; cleared when the sync worker consumes it.",
    )
    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="المتحصل",
        on_delete=models.PROTECT,
        related_name='collections'
    )
    market = models.ForeignKey(
        Market,
        verbose_name="السوق",
        on_delete=models.PROTECT,
        related_name='collections'
    )
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="تم الإلغاء بواسطة",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='cancelled_collections'
    )
    cancellation_reason = models.TextField(verbose_name="سبب الإلغاء", null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="تاريخ التحديث", auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="المنشئ",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='+'
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="المحدث",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='+'
    )

    class Meta:
        verbose_name = "إيصال تحصيل"
        verbose_name_plural = "إيصالات التحصيل"
        indexes = [
            Index(fields=["receipt_number"], name="idx_collection_receipt_number"),
            Index(fields=["rrn_number"], name="idx_collection_rrn_number"),
            Index(fields=["miner_name"], name="idx_collection_miner_name"),
        ]

    def __str__(self) -> str:
        return f"إيصال {self.receipt_number} - {self.get_status_display()}"

    def clean(self) -> None:
        """
        Custom validation for state transitions and immutability.
        """
        if self.pk:
            old_instance = CollectionForm.objects.get(pk=self.pk)
            
            # BR-02: Locking: Forms in Pending Payment or Paid status must be immutable for standard fields.
            if old_instance.status in [
                self.Status.COLLECTOR_CONFIRMATION,
                self.Status.INVOICE_REQUESTED,
                self.Status.INVOICE_QUEUED,
                self.Status.PENDING_PAYMENT,
                self.Status.PAID,
            ]:
                # List of fields that should not change after Draft
                protected_fields = [
                    'miner_name', 'sacks_count', 
                    'phone', 'total_amount', 'collector', 'market'
                ]
                for field in protected_fields:
                    if getattr(self, field) != getattr(old_instance, field):
                        raise ValidationError(f"الحقل '{field}' غير قابل للتعديل بعد أن أصبحت حالة الإيصال '{old_instance.get_status_display()}'.")

            # BR-03: Pre-payment Only: Cancellation is forbidden once the status is Paid.
            if old_instance.status == self.Status.PAID and self.status == self.Status.CANCELLED:
                raise ValidationError("لا يمكن إلغاء إيصال تم دفعه بالفعل.")

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Ensure total_amount is always calculated.
        self.total_amount = self.sacks_count * PRICE_PER_SACK
        self.full_clean()
        super().save(*args, **kwargs)

    def transition_status(
        self,
        new_status: str,
        *,
        action: str = "collection_status_change",
        user: Any = None,
        ip_address: str | None = None,
        request_data: dict[str, Any] | None = None,
        response_data: dict[str, Any] | None = None,
        status_code: int = 200,
        update_fields: list[str] | None = None,
    ) -> None:
        """
        Transition to a new status and create a per-record APILog entry.

        Notes:
        - `user` may be None for API-key / background operations.
        - `ip_address` may be None outside HTTP requests.
        """
        old_status = str(self.status)
        self.status = new_status
        if update_fields is None:
            self.save()
        else:
            if "status" not in update_fields:
                update_fields = [*update_fields, "status"]
            self.save(update_fields=update_fields)

        payload = dict(request_data or {})
        payload.setdefault("from", old_status)
        payload.setdefault("to", new_status)
        payload.setdefault("at", timezone.now().isoformat())

        from form15_tra.models import APILog  # local import to avoid circulars in migrations

        APILog.objects.create(
            action=action,
            user=user if getattr(user, "is_authenticated", False) else None,
            request_data=payload,
            response_data=response_data,
            status_code=int(status_code),
            ip_address=ip_address,
            collection_form=self,
        )

class APILog(models.Model):
    """
    Logs API actions for auditing and debugging.
    """
    action = models.CharField(verbose_name="الإجراء", max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="المستخدم",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='api_logs'
    )
    request_data = models.JSONField(verbose_name="بيانات الطلب", null=True, blank=True)
    response_data = models.JSONField(verbose_name="بيانات الرد", null=True, blank=True)
    status_code = models.IntegerField()
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP", null=True, blank=True)
    collection_form = models.ForeignKey(
        'CollectionForm',
        verbose_name="إيصال التحصيل",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='api_logs'
    )
    created_at = models.DateTimeField(verbose_name="تاريخ الإنشاء", auto_now_add=True)

    class Meta:
        verbose_name = "سجل واجهة البرمجة"
        verbose_name_plural = "سجلات واجهة البرمجة"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.action} - {self.status_code} ({self.created_at})"
