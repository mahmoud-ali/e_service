from django import forms
from django.utils.translation import gettext_lazy as _

from company_profile.models import LkpState
from prices.models import (
    GlobalGoldPrice,
    BankSudanGoldPrice,
    StateGoldPrice,
    DollarPrice,
    BANK_CATEGORY_CHOICES,
    DOLLAR_TYPE_CHOICES,
    DOLLAR_OFFICIAL,
    DOLLAR_PARALLEL,
    BANK_CATEGORY_CONCESSION,
    BANK_CATEGORY_WASTE,
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

    bank_concession_price = forms.DecimalField(
        label=_('سعر شراء بنك السودان - شركات الامتياز (جنيه/جرام)'),
        max_digits=12, decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
    )

    bank_waste_price = forms.DecimalField(
        label=_('سعر شراء بنك السودان - شركات المخلفات (جنيه/جرام)'),
        max_digits=12, decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
    )

    # --- أسعار الصرف ---
    official_dollar_price = forms.DecimalField(
        label=_('سعر الدولار الرسمي (جنيه)'),
        max_digits=10, decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
    )

    parallel_market_dollar_price = forms.DecimalField(
        label=_('سعر الدولار بالسوق الموازي (جنيه)'),
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
        super().__init__(*args, **kwargs)
        self._apply_role_restrictions()
        self._prefill_last_prices()

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

        # Main fields: global gold (both karats), bank sudan (both), official dollar
        main_fields = {
            'global_gold_24k', 'global_gold_24k_ounce', 'global_gold_21k',
            'bank_concession_price', 'bank_waste_price',
            'official_dollar_price',
        }

        # Parallel dollar field
        parallel_fields = {'parallel_market_dollar_price'}

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
            last = GlobalGoldPrice.objects.filter(karat=GOLD_KARAT_24).order_by('-created_at').first()
            if last:
                self.fields['global_gold_24k'].initial = last.price_per_gram_usd
                self.fields['global_gold_24k_ounce'].initial = last.price_per_ounce_usd

        if 'global_gold_21k' in self.fields:
            last = GlobalGoldPrice.objects.filter(karat=GOLD_KARAT_21).order_by('-created_at').first()
            if last:
                self.fields['global_gold_21k'].initial = last.price_per_gram_usd

        if 'bank_concession_price' in self.fields:
            last = BankSudanGoldPrice.objects.filter(category=BANK_CATEGORY_CONCESSION).order_by('-created_at').first()
            if last:
                self.fields['bank_concession_price'].initial = last.price_per_gram_sdg

        if 'bank_waste_price' in self.fields:
            last = BankSudanGoldPrice.objects.filter(category=BANK_CATEGORY_WASTE).order_by('-created_at').first()
            if last:
                self.fields['bank_waste_price'].initial = last.price_per_gram_sdg

        if 'official_dollar_price' in self.fields:
            last = DollarPrice.objects.filter(rate_type=DOLLAR_OFFICIAL).order_by('-created_at').first()
            if last:
                self.fields['official_dollar_price'].initial = last.price_in_sdg

        if 'parallel_market_dollar_price' in self.fields:
            last = DollarPrice.objects.filter(rate_type=DOLLAR_PARALLEL).order_by('-created_at').first()
            if last:
                self.fields['parallel_market_dollar_price'].initial = last.price_in_sdg

    def save(self, user):
        """حفظ جميع الأسعار المدخلة في سجلات منفصلة (مسار تدقيق كامل)."""
        data = self.cleaned_data

        # الذهب العالمي - عيار 24
        if 'global_gold_24k' in data:
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

            # الذهب العالمي - عيار 21
            price_21k = data.get('global_gold_21k')
            if price_21k is None:
                price_21k = round(float(data['global_gold_24k']) * KARAT_21_FACTOR, 2)
            GlobalGoldPrice.objects.create(
                karat=GOLD_KARAT_21,
                price_per_gram_usd=price_21k,
                created_by=user,
                updated_by=user,
            )

        # بنك السودان - شركات الامتياز
        if 'bank_concession_price' in data:
            BankSudanGoldPrice.objects.create(
                category=BANK_CATEGORY_CONCESSION,
                price_per_gram_sdg=data['bank_concession_price'],
                created_by=user,
                updated_by=user,
            )

        # بنك السودان - شركات المخلفات
        if 'bank_waste_price' in data:
            BankSudanGoldPrice.objects.create(
                category=BANK_CATEGORY_WASTE,
                price_per_gram_sdg=data['bank_waste_price'],
                created_by=user,
                updated_by=user,
            )

        # الدولار الرسمي
        if 'official_dollar_price' in data:
            DollarPrice.objects.create(
                rate_type=DOLLAR_OFFICIAL,
                price_in_sdg=data['official_dollar_price'],
                created_by=user,
                updated_by=user,
            )

        # الدولار الموازي
        if 'parallel_market_dollar_price' in data:
            DollarPrice.objects.create(
                rate_type=DOLLAR_PARALLEL,
                price_in_sdg=data['parallel_market_dollar_price'],
                created_by=user,
                updated_by=user,
            )

        # أسعار الولايات
        if 'state_gold_prices' in data:
            import json
            state_prices_json = data.get('state_gold_prices', '')
            if state_prices_json:
                state_prices = json.loads(state_prices_json)
                for entry in state_prices:
                    state_id = entry.get('state_id')
                    price = entry.get('price')
                    if state_id and price is not None:
                        StateGoldPrice.objects.create(
                            state_id=state_id,
                            price_per_gram_sdg=price,
                            created_by=user,
                            updated_by=user,
                        )
