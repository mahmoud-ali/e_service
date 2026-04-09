from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from typing import Any
from django.db import transaction
import os

from cryptography.fernet import Fernet, InvalidToken

# from traditional_app.models import LkpSoag

PRICE_PER_SACK = getattr(settings, "PRICE_PER_SACK", 25000)

class Market(models.Model):
    """
    Represents a market where revenue is collected.
    """
    market_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

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
        on_delete=models.CASCADE,
        related_name='assignment'
    )
    market = models.ForeignKey(
        Market,
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
    esali_username = models.CharField(max_length=128, blank=True, default="")
    esali_password_enc = models.TextField(blank=True, default="")
    esali_service_id = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        verbose_name = "تكليف متحصل"
        verbose_name_plural = "تكليف المتحصلين"

    def __str__(self) -> str:
        return f"{self.user.username} -> {self.market.market_name}"

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

    receipt_number = models.CharField(
        max_length=64,
        blank=True
    )
    rrn_number = models.CharField(max_length=64, blank=True, default="")
    miner_name = models.CharField(max_length=255)
    phone = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^\d{10}$",
                message="رقم الهاتف يجب أن يكون 10 أرقام بالضبط.",
            )
        ],
    )
    sacks_count = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    invoice_id = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT
    )
    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='collections'
    )
    market = models.ForeignKey(
        Market,
        on_delete=models.PROTECT,
        related_name='collections'
    )
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='cancelled_collections'
    )
    cancellation_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='+'
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='+'
    )

    class Meta:
        verbose_name = "إيصال تحصيل"
        verbose_name_plural = "إيصالات التحصيل"

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
        if not self.receipt_number:
            # Calculate total amount
            self.total_amount = self.sacks_count * PRICE_PER_SACK

        self.full_clean()
        super().save(*args, **kwargs)

class APILog(models.Model):
    """
    Logs API actions for auditing and debugging.
    """
    action = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='api_logs'
    )
    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    status_code = models.IntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    collection_form = models.ForeignKey(
        'CollectionForm',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='api_logs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "سجل واجهة البرمجة"
        verbose_name_plural = "سجلات واجهة البرمجة"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.action} - {self.status_code} ({self.created_at})"
