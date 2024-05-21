from django.utils.translation import gettext_lazy as _

from ..models import TblCompanyOpenningBalanceDetail, TblCompanyOpenningBalanceMaster
from ..forms import TblCompanyOpenningBalanceForm

from ..tables import TblCompanyOpenningBalanceTable,OpenningBalanceFilter

from .application import ApplicationDeleteMasterDetailView, ApplicationListView, ApplicationMasterDetailCreateView, ApplicationMasterDetailUpdateView, ApplicationReadonlyView

model_master = TblCompanyOpenningBalanceMaster
details = [
        {
            "id":1,
            "title":"تفاصيل السجل",
            "args":[
                model_master,
                TblCompanyOpenningBalanceDetail
            ],
            "kwargs":{
               "fields":['item','amount'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
    ]

class TblCompanyOpenningBalanceListView(ApplicationListView):
    model = model_master
    table_class = TblCompanyOpenningBalanceTable
    filterset_class = OpenningBalanceFilter
    menu_name = "pa:openning_balance_list"
    title = _("List of openning balance")
    
class TblCompanyOpenningBalanceCreateView(ApplicationMasterDetailCreateView):
    model = model_master
    form_class = TblCompanyOpenningBalanceForm
    details = details
    menu_name = "pa:openning_balance_list"
    title = _("Add new openning balance")            

class TblCompanyOpenningBalanceUpdateView(ApplicationMasterDetailUpdateView):
    model = model_master
    form_class = TblCompanyOpenningBalanceForm
    details = details
    menu_name = "pa:openning_balance_list"
    menu_show_name = "pa:openning_balance_show"
    title = _("Edit openning balance")

class TblCompanyOpenningBalanceReadonlyView(ApplicationReadonlyView):
    model = model_master
    form_class = TblCompanyOpenningBalanceForm
    details = details
    menu_name = "pa:openning_balance_list"
    menu_edit_name = "pa:openning_balance_edit"
    menu_delete_name = "pa:openning_balance_delete"
    title = _("Show added openning balance")

class TblCompanyOpenningBalanceDeleteView(ApplicationDeleteMasterDetailView):
    model = model_master
    form_class = TblCompanyOpenningBalanceForm
    details = details
    menu_name = "pa:openning_balance_list"
    title = _("Delete openning balance")
