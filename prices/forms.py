from datetime import date

from django import forms
from django.utils.translation import gettext_lazy as _

from company_profile.models import LkpState
from prices.models import (
    GlobalGoldPrice,
    BankSudanGoldPrice,
    StateGoldPrice,
    DollarPrice,
    DOLLAR_TYPE_CHOICES,
    DOLLAR_OFFICIAL,
    DOLLAR_PARALLEL,
    GOLD_KARAT_24,
    GOLD_KARAT_21,
    KARAT_21_FACTOR,
    OUNCE_TO_GRAM,
)


class PriceEntryForm(forms.Form):
    """نموذج إدخال جميع الأسعار دفعة واحدة مع تعبئة تلقائية بآخر سعر مسجل."""

    # --- أسعار الذهب ---
    global_gold_24k = forms.DecimalField(
        label=_('سعر الذهب العالمي عيار 24 (دولار/جرام)'),
        max_digits=10, decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
    )

    global_gold_24k_ounce = forms.DecimalField(
        label=_('سعر الذهب العالمي عيار 24 (دولار/أوقية)'),
        max_digits=10, decimal_places=2,
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'step': '0.01', 'class': 'form-control', 'readonly': 'readonly',
        }),
    )

    global_gold_21k = forms.DecimalField(
        label=_('سعر الذهب العالمي عيار 21 (دولار/جرام)'),
        max_digits=10, decimal_places=2,
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'step': '0.01', 'class': 'form-control', 'readonly': 'readonly',
        }),
    )

    bank_sudan_price = forms.DecimalField(
        label=_('سعر شراء بنك السودان (جنيه/جرام)'),
        max_digits=12, decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
    )

    # --- أسعار الصرف ---
    official_dollar_buy_price = forms.DecimalField(
        label=_('سعر شراء الدولار الرسمي (جنيه)'),
        max_digits=10, decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
    )

    official_dollar_sell_price = forms.DecimalField(
        label=_('سعر بيع الدولار الرسمي (جنيه)'),
        max_digits=10, decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
    )

    parallel_dollar_buy_price = forms.DecimalField(
        label=_('سعر شراء الدولار بالسوق الموازي (جنيه)'),
        max_digits=10, decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
    )

    parallel_dollar_sell_price = forms.DecimalField(
        label=_('سعر بيع الدولار بالسوق الموازي (جنيه)'),
        max_digits=10, decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
    )

    # --- أسعار الذهب بالولايات ---
    state_gold_prices = forms.CharField(
        label=_('أسعار الذهب بالولايات'),
        required=False,
        widget=forms.HiddenInput(),
        help_text=_('JSON field — managed by the dynamic state-price widget in the template.'),
    )

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user', None)
        self._allowed_state_ids = kwargs.pop('allowed_state_ids', None)
        super().__init__(*args, **kwargs)
        self._apply_role_restrictions()
        self._prefill_last_prices()

    def clean_state_gold_prices(self):
        raw = self.cleaned_data.get('state_gold_prices', '')
        if not raw:
            return raw
        try:
            import json
            entries = json.loads(raw)
        except (ValueError, json.JSONDecodeError):
            raise forms.ValidationError(_('بيانات الولايات غير صالحة.'))
        if self._allowed_state_ids is not None:
            allowed = set(self._allowed_state_ids)
            for entry in entries:
                if entry.get('state_id') not in allowed:
                    raise forms.ValidationError(
                        _('ليس لديك صلاحية لإدخال سعر هذه الولاية.')
                    )
        return raw

    def _apply_role_restrictions(self):
        """Remove fields the user's role is not authorized to enter."""
        if self._user is None or self._user.is_superuser:
            return  # superuser sees all fields

        # User must be saved to have groups
        if not self._user.pk:
            for name in list(self.fields.keys()):
                del self.fields[name]
            return

        user_groups = set(self._user.groups.values_list('name', flat=True))

        # If user has no prices group at all, remove everything
        if not user_groups:
            for name in list(self.fields.keys()):
                del self.fields[name]
            return

        # Determine which sections to keep
        show_main = 'prices_main' in user_groups
        show_parallel = 'prices_parallel_dollar' in user_groups
        show_state = 'prices_state_gold' in user_groups

        # Main fields: global gold (both karats), bank sudan, official dollar (buy & sell)
        main_fields = {
            'global_gold_24k', 'global_gold_24k_ounce', 'global_gold_21k',
            'bank_sudan_price',
            'official_dollar_buy_price', 'official_dollar_sell_price',
        }

        # Parallel dollar fields (buy & sell)
        parallel_fields = {'parallel_dollar_buy_price', 'parallel_dollar_sell_price'}

        # State gold field
        state_fields = {'state_gold_prices'}

        keep = set()
        if show_main:
            keep |= main_fields
        if show_parallel:
            keep |= parallel_fields
        if show_state:
            keep |= state_fields

        for name in list(self.fields.keys()):
            if name not in keep:
                del self.fields[name]

    def _prefill_last_prices(self):
        """تعبئة الحقول بآخر الأسعار المسجلة تلقائياً (المتطلب: آلية الإدخال الذكية)."""
        if 'global_gold_24k' in self.fields:
            last = GlobalGoldPrice.objects.filter(karat=GOLD_KARAT_24).order_by('-date', '-created_at').first()
            if last:
                self.fields['global_gold_24k'].initial = last.price_per_gram_usd
                self.fields['global_gold_24k_ounce'].initial = last.price_per_ounce_usd

        if 'global_gold_21k' in self.fields:
            last = GlobalGoldPrice.objects.filter(karat=GOLD_KARAT_21).order_by('-date', '-created_at').first()
            if last:
                self.fields['global_gold_21k'].initial = last.price_per_gram_usd

        if 'bank_sudan_price' in self.fields:
            last = BankSudanGoldPrice.objects.order_by('-date', '-created_at').first()
            if last:
                self.fields['bank_sudan_price'].initial = last.price_per_gram_sdg

        if 'official_dollar_buy_price' in self.fields:
            last = DollarPrice.objects.filter(rate_type=DOLLAR_OFFICIAL).order_by('-date', '-created_at').first()
            if last:
                self.fields['official_dollar_buy_price'].initial = last.buy_price_in_sdg
                self.fields['official_dollar_sell_price'].initial = last.sell_price_in_sdg

        if 'parallel_dollar_buy_price' in self.fields:
            last = DollarPrice.objects.filter(rate_type=DOLLAR_PARALLEL).order_by('-date', '-created_at').first()
            if last:
                self.fields['parallel_dollar_buy_price'].initial = last.buy_price_in_sdg
                self.fields['parallel_dollar_sell_price'].initial = last.sell_price_in_sdg

    def save(self, user):
        """حفظ جميع الأسعار المدخلة في سجلات منفصلة (مسار تدقيق كامل)."""
        data = self.cleaned_data
        today = date.today()

        def _same_as_latest(qs_filter, **price_fields):
            """True if the latest record for qs_filter holds the same actual
            price fields (audit/log fields are never compared)."""
            latest = qs_filter.order_by('-created_at').first()
            if latest is None:
                return False
            return all(
                getattr(latest, field) == value
                for field, value in price_fields.items()
            )

        # الذهب العالمي - عيار 24
        if 'global_gold_24k' in data:
            if not _same_as_latest(
                GlobalGoldPrice.objects.filter(karat=GOLD_KARAT_24, date=today),
                price_per_gram_usd=data['global_gold_24k'],
            ):
                ounce_price = data.get('global_gold_24k_ounce')
                if ounce_price is None:
                    ounce_price = round(float(data['global_gold_24k']) * OUNCE_TO_GRAM, 2)
                GlobalGoldPrice.objects.create(
                    karat=GOLD_KARAT_24,
                    price_per_gram_usd=data['global_gold_24k'],
                    price_per_ounce_usd=ounce_price,
                    created_by=user,
                    updated_by=user,
                )

            # الذهب العالمي - عيار 21 (مقارنة مستقلة)
            price_21k = data.get('global_gold_21k')
            if price_21k is None:
                price_21k = round(float(data['global_gold_24k']) * KARAT_21_FACTOR, 2)
            if not _same_as_latest(
                GlobalGoldPrice.objects.filter(karat=GOLD_KARAT_21, date=today),
                price_per_gram_usd=price_21k,
            ):
                GlobalGoldPrice.objects.create(
                    karat=GOLD_KARAT_21,
                    price_per_gram_usd=price_21k,
                    created_by=user,
                    updated_by=user,
                )

        # بنك السودان
        if 'bank_sudan_price' in data:
            if not _same_as_latest(
                BankSudanGoldPrice.objects.filter(date=today),
                price_per_gram_sdg=data['bank_sudan_price'],
            ):
                BankSudanGoldPrice.objects.create(
                    price_per_gram_sdg=data['bank_sudan_price'],
                    created_by=user,
                    updated_by=user,
                )

        # الدولار الرسمي
        if 'official_dollar_buy_price' in data:
            if not _same_as_latest(
                DollarPrice.objects.filter(rate_type=DOLLAR_OFFICIAL, date=today),
                buy_price_in_sdg=data['official_dollar_buy_price'],
                sell_price_in_sdg=data['official_dollar_sell_price'],
            ):
                DollarPrice.objects.create(
                    rate_type=DOLLAR_OFFICIAL,
                    buy_price_in_sdg=data['official_dollar_buy_price'],
                    sell_price_in_sdg=data['official_dollar_sell_price'],
                    created_by=user,
                    updated_by=user,
                )

        # الدولار الموازي
        if 'parallel_dollar_buy_price' in data:
            if not _same_as_latest(
                DollarPrice.objects.filter(rate_type=DOLLAR_PARALLEL, date=today),
                buy_price_in_sdg=data['parallel_dollar_buy_price'],
                sell_price_in_sdg=data['parallel_dollar_sell_price'],
            ):
                DollarPrice.objects.create(
                    rate_type=DOLLAR_PARALLEL,
                    buy_price_in_sdg=data['parallel_dollar_buy_price'],
                    sell_price_in_sdg=data['parallel_dollar_sell_price'],
                    created_by=user,
                    updated_by=user,
                )

        # أسعار الولايات (المقارنة تشمل السعر والملاحظات — أي تغيير يسجّل)
        if 'state_gold_prices' in data:
            import json
            state_prices_json = data.get('state_gold_prices', '')
            if state_prices_json:
                state_prices = json.loads(state_prices_json)
                for entry in state_prices:
                    state_id = entry.get('state_id')
                    price = entry.get('price')
                    comment = entry.get('comment', '')
                    if state_id and price is not None:
                        if not _same_as_latest(
                            StateGoldPrice.objects.filter(state_id=state_id, date=today),
                            price_per_gram_sdg=price,
                            comment=comment,
                        ):
                            StateGoldPrice.objects.create(
                                state_id=state_id,
                                price_per_gram_sdg=price,
                                comment=comment,
                                created_by=user,
                                updated_by=user,
                            )
