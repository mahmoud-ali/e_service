from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib import admin

from .models import LkpNationality,LkpState,LkpLocality,LkpCompanyProductionStatus,TblCompanyProduction, \
                                      LkpCompanyProductionFactoryType,TblCompanyProductionFactory,LkpCompanyProductionLicenseStatus, \
                                      TblCompanyProductionLicense,AppForignerMovement,TblCompanyProductionUserRole, \
                                      AppBorrowMaterial,AppBorrowMaterialDetail

from .forms import TblCompanyProductionForm,AppForignerMovementAdminForm,AppBorrowMaterialAdminForm

from .workflow import get_state_choices,send_transition_email,ACCEPTED,APPROVED,REJECTED

admin.site.title = _("Site header")
admin.site.site_title = _("Site header")
admin.site.site_header = _("Site header")
admin.site.site_url = None
    
class LoggingAdminMixin:
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

class WorkflowAdminMixin:
    class Media:
        js = ('admin/js/jquery.init.js',"company_profile/js/state_control.js",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # if request.user.is_superuser:
            # return qs
        filter = []

        if request.user.groups.filter(name="pro_company_application_accept").exists():
            filter += ["submitted"]
        if request.user.groups.filter(name="pro_company_application_approve").exists():
            filter += ["accepted","approved","rejected"]

        return qs.filter(state__in=filter)
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

        user= None
        email = None
        lang = 'ar'
        url = settings.BASE_URL
        
        if obj.notify:
            # print("next transition*****",obj.state)
            if obj.state in (ACCEPTED,APPROVED,REJECTED):
                email = obj.company.email
                lang = get_user_model().objects.get(email=email).lang
                url += obj.get_absolute_url()
            else:
                email = request.user.email
                lang = request.user.lang
                url += request.path
                                
            send_transition_email(obj.state,email,url,lang.lower())
            obj.notify = False
            obj.save()
        

class TblCompanyProductionAdmin(LoggingAdminMixin,admin.ModelAdmin):
    form = TblCompanyProductionForm
    fieldsets = [
        (None, {"fields": [("name_ar","name_en"),"nationality"]}),
        (_("Location information"), {"fields": [("state","locality"),"location","cordinates","address",("website","email")]}),
        (_("Contact information"), {"fields": [("manager_name","manager_phone"),("rep_name","rep_phone")]}),
        (_("Company Status"), {"fields": ["status"]}),
     ]
     
    list_display = ["name_ar", "name_en", "state","status"]
    list_filter = ["name_ar","name_en","state"]
         
    exclude = ["created_at","created_by","updated_at","updated_by"]
    view_on_site = False

    class Media:
        js = ('admin/js/jquery.init.js','company_profile/js/lkp_state_change.js')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)                

        User = get_user_model()
        
        com_user = User.objects.create_user(obj.name_en,obj.email,"changethispassword")
    
        u = TblCompanyProductionUserRole(company=obj,user=com_user)
        u.save()
        
class TblCompanyProductionFactoryAdmin(LoggingAdminMixin,admin.ModelAdmin):
    fields = ["company", ("factory_type","capacity")]
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["company", "factory_type", "capacity"]    
    list_filter = ["factory_type"]
    view_on_site = False
    
class TblCompanyProductionLicenseAdmin(LoggingAdminMixin,admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["company"]}),
        (_("General information"), {"fields": ["date",("start_date","end_date"),("sheet_no","cordinates")]}),
        (_("Contract information"), {"fields": ["area","reserve","gov_rep","rep_percent","com_percent","royalty","zakat","annual_rent","contract_status","contract_file"]}),
     ]        
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["company","sheet_no","date", "start_date", "end_date"]        
    list_filter = ["date","sheet_no"]
    view_on_site = False    
     
admin.site.register(LkpNationality)
admin.site.register(LkpState)
admin.site.register(LkpLocality)
#admin.site.register(LkpCompanyProductionStatus)
admin.site.register(TblCompanyProduction,TblCompanyProductionAdmin)

#admin.site.register(LkpCompanyProductionFactoryType)
admin.site.register(TblCompanyProductionFactory,TblCompanyProductionFactoryAdmin)

#admin.site.register(LkpCompanyProductionLicenseStatus)
admin.site.register(TblCompanyProductionLicense,TblCompanyProductionLicenseAdmin)

#class TblCompanyProductionUserRoleAdmin( admin.ModelAdmin):
#    
#    list_display = ["company","user"]        
#    list_filter = ["company","user"]
#    
#admin.site.register(TblCompanyProductionUserRole, TblCompanyProductionUserRoleAdmin)

class AppForignerMovementAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppForignerMovementAdminForm
    
    list_display = ["company","period_from","period_to", "nationality", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company"]
    view_on_site = False
    
admin.site.register(AppForignerMovement, AppForignerMovementAdmin)

class AppBorrowMaterialDetailInline(admin.TabularInline):
    model = AppBorrowMaterialDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class AppBorrowMaterialAdmin(WorkflowAdminMixin,admin.ModelAdmin):
    form = AppBorrowMaterialAdminForm
    inlines = [AppBorrowMaterialDetailInline]     
    
    list_display = ["company","company_from","borrow_date", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["borrow_date"]
    view_on_site = False
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)                
            
admin.site.register(AppBorrowMaterial, AppBorrowMaterialAdmin)

