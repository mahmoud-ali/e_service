from django.db import models
from django.forms.widgets import TextInput
from django.utils.translation import gettext_lazy as _

from django.contrib import admin

from hr.models import EmployeeFamily
from hr_bot.models import STATE_ACCEPTED, STATE_DRAFT, STATE_REJECTED, EmployeeTelegram, EmployeeTelegramFamily, EmployeeTelegramRegistration

class PermissionMixin:
    def has_add_permission(self, request):
        return False

    # def has_change_permission(self, request, obj=None):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

class FlowMixin:
    actions = ['accept','reject']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(state=STATE_DRAFT)

    @admin.action(description=_('Accept'))
    def accept(self, request, queryset):
        raise NotImplementedError
    
    @admin.action(description=_('Reject'))
    def reject(self, request, queryset):
        for obj in queryset:
            obj.state = STATE_REJECTED
            obj.save()


@admin.register(EmployeeTelegram)
class EmployeeTelegramAdmin(admin.ModelAdmin):
    model = EmployeeTelegram
    exclude = ["created_at","created_by","updated_at","updated_by"] #,"user_id"
    list_display = ["employee","phone"]        
    # list_filter = ["category"]
    autocomplete_fields = ["employee"]
    view_on_site = False
    search_fields = ["employee__name","phone"]

    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)    

@admin.register(EmployeeTelegramRegistration)
class EmployeeTelegramRegistrationAdmin(PermissionMixin,FlowMixin,admin.ModelAdmin):
    model = EmployeeTelegramRegistration
    exclude = ["created_at","created_by","updated_at","updated_by","state"] #,"user_id"
    list_display = ["employee","name","phone"]        
    # list_filter = ["category"]
    view_on_site = False
    search_fields = ["employee__name","phone","name"]
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    @admin.action(description=_('Accept'))
    def accept(self, request, queryset):
        for obj in queryset:
            obj.state = STATE_ACCEPTED
            obj.save()

            EmployeeTelegram.objects.create(
                employee=obj.employee,
                user_id=obj.user_id,
                phone=obj.phone,
                created_by=request.user,
                updated_by=request.user,
            )


@admin.register(EmployeeTelegramFamily)
class EmployeeTelegramFamilyAdmin(PermissionMixin,FlowMixin,admin.ModelAdmin):
    model = EmployeeTelegramFamily
    exclude = ["created_at","created_by","updated_at","updated_by","state"] #,"user_id"
    list_display = ["employee","name","relation"]        
    # list_filter = ["category"]
    autocomplete_fields = ["employee"]
    view_on_site = False
    search_fields = ["employee__name","name"]

    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)    

    @admin.action(description=_('Accept'))
    def accept(self, request, queryset):
        for obj in queryset:
            print(f"obj: {obj}")
            obj.state = STATE_ACCEPTED
            obj.save()

            EmployeeFamily.objects.create(
                employee=obj.employee,
                relation=obj.relation,
                name=obj.name,
                tarikh_el2dafa=obj.tarikh_el2dafa,
                attachement_file=obj.attachement_file,

                created_by=request.user,
                updated_by=request.user,
            )
