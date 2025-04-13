from django.forms import modelform_factory
from django.shortcuts import get_object_or_404,render
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.contrib import messages

from company_profile.models import TblCompanyProduction
from company_profile_exploration.models.work_plan import AppWorkPlan, Brief, Coordinate, Equipment, LogisticsAdministration, Other, Phase, SamplePreparation, StaffInformation, SubsurfaceExplorationActivitie, SurfaceExplorationActivitie, TargetCommodity
from company_profile_exploration.tables.workplan import AppWorkPlanTable

from .application import ApplicationDeleteMasterDetailView, ApplicationListView, ApplicationMasterDetailCreateView, ApplicationMasterDetailUpdateView, ApplicationReadonlyView

model_master = AppWorkPlan
form_master = modelform_factory(model_master,fields=["currency"])
details = [
        {
            "id":1,
            "title":TargetCommodity._meta.verbose_name_plural,
            "args":[
                model_master,
                TargetCommodity
            ],
            "kwargs":{
                "form": modelform_factory(TargetCommodity,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
        {
            "id":2,
            "title":Coordinate._meta.verbose_name_plural,
            "args":[
                model_master,
                Coordinate
            ],
            "kwargs":{
                "form": modelform_factory(Coordinate,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
        {
            "id":3,
            "title":Brief._meta.verbose_name_plural,
            "args":[
                model_master,
                Brief
            ],
            "kwargs":{
                "form": modelform_factory(Brief,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "max_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
        {
            "id":4,
            "title":Phase._meta.verbose_name_plural,
            "args":[
                model_master,
                Phase
            ],
            "kwargs":{
                "form": modelform_factory(Phase,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
        {
            "id":5,
            "title":StaffInformation._meta.verbose_name_plural,
            "args":[
                model_master,
                StaffInformation
            ],
            "kwargs":{
                "form": modelform_factory(StaffInformation,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
        {
            "id":6,
            "title":LogisticsAdministration._meta.verbose_name_plural,
            "args":[
                model_master,
                LogisticsAdministration
            ],
            "kwargs":{
                "form": modelform_factory(LogisticsAdministration,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
        {
            "id":7,
            "title":Equipment._meta.verbose_name_plural,
            "args":[
                model_master,
                Equipment
            ],
            "kwargs":{
                "form": modelform_factory(Equipment,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
        {
            "id":8,
            "title":SurfaceExplorationActivitie._meta.verbose_name_plural,
            "args":[
                model_master,
                SurfaceExplorationActivitie
            ],
            "kwargs":{
                "form": modelform_factory(SurfaceExplorationActivitie,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
        {
            "id":9,
            "title":SubsurfaceExplorationActivitie._meta.verbose_name_plural,
            "args":[
                model_master,
                SubsurfaceExplorationActivitie
            ],
            "kwargs":{
                "form": modelform_factory(SubsurfaceExplorationActivitie,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
        {
            "id":10,
            "title":SamplePreparation._meta.verbose_name_plural,
            "args":[
                model_master,
                SamplePreparation
            ],
            "kwargs":{
                "form": modelform_factory(SamplePreparation,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
        {
            "id":11,
            "title":Other._meta.verbose_name_plural,
            "args":[
                model_master,
                Other
            ],
            "kwargs":{
                "form": modelform_factory(Other,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":True,
            },
        },
    ]

class AppWorkPlanListView(ApplicationListView):
    model = model_master
    table_class = AppWorkPlanTable
    # filterset_class = CommitmentFilter
    menu_name = "exploration:workplan_list"
    title = _("List of work plans")
    template_name = "company_profile_exploration/application_list.html"     

    def get_queryset(self):                
        query = super().get_queryset()
        query = query.filter(state__in=[AppWorkPlan.STATE_DRAFT,AppWorkPlan.STATE_REVIEW_COMPANY])
        return query

class AppWorkPlanCreateView(ApplicationMasterDetailCreateView):
    model = model_master
    form_class = form_master
    details = details
    menu_name = "exploration:workplan_list"
    title = _("Add new work plan")            
    template_name = "company_profile_exploration/application_add_master_details.html"     

class AppWorkPlanUpdateView(ApplicationMasterDetailUpdateView):
    model = model_master
    form_class = form_master
    details = details
    menu_name = "exploration:workplan_list"
    menu_show_name = "exploration:workplan_show"
    title = _("Edit work plan")
    template_name = "company_profile_exploration/application_add_master_details.html"     

    def get_queryset(self):                
        query = super().get_queryset()
        query = query.filter(state__in=[AppWorkPlan.STATE_DRAFT,AppWorkPlan.STATE_REVIEW_COMPANY])
        return query

    def post(self, request, *args, **kwargs):
        response = super().post(request,*args, **kwargs)
        obj = self.get_object()
        if self.request.POST.get('_save_confirm') and self.test_group('pa_manager'):
            obj.state = AppWorkPlan.STATE_GM_DECISION
            obj.save()

        return response
        
class AppWorkPlanReadonlyView(ApplicationReadonlyView):
    model = model_master
    form_class = form_master
    details = details
    menu_name = "exploration:workplan_list"
    menu_edit_name = "exploration:workplan_edit"
    menu_delete_name = "exploration:workplan_delete"
    title = _("Show work plan")
    template_name = "company_profile_exploration/application_readonly_master_details.html"     

    def get_queryset(self):                
        query = super().get_queryset()
        query = query.filter(state__in=[AppWorkPlan.STATE_DRAFT,AppWorkPlan.STATE_REVIEW_COMPANY])
        return query

    # def get(self,request,*args, **kwargs):        
    #     obj = self.get_object()
    #     return super().get(request,*args, **kwargs)

class AppWorkPlanDeleteView(ApplicationDeleteMasterDetailView):
    model = model_master
    form_class = form_master
    details = details
    menu_name = "exploration:workplan_list"
    title = _("Delete work plan")
    template_name = "company_profile_exploration/application_delete_master_detail.html"     

    def get_queryset(self):                
        query = super().get_queryset()
        query = query.filter(state__in=[AppWorkPlan.STATE_DRAFT,])
        return query
