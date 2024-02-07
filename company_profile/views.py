from django.urls import reverse_lazy
from django.views.generic import View,TemplateView,ListView,DetailView,CreateView,UpdateView,DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from django.conf import settings

from django.forms import inlineformset_factory

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from django_tables2 import SingleTableView
from django_tables2.paginators import LazyPaginator

from .models import LkpState,LkpLocality,TblCompanyProduction,AppForignerMovement,AppBorrowMaterial,AppBorrowMaterialDetail
from .forms import AppForignerMovementForm,AppBorrowMaterialForm

from .workflow import STATE_CHOICES,SUBMITTED,ACCEPTED,APPROVED,REJECTED,send_transition_email,get_sumitted_responsible_email
from .tables import AppForignerMovementTable,AppBorrowMaterialTable

        
class ApplicationListView(LoginRequiredMixin,SingleTableView):
    model = None
    table_class = None
    title = None
    menu_name = ""
    context_object_name = "apps"    
    template_name = "company_profile/application_list.html"     
    paginator_class = LazyPaginator
    
    def dispatch(self, *args, **kwargs):         
        self.extra_context = {
                            "type":kwargs.get("type",1),
                            "menu_name":self.menu_name,
                            "title":self.title,
         }
        return super().dispatch(*args, **kwargs)       
        
    def get_queryset(self):
        query_filter = []
        if self.extra_context["type"] == 1:
            query_filter = [SUBMITTED,ACCEPTED]
        elif self.extra_context["type"] == 2:
            query_filter = [APPROVED]
        elif self.extra_context["type"] == 3:
            query_filter = [REJECTED]
                
        query = super().get_queryset()
        return query.filter(state__in=query_filter).prefetch_related(*self.table_class.relation_fields)
        
class ApplicationCreateView(LoginRequiredMixin,CreateView):
    model = None
    form_class = None
    success_url = None
    title = None    
    menu_name = ""  
    template_name = "company_profile/application_add.html"    
    
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse_lazy(self.menu_name)    
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
         }
        return super().dispatch(*args, **kwargs)        
        
class ApplicationReadonlyView(LoginRequiredMixin,SingleObjectMixin,View):
    model = None
    form_class = None
    title = None    
    menu_name = ""  
    template_name = "company_profile/application_readonly.html"    
    
    def dispatch(self, *args, **kwargs):
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    

        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
                            "state":STATE_CHOICES[self.get_object().state], 
         }
        return super().dispatch(*args, **kwargs)        
        
    def get_queryset(self):

        query = super().get_queryset()        
        return query.filter(company=self.request.user.pro_company.company)
                
    def get(self,request,pk=0):        
        self.extra_context["form"] = self.form_class(instance=self.get_object())
        return render(request, self.template_name, self.extra_context)
        
class LkpSelectView(LoginRequiredMixin,TemplateView):
    template_name = 'company_profile/select.html'
    kwargs = None

    def get_queryset(self):
        return None #not implemented

    def dispatch(self, *args, **kwargs):
        self.kwargs = kwargs
        self.extra_context = {
                            "options":self.get_queryset(), 
                            "old_value":self.kwargs['dependent_id']
         }
        return super().dispatch(*args, **kwargs)                    

    def get(self, request, *args, **kwargs):                   
        return render(request, self.template_name, self.extra_context)    

class AppForignerMovementListView(ApplicationListView):
    model = AppForignerMovement
    table_class = AppForignerMovementTable
    menu_name = "profile:app_foreigner_list"
    title = "List of foreigner movements"
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            
    def get_queryset(self):

        query = super().get_queryset()        
        return query.filter(company__id=self.request.user.pro_company.company.id)


class AppForignerMovementCreateView(ApplicationCreateView):
    model = AppForignerMovement
    form_class = AppForignerMovementForm
    menu_name = "profile:app_foreigner_list"
    title = "Add new movement"

    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)        
            

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.company = self.request.user.pro_company.company
        self.object.created_by = self.object.updated_by = self.request.user
        self.object.official_letter_file = self.request.FILES["official_letter_file"]
        self.object.passport_copy_file = self.request.FILES["passport_copy_file"]
        self.object.cv_file = self.request.FILES["cv_file"]
        self.object.experiance_certificates_file = self.request.FILES["experiance_certificates_file"]
        self.object.save()
        
        messages.add_message(self.request,messages.SUCCESS,_("Application sent successfully."))
        
        info = (self.object._meta.app_label, self.object._meta.model_name)
        url = settings.BASE_URL+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
        send_transition_email(self.object.state,get_sumitted_responsible_email('pro_company'),url)
        
        return HttpResponseRedirect(self.get_success_url())
        
class AppForignerMovementReadonlyView(ApplicationReadonlyView):
    model = AppForignerMovement
    form_class = AppForignerMovementForm
    menu_name = "profile:app_foreigner_list"
    title = "Show movement"
        
class AppBorrowMaterialListView(ApplicationListView):
    model = AppBorrowMaterial
    table_class = AppBorrowMaterialTable
    menu_name = "profile:app_borrow_list"
    title = "List of borrow materials"
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))    
            
        return super().dispatch(*args, **kwargs)                    
    
    def get_queryset(self):
        query = super().get_queryset()        
        return query.filter(company__id=self.request.user.pro_company.company.id).only(*self.table_class.Meta.fields)
        
class AppBorrowMaterialCreateView(LoginRequiredMixin,View):
    model = AppBorrowMaterial
    model_details = AppBorrowMaterialDetail
    model_details_fields = ["material","quantity"]
    form_class = AppBorrowMaterialForm    
    detail_formset = None
    menu_name = "profile:app_borrow_list"
    title = "Add new borrow materials"
    template_name = "company_profile/application_add_master_details.html"
    
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))        
            
        self.detail_formset = inlineformset_factory(self.model, self.model_details, fields=self.model_details_fields,extra=10,can_delete=False,min_num=1, validate_min=True)
            
        self.success_url = reverse_lazy(self.menu_name)    
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
                            "form": self.form_class,
                            "detail_formset": self.detail_formset,
         }
        return super().dispatch(*args, **kwargs)                    

    def get(self,request):        
        return render(request, self.template_name, self.extra_context)

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
                url = settings.BASE_URL+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
                send_transition_email(self.object.state,get_sumitted_responsible_email('pro_company'),url)
                
                return HttpResponseRedirect(self.success_url)
            
            return render(request, self.template_name, self.extra_context)
            
class AppBorrowMaterialReadonlyView(ApplicationReadonlyView):
    model = AppBorrowMaterial
    model_details = AppBorrowMaterialDetail
    model_details_fields = ["material","quantity"]
    form_class = AppBorrowMaterialForm
    detail_formset = None
    menu_name = "profile:app_borrow_list"
    title = "Show borrow materials" 
    template_name = "company_profile/application_readonly_master_details.html"
        
    def dispatch(self, *args, **kwargs):         
        if not hasattr(self.request.user,"pro_company"):
            return HttpResponseRedirect(reverse_lazy("profile:home"))        
            
        self.detail_formset = inlineformset_factory(self.model, self.model_details, fields=self.model_details_fields,extra=0,can_delete=False)
            
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
                            "form": self.form_class,
                            "detail_formset": self.detail_formset,
         }
        return super().dispatch(*args, **kwargs)                    

    def get(self,request,pk=0):        
        obj = self.get_object()
        self.extra_context["form"] = self.form_class(instance=obj)
        self.extra_context["detail_formset"] = self.detail_formset(instance=obj)
        
        return render(request, self.template_name, self.extra_context)

class HomePageView(LoginRequiredMixin,TemplateView):
    template_name = 'company_profile/home.html'
    menu_name = 'profile:home'
    def dispatch(self, *args, **kwargs):                   

        self.extra_context = {
                            "menu_name":self.menu_name,
         }
        return super().dispatch(*args, **kwargs)                    

class LkpLocalitySelectView(LkpSelectView):
    def get_queryset(self):
        qs = LkpLocality.objects.filter(state__id = self.kwargs['master_id'])
        return qs
    
