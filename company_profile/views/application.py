import datetime
from django.urls import reverse_lazy
from django.views.generic import View,ListView,CreateView,DetailView
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from django.forms import inlineformset_factory

from django.conf import settings

from django.contrib.auth.mixins import LoginRequiredMixin

from django_tables2 import SingleTableView
from django_tables2.paginators import LazyPaginator

from ..workflow import STATE_CHOICES,SUBMITTED,ACCEPTED,APPROVED,REJECTED,send_transition_email,get_sumitted_responsible

class TranslationMixin:
    def dispatch(self,request,*args, **kwargs):  
        response = super().dispatch(request,*args, **kwargs)
        translation.activate(request.user.lang)

        lang_cookie = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)

        if not lang_cookie or lang_cookie != request.user.lang:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME,request.user.lang,max_age=datetime.timedelta(days=365))

        return response

class ApplicationListView(LoginRequiredMixin,TranslationMixin,SingleTableView):
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
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
                            "reject_comments":self.get_object().reject_comments, 
                            "state":STATE_CHOICES[self.get_object().state], 
         }
        return super().dispatch(*args, **kwargs)        
                        
    def get(self,request,pk=0):     
        obj = self.get_object()
        self.extra_context["form"] = self.form_class(instance=obj)
        self.extra_context["object"] = obj
        return render(request, self.template_name, self.extra_context)

class ApplicationMasterDetailCreateView(LoginRequiredMixin,View):
    model = None
    model_details = None
    model_details_fields = []
    form_class = None
    detail_formset = None
    menu_name = ""
    title = ""
    template_name = "company_profile/application_add_master_details.html"
    
    def dispatch(self, *args, **kwargs):         
        self.detail_formset = inlineformset_factory(self.model, self.model_details, fields=self.model_details_fields,extra=0,can_delete=False,min_num=1, validate_min=True)
            
        self.success_url = reverse_lazy(self.menu_name)    
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
                            "form": self.form_class,
                            "detail_formset": self.detail_formset,
                            "detail_title":self.model_details._meta.verbose_name_plural,
         }
        return super().dispatch(*args, **kwargs)                    

    def get(self,request):        
        return render(request, self.template_name, self.extra_context)

class ApplicationMasterDetailReadonlyView(LoginRequiredMixin,DetailView):
    model = None
    model_details = None
    model_details_fields = []
    form_class = None
    detail_formset = None
    menu_name = ""
    title = ""
    template_name = "company_profile/application_readonly_master_details.html"
        
    def dispatch(self, *args, **kwargs):                   
        self.detail_formset = inlineformset_factory(self.model, self.model_details, fields=self.model_details_fields,extra=0,can_delete=False)
        obj = self.get_object()
        state_key = obj.state
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
                            "form": self.form_class,
                            "detail_formset": self.detail_formset,
                            "detail_title":self.model_details._meta.verbose_name_plural,
                            "state":STATE_CHOICES[state_key], 
         }
        return super().dispatch(*args, **kwargs)                    

    def get(self,request,pk=0):        
        obj = self.get_object()
        self.extra_context["form"] = self.form_class(instance=obj)
        self.extra_context["detail_formset"] = self.detail_formset(instance=obj)
        self.extra_context["object"] = obj

        return render(request, self.template_name, self.extra_context)

