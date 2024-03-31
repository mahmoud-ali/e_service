from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.contrib import messages

from ..models import STATE_TYPE_CONFIRM, TblCompanyCommitment
from ..forms import TblCompanyCommitmentForm

from ..tables import TblCompanyCommitmentTable,CommitmentFilter

from .application import ApplicationDeleteView, ApplicationListView, ApplicationCreateView, ApplicationReadonlyView, ApplicationUpdateView

class TblCompanyCommitmentListView(ApplicationListView):
    model = TblCompanyCommitment
    table_class = TblCompanyCommitmentTable
    filterset_class = CommitmentFilter
    menu_name = "pa:commitment_list"
    title = _("List of commitments")
    
class TblCompanyCommitmentCreateView(ApplicationCreateView):
    model = TblCompanyCommitment
    form_class = TblCompanyCommitmentForm
    menu_name = "pa:commitment_list"
    title = _("Add new commitment")            

class TblCompanyCommitmentUpdateView(ApplicationUpdateView):
    model = TblCompanyCommitment
    form_class = TblCompanyCommitmentForm
    menu_name = "pa:commitment_list"
    menu_show_name = "pa:commitment_show"
    title = _("Edit commitment")

class TblCompanyCommitmentReadonlyView(ApplicationReadonlyView):
    model = TblCompanyCommitment
    form_class = TblCompanyCommitmentForm
    menu_name = "pa:commitment_list"
    menu_edit_name = "pa:commitment_edit"
    menu_delete_name = "pa:commitment_delete"
    title = _("Show added commitment")

class TblCompanyCommitmentDeleteView(ApplicationDeleteView):
    model = TblCompanyCommitment
    form_class = TblCompanyCommitmentForm
    menu_name = "pa:commitment_list"
    title = _("Delete commitment")
