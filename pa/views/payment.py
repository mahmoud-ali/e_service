from django.forms import ValidationError
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.contrib import messages

from ..models import TblCompanyPayment,TblCompanyRequest,STATE_TYPE_CONFIRM
from ..forms import TblCompanyPaymentShowForm,TblCompanyPaymentEditForm

from ..tables import TblCompanyPaymentTable,PaymentFilter

from .application import ApplicationDeleteView, ApplicationListView, ApplicationCreateView, ApplicationReadonlyView, ApplicationUpdateView

class TblCompanyPaymentListView(ApplicationListView):
    model = TblCompanyPayment
    table_class = TblCompanyPaymentTable
    filterset_class = PaymentFilter
    menu_name = "pa:payment_list"
    title = _("List of payments")
    
    # def dispatch(self, *args, **kwargs):         
    #     # if not hasattr(self.request.user,"pro_company"):
    #     #     return HttpResponseRedirect(reverse_lazy("pa:home"))    
            
    #     return super().dispatch(*args, **kwargs)        
            
    # def get_queryset(self):

    #     query = super().get_queryset()        
    #     return query


class TblCompanyPaymentCreateView(ApplicationCreateView):
    model = TblCompanyPayment
    form_class = TblCompanyPaymentEditForm
    menu_name = "pa:payment_list"
    title = _("Add new payment")

    def dispatch(self, *args, **kwargs):         
        # if not hasattr(self.request.user,"pro_company"):
        #     return HttpResponseRedirect(reverse_lazy("pa:home"))    
            
        return super().dispatch(*args, **kwargs)        
            

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.created_by = self.object.updated_by = self.request.user

        if self.request.POST.get('_save_confirm'):
            self.object.state = STATE_TYPE_CONFIRM            

        self.object.save()

        if self.object.state == STATE_TYPE_CONFIRM:
            self.object.request.update_payment_state()
        
        messages.add_message(self.request,messages.SUCCESS,_("Record saved successfully."))
        
        # info = (self.object._meta.app_label, self.object._meta.model_name)
        # resp_user = get_sumitted_responsible('pro_company')
        # url = 'https://'+Site.objects.get_current().domain+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
        # send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
        
        return HttpResponseRedirect(self.get_success_url())

class TblCompanyPaymentUpdateView(ApplicationUpdateView):
    model = TblCompanyPayment
    form_class = TblCompanyPaymentEditForm
    menu_name = "pa:payment_list"
    menu_show_name = "pa:payment_show"
    title = _("Edit payment")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.updated_by = self.request.user

        if self.request.POST.get('_save_confirm'):
            self.object.state = STATE_TYPE_CONFIRM            

        self.object.save()

        if self.object.state == STATE_TYPE_CONFIRM:
            self.object.request.update_payment_state()
        
        messages.add_message(self.request,messages.SUCCESS,_("Record saved successfully."))
                
        return HttpResponseRedirect(self.get_success_url())

class TblCompanyPaymentReadonlyView(ApplicationReadonlyView):
    model = TblCompanyPayment
    form_class = TblCompanyPaymentShowForm
    menu_name = "pa:payment_list"
    menu_edit_name = "pa:payment_edit"
    menu_delete_name = "pa:payment_delete"
    title = _("Show added payment")

    def dispatch(self, *args, **kwargs):         
        # if not hasattr(self.request.user,"pro_company"):
        #     return HttpResponseRedirect(reverse_lazy("pa:home"))               
        return super().dispatch(*args, **kwargs)        

    def get_queryset(self):
        query = super().get_queryset()        
        return query

class TblCompanyPaymentDeleteView(ApplicationDeleteView):
    model = TblCompanyPayment
    form_class = TblCompanyPaymentShowForm
    menu_name = "pa:payment_list"
    title = _("Delete payment")
