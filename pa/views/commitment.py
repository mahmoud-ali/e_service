from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.contrib import messages

from pa.forms.commitment import TblCompanyCommitmentDetailForm

from ..models import STATE_TYPE_CONFIRM, TblCompanyCommitmentDetail, TblCompanyCommitmentMaster
from ..forms import TblCompanyCommitmentForm

from ..tables import TblCompanyCommitmentTable,CommitmentFilter

from .application import ApplicationDeleteMasterDetailView, ApplicationDeleteView, ApplicationListView, ApplicationCreateView, ApplicationMasterDetailCreateView, ApplicationMasterDetailUpdateView, ApplicationReadonlyView, ApplicationUpdateView

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
               "fields":['item','amount_factor'],
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
    
class TblCompanyCommitmentCreateView(ApplicationMasterDetailCreateView):
    model = model_master
    form_class = TblCompanyCommitmentForm
    details = details
    menu_name = "pa:commitment_list"
    title = _("Add new commitment")            

class TblCompanyCommitmentUpdateView(ApplicationMasterDetailUpdateView):
    model = model_master
    form_class = TblCompanyCommitmentForm
    details = details
    menu_name = "pa:commitment_list"
    menu_show_name = "pa:commitment_show"
    title = _("Edit commitment")

class TblCompanyCommitmentReadonlyView(ApplicationReadonlyView):
    model = model_master
    form_class = TblCompanyCommitmentForm
    details = details
    menu_name = "pa:commitment_list"
    menu_edit_name = "pa:commitment_edit"
    menu_delete_name = "pa:commitment_delete"
    title = _("Show added commitment")

class TblCompanyCommitmentDeleteView(ApplicationDeleteMasterDetailView):
    model = model_master
    form_class = TblCompanyCommitmentForm
    details = details
    menu_name = "pa:commitment_list"
    title = _("Delete commitment")
