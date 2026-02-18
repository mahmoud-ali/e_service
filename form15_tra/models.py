from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from typing import Any

# from traditional_app.models import LkpSoag

PRICE_PER_SACK = 25000

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
        default=False,
        help_text="يسمح للمستخدم بإنشاء وتأكيد إيصالات التحصيل."
    )
    is_senior_collector = models.BooleanField(
        default=False,
        help_text="يسمح للمستخدم بإلغاء إيصالات التحصيل."
    )

    is_observer = models.BooleanField(
        default=False,
        help_text="يسمح للمستخدم بإنشاء إيصالات مسودة فقط."
    )

    class Meta:
        verbose_name = "تكليف متحصل"
        verbose_name_plural = "تكليف المتحصلين"

    def __str__(self) -> str:
        return f"{self.user.username} -> {self.market.market_name}"

    def clean(self) -> None:
        if sum([self.is_collector, self.is_senior_collector, self.is_observer]) > 1:
            raise ValidationError("لا يمكن للمستخدم أن يمتلك أكثر من دور واحد (مراقب، محصل، كبير متحصلين) في نفس الوقت.")

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
        WAITING_APPROVAL = 'Waiting Approval', 'بانتظار الموافقة'
        PENDING_PAYMENT = 'Pending Payment', 'بانتظار الدفع'
        PAID = 'Paid', 'تم الدفع'
        CANCELLED = 'Cancelled', 'ملغي'

    receipt_number = models.CharField(
        max_length=10,
        unique=True,
        blank=True,  # Auto-generated
        validators=[
            RegexValidator(
                regex='^\d{10}$',
                message='رقم الإيصال يجب أن يتكون من 10 أرقام بالضبط.',
                code='invalid_receipt_number'
            )
        ]
    )
    miner_name = models.CharField(max_length=255)
    sacks_count = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
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
            if old_instance.status in [self.Status.PENDING_PAYMENT, self.Status.PAID, self.Status.WAITING_APPROVAL]:
                # List of fields that should not change after Draft
                protected_fields = [
                    'receipt_number', 'miner_name', 'sacks_count', 
                    'total_amount', 'collector', 'market'
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

            prefix = str(self.market.id)
            # Find the next sequence number for this market
            last_receipt = CollectionForm.objects.filter(market=self.market).order_by('-receipt_number').first()
            if last_receipt and last_receipt.receipt_number.startswith(prefix):
                 # Extract sequence part. Assuming format is {prefix}{sequence}
                 # Be careful if receipt_number format was different before or if prefix length varies.
                 # Given the requirement, I'll count + 1 which is simpler but has race conditions.
                 # For robust unique generation, usually one would use a separate Sequence model or DB sequence.
                 # For this task, I will use count + 1 logic adjusted to ensure uniqueness loop or use max.
                 
                 # Using max receipt number for safety against deletions
                 # However, since receipt_number is string, naive max might be wrong if lengths differ, but here fixed 10.
                 # Let's try simple count logic first as requested "start by market id".
                 # Actually, better practice:
                 pass

            # Count verification
            count = CollectionForm.objects.filter(market=self.market).count() + 1
            while True:
                candidate = f"{prefix}{count:0{10-len(prefix)}d}"
                if not CollectionForm.objects.filter(receipt_number=candidate).exists():
                    self.receipt_number = candidate
                    break
                count += 1

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
