from django.shortcuts import render
from django.views.generic import View
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models import FloatField, CharField, Value,Sum,F
from django.contrib.auth.mixins import LoginRequiredMixin

from .application import TranslationMixin
from ..forms import PaDailyForm
from ..models import TblCompanyRequest,TblCompanyPayment,STATE_TYPE_CONFIRM

class PaDailyView(LoginRequiredMixin,TranslationMixin,View):
    form = PaDailyForm
    menu_name = "pa:daily_list"
    title = _("List of payments")
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
            from_dt = form.cleaned_data["from_dt"]
            to_dt = form.cleaned_data["to_dt"]
            request_qs = TblCompanyRequest.objects.filter(
                    commitement__company=company,
                    created_at__gte=from_dt,
                    created_at__lte=to_dt,
                    state=STATE_TYPE_CONFIRM,
                ).annotate(
                    exchange_rate=Value('1', output_field=FloatField()),
                    type=Value('request', output_field=CharField()),
                )
            
            request_total = request_qs.aggregate(Sum("amount"))['amount__sum']
            
            request_qs = request_qs.values_list("id","created_at","commitement__item__name","amount","currency","exchange_rate","type")
            
            payment_qs = TblCompanyPayment.objects.filter(
                    request__commitement__company=company,
                    created_at__date__gte=from_dt,
                    created_at__date__lte=to_dt,
                    state=STATE_TYPE_CONFIRM,
                ).annotate(
                    type=Value('payment', output_field=CharField()),
                )
            
            payment_total = payment_qs.aggregate(amount__sum=Sum(F("amount")*F("exchange_rate")))['amount__sum']

            payment_qs = payment_qs.values_list("id","created_at","request__commitement__item__name","amount","currency","exchange_rate","type")
            
            qs = request_qs.union(payment_qs).order_by("created_at")

        self.extra_context["form"] = form
        self.extra_context["qs"] = qs
        self.extra_context["request_total"] = request_total or 0
        self.extra_context["payment_total"] = payment_total or 0
        
        return render(request, self.template_name, self.extra_context)
