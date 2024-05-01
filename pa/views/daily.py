from django.shortcuts import render
from django.views.generic import View
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models import FloatField, CharField, Value,Sum,F
from django.contrib.auth.mixins import LoginRequiredMixin

from .application import TranslationMixin
from ..forms import PaDailyForm
from ..models import TblCompanyOpenningBalanceDetail, TblCompanyOpenningBalanceMaster, TblCompanyPaymentDetail, TblCompanyRequestDetail, TblCompanyRequestMaster,TblCompanyPaymentMaster,STATE_TYPE_CONFIRM

class PaDailyView(LoginRequiredMixin,TranslationMixin,View):
    form = PaDailyForm
    menu_name = "pa:daily_list"
    title = _("Pa_daily page")
    template_name = "pa/pa_daily.html"     

    def dispatch(self, *args, **kwargs):         
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title,
                            "table":None,
         }
        return super().dispatch(*args, **kwargs)       
        
    def get(self, request, *args, **kwargs):
        form = self.form(request.GET)
        qs = None

        self.extra_context["form"] = self.form
        self.extra_context["qs"] = qs
        self.extra_context["is_get"] = True
        
        return render(request, self.template_name, self.extra_context)
    
    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        qs = None
        request_total = 0
        payment_total = 0

        if form.is_valid():
            company = form.cleaned_data["company"]
            currency = form.cleaned_data["currency"]
            from_dt = form.cleaned_data["from_dt"]
            to_dt = form.cleaned_data["to_dt"]
            openning_qs_all = TblCompanyOpenningBalanceDetail.objects.filter(
                commitment_master__state=STATE_TYPE_CONFIRM,
            )

            if company:
                openning_qs_all = openning_qs_all.filter(
                    commitment_master__company=company,
                )

            openning_total = openning_qs_all.aggregate(total=Sum("amount"))['total'] or 0

            request_qs_all = TblCompanyRequestDetail.objects.filter(
                    request_master__state=STATE_TYPE_CONFIRM,
                ).annotate(
                    exchange_rate=Value('1.0', output_field=FloatField()),
                    type=Value('request', output_field=CharField()),
                )
            if company:
                request_qs_all = request_qs_all.filter(
                        request_master__commitment__company=company,
                )
            if currency:
                request_qs_all = request_qs_all.filter(
                        request_master__currency=currency,
                )
            request_qs = request_qs_all.filter(
                    request_master__created_at__date__range=(from_dt,to_dt)
            )

            request_total = request_qs.aggregate(total=Sum("amount"))['total']
            request_total_befor = request_qs_all \
                .filter(request_master__created_at__date__lt=from_dt) \
                .aggregate(total=Sum("amount"))['total'] or 0
            
            request_qs = request_qs.values_list("request_master__id","request_master__created_at","item__name","amount","request_master__currency","exchange_rate","type") #,"request_master__commitment__company__name_ar"

            payment_qs_all = TblCompanyPaymentDetail.objects.filter(
                    payment_master__state=STATE_TYPE_CONFIRM,
                ).annotate(
                    type=Value('payment', output_field=CharField()),
                )
            
            if company:
                payment_qs_all = payment_qs_all.filter(
                        payment_master__request__commitment__company=company,
                )
            if currency:
                payment_qs_all = payment_qs_all.filter(
                        payment_master__request__currency=currency,
                )

            payment_qs = payment_qs_all.filter(
                    payment_master__created_at__date__range=(from_dt,to_dt)
            )
            
            payment_total = payment_qs.aggregate(amount__sum=Sum(F("amount")*F("payment_master__exchange_rate")))['amount__sum']
            payment_total_before = payment_qs_all \
                .filter(payment_master__created_at__date__lt=from_dt) \
                .aggregate(amount__sum=Sum(F("amount")*F("payment_master__exchange_rate")))['amount__sum'] or 0

            payment_qs = payment_qs.values_list("payment_master__id","payment_master__created_at","item__name","amount","payment_master__currency","payment_master__exchange_rate","type") #,"payment_master__request__commitment__company__name_ar"

            qs = request_qs.union(payment_qs).order_by("request_master__created_at")

            data = []
            balance_opening = openning_total + request_total_befor - payment_total_before
            balance = balance_opening
            for d in qs:
                a = list(d)
                if a[6] == 'payment':
                    balance -= a[3]
                else:
                    balance += a[3]
                a.append(balance)
                data.append(a)

            self.extra_context["form"] = form
            self.extra_context["data"] = data
            self.extra_context["opening"] = openning_total or 0
            self.extra_context["request_opening"] = request_total_befor or 0
            self.extra_context["payment_opening"] = payment_total_before or 0
            self.extra_context["balance_opening"] = balance_opening or 0
            self.extra_context["request_total"] = request_total or 0
            self.extra_context["payment_total"] = payment_total or 0
            self.extra_context["balance_total"] = balance or 0
        
        return render(request, self.template_name, self.extra_context)
