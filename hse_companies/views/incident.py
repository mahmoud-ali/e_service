from django.forms import modelform_factory
from django.shortcuts import get_object_or_404,render
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.contrib import messages

from hse_companies.models.corrective_actions import AppHSECorrectiveAction
from hse_companies.models.incidents import ContributingFactor, FactorsAssessment, IncidentAnalysis, IncidentCost, IncidentInfo, IncidentInjuredDetails, IncidentInjuredPPE, IncidentInjuredPerson, IncidentPhoto, IncidentProperty, IncidentWitness, LeasonLearnt
from hse_companies.tables.incident import IncidentInfoTable


from .application import ApplicationDeleteMasterDetailView, ApplicationListView, ApplicationMasterDetailCreateView, ApplicationMasterDetailUpdateView, ApplicationReadonlyView

model_master = IncidentInfo
form_master = modelform_factory(model_master,exclude=['company','state','created_by','updated_by','created_at','updated_at'])
details = [
        {
            "id":1,
            "title":IncidentInjuredPerson._meta.verbose_name_plural,
            "args":[
                model_master,
                IncidentInjuredPerson
            ],
            "kwargs":{
                "form": modelform_factory(IncidentInjuredPerson,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":False,
            },
        },
        {
            "id":2,
            "title":IncidentInjuredPPE._meta.verbose_name_plural,
            "args":[
                model_master,
                IncidentInjuredPPE
            ],
            "kwargs":{
                "form": modelform_factory(IncidentInjuredPPE,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":False,
            },
        },
        {
            "id":3,
            "title":IncidentInjuredDetails._meta.verbose_name_plural,
            "args":[
                model_master,
                IncidentInjuredDetails
            ],
            "kwargs":{
                "form": modelform_factory(IncidentInjuredDetails,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":False,
            },
        },
        {
            "id":4,
            "title":IncidentProperty._meta.verbose_name_plural,
            "args":[
                model_master,
                IncidentProperty
            ],
            "kwargs":{
                "form": modelform_factory(IncidentProperty,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":False,
            },
        },
        {
            "id":5,
            "title":IncidentCost._meta.verbose_name_plural,
            "args":[
                model_master,
                IncidentCost
            ],
            "kwargs":{
                "form": modelform_factory(IncidentCost,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "max_num":1, 
                "validate_min":True,
                "can_delete":False,
            },
        },
        {
            "id":6,
            "title":IncidentWitness._meta.verbose_name_plural,
            "args":[
                model_master,
                IncidentWitness
            ],
            "kwargs":{
                "form": modelform_factory(IncidentWitness,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":False,
            },
        },
        {
            "id":7,
            "title":IncidentPhoto._meta.verbose_name_plural,
            "args":[
                model_master,
                IncidentPhoto
            ],
            "kwargs":{
                "form": modelform_factory(IncidentPhoto,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":False,
            },
        },
        {
            "id":8,
            "title":IncidentAnalysis._meta.verbose_name_plural,
            "args":[
                model_master,
                IncidentAnalysis
            ],
            "kwargs":{
                "form": modelform_factory(IncidentAnalysis,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":False,
            },
        },
        {
            "id":9,
            "title":ContributingFactor._meta.verbose_name_plural,
            "args":[
                model_master,
                ContributingFactor
            ],
            "kwargs":{
                "form": modelform_factory(ContributingFactor,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":False,
            },
        },
        {
            "id":10,
            "title":FactorsAssessment._meta.verbose_name_plural,
            "args":[
                model_master,
                FactorsAssessment
            ],
            "kwargs":{
                "form": modelform_factory(FactorsAssessment,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":False,
            },
        },
        {
            "id":11,
            "title":AppHSECorrectiveAction._meta.verbose_name_plural,
            "args":[
                model_master,
                AppHSECorrectiveAction
            ],
            "kwargs":{
                "form": modelform_factory(AppHSECorrectiveAction,fields="__all__"),
                "exclude":['report', 'state',],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":False,
            },
        },
        {
            "id":12,
            "title":LeasonLearnt._meta.verbose_name_plural,
            "args":[
                model_master,
                LeasonLearnt
            ],
            "kwargs":{
                "form": modelform_factory(LeasonLearnt,fields="__all__"),
                "exclude":['created_by'],
                "extra":0,
                "min_num":1, 
                "validate_min":True,
                "can_delete":False,
            },
        },
    ]

class IncidentInfoListView(ApplicationListView):
    model = model_master
    table_class = IncidentInfoTable
    # filterset_class = CommitmentFilter
    menu_name = "hse_companies:incident_list"
    title = _("List of incidents")
    template_name = "company_profile_exploration/application_list.html"     

    def get_queryset(self):                
        query = super().get_queryset()
        query = query.filter(state__in=[IncidentInfo.STATE_SUBMITTED,])
        return query

class IncidentInfoCreateView(ApplicationMasterDetailCreateView):
    model = model_master
    form_class = form_master
    details = details
    menu_name = "hse_companies:incident_list"
    title = _("Add new incident")            
    template_name = "hse_companies/application_add_master_details.html"     

    def dispatch(self, request,*args, **kwargs):         
        return super().dispatch(request,*args, **kwargs)                    

# class AppWorkPlanUpdateView(ApplicationMasterDetailUpdateView):
#     model = model_master
#     form_class = form_master
#     details = details
#     menu_name = "hse_companies:incident_list"
#     menu_show_name = "hse_companies:incident_show"
#     title = _("Edit work plan")
#     template_name = "company_profile_exploration/application_add_master_details.html"     

#     def get_queryset(self):                
#         query = super().get_queryset()
#         query = query.filter(state__in=[AppWorkPlan.STATE_DRAFT,AppWorkPlan.STATE_REVIEW_COMPANY])
#         return query

#     def post(self, request, *args, **kwargs):
#         response = super().post(request,*args, **kwargs)
#         obj = self.get_object()
#         if self.request.POST.get('_save_confirm') and self.test_group('pa_manager'):
#             obj.state = AppWorkPlan.STATE_GM_DECISION
#             obj.save()

#         return response
        
class IncidentInfoReadonlyView(ApplicationReadonlyView):
    model = model_master
    form_class = form_master
    details = details
    menu_name = "hse_companies:incident_list"
    # menu_edit_name = "hse_companies:incident_edit"
    # menu_delete_name = "hse_companies:incident_delete"
    title = _("Show incident")
    template_name = "hse_companies/application_readonly_master_details.html"     

    def get_queryset(self):                
        query = super().get_queryset()
        query = query.filter(state__in=[IncidentInfo.STATE_SUBMITTED])
        return query

    # def get(self,request,*args, **kwargs):        
    #     obj = self.get_object()
    #     return super().get(request,*args, **kwargs)

# class IncidentInfoDeleteView(ApplicationDeleteMasterDetailView):
#     model = model_master
#     form_class = form_master
#     details = details
#     menu_name = "hse_companies:incident_list"
#     title = _("Delete work plan")
#     template_name = "company_profile_exploration/application_delete_master_detail.html"     

#     def get_queryset(self):                
#         query = super().get_queryset()
#         query = query.filter(state__in=[AppWorkPlan.STATE_DRAFT,])
#         return query
