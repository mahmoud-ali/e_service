from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import View,UpdateView,CreateView,DetailView,DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from django.forms import inlineformset_factory

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages

from django_tables2 import SingleTableView
from django_tables2.paginators import LazyPaginator

from ..models import STATE_TYPE_CONFIRM, STATE_TYPE_DRAFT

class ApplicationListView(LoginRequiredMixin,SingleTableView):
    model = None
    table_class = None
    filterset_class = None
    title = None
    menu_name = ""
    relation_fields = []
    context_object_name = "apps"    
    template_name = "pa/application_list.html"     
    paginator_class = LazyPaginator
    
    def dispatch(self, *args, **kwargs):         
        self.extra_context = {
                            "type":kwargs.get("type",1),
                            "menu_name":self.menu_name,
                            "title":self.title,
                            "filter":self.filterset_class(self.request.GET) if self.filterset_class else None
         }
        return super().dispatch(*args, **kwargs)       
        
    def get_queryset(self):                
        query = super().get_queryset()
        if self.filterset_class:
            query = self.filterset_class(self.request.GET,queryset=query).qs
        return query.prefetch_related(*self.table_class.relation_fields)
    
    def get(self,request,*args, **kwargs):  
        translation.activate(request.user.lang)
        response = super().get(request,*args, **kwargs)

        if not request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME):
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME,request.user.lang)

        return response
        
class ApplicationCreateView(LoginRequiredMixin,CreateView):
    model = None
    form_class = None
    success_url = None
    title = None    
    menu_name = ""  
    template_name = "pa/application_add.html"    
    
    def dispatch(self, *args, **kwargs):
        self.success_url = reverse_lazy(self.menu_name)    
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
         }
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.created_by = self.object.updated_by = self.request.user

        if self.request.POST.get('_save_confirm'):
            self.object.state = STATE_TYPE_CONFIRM

        self.object.save()

        messages.add_message(self.request,messages.SUCCESS,_("Record saved successfully."))
        
        return HttpResponseRedirect(self.get_success_url())

class ApplicationUpdateView(LoginRequiredMixin,UpdateView):
    model = None
    form_class = None
    title = None    
    menu_name = ""  
    menu_show_name = ""  
    template_name = "pa/application_add.html"    
    
    def dispatch(self, *args, **kwargs):
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "menu_show_name":self.menu_show_name,
                            "title":self.title, 
         }
        return super().dispatch(*args, **kwargs)        
                        
    def get_queryset(self):
        query = super().get_queryset()        
        return query.filter(state=STATE_TYPE_DRAFT)

    def get(self,request,pk=0):     
        obj = self.get_object()
        self.extra_context["form"] = self.form_class(instance=obj)
        self.extra_context["object"] = obj
        return render(request, self.template_name, self.extra_context)
    
    def post(self,*args, **kwargs):     
        obj = self.get_object()
        self.success_url = reverse_lazy(self.menu_name,args=(obj.id,))    
        return super().post(*args, **kwargs)        
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.updated_by = self.request.user

        if self.request.POST.get('_save_confirm'):
            self.object.state = STATE_TYPE_CONFIRM

        self.object.save()

        messages.add_message(self.request,messages.SUCCESS,_("Record saved successfully."))
                
        return HttpResponseRedirect(self.get_success_url())

class ApplicationReadonlyView(LoginRequiredMixin,SingleObjectMixin,View):
    model = None
    form_class = None
    title = None    
    menu_name = ""  
    menu_edit_name = ""
    menu_delete_name = ""
    template_name = "pa/application_readonly.html"    
    
    def dispatch(self, *args, **kwargs):
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "menu_edit_name":self.menu_edit_name,
                            "menu_delete_name":self.menu_delete_name,
                            "title":self.title, 
         }
        return super().dispatch(*args, **kwargs)        
                        
    def get(self,request,pk=0):     
        obj = self.get_object()
        self.extra_context["form"] = self.form_class(instance=obj)
        self.extra_context["object"] = obj
        return render(request, self.template_name, self.extra_context)

class ApplicationDeleteView(DeleteView):
    model = None
    form_class = None
    title = None    
    menu_name = ""  
    template_name = "pa/application_delete.html"    

    def dispatch(self, *args, **kwargs):
        self.success_url = reverse_lazy(self.menu_name)
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
         }
        return super().dispatch(*args, **kwargs)        

    def get_queryset(self):
        query = super().get_queryset()        
        return query.filter(state=STATE_TYPE_DRAFT)
    
    def get(self,request,pk=0):     
        obj = self.get_object()
        self.extra_context["form"] = self.form_class(instance=obj)
        self.extra_context["object"] = obj
        return render(request, self.template_name, self.extra_context)
