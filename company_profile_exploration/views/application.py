import datetime
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import View,UpdateView,CreateView,DetailView,DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django.forms import inlineformset_factory

from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin

from django.contrib import messages

from django_tables2 import SingleTableView
from django_tables2.paginators import LazyPaginator

class TranslationMixin:
    def dispatch(self,request,*args, **kwargs):  
        response = super().dispatch(request,*args, **kwargs)
        translation.activate(request.user.lang)

        lang_cookie = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)

        if not lang_cookie or lang_cookie != request.user.lang:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME,request.user.lang,max_age=datetime.timedelta(days=365))

        return response
    
class UserPermissionMixin(UserPassesTestMixin):
    user_groups = []

    def test_func(self):
        if not self.user_groups:
            return True

        return self.request.user.groups.filter(name__in=self.user_groups).exists()
    
    def test_group(self,group):
        return self.request.user.groups.filter(name=group).exists()

class ApplicationListView(LoginRequiredMixin,UserPermissionMixin,TranslationMixin,SingleTableView):
    model = None
    table_class = None
    # filterset_class = None
    title = None
    user_groups = ['pa_data_entry','pa_manager']
    menu_name = ""
    relation_fields = []
    context_object_name = "apps"
    template_name = "company_profile_exploration/application_list.html"     
    paginator_class = LazyPaginator
    
    def dispatch(self, *args, **kwargs):         
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title,
                            # "filter":self.filterset_class(self.request.GET,request=self.request) if self.filterset_class else None
         }
        return super().dispatch(*args, **kwargs)       
        
    def get_queryset(self):                
        query = super().get_queryset()
        query = query.filter(company=self.request.user.pro_company.company)
        return query.prefetch_related(*self.table_class.relation_fields)
                
class ApplicationMasterDetailCreateView(LoginRequiredMixin,UserPermissionMixin,View):
    model = None
    form_class = None
    details = []
    success_url = None
    title = None    
    user_groups = ['pa_data_entry','pa_manager']
    menu_name = ""  
    template_name = "pa/application_add_master_details.html"
    
    def dispatch(self,request, *args, **kwargs):         
        self.details_formset = []
        i = 0
        for d in self.details:
            i += 1
            self.details_formset.append({
                "id":d['id'] or i,
                "title":d['title'],
                "formset":inlineformset_factory(*d['args'], **d['kwargs']),
            })
            
        self.form_class.request = request
        self.form_class.user = request.user
        self.success_url = reverse_lazy(self.menu_name)    
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
                            "form": self.form_class,
                            "details": self.details_formset,
         }
        return super().dispatch(request,*args, **kwargs)                    

    def get(self,request, *args, **kwargs):        
        return render(request, self.template_name, self.extra_context)
    
    def post(self, request, *args, **kwargs):
        form = None

        if isinstance(self.extra_context["form"],self.form_class) :
            form = self.extra_context["form"]
        else:
            form = self.form_class(request.POST,request.FILES)

        if form.is_valid():
            self.object = form.save(commit=False)
            self.object.company = self.request.user.pro_company.company

            self.object.created_by = self.object.updated_by = request.user
            
            flag = True
            formset_list = []
            for detail in self.details_formset:
                formset = detail['formset'](request.POST,request.FILES,instance=self.object)
                detail['formset'] = formset
                if not formset.is_valid():
                    flag = False
                
                formset_list.append(formset)
                
            # if self.request.POST.get('_save_confirm') and self.test_group('pa_manager'):
            #     self.object.state = STATE_TYPE_CONFIRM

            if flag:
                self.object.save()
                for formset in formset_list:
                    for form in formset:
                        formset_obj = form.save(commit=False)
                        formset_obj.created_by = formset_obj.updated_by = request.user
                        formset_obj.save()
                
                messages.add_message(request,messages.SUCCESS,_("Application sent successfully."))
                return HttpResponseRedirect(self.success_url)
        else:   
            for detail in self.details_formset:
                detail['formset'] = detail['formset'](request.POST,request.FILES)

        self.extra_context["form"] = form
        self.extra_context['details'] = self.details_formset

        return render(request, self.template_name, self.extra_context)
                
class ApplicationMasterDetailUpdateView(LoginRequiredMixin,UserPermissionMixin,SingleObjectMixin,View):
    model = None
    form_class = None
    details = []
    success_url = None
    title = None    
    user_groups = ['pa_data_entry','pa_manager']
    menu_name = ""  
    template_name = "pa/application_add_master_details.html"
    
    def dispatch(self, request,*args, **kwargs):         
        self.details_formset = []
        i = 0
        for d in self.details:
            i += 1
            self.details_formset.append({
                "id":d['id'] or i,
                "title":d['title'],
                "formset":inlineformset_factory(*d['args'], **d['kwargs']),
            })
            
        self.form_class.request = request
        self.form_class.user = request.user
        self.success_url = reverse_lazy(self.menu_name)    
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "menu_show_name":self.menu_show_name,
                            "title":self.title, 
                            "form": self.form_class,
                            "details": self.details_formset,
         }
        return super().dispatch(request,*args, **kwargs)                    
    def get_queryset(self):
        query = super().get_queryset()        
        query = query.filter(company=self.request.user.pro_company.company)
        return query
    def get(self,request, *args, **kwargs):        
        # obj = self.model.objects.get(id=pk)
        obj = self.get_object()
        self.extra_context["form"] = self.form_class(instance=obj)
        self.extra_context["object"] = obj
        for detail in self.details_formset:
            formset = detail['formset'](instance=obj)
            detail['formset'] = formset

        self.extra_context['details'] = self.details_formset

        return render(request, self.template_name, self.extra_context)
    
    def post(self, request,pk, *args, **kwargs):
        form = self.form_class(request.POST,request.FILES,instance=self.model.objects.get(id=pk))
        self.extra_context["form"] = form
        form.id = pk
        if form.is_valid():
            self.object = form.save(commit=False)
            
            if not self.object.id:
                self.object.created_by = self.object.updated_by = request.user
                self.object.created_at = self.object.updated_at = timezone.now()
            else:
                self.object.updated_by = request.user
                self.object.updated_at = timezone.now()

            flag = True
            formset_list = []
            for detail in self.details_formset:
                formset = detail['formset'](request.POST,request.FILES,instance=self.object)
                detail['formset'] = formset
                if not formset.is_valid():
                    flag = False
                    
                formset_list.append( formset)

            self.extra_context['details'] = self.details_formset
            
            # if self.request.POST.get('_save_confirm') and self.test_group('pa_manager'):
            #     self.object.state = STATE_TYPE_CONFIRM
            
            if flag:
                self.object.save()
                for formset in formset_list:                    
                    for form in formset:
                        if form.is_valid():
                            formset_obj = form.save(commit=False)
                            formset_obj.updated_by = request.user
                            if not formset_obj.id:
                                formset_obj.created_by = request.user
                            formset_obj.save()

                messages.add_message(request,messages.SUCCESS,_("Application sent successfully."))
                return HttpResponseRedirect(self.success_url)

        else:   
            for detail in self.details_formset:
                detail['formset'] = detail['formset'](request.POST,request.FILES)

        self.extra_context["form"] = form
        self.extra_context['details'] = self.details_formset

        return render(request, self.template_name, self.extra_context)
                

class ApplicationReadonlyView(LoginRequiredMixin,UserPermissionMixin,SingleObjectMixin,View):
    model = None
    form_class = None
    details = []
    success_url = None
    title = None    
    user_groups = ['pa_data_entry','pa_manager']
    menu_name = ""  
    template_name = "company_profile_exploration/application_readonly_master_details.html"
    
    def dispatch(self, request,*args, **kwargs):         
        self.details_formset = []
        i=0
        
        for d in self.details:
            i += 1
            if d['kwargs'].get('can_delete'):
                d['kwargs']['can_delete'] = False
            self.details_formset.append({
                "id":d['id'] or i,
                "title":d['title'],
                "formset":inlineformset_factory(*d['args'], **d['kwargs']),
            })

        self.form_class.request = request            
        self.form_class.user = request.user

        self.success_url = reverse_lazy(self.menu_name)    
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "menu_edit_name":self.menu_edit_name,
                            "menu_delete_name":self.menu_delete_name,
                            "title":self.title, 
                            "form": self.form_class,
                            "details": self.details_formset,
         }
        return super().dispatch(request,*args, **kwargs)                    

    def get_queryset(self):
        query = super().get_queryset()        
        query = query.filter(company=self.request.user.pro_company.company)
        return query

    def get(self,request,*args, **kwargs):        
        obj = self.get_object()
        self.extra_context["form"] = self.form_class(instance=obj)
        self.extra_context["object"] = obj
        for detail in self.details_formset:
            formset = detail['formset'](instance=obj)
            detail['formset'] = formset
        return render(request, self.template_name, self.extra_context)

class ApplicationDeleteMasterDetailView(LoginRequiredMixin,UserPermissionMixin,SingleObjectMixin,View):
    model = None
    form_class = None
    details = []
    success_url = None
    title = None    
    user_groups = ['pa_data_entry','pa_manager']
    menu_name = ""  
    template_name = "pa/application_delete_master_detail.html"
    
    def dispatch(self, request,*args, **kwargs):         
        self.details_formset = []
        for d in self.details:
            self.details_formset.append({
                "title":d['title'],
                "formset":inlineformset_factory(*d['args'], **d['kwargs']),
            })

        self.form_class.request = request
        self.form_class.user = request.user
        self.success_url = reverse_lazy(self.menu_name)    
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
                            "form": self.form_class,
                            "details": self.details_formset,
         }
        return super().dispatch(request,*args, **kwargs)                    

    def get_queryset(self):
        query = super().get_queryset()        
        query = query.filter(company=self.request.user.pro_company.company)
        return query

    def get(self,request,*args, **kwargs):        
        obj = self.get_object()
        self.extra_context["form"] = self.form_class(instance=obj)
        self.extra_context["object"] = obj
        for detail in self.details_formset:
            formset = detail['formset'](instance=obj)
            detail['formset'] = formset
        return render(request, self.template_name, self.extra_context)

    def post(self,request,*args, **kwargs):     
        obj = self.get_object()

        for detail in self.details_formset:
            formset = detail['formset'](instance=obj)
            objects = formset.save(commit=False)
            
            for obj1 in objects:
                obj1.delete()

        obj.delete()

        self.success_url = reverse_lazy(self.menu_name)    
        messages.add_message(self.request,messages.SUCCESS,_("Record removed successfully."))
        return HttpResponseRedirect(self.success_url)
