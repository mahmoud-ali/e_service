from django.contrib import admin

from doc_workflow.models import ActionType, ApplicationDelivery, ApplicationDepartmentProcessing, ApplicationExectiveProcessing, ApplicationRecord, ApplicationType, Department, Destination

admin.site.register(ApplicationType)
admin.site.register(ActionType)
admin.site.register(Department)
admin.site.register(Destination)

class ApplicationDepartmentProcessingInline(admin.TabularInline):
    model = ApplicationDepartmentProcessing
    exclude = ["created_at","created_by","updated_at","updated_by","attachement_file","action_state"]
    extra = 1    

class ApplicationDeliveryInline(admin.TabularInline):
    model = ApplicationDelivery
    exclude = ["created_at","created_by","updated_at","updated_by","delivery_state"]
    extra = 1    

class ApplicationRecordAdmin(admin.ModelAdmin):
    # form = TblCompanyCommitmentAdminForm
    exclude = ["created_at","created_by","updated_at","updated_by"]
    inlines = [ApplicationDepartmentProcessingInline,ApplicationDeliveryInline]     
    
    list_display = ["company","app_type", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["company","app_type"]
    view_on_site = False

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if obj.pk:
                obj.updated_by = request.user
            else:
                obj.created_by = obj.updated_by = request.user

        super().save_formset(request, form, formset, change)                      

admin.site.register(ApplicationRecord, ApplicationRecordAdmin)

class ApplicationDepartmentProcessingAdmin(admin.ModelAdmin):
    # form = TblCompanyCommitmentAdminForm
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["app_record","department","action_type", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["app_record","department"]
    view_on_site = False

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

admin.site.register(ApplicationDepartmentProcessing, ApplicationDepartmentProcessingAdmin)

class ApplicationExectiveProcessingAdmin(admin.ModelAdmin):
    # form = TblCompanyCommitmentAdminForm
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["department_processing", "created_at", "created_by","updated_at", "updated_by"]        
    list_filter = ["department_processing"]
    view_on_site = False

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

admin.site.register(ApplicationExectiveProcessing, ApplicationExectiveProcessingAdmin)
