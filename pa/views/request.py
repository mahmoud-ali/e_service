from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.contrib import messages

from ..models import STATE_TYPE_CONFIRM, TblCompanyRequest
from ..forms import TblCompanyRequestForm
from django_filters.views import FilterView

from ..tables import TblCompanyRequestTable,RequestFilter

from .application import ApplicationConfirmStateView, ApplicationListView, ApplicationCreateView, ApplicationReadonlyView

class TblCompanyRequestListView(ApplicationListView,FilterView):
    model = TblCompanyRequest
    table_class = TblCompanyRequestTable
    filterset_class = RequestFilter
    menu_name = "pa:request_list"
    title = _("List of requests")
    
    # def dispatch(self, *args, **kwargs):         
    #     # if not hasattr(self.request.user,"pro_company"):
    #     #     return HttpResponseRedirect(reverse_lazy("pa:home"))    
            
    #     return super().dispatch(*args, **kwargs)        
            
    # def get_queryset(self):

    #     query = super().get_queryset()        
    #     return query


class TblCompanyRequestCreateView(ApplicationCreateView):
    model = TblCompanyRequest
    form_class = TblCompanyRequestForm
    menu_name = "pa:request_list"
    title = _("Add new request")

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
        
        messages.add_message(self.request,messages.SUCCESS,_("Record saved successfully."))
        
        # info = (self.object._meta.app_label, self.object._meta.model_name)
        # resp_user = get_sumitted_responsible('pro_company')
        # url = 'https://'+Site.objects.get_current().domain+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
        # send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
        
        return HttpResponseRedirect(self.get_success_url())
        
class TblCompanyRequestReadonlyView(ApplicationReadonlyView):
    model = TblCompanyRequest
    form_class = TblCompanyRequestForm
    menu_name = "pa:request_list"
    title = _("Show added request")

    def dispatch(self, *args, **kwargs):         
        # if not hasattr(self.request.user,"pro_company"):
        #     return HttpResponseRedirect(reverse_lazy("pa:home"))               
        return super().dispatch(*args, **kwargs)        

    def get_queryset(self):
        query = super().get_queryset()        
        return query

class TblCompanyRequestConfirmStateView(ApplicationConfirmStateView):
    model = TblCompanyRequest
    menu_name = "pa:request_show"
