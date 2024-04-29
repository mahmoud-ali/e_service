import datetime
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render

from django.contrib import messages

from company_profile.models import TblCompanyProductionLicense
from pa.forms.request import TblCompanyRequestChooseCommitmentForm

from ..models import STATE_TYPE_CONFIRM, TblCompanyCommitmentMaster, TblCompanyRequestDetail, TblCompanyRequestMaster, TblCompanyRequestReceive
from ..forms import TblCompanyRequestAddForm, TblCompanyRequestShowEditForm
from django_filters.views import FilterView

from ..tables import TblCompanyRequestTable,RequestFilter

from .application import ApplicationDeleteMasterDetailView, ApplicationDeleteView, ApplicationListView, ApplicationCreateView, ApplicationMasterDetailCreateView, ApplicationMasterDetailUpdateView, ApplicationReadonlyView, ApplicationUpdateView
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
        
        obj = TblCompanyCommitmentMaster.objects.get(id=commitment_id)
        license = TblCompanyProductionLicense.objects.filter(company=obj.company).first()
        form = self.form_class(commitment_id=obj.id,initial={
            "commitment": obj,
            "currency": obj.currency,
            "from_dt": license.start_date,
            "to_dt": license.start_date+datetime.timedelta(days=364)
        })

        for detail in self.details_formset:
            if detail.get('id') == 1:
                d_obj = [
                        {'item':c.item,'amount':c.item.calculate_value(c.amount_factor,obj.company)} \
                        for c in obj.tblcompanycommitmentdetail_set.all()
                ]
                detail['formset'].extra=len(d_obj)-1
                formset = detail['formset'](initial=d_obj)
                detail['formset'] = formset

        self.extra_context['form'] = form
        self.extra_context['details'] = self.details_formset
        return render(request, self.template_name, self.extra_context)

class TblCompanyRequestUpdateView(ApplicationMasterDetailUpdateView):
    model = model_master
    form_class = TblCompanyRequestShowEditForm
    details = details
    menu_name = "pa:request_list"
    menu_show_name = "pa:request_show"
    title = _("Edit request")

class TblCompanyRequestReadonlyView(ApplicationReadonlyView):
    model = model_master
    form_class = TblCompanyRequestShowEditForm
    details = details
    menu_name = "pa:request_list"
    menu_edit_name = "pa:request_edit"
    menu_delete_name = "pa:request_delete"
    title = _("Show added request")

class TblCompanyRequestDeleteView(ApplicationDeleteMasterDetailView):
    model = model_master
    form_class = TblCompanyRequestShowEditForm
    details = details
    menu_name = "pa:request_list"
    title = _("Delete request")
