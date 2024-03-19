from django.shortcuts import render
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

from ..models import AppImportPermission, AppImportPermissionDetail
from ..forms import AppImportPermissionForm

from ..workflow import STATE_CHOICES,SUBMITTED,ACCEPTED,APPROVED,REJECTED,send_transition_email,get_sumitted_responsible
from ..tables import AppImportPermissionTable

from .application import ApplicationListView, ApplicationMasterDetailCreateView, ApplicationMasterDetailReadonlyView

class AppImportPermissionListView(ApplicationListView):
    model = AppImportPermission
    table_class = AppImportPermissionTable
    menu_name = "profile:app_import_permission_list"
    title = _("List of Import Permissions")
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            
    def get_queryset(self):

        query = super().get_queryset()        
        return query.filter(company__id=self.request.user.pro_company.company.id)


class AppImportPermissionCreateView(ApplicationMasterDetailCreateView):
    model = AppImportPermission
    model_details = AppImportPermissionDetail
    model_details_fields = ["import_material_name","import_qty"]
    form_class = AppImportPermissionForm
    detail_formset = None
    menu_name = "profile:app_import_permission_list"
    title = _("Add Import Permission")
    template_name = "company_profile/application_add_master_details.html"

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST,request.FILES)
        self.extra_context["form"] = form
        
        if form.is_valid():
            self.object = form.save(commit=False)
            
            self.object.company = request.user.pro_company.company
            self.object.created_by = self.object.updated_by = request.user
            
        
            formset = self.detail_formset(request.POST,instance=self.object)
            self.extra_context["detail_formset"] = formset
            if formset.is_valid():
                self.object.save()
                formset.save()
                
                messages.add_message(request,messages.SUCCESS,_("Application sent successfully."))
                
                info = (self.object._meta.app_label, self.object._meta.model_name)
                resp_user = get_sumitted_responsible('pro_company')
                url = 'https://'+Site.objects.get_current().domain+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
                send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
                
                return HttpResponseRedirect(self.success_url)
            
            return render(request, self.template_name, self.extra_context)

class AppImportPermissionReadonlyView(ApplicationMasterDetailReadonlyView):
    model = AppImportPermission
    model_details = AppImportPermissionDetail
    model_details_fields = ["import_material_name","import_qty"]
    form_class = AppImportPermissionForm
    detail_formset = None
    menu_name = "profile:app_import_permission_list"
    title = _("Show Import Permission")
