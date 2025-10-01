from django.shortcuts import render,get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import View,ListView,CreateView
from django.views.generic.detail import SingleObjectMixin

from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.forms import ModelForm

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from django_tables2 import SingleTableView
from django_tables2.paginators import LazyPaginator

from bootstrap_datepicker_plus.widgets import DatePickerInput

from company_profile.views.application import TranslationMixin
from company_profile_entaj.models import ForeignerPermission, ForeignerRecord
from company_profile_entaj.tables import AppForeignerPermissionTable, AppForeignerRecordTable

class AppForeignerRecordForm(ModelForm):
    company = None
    class Meta:
        model = ForeignerRecord        
        exclude = ["company","state",]
        widgets = {}

class AppForeignerPermissionForm(ModelForm):
    class Meta:
        model = ForeignerPermission        
        exclude = ["company","state","foreigner_record"]
        widgets = {
            "validity_due_date":DatePickerInput(),
        }

class AppForeignerRecordListView(LoginRequiredMixin,TranslationMixin,SingleTableView):
    model = ForeignerRecord
    table_class = AppForeignerRecordTable
    menu_name = "profile:app_foreigner_record_list"
    title = _("قائمة الاجانب")
    template_name = "company_profile_entaj/application_list.html"     
    context_object_name = "apps"    
    paginator_class = LazyPaginator

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title,
         }
        return super().dispatch(*args, **kwargs)       
            
    def get_queryset(self):

        query = super().get_queryset()        
        return query.filter(company__id=self.request.user.pro_company.company.id)

class  AppForeignerRecordCreateView(LoginRequiredMixin,CreateView):
    model = ForeignerRecord
    form_class = AppForeignerRecordForm
    success_url = None
    title = "إضافة اجنبي"    
    menu_name = "profile:app_foreigner_record_list"  
    template_name = "company_profile/application_add.html"    
    
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse_lazy(self.menu_name)    
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
         }
        return super().dispatch(*args, **kwargs)        
        
    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.company = self.request.user.pro_company.company
        self.object.created_by = self.object.updated_by = self.request.user

        self.object.cv = self.request.FILES["cv"]
        self.object.save()
        
        messages.add_message(self.request,messages.SUCCESS,_("Application sent successfully."))
                
        return HttpResponseRedirect(self.get_success_url())
        
class AppForeignerRecordReadonlyView(LoginRequiredMixin,SingleObjectMixin,View):
    model = ForeignerRecord
    form_class = AppForeignerRecordForm
    title = "بيانات اجنبي"    
    menu_name = "profile:app_foreigner_record_list"  
    template_name = "company_profile_entaj/application_readonly.html"    
    
    def dispatch(self, *args, **kwargs):
        table = AppForeignerPermissionTable(
            ForeignerPermission.objects.filter(foreigner_record=self.get_object()).order_by("-id")
        )

        self.extra_context = {
                            "table":table,
                            "menu_name":self.menu_name,
                            "title":self.title, 
                            "state":self.get_object().get_state_display(), 
         }
        return super().dispatch(*args, **kwargs)        
                        
    def get(self,request,pk=0):     
        obj = self.get_object()
        if obj.company == self.request.user.pro_company.company:
            self.extra_context["form"] = self.form_class(instance=obj)
            self.extra_context["object"] = obj
        return render(request, self.template_name, self.extra_context)

class  AppForeignerPermissionCreateView(LoginRequiredMixin,CreateView):
    model = ForeignerPermission
    form_class = AppForeignerPermissionForm
    success_url = None
    title = "إضافة مستند اجنبي"    
    menu_name = "profile:app_foreigner_record_show"  
    template_name = "company_profile/application_add.html"    
    object = None
    
    def dispatch(self, *args, **kwargs):
        id = kwargs.get("id")
        self.foreigner_object = get_object_or_404(ForeignerRecord,pk=id)

        self.success_url = reverse_lazy(self.menu_name,kwargs={"pk":self.foreigner_object.id}   )    
        self.extra_context = {
                            "foreigner_object":self.foreigner_object,
                            "menu_name":self.menu_name,
                            "title":self.title, 
         }
        return super().dispatch(*args, **kwargs)        
        
    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.company = self.request.user.pro_company.company
        self.object.created_by = self.object.updated_by = self.request.user

        self.object.foreigner_record = self.foreigner_object

        self.object.attachment = self.request.FILES["attachment"]
        self.object.save()
        
        messages.add_message(self.request,messages.SUCCESS,_("Application sent successfully."))
                
        return HttpResponseRedirect(self.get_success_url())
