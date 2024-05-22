from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404,render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django.contrib import messages

from company_profile.models import TblCompanyProduction
from ..forms import ApplicationRecordShowEditForm,ApplicationRecordAddForm
from ..tables import ApplicationRecordFilter, ApplicationRecordTable
# from pa.forms.commitment import TblCompanyAddCommitmentForm, ApplicationRecordDetailForm, TblCompanyRequestChooseCompanyForm, TblCompanyShowEditCommitmentForm

from ..models import  STATE_TYPE_CONFIRM, ApplicationDelivery, ApplicationDepartmentProcessing, ApplicationExectiveProcessing, ApplicationRecord

# from ..tables import ApplicationRecordTable,ApplicationRecordFilter

from .application import ApplicationDeleteMasterDetailView, ApplicationListView, ApplicationMasterDetailCreateView, ApplicationMasterDetailUpdateView, ApplicationReadonlyView

model_master = ApplicationRecord
details = [
        {
            "id":1,
            "title":"معالجة الادارة المختصة",
            "args":[
                model_master,
                ApplicationDepartmentProcessing
            ],
            "kwargs":{
               "fields":['department','action_type'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
        {
            "id":2,
            "title":"تسليم الطلب",
            "args":[
                model_master,
                ApplicationDelivery
            ],
            "kwargs":{
               "fields":['destination'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
    ]

details_show = [
        {
            "id":1,
            "title":"معالجة الادارة المختصة",
            "args":[
                model_master,
                ApplicationDepartmentProcessing
            ],
            "kwargs":{
               "fields":['department','action_type','attachement_file','action_state'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
        {
            "id":2,
            "title":"معالجة المكتب التنفيذي",
            "args":[
                model_master,
                ApplicationExectiveProcessing
            ],
            "kwargs":{
               "fields":['department','action_type','attachement_file','action_state'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
        {
            "id":3,
            "title":"تسليم الطلب",
            "args":[
                model_master,
                ApplicationDelivery
            ],
            "kwargs":{
               "fields":['destination','delivery_state'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
    ]

class ApplicationRecordListView(ApplicationListView):
    model = model_master
    table_class = ApplicationRecordTable
    filterset_class = ApplicationRecordFilter
    user_groups = ['doc_executive','doc_department']
    menu_name = "doc_workflow:app_record_list"
    title = _("List of application records")
    
class ApplicationRecordCreateView(ApplicationMasterDetailCreateView):
    model = model_master
    form_class = ApplicationRecordAddForm
    details = details
    user_groups = ['doc_executive']
    menu_name = "doc_workflow:app_record_list"
    title = _("Add new application record")            
    
    def post(self, request, *args, **kwargs):
        form = None

        if isinstance(self.extra_context["form"],self.form_class) :
            form = self.extra_context["form"]
        else:
            form = self.form_class(request.POST,request.FILES)

        if form.is_valid():
            self.object = form.save(commit=False)
            
            self.object.created_by = self.object.updated_by = request.user
            
            flag = True
            formset_list = []
            for detail in self.details_formset:
                formset = detail['formset'](request.POST,request.FILES,instance=self.object)
                detail['formset'] = formset
                if not formset.is_valid():
                    flag = False
                
                formset_list.append(formset)
                
            if self.request.POST.get('_save_confirm') and self.test_group('doc_executive'):
                self.object.state = ApplicationRecord.STATE_TYPE_PROCESSING_DEPARTMENT

            if flag:
                self.object.save()
                for formset in formset_list:
                    instances = formset.save(commit=False)
                    for obj in instances:
                        if obj.pk:
                            obj.updated_by = request.user
                        else:
                            obj.created_by = obj.updated_by = request.user

                        obj.save()
                
                messages.add_message(request,messages.SUCCESS,_("Application sent successfully."))
                return HttpResponseRedirect(self.success_url)
        else:   
            for detail in self.details_formset:
                detail['formset'] = detail['formset'](request.POST,request.FILES)

        self.extra_context["form"] = form
        self.extra_context['details'] = self.details_formset

        return render(request, self.template_name, self.extra_context)

class ApplicationRecordUpdateView(ApplicationMasterDetailUpdateView):
    model = model_master
    form_class = ApplicationRecordShowEditForm
    details = details
    user_groups = ['doc_executive']
    menu_name = "doc_workflow:app_record_list"
    menu_show_name = "doc_workflow:app_record_show"
    title = _("Edit application record")

    def get_queryset(self):
        query = ApplicationRecord.objects.all()     
        return query.filter(state=ApplicationRecord.STATE_TYPE_NEW)

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
            
            if self.request.POST.get('_save_confirm') and self.test_group('doc_executive'):
                self.object.state = ApplicationRecord.STATE_TYPE_PROCESSING_DEPARTMENT
            
            if flag:
                self.object.save()
                for formset in formset_list:                    
                    instances = formset.save(commit=False)
                    for obj in instances:
                        if obj.pk:
                            obj.updated_by = request.user
                        else:
                            obj.created_by = obj.updated_by = request.user

                        obj.save()

                messages.add_message(request,messages.SUCCESS,_("Application sent successfully."))
                return HttpResponseRedirect(self.success_url)

        else:   
            for detail in self.details_formset:
                detail['formset'] = detail['formset'](request.POST,request.FILES)

        self.extra_context["form"] = form
        self.extra_context['details'] = self.details_formset

        return render(request, self.template_name, self.extra_context)

class ApplicationRecordReadonlyView(ApplicationReadonlyView):
    model = model_master
    form_class = ApplicationRecordShowEditForm
    details = details_show
    user_groups = ['doc_executive','doc_department']
    menu_name = "doc_workflow:app_record_list"
    menu_edit_name = "doc_workflow:app_record_edit"
    menu_delete_name = "doc_workflow:app_record_delete"
    title = _("Show application record")
    template_name = "doc_workflow/views/application_record_readonly.html"

class ApplicationRecordDeleteView(ApplicationDeleteMasterDetailView):
    model = model_master
    form_class = ApplicationRecordShowEditForm
    details = details
    user_groups = ['doc_executive']
    menu_name = "doc_workflow:app_record_list"
    title = _("Delete application record")

    def get_queryset(self):
        query = ApplicationRecord.objects.all()     
        return query.filter(state=ApplicationRecord.STATE_TYPE_NEW)

