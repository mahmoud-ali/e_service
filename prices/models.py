from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from workflow.model_utils import LoggingModel
from company_profile.models import LkpState


# --- Constants ---

BANK_CATEGORY_CONCESSION = 'concession'
BANK_CATEGORY_WASTE = 'waste'

BANK_CATEGORY_CHOICES = {
    BANK_CATEGORY_CONCESSION: _('شركات الامتياز'),
    BANK_CATEGORY_WASTE: _('شركات المخلفات'),
}

DOLLAR_OFFICIAL = 'official'
DOLLAR_PARALLEL = 'parallel'

DOLLAR_TYPE_CHOICES = {
    DOLLAR_OFFICIAL: _('الدولار الرسمي'),
    DOLLAR_PARALLEL: _('الدولار بالسوق الموازي'),
}

GOLD_KARAT_24 = 24
GOLD_KARAT_21 = 21

GOLD_KARAT_CHOICES = {
    GOLD_KARAT_24: _('عيار 24'),
    GOLD_KARAT_21: _('عيار 21'),
}

KARAT_21_FACTOR = 0.875  # 21K = 24K × 0.875
OUNCE_TO_GRAM = 31.1034768


# --- Models ---

class GlobalGoldPrice(LoggingModel):
    """سعر الذهب عالمياً (بالدولار للجرام)"""
    karat = models.PositiveSmallIntegerField(
        _('العيار'),
        choices=GOLD_KARAT_CHOICES,
        default=GOLD_KARAT_24,
    )
    price_per_gram_usd = models.DecimalField(
        _('سعر الجرام بالدولار'),
        max_digits=10, decimal_places=2,
    )
    price_per_ounce_usd = models.DecimalField(
        _('سعر الأوقية بالدولار'),
        max_digits=10, decimal_places=2,
        default=0,
    )

    def __str__(self):
        karat_label = dict(GOLD_KARAT_CHOICES).get(self.karat, self.karat)
        return f'{karat_label} — ${self.price_per_gram_usd}/g (${self.price_per_ounce_usd}/oz) — {self.created_at:%Y-%m-%d %H:%M}'

    class Meta:
        verbose_name = _('سعر الذهب العالمي')
        verbose_name_plural = _('أسعار الذهب العالمية')
        ordering = ['-created_at']


class BankSudanGoldPrice(LoggingModel):
    """سعر شراء بنك السودان للجرام (بالجنيه السوداني)"""
    category = models.CharField(
        _('الفئة'),
        max_length=20,
        choices=BANK_CATEGORY_CHOICES,
    )
    price_per_gram_sdg = models.DecimalField(
        _('سعر الجرام بالجنيه'),
        max_digits=12, decimal_places=2,
    )

    def __str__(self):
        cat = dict(BANK_CATEGORY_CHOICES).get(self.category, self.category)
        return f'{cat} — {self.price_per_gram_sdg} SDG — {self.created_at:%Y-%m-%d %H:%M}'

    class Meta:
        verbose_name = _('سعر الذهب - بنك السودان')
        verbose_name_plural = _('أسعار الذهب - بنك السودان')
        ordering = ['-created_at']


class StateGoldPrice(LoggingModel):
    """سعر الذهب بالولاية (بالجنيه السوداني للجرام)"""
    state = models.ForeignKey(
        LkpState,
        on_delete=models.PROTECT,
        verbose_name=_('الولاية'),
    )
    price_per_gram_sdg = models.DecimalField(
        _('سعر الجرام بالجنيه'),
        max_digits=12, decimal_places=2,
    )
    comment = models.TextField(
        _('ملاحظات'),
        blank=True,
        default='',
    )

    def __str__(self):
        return f'{self.state.name} — {self.price_per_gram_sdg} SDG — {self.created_at:%Y-%m-%d %H:%M}'

    class Meta:
        verbose_name = _('سعر الذهب بالولاية')
        verbose_name_plural = _('أسعار الذهب بالولايات')
        ordering = ['-created_at']


class DollarPrice(LoggingModel):
    """سعر صرف الدولار (بالجنيه السوداني)"""
    rate_type = models.CharField(
        _('نوع السعر'),
        max_length=20,
        choices=DOLLAR_TYPE_CHOICES,
    )
    price_in_sdg = models.DecimalField(
        _('السعر بالجنيه'),
        max_digits=10, decimal_places=2,
    )

    def __str__(self):
        label = dict(DOLLAR_TYPE_CHOICES).get(self.rate_type, self.rate_type)
        return f'{label} — {self.price_in_sdg} SDG — {self.created_at:%Y-%m-%d %H:%M}'

    class Meta:
        verbose_name = _('سعر صرف الدولار')
        verbose_name_plural = _('أسعار صرف الدولار')
        ordering = ['-created_at']


class PricesStateUser(LoggingModel):
    """ربط مستخدم بولاية معينة لإدخال أسعار الذهب بالولايات"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='prices_state_users',
        verbose_name=_('المستخدم'),
    )
    state = models.ForeignKey(
        LkpState,
        on_delete=models.PROTECT,
        verbose_name=_('الولاية'),
    )

    def __str__(self):
        return f'{self.user} — {self.state.name}'

    class Meta:
        verbose_name = _('مستخدم ولاية - الأسعار')
        verbose_name_plural = _('مستخدمي الولايات - الأسعار')
        ordering = ['user']
        unique_together = [('user', 'state')]
