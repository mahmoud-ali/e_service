from django.forms import ValidationError
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.contrib import messages

from ..models import TblCompanyPayment,TblCompanyRequest,STATE_TYPE_CONFIRM
from ..forms import TblCompanyPaymentShowEditForm,TblCompanyPaymentAddForm

from ..tables import TblCompanyPaymentTable,PaymentFilter

from .application import ApplicationDeleteView, ApplicationListView, ApplicationCreateView, ApplicationReadonlyView, ApplicationUpdateView

class TblCompanyPaymentListView(ApplicationListView):
    model = TblCompanyPayment
    table_class = TblCompanyPaymentTable
    filterset_class = PaymentFilter
    menu_name = "pa:payment_list"
    title = _("List of payments")
    
class TblCompanyPaymentCreateView(ApplicationCreateView):
    model = TblCompanyPayment
    form_class = TblCompanyPaymentAddForm
    menu_name = "pa:payment_list"
    title = _("Add new payment")

class TblCompanyPaymentUpdateView(ApplicationUpdateView):
    model = TblCompanyPayment
    form_class = TblCompanyPaymentShowEditForm
    menu_name = "pa:payment_list"
    menu_show_name = "pa:payment_show"
    title = _("Edit payment")

class TblCompanyPaymentReadonlyView(ApplicationReadonlyView):
    model = TblCompanyPayment
    form_class = TblCompanyPaymentShowEditForm
    menu_name = "pa:payment_list"
    menu_edit_name = "pa:payment_edit"
    menu_delete_name = "pa:payment_delete"
    title = _("Show added payment")

class TblCompanyPaymentDeleteView(ApplicationDeleteView):
    model = TblCompanyPayment
    form_class = TblCompanyPaymentShowEditForm
    menu_name = "pa:payment_list"
    title = _("Delete payment")
