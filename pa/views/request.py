from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.contrib import messages

from ..models import STATE_TYPE_CONFIRM, TblCompanyRequest
from ..forms import TblCompanyRequestAddForm, TblCompanyRequestShowEditForm
from django_filters.views import FilterView

from ..tables import TblCompanyRequestTable,RequestFilter

from .application import ApplicationDeleteView, ApplicationListView, ApplicationCreateView, ApplicationReadonlyView, ApplicationUpdateView

class TblCompanyRequestListView(ApplicationListView,FilterView):
    model = TblCompanyRequest
    table_class = TblCompanyRequestTable
    filterset_class = RequestFilter
    menu_name = "pa:request_list"
    title = _("List of requests")
    
class TblCompanyRequestCreateView(ApplicationCreateView):
    model = TblCompanyRequest
    form_class = TblCompanyRequestAddForm
    menu_name = "pa:request_list"
    title = _("Add new request")

class TblCompanyRequestUpdateView(ApplicationUpdateView):
    model = TblCompanyRequest
    form_class = TblCompanyRequestShowEditForm
    menu_name = "pa:request_list"
    menu_show_name = "pa:request_show"
    title = _("Edit request")

class TblCompanyRequestReadonlyView(ApplicationReadonlyView):
    model = TblCompanyRequest
    form_class = TblCompanyRequestShowEditForm
    menu_name = "pa:request_list"
    menu_edit_name = "pa:request_edit"
    menu_delete_name = "pa:request_delete"
    title = _("Show added request")

class TblCompanyRequestDeleteView(ApplicationDeleteView):
    model = TblCompanyRequest
    form_class = TblCompanyRequestShowEditForm
    menu_name = "pa:request_list"
    title = _("Delete request")
