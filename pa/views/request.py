from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.contrib import messages

from ..models import STATE_TYPE_CONFIRM, TblCompanyRequest
from ..forms import TblCompanyRequestEditForm, TblCompanyRequestShowForm
from django_filters.views import FilterView

from ..tables import TblCompanyRequestTable,RequestFilter

from .application import ApplicationDeleteView, ApplicationListView, ApplicationCreateView, ApplicationReadonlyView, ApplicationUpdateView

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
    form_class = TblCompanyRequestEditForm
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

        if self.object.state == STATE_TYPE_CONFIRM:
            self.object.send_email()
        
        messages.add_message(self.request,messages.SUCCESS,_("Record saved successfully."))
        
        # info = (self.object._meta.app_label, self.object._meta.model_name)
        # resp_user = get_sumitted_responsible('pro_company')
        # url = 'https://'+Site.objects.get_current().domain+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
        # send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
        
        return HttpResponseRedirect(self.get_success_url())

class TblCompanyRequestUpdateView(ApplicationUpdateView):
    model = TblCompanyRequest
    form_class = TblCompanyRequestEditForm
    menu_name = "pa:request_list"
    menu_show_name = "pa:request_show"
    title = _("Edit request")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.updated_by = self.request.user

        if self.request.POST.get('_save_confirm'):
            self.object.state = STATE_TYPE_CONFIRM

        self.object.save()

        if self.object.state == STATE_TYPE_CONFIRM:
            self.object.send_email()
        
        messages.add_message(self.request,messages.SUCCESS,_("Record saved successfully."))
                
        return HttpResponseRedirect(self.get_success_url())

class TblCompanyRequestReadonlyView(ApplicationReadonlyView):
    model = TblCompanyRequest
    form_class = TblCompanyRequestShowForm
    menu_name = "pa:request_list"
    menu_edit_name = "pa:request_edit"
    menu_delete_name = "pa:request_delete"
    title = _("Show added request")

    def dispatch(self, *args, **kwargs):         
        # if not hasattr(self.request.user,"pro_company"):
        #     return HttpResponseRedirect(reverse_lazy("pa:home"))               
        return super().dispatch(*args, **kwargs)        

class TblCompanyRequestDeleteView(ApplicationDeleteView):
    model = TblCompanyRequest
    form_class = TblCompanyRequestShowForm
    menu_name = "pa:request_list"
    title = _("Delete request")
