import datetime
from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.contrib import messages

from company_profile.models import TblCompanyProductionLicense
from pa.forms.commitment import TblCompanyCommitmentDetailForm, TblCompanyCommitmentScheduleForm
from pa.forms.request import TblCompanyRequestChooseCommitmentForm
from pa.tables.commitment_schedule import CommitmentScheduleFilter, TblCompanyCommitmentScheduleTable

from ..models import STATE_TYPE_CONFIRM, TblCompanyCommitmentDetail, TblCompanyCommitmentMaster, TblCompanyCommitmentSchedular
from ..forms import TblCompanyCommitmentForm

from ..tables import TblCompanyCommitmentTable,CommitmentFilter

from .application import ApplicationDeleteMasterDetailView, ApplicationDeleteView, ApplicationListView, ApplicationCreateView, ApplicationMasterDetailCreateView, ApplicationMasterDetailUpdateView, ApplicationReadonlyView, ApplicationUpdateView

model_master = TblCompanyCommitmentSchedular

class TblCompanyCommitmentScheduleListView(ApplicationListView):
    model = model_master
    table_class = TblCompanyCommitmentScheduleTable
    filterset_class = CommitmentScheduleFilter
    menu_name = "pa:commitment_schedule_list"
    title = _("List of commitments scheduler")
    
class TblCompanyCommitmentScheduleCreateView(ApplicationCreateView):
    model = model_master
    form_class = TblCompanyCommitmentScheduleForm
    menu_name = "pa:commitment_schedule_list"
    title = _("Add new commitment schedule")            

    def get(self,request, *args, **kwargs):   
        commitment_id = request.GET.get('commitment')
        if not commitment_id:
            self.extra_context['form'] = TblCompanyRequestChooseCommitmentForm
            return render(request, 'pa/application_choose.html', self.extra_context)
        
        obj = TblCompanyCommitmentMaster.objects.get(id=commitment_id)
        license = TblCompanyProductionLicense.objects.filter(company=obj.company).first()
        form = self.form_class(initial={
            "commitment": obj,
            "request_interval": self.model.INTERVAL_TYPE_YEAR,
            "request_next_interval_dt": license.start_date,
        })

        self.extra_context['form'] = form
        return render(request, self.template_name, self.extra_context)

class TblCompanyCommitmentScheduleUpdateView(ApplicationUpdateView):
    model = model_master
    form_class = TblCompanyCommitmentScheduleForm
    menu_name = "pa:commitment_schedule_list"
    menu_show_name = "pa:commitment_schedule_show"
    title = _("Edit commitment schedule")

class TblCompanyCommitmentScheduleReadonlyView(ApplicationReadonlyView):
    model = model_master
    form_class = TblCompanyCommitmentScheduleForm
    menu_name = "pa:commitment_schedule_list"
    menu_edit_name = "pa:commitment_schedule_edit"
    menu_delete_name = "pa:commitment_schedule_delete"
    title = _("Show commitment schedule")

class TblCompanyCommitmentScheduleDeleteView(ApplicationDeleteView):
    model = model_master
    form_class = TblCompanyCommitmentScheduleForm
    menu_name = "pa:commitment_schedule_list"
    title = _("Delete commitment schedule")
