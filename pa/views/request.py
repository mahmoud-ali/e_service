import datetime
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404, render

from django.contrib import messages

from company_profile.models import TblCompanyProductionLicense
from pa.forms.request import TblCompanyRequestChooseCommitmentForm
from pa.utils import get_company_types_from_groups

from ..models import STATE_TYPE_CONFIRM, TblCompanyCommitmentMaster, TblCompanyRequestDetail, TblCompanyRequestMaster, TblCompanyRequestReceive
from ..forms import TblCompanyRequestAddForm, TblCompanyRequestShowEditForm, TblCompanyRequestDetailsForm
from django_filters.views import FilterView

from ..tables import TblCompanyRequestTable,RequestFilter

from .application import ApplicationDeleteMasterDetailView, ApplicationDeleteView, ApplicationListView, ApplicationCreateView, ApplicationMasterDetailCreateView, ApplicationMasterDetailUpdateView, ApplicationReadonlyView, ApplicationUpdateView
from .utils import get_company_details

model_master = TblCompanyRequestMaster
details = [
        {
            "id":1,
            "title":"تفاصيل المطالبة",
            "args":[
                model_master,
                TblCompanyRequestDetail
            ],
            "kwargs":{
               "fields":['item','amount'],
                "form": TblCompanyRequestDetailsForm,
                "extra":0,
                "can_delete":True,
                "min_num":1, 
                "validate_min":True,
            },
        },
    ]

class TblCompanyRequestListView(ApplicationListView,FilterView):
    model = model_master
    table_class = TblCompanyRequestTable
    filterset_class = RequestFilter
    menu_name = "pa:request_list"
    title = _("List of requests")
    
    def get_queryset(self):                
        query = super().get_queryset()
        query = query.filter(commitment__company__company_type__in=get_company_types_from_groups(self.request.user))
        return query

class TblCompanyRequestCreateView(ApplicationMasterDetailCreateView):
    model = model_master
    form_class = TblCompanyRequestAddForm
    details = details
    menu_name = "pa:request_list"
    title = _("Add new request")

    def get(self,request, *args, **kwargs):   
        commitment_id = request.GET.get('commitment')
        if not commitment_id:
            self.extra_context['form'] = TblCompanyRequestChooseCommitmentForm
            self.extra_context['details'] = []
            return render(request, 'pa/application_choose.html', self.extra_context)
        
        obj = get_object_or_404(TblCompanyCommitmentMaster,id=commitment_id)
        license = TblCompanyProductionLicense.objects.filter(company=obj.company).first()
        form = self.form_class(commitment_id=obj.id,initial={
            "commitment": obj,
            "currency": obj.currency,
            "from_dt": license.start_date,
            "to_dt": license.start_date+datetime.timedelta(days=364)
        })

        for detail in self.details_formset:
            if detail.get('id') == 1:
                TblCompanyRequestDetailsFormWithCompanyType=TblCompanyRequestDetailsForm
                TblCompanyRequestDetailsFormWithCompanyType.company_type = license.company.company_type
                d_obj = [
                        {'item':c.item,'amount':c.item.calculate_value(c.amount_factor,obj.company)} \
                        for c in obj.tblcompanycommitmentdetail_set.all()
                ]
                detail['formset'].extra=len(d_obj)-1
                detail['formset'].form = TblCompanyRequestDetailsFormWithCompanyType
                formset = detail['formset'](initial=d_obj)
                detail['formset'] = formset

        self.extra_context['company'] = get_company_details(obj)
        self.extra_context['form'] = form
        self.extra_context['details'] = self.details_formset
        return render(request, self.template_name, self.extra_context)
    
    def post(self,request,*args, **kwargs):        
        commitment_id = request.POST.get('commitment')
        commitment = get_object_or_404(TblCompanyCommitmentMaster,id=commitment_id)

        form = self.form_class(request.POST,request.FILES,commitment_id=commitment_id)

        self.extra_context['company'] = get_company_details(commitment)
        self.extra_context['form'] = form
        return super().post(request,*args, **kwargs)

class TblCompanyRequestUpdateView(ApplicationMasterDetailUpdateView):
    model = model_master
    form_class = TblCompanyRequestShowEditForm
    details = details
    menu_name = "pa:request_list"
    menu_show_name = "pa:request_show"
    title = _("Edit request")

    def get(self,request,*args, **kwargs):        
        obj = self.get_object()
        license = TblCompanyProductionLicense.objects.filter(company=obj.commitment.company).first()
        self.extra_context['company'] = get_company_details(obj.commitment)

        for detail in self.details_formset:
            if detail.get('id') == 1:
                TblCompanyRequestDetailsFormWithCompanyType=TblCompanyRequestDetailsForm
                TblCompanyRequestDetailsFormWithCompanyType.company_type = license.company.company_type
                detail['formset'].form = TblCompanyRequestDetailsFormWithCompanyType

        return super().get(request,*args, **kwargs)

class TblCompanyRequestReadonlyView(ApplicationReadonlyView):
    model = model_master
    form_class = TblCompanyRequestShowEditForm
    details = details
    menu_name = "pa:request_list"
    menu_edit_name = "pa:request_edit"
    menu_delete_name = "pa:request_delete"
    title = _("Show added request")

    def get(self,request,*args, **kwargs):        
        obj = self.get_object()
        self.extra_context['company'] = get_company_details(obj.commitment)
        return super().get(request,*args, **kwargs)

class TblCompanyRequestDeleteView(ApplicationDeleteMasterDetailView):
    model = model_master
    form_class = TblCompanyRequestShowEditForm
    details = details
    menu_name = "pa:request_list"
    title = _("Delete request")

    def get(self,request,*args, **kwargs):        
        obj = self.get_object()
        self.extra_context['company'] = get_company_details(obj.commitment)
        return super().get(request,*args, **kwargs)
