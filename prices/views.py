import json
from collections import defaultdict
from datetime import date, timedelta

import requests
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max as DMax
from django.db.models import Avg, Min
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView, View

from company_profile.models import LkpState
from prices.forms import PriceEntryForm
from prices.models import (
    BankSudanGoldPrice,
    DollarPrice,
    GlobalGoldPrice,
    StateGoldPrice,
    PricesStateUser,
    DOLLAR_OFFICIAL,
    DOLLAR_PARALLEL,
    GOLD_KARAT_24,
    GOLD_KARAT_21,
    OUNCE_TO_GRAM,
)


# ---------------------------------------------------------------------------
# 1. نموذج الإدخال
# ---------------------------------------------------------------------------
class PriceEntryView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy('prices:login')
    template_name = 'prices/price_entry.html'
    form_class = PriceEntryForm
    success_url = reverse_lazy('prices:report')

    def dispatch(self, request, *args, **kwargs):
        # View-only users redirected to report
        has_add = (
            request.user.has_perm('prices.add_globalgoldprice')
            or request.user.has_perm('prices.add_dollarprice')
            or request.user.has_perm('prices.add_stategoldprice')
        )
        if not has_add and not request.user.is_superuser:
            return redirect('prices:report')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['allowed_state_ids'] = list(
            self._get_allowed_states().values_list('pk', flat=True)
        )
        return kwargs

    def _get_allowed_states(self):
        """Return states the user is allowed to enter prices for."""
        user = self.request.user
        if user.is_superuser:
            return LkpState.objects.all().order_by('name')
        state_ids = PricesStateUser.objects.filter(
            user=user
        ).values_list('state_id', flat=True)
        return LkpState.objects.filter(pk__in=state_ids).order_by('name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['states'] = self._get_allowed_states()

        # Last state prices for the dynamic widget (user's states only)
        allowed_state_ids = ctx['states'].values_list('pk', flat=True)
        last_state_prices = {}
        for sp in StateGoldPrice.objects.filter(
            state__in=allowed_state_ids
        ).filter(
            pk__in=StateGoldPrice.objects.values('state').annotate(
                max_id=DMax('id')
            ).values('max_id')
        ).select_related('state'):
            last_state_prices[sp.state_id] = float(sp.price_per_gram_sdg)
        ctx['states'] = self._get_allowed_states()
        ctx['last_state_prices_json'] = json.dumps(last_state_prices)
        return ctx

    def form_valid(self, form):
        form.save(user=self.request.user)
        messages.success(self.request, _('تم حفظ جميع الأسعار بنجاح.'))
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# 2. تقرير ملخص — آخر الأسعار المسجلة لجميع العناصر
# ---------------------------------------------------------------------------
class PriceReportView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('prices:login')
    template_name = 'prices/price_report.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Last prices for each item
        ctx['last_global'] = GlobalGoldPrice.objects.filter(
            karat=GOLD_KARAT_24
        ).order_by('-created_at').first()
        ctx['last_global_21k'] = GlobalGoldPrice.objects.filter(
            karat=GOLD_KARAT_21
        ).order_by('-created_at').first()
        ctx['last_bank_sudan'] = BankSudanGoldPrice.objects.order_by('-created_at').first()
        ctx['last_official'] = DollarPrice.objects.filter(
            rate_type=DOLLAR_OFFICIAL
        ).order_by('-created_at').first()
        ctx['last_parallel'] = DollarPrice.objects.filter(
            rate_type=DOLLAR_PARALLEL
        ).order_by('-created_at').first()

        # Latest state prices (most recent per state)
        ctx['last_state_prices'] = StateGoldPrice.objects.filter(
            pk__in=StateGoldPrice.objects.values('state').annotate(
                max_id=DMax('id')
            ).values('max_id')
        ).select_related('state', 'created_by').order_by('state__name')

        return ctx


# ---------------------------------------------------------------------------
# 3. سجل الأسعار — تاريخ لفترة زمنية محددة
# ---------------------------------------------------------------------------
class PriceHistoryView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('prices:login')
    template_name = 'prices/price_history.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Default: last 7 days
        end_date = self.request.GET.get('end_date', date.today().isoformat())
        start_date = self.request.GET.get(
            'start_date',
            (date.today() - timedelta(days=7)).isoformat(),
        )

        ctx['start_date'] = start_date
        ctx['end_date'] = end_date

        dt_filter = {'created_at__date__gte': start_date, 'created_at__date__lte': end_date}

        ctx['global_prices'] = GlobalGoldPrice.objects.filter(**dt_filter)
        ctx['bank_sudan_prices'] = BankSudanGoldPrice.objects.filter(**dt_filter)
        ctx['official_prices'] = DollarPrice.objects.filter(
            rate_type=DOLLAR_OFFICIAL, **dt_filter
        )
        ctx['parallel_prices'] = DollarPrice.objects.filter(
            rate_type=DOLLAR_PARALLEL, **dt_filter
        )
        ctx['state_prices'] = StateGoldPrice.objects.filter(
            **dt_filter
        ).select_related('state', 'created_by')

        # --- Compute stats (avg / min / max) for each price type ---
        def _stats(qs, value_field):
            agg = qs.aggregate(
                avg=Avg(value_field),
                min=Min(value_field),
                max=DMax(value_field),
            )
            return {
                'avg': round(agg['avg'], 2) if agg['avg'] is not None else None,
                'min': round(agg['min'], 2) if agg['min'] is not None else None,
                'max': round(agg['max'], 2) if agg['max'] is not None else None,
            }

        ctx['global_24k_stats'] = _stats(
            GlobalGoldPrice.objects.filter(karat=GOLD_KARAT_24, **dt_filter),
            'price_per_gram_usd',
        )
        ctx['global_21k_stats'] = _stats(
            GlobalGoldPrice.objects.filter(karat=GOLD_KARAT_21, **dt_filter),
            'price_per_gram_usd',
        )
        ctx['bank_sudan_stats'] = _stats(ctx['bank_sudan_prices'], 'price_per_gram_sdg')
        ctx['official_stats'] = _stats(ctx['official_prices'], 'price_in_sdg')
        ctx['parallel_stats'] = _stats(ctx['parallel_prices'], 'price_in_sdg')
        ctx['state_stats'] = _stats(ctx['state_prices'], 'price_per_gram_sdg')

        return ctx


# ---------------------------------------------------------------------------
# 4. تقرير مقارنة — مقارنة أسعار الذهب المحلية (محولة للدولار) مع السعر العالمي
# ---------------------------------------------------------------------------
class PriceComparisonView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('prices:login')
    template_name = 'prices/price_comparison.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Latest parallel dollar rate (used for conversion)
        last_parallel = DollarPrice.objects.filter(
            rate_type=DOLLAR_PARALLEL
        ).order_by('-created_at').first()
        last_official = DollarPrice.objects.filter(
            rate_type=DOLLAR_OFFICIAL
        ).order_by('-created_at').first()
        ctx['last_parallel'] = last_parallel
        ctx['last_official'] = last_official

        if last_parallel and last_parallel.price_in_sdg > 0:
            rate = float(last_parallel.price_in_sdg)

            # Global gold price
            last_global = GlobalGoldPrice.objects.filter(
                karat=GOLD_KARAT_24
            ).order_by('-created_at').first()
            last_global_21k = GlobalGoldPrice.objects.filter(
                karat=GOLD_KARAT_21
            ).order_by('-created_at').first()
            ctx['last_global'] = last_global
            ctx['last_global_21k'] = last_global_21k

            # Bank Sudan prices → USD
            last_bank = BankSudanGoldPrice.objects.order_by('-created_at').first()

            rows = []

            # Bank Sudan comparison
            if last_bank:
                local_usd = float(last_bank.price_per_gram_sdg) / rate
                gap = local_usd - float(last_global.price_per_gram_usd) if last_global else 0
                gap_pct = (gap / float(last_global.price_per_gram_usd) * 100) if last_global and float(last_global.price_per_gram_usd) > 0 else 0
                rows.append({
                    'label': _('شراء بنك السودان'),
                    'local_sdg': float(last_bank.price_per_gram_sdg),
                    'local_usd': round(local_usd, 2),
                    'global_usd': float(last_global.price_per_gram_usd) if last_global else None,
                    'gap_usd': round(gap, 2),
                    'gap_pct': round(gap_pct, 2),
                    'source_record': last_bank,
                })

            # State prices comparison
            latest_state_ids = StateGoldPrice.objects.values('state').annotate(
                max_id=DMax('id')
            ).values('max_id')
            for sp in StateGoldPrice.objects.filter(
                pk__in=latest_state_ids
            ).select_related('state', 'created_by').order_by('state__name'):
                local_usd = float(sp.price_per_gram_sdg) / rate
                gap = local_usd - float(last_global.price_per_gram_usd) if last_global else 0
                gap_pct = (gap / float(last_global.price_per_gram_usd) * 100) if last_global and float(last_global.price_per_gram_usd) > 0 else 0
                rows.append({
                    'label': f'{sp.state.name}',
                    'local_sdg': float(sp.price_per_gram_sdg),
                    'local_usd': round(local_usd, 2),
                    'global_usd': float(last_global.price_per_gram_usd) if last_global else None,
                    'gap_usd': round(gap, 2),
                    'gap_pct': round(gap_pct, 2),
                    'source_record': sp,
                })

            ctx['comparison_rows'] = rows
            ctx['comparison_rows_json'] = json.dumps([
                {
                    'label': str(r['label']),
                    'local_sdg': r['local_sdg'],
                    'local_usd': r['local_usd'],
                    'global_usd': r['global_usd'],
                    'gap_usd': r['gap_usd'],
                    'gap_pct': r['gap_pct'],
                }
                for r in rows
            ])

        # --- Time-series data for gold vs dollar chart (last 30 days) ---
        self._add_timeseries_context(ctx)

        return ctx

    def _add_timeseries_context(self, ctx):
        """Build time-series JSON for gold prices (SDG) vs dollar rates over last 30 days."""
        cutoff = date.today() - timedelta(days=30)

        def _latest_per_date(queryset, value_attr):
            """Return dict of {date_iso: latest_value} for the queryset."""
            result = {}
            for record in queryset.filter(created_at__date__gte=cutoff).order_by('created_at__date', '-created_at'):
                d = record.created_at.date().isoformat()
                if d not in result:
                    result[d] = float(getattr(record, value_attr))
            return result

        bank_by_date = _latest_per_date(
            BankSudanGoldPrice.objects.all(),
            'price_per_gram_sdg',
        )
        official_by_date = _latest_per_date(
            DollarPrice.objects.filter(rate_type=DOLLAR_OFFICIAL),
            'price_in_sdg',
        )
        parallel_by_date = _latest_per_date(
            DollarPrice.objects.filter(rate_type=DOLLAR_PARALLEL),
            'price_in_sdg',
        )

        # Collect all dates across all datasets
        all_dates = sorted(set(
            list(bank_by_date.keys())
            + list(official_by_date.keys())
            + list(parallel_by_date.keys())
        ))

        ctx['timeseries_labels_json'] = json.dumps(all_dates)
        ctx['timeseries_bank_json'] = json.dumps([
            bank_by_date.get(d) for d in all_dates
        ])
        ctx['timeseries_official_json'] = json.dumps([
            official_by_date.get(d) for d in all_dates
        ])
        ctx['timeseries_parallel_json'] = json.dumps([
            parallel_by_date.get(d) for d in all_dates
        ])


# ---------------------------------------------------------------------------
# 5. جلب سعر الذهب العالمي من الإنترنت
# ---------------------------------------------------------------------------
GOLD_API_URL = 'https://data-asg.goldprice.org/dbXRates/USD'


class FetchGoldPriceView(LoginRequiredMixin, View):
    login_url = reverse_lazy('prices:login')
    """Proxy endpoint to fetch live global gold price (USD/gram) from a free API."""

    def get(self, request):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Referer': 'https://goldprice.org/',
            }
            resp = requests.get(GOLD_API_URL, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            item = data['items'][0]
            price_per_ounce = float(item['xauPrice'])
            price_per_gram = round(price_per_ounce / OUNCE_TO_GRAM, 2)
            return JsonResponse({
                'success': True,
                'price_per_gram_usd': price_per_gram,
                'price_per_ounce_usd': price_per_ounce,
                'updated_at': data.get('date', ''),
            })
        except (requests.RequestException, ValueError, KeyError, IndexError) as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=502)
