from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib import messages

from pa.forms.payment import TblCompanyPaymentChooseRequestForm
from pa.utils import get_company_types_from_groups

from ..models import TblCompanyCommitmentMaster, TblCompanyPaymentDetail, TblCompanyPaymentMaster, TblCompanyPaymentMethod,TblCompanyRequestMaster,STATE_TYPE_CONFIRM
from ..forms import TblCompanyPaymentShowEditForm,TblCompanyPaymentAddForm,TblCompanyPaymentDetailForm

from ..tables import TblCompanyPaymentTable,PaymentFilter

from .application import ApplicationDeleteMasterDetailView, ApplicationDeleteView, ApplicationListView, ApplicationCreateView, ApplicationMasterDetailCreateView, ApplicationMasterDetailUpdateView, ApplicationReadonlyView, ApplicationUpdateView
from .utils import get_company_details

model_master = TblCompanyPaymentMaster
details = [
        {
            "id":1,
            "title":"تفاصيل السداد",
            "args":[
                model_master,
                TblCompanyPaymentDetail
            ],
            "kwargs":{
               "fields":['item','amount'],
                "extra":0,
                "can_delete":True,
                "min_num":1, 
                "validate_min":True,
            },
        },
        {
            "id":2,
            "title":"طريقة السداد",
            "args":[
                model_master,
                TblCompanyPaymentMethod,
            ],
            "kwargs":{
               "fields":['amount','method','ref_key','attachement_file'],
                "extra":0,
                "can_delete":True,
                "min_num":1, 
                "validate_min":True
            },
        },
    ]

class TblCompanyPaymentListView(ApplicationListView):
    model = model_master
    table_class = TblCompanyPaymentTable
    filterset_class = PaymentFilter
    menu_name = "pa:payment_list"
    title = _("List of payments")

    def get_queryset(self):                
        query = super().get_queryset().select_related("request__commitment","request__commitment__company")
        query = query.filter(request__commitment__company__company_type__in=get_company_types_from_groups(self.request.user))
        return query
    
class TblCompanyPaymentCreateView(ApplicationMasterDetailCreateView):
    model = model_master
    form_class = TblCompanyPaymentAddForm
    details = details
    menu_name = "pa:payment_list"
    title = _("Add new payment")

    def get(self,request, *args, **kwargs):   
        request_id = request.GET.get('request')
        if not request_id:
            self.extra_context['form'] = TblCompanyPaymentChooseRequestForm
            self.extra_context['details'] = []
            return render(request, 'pa/application_choose.html', self.extra_context)
        
        obj = get_object_or_404(TblCompanyRequestMaster,id=request_id)
        form = self.form_class(request_id=request_id,initial={
            "request": obj,
            "currency": obj.currency,
            "payment_dt": timezone.now(),
        })

        for detail in self.details_formset:
            if detail.get('id') == 1:
                # d_obj = [
                #         {'item':c.item,'amount':c.amount-c.get_item_payed_amount()} \
                #         for c in obj.tblcompanyrequestdetail_set.filter(amount__gt=0)
                # ]
                # detail['formset'].extra=len(d_obj)-1
                formset = detail['formset']() #(initial=d_obj)
                detail['formset'] = formset
                
                TblCompanyPaymentDetailFormWithCompanyType=TblCompanyPaymentDetailForm
                TblCompanyPaymentDetailFormWithCompanyType.company_type = obj.commitment.company.company_type
                detail['formset'].form = TblCompanyPaymentDetailFormWithCompanyType

        self.extra_context['company'] = get_company_details(obj.commitment)
        self.extra_context['form'] = form
        self.extra_context['details'] = self.details_formset
        return render(request, self.template_name, self.extra_context)

    def post(self,request,*args, **kwargs):        
        request_id = request.POST.get('request')
        obj = get_object_or_404(TblCompanyRequestMaster,id=request_id)
        form = self.form_class(request.POST,request.FILES,request_id=request_id)

        self.extra_context['company'] = get_company_details(obj.commitment)
        self.extra_context['form'] = form
        return super().post(request,*args, **kwargs)

class TblCompanyPaymentUpdateView(ApplicationMasterDetailUpdateView):
    model = model_master
    form_class = TblCompanyPaymentShowEditForm
    details = details
    menu_name = "pa:payment_list"
    menu_show_name = "pa:payment_show"
    title = _("Edit payment")

    def get(self,request,pk, *args, **kwargs):                 
        obj = self.get_object()
        self.extra_context["form"] = self.form_class(instance=obj)
        self.extra_context["object"] = obj
        for detail in self.details_formset:
            formset = detail['formset'](instance=obj)
            for f in formset:
                if f.fields.get('item'):
                    # print(f.fields)
                    f.fields['item'].queryset = f.fields['item'].queryset.filter(company_type=obj.request.commitment.company.company_type)
            detail['formset'] = formset

            if detail.get('id') == 1:
                TblCompanyPaymentDetailFormWithCompanyType=TblCompanyPaymentDetailForm
                TblCompanyPaymentDetailFormWithCompanyType.company_type = obj.request.commitment.company.company_type
                detail['formset'].form = TblCompanyPaymentDetailFormWithCompanyType


        self.extra_context['company'] = get_company_details(obj.request.commitment)
        self.extra_context['details'] = self.details_formset

        return render(request, self.template_name, self.extra_context)
    
class TblCompanyPaymentReadonlyView(ApplicationReadonlyView):
    model = model_master
    form_class = TblCompanyPaymentShowEditForm
    details = details
    menu_name = "pa:payment_list"
    menu_edit_name = "pa:payment_edit"
    menu_delete_name = "pa:payment_delete"
    title = _("Show added payment")

    def get(self,request,*args, **kwargs):        
        obj = self.get_object()
        self.extra_context['company'] = get_company_details(obj.request.commitment)
        return super().get(request,*args, **kwargs)

class TblCompanyPaymentDeleteView(ApplicationDeleteMasterDetailView):
    model = model_master
    form_class = TblCompanyPaymentShowEditForm
    details = details
    menu_name = "pa:payment_list"
    title = _("Delete payment")

    def get(self,request,*args, **kwargs):        
        obj = self.get_object()
        self.extra_context['company'] = get_company_details(obj.request.commitment)
        return super().get(request,*args, **kwargs)
