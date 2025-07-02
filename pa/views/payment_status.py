from django.shortcuts import render
from django.views.generic import View
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models import FloatField, CharField, Value,Sum,F
from django.contrib.auth.mixins import LoginRequiredMixin

from .application import TranslationMixin, UserPermissionMixin
from ..forms import PaDailyForm
from ..models import TblCompanyOpenningBalanceDetail, TblCompanyOpenningBalanceMaster, TblCompanyPaymentDetail, TblCompanyRequestDetail, TblCompanyRequestMaster,TblCompanyPaymentMaster,STATE_TYPE_CONFIRM

class PaymentStatusView(LoginRequiredMixin,UserPermissionMixin,TranslationMixin,View):
    form = PaDailyForm
    menu_name = "pa:payment_status"
    title = "إيرادات الشركات"
    template_name = "pa/payment_status.html"     
    user_groups = ['pa_data_entry','pa_manager']

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
            qs = TblCompanyPaymentDetail.objects.filter(
                payment_master__payment_dt__gte=from_dt,
                payment_master__payment_dt__lte=to_dt,
                payment_master__currency=currency,
                payment_master__state=STATE_TYPE_CONFIRM,
            )

            if company:
                qs = qs.filter(
                    payment_master__request__commitment__company=company,
                )

            qs = qs.values("item__name").annotate(
                total=Sum("amount", output_field=FloatField()),
            ).filter(
                total__gt=0,
            ).order_by("item__name")

            # print(qs)
            sum_payment = 0

            for obj in qs:
                sum_payment += obj.get('total', 0)

            self.extra_context["qs"] = qs
            self.extra_context["sum_payment"] = sum_payment

        self.extra_context["form"] = form
        return render(request, self.template_name, self.extra_context)
