from django.forms import ValidationError
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.contrib import messages

from ..models import TblCompanyPaymentDetail, TblCompanyPaymentMaster, TblCompanyPaymentMethod,TblCompanyRequestMaster,STATE_TYPE_CONFIRM
from ..forms import TblCompanyPaymentShowEditForm,TblCompanyPaymentAddForm

from ..tables import TblCompanyPaymentTable,PaymentFilter

from .application import ApplicationDeleteMasterDetailView, ApplicationDeleteView, ApplicationListView, ApplicationCreateView, ApplicationMasterDetailCreateView, ApplicationMasterDetailUpdateView, ApplicationReadonlyView, ApplicationUpdateView

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
                "validate_min":True
            },
        },
        {
            "id":1,
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
    
class TblCompanyPaymentCreateView(ApplicationMasterDetailCreateView):
    model = model_master
    form_class = TblCompanyPaymentAddForm
    details = details
    menu_name = "pa:payment_list"
    title = _("Add new payment")

class TblCompanyPaymentUpdateView(ApplicationMasterDetailUpdateView):
    model = model_master
    form_class = TblCompanyPaymentShowEditForm
    details = details
    menu_name = "pa:payment_list"
    menu_show_name = "pa:payment_show"
    title = _("Edit payment")

class TblCompanyPaymentReadonlyView(ApplicationReadonlyView):
    model = model_master
    form_class = TblCompanyPaymentShowEditForm
    details = details
    menu_name = "pa:payment_list"
    menu_edit_name = "pa:payment_edit"
    menu_delete_name = "pa:payment_delete"
    title = _("Show added payment")

class TblCompanyPaymentDeleteView(ApplicationDeleteMasterDetailView):
    model = model_master
    form_class = TblCompanyPaymentShowEditForm
    details = details
    menu_name = "pa:payment_list"
    title = _("Delete payment")
