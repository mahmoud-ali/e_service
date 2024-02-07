from django.urls import reverse_lazy
from django.views.generic import View,ListView,CreateView
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.utils import translation

from django.conf import settings

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site

from django_tables2 import SingleTableView
from django_tables2.paginators import LazyPaginator

from ..models import AppExplorationTime
from ..forms import AppExplorationTimeForm

from ..workflow import STATE_CHOICES,SUBMITTED,ACCEPTED,APPROVED,REJECTED,send_transition_email,get_sumitted_responsible
from ..tables import AppExplorationTimeTable

from .application import ApplicationListView, ApplicationCreateView, ApplicationReadonlyView

class AppExplorationTimeListView(ApplicationListView):
    model = AppExplorationTime
    table_class = AppExplorationTimeTable
    menu_name = "profile:app_exploration_time_list"
    title = _("List of exploration times")
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            
    def get_queryset(self):

        query = super().get_queryset()        
        return query.filter(company__id=self.request.user.pro_company.company.id)


class AppExplorationTimeCreateView(ApplicationCreateView):
    model = AppExplorationTime
    form_class = AppExplorationTimeForm
    menu_name = "profile:app_exploration_time_list"
    title = _("Add new exploration time")

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.company = self.request.user.pro_company.company
        self.object.created_by = self.object.updated_by = self.request.user

        self.object.expo_cause_for_change_file = self.request.FILES["expo_cause_for_change_file"]
        self.object.save()
        
        messages.add_message(self.request,messages.SUCCESS,_("Application sent successfully."))
        
        info = (self.object._meta.app_label, self.object._meta.model_name)
        resp_user = get_sumitted_responsible('pro_company')
        url = 'https://'+Site.objects.get_current().domain+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
        send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
        
        return HttpResponseRedirect(self.get_success_url())
        
class AppExplorationTimeReadonlyView(ApplicationReadonlyView):
    model = AppExplorationTime
    form_class = AppExplorationTimeForm
    menu_name = "profile:app_exploration_time_list"
    title = _("Show exploration time")

