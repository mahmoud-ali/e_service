from django.shortcuts import get_object_or_404,render
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.contrib import messages

from company_profile.models import TblCompanyProduction
from pa.forms.commitment import TblCompanyAddCommitmentForm, TblCompanyCommitmentDetailForm, TblCompanyRequestChooseCompanyForm, TblCompanyShowEditCommitmentForm
from pa.utils import get_company_types_from_groups

from ..models import STATE_TYPE_CONFIRM, TblCompanyCommitmentDetail, TblCompanyCommitmentMaster

from ..tables import TblCompanyCommitmentTable,CommitmentFilter

from .application import ApplicationDeleteMasterDetailView, ApplicationDeleteView, ApplicationListView, ApplicationCreateView, ApplicationMasterDetailCreateView, ApplicationMasterDetailUpdateView, ApplicationReadonlyView, ApplicationUpdateView
from .utils import get_company_details

model_master = TblCompanyCommitmentMaster
details = [
        {
            "id":1,
            "title":"تفاصيل السجل",
            "args":[
                model_master,
                TblCompanyCommitmentDetail
            ],
            "kwargs":{
            #    "fields":['item','amount_factor'],
               "form": TblCompanyCommitmentDetailForm,
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
    ]


class TblCompanyCommitmentListView(ApplicationListView):
    model = model_master
    table_class = TblCompanyCommitmentTable
    filterset_class = CommitmentFilter
    menu_name = "pa:commitment_list"
    title = _("List of commitments")
    
    def get_queryset(self):                
        query = super().get_queryset()
        query = query.filter(company__company_type__in=get_company_types_from_groups(self.request.user))
        return query

class TblCompanyCommitmentCreateView(ApplicationMasterDetailCreateView):
    model = model_master
    form_class = TblCompanyAddCommitmentForm
    details = details
    menu_name = "pa:commitment_list"
    title = _("Add new commitment")            

    def get(self,request, *args, **kwargs):   
        company_id = request.GET.get('company')
        if not company_id:
            self.extra_context['form'] = TblCompanyRequestChooseCompanyForm
            self.extra_context['form'].user = request.user
            self.extra_context['details'] = []
            return render(request, 'pa/application_choose.html', self.extra_context)
        
        obj = get_object_or_404(TblCompanyProduction,id=company_id)
        form = self.form_class(company_id=obj.id,initial={
            "company": obj,
        })

        self.extra_context['form'] = form

        for detail in self.details_formset:
            if detail.get('id') == 1:
                TblCompanyCommitmentDetailFormWithCompanyType=TblCompanyCommitmentDetailForm
                TblCompanyCommitmentDetailFormWithCompanyType.company_type = obj.company_type
                detail['formset'].form = TblCompanyCommitmentDetailFormWithCompanyType
        return render(request, self.template_name, self.extra_context)
    
    def post(self,request,*args, **kwargs):        
        company_id = request.POST.get('company')

        form = self.form_class(request.POST,request.FILES,company_id=company_id)

        self.extra_context['form'] = form
        return super().post(request,*args, **kwargs)

class TblCompanyCommitmentUpdateView(ApplicationMasterDetailUpdateView):
    model = model_master
    form_class = TblCompanyShowEditCommitmentForm
    details = details
    menu_name = "pa:commitment_list"
    menu_show_name = "pa:commitment_show"
    title = _("Edit commitment")

    def get(self,request,*args, **kwargs):        
        obj = self.get_object()
        self.extra_context['company'] = get_company_details(obj)

        for detail in self.details_formset:
            if detail.get('id') == 1:
                TblCompanyCommitmentDetailFormWithCompanyType=TblCompanyCommitmentDetailForm
                TblCompanyCommitmentDetailFormWithCompanyType.company_type = obj.company.company_type
                detail['formset'].form = TblCompanyCommitmentDetailFormWithCompanyType

        return super().get(request,*args, **kwargs)

class TblCompanyCommitmentReadonlyView(ApplicationReadonlyView):
    model = model_master
    form_class = TblCompanyShowEditCommitmentForm
    details = details
    menu_name = "pa:commitment_list"
    menu_edit_name = "pa:commitment_edit"
    menu_delete_name = "pa:commitment_delete"
    title = _("Show added commitment")

    def get(self,request,*args, **kwargs):        
        obj = self.get_object()
        self.extra_context['company'] = get_company_details(obj)

        for detail in self.details_formset:
            if detail.get('id') == 1:
                TblCompanyCommitmentDetailFormWithCompanyType=TblCompanyCommitmentDetailForm
                TblCompanyCommitmentDetailFormWithCompanyType.company_type = obj.company.company_type
                detail['formset'].form = TblCompanyCommitmentDetailFormWithCompanyType

        return super().get(request,*args, **kwargs)

class TblCompanyCommitmentDeleteView(ApplicationDeleteMasterDetailView):
    model = model_master
    form_class = TblCompanyShowEditCommitmentForm
    details = details
    menu_name = "pa:commitment_list"
    title = _("Delete commitment")

    def get(self,request,*args, **kwargs):        
        obj = self.get_object()
        self.extra_context['company'] = get_company_details(obj)
        return super().get(request,*args, **kwargs)

