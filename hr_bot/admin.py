import random
from django.db import models
from django.forms.widgets import TextInput
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django.contrib import admin
import requests
from django.contrib.auth.models import  Group
from django.contrib.auth import get_user_model

from hr.admin import SalafiatForm
from hr.models import EmployeeBankAccount, EmployeeFamily, EmployeeMoahil
from hr_bot.management.commands.telegram_main import TOKEN_ID
from hr_bot.models import STATE_ACCEPTED, STATE_DRAFT, STATE_REJECTED, EmployeeBankAccountProxy, EmployeeBasicProxy, EmployeeFamilyProxy, EmployeeMoahilProxy, EmployeeTelegram, EmployeeTelegramBankAccount, EmployeeTelegramFamily, EmployeeTelegramMoahil, EmployeeTelegramRegistration, JazaatProxy, SalafiatProxy

User = get_user_model()

class PermissionMixin:
    def has_add_permission(self, request):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            return True
        
        return False

    # def has_change_permission(self, request, obj=None):
    #     return False

    def has_delete_permission(self, request, obj=None):
        if obj and obj.state == STATE_DRAFT:
            return True
        
        return False

class FlowMixin:
    actions = ['accept','reject']

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user

        obj.employee = EmployeeTelegram.objects.get(email=request.user.email).employee
        super().save_model(request, obj, form, change)    

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name__in=["hr_manager","hr_manpower"]).exists():
            return qs.filter(state=STATE_DRAFT)

        return qs.filter(employee__email=request.user.email)
    
    def get_exclude(self,request, obj=None):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            return self.exclude+['employee']

        return self.exclude
    
    def get_readonly_fields(self,request, obj=None):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            return []

        return ["employee",]

    @admin.action(description=_('Accept'))
    def accept(self, request, queryset):
        raise NotImplementedError
    
    @admin.action(description=_('Reject'))
    def reject(self, request, queryset):
        for obj in queryset:
            obj.state = STATE_REJECTED
            obj.save()
            self.message_user(request,_('application rejected!'))

# @admin.register(EmployeeTelegram)
# class EmployeeTelegramAdmin(admin.ModelAdmin):
#     model = EmployeeTelegram
#     exclude = ["created_at","created_by","updated_at","updated_by"] #,"user_id"
#     list_display = ["employee","phone"]        
#     # list_filter = ["category"]
#     autocomplete_fields = ["employee"]
#     view_on_site = False
#     search_fields = ["employee__name","phone"]

#     formfield_overrides = {
#         models.FloatField: {"widget": TextInput},
#     }    

#     def save_model(self, request, obj, form, change):
#         if obj.pk:
#             obj.updated_by = request.user
#         else:
#             obj.created_by = obj.updated_by = request.user
#         super().save_model(request, obj, form, change)    

@admin.register(EmployeeTelegramRegistration)
class EmployeeTelegramRegistrationAdmin(FlowMixin,admin.ModelAdmin):
    model = EmployeeTelegramRegistration
    exclude = ["created_at","created_by","updated_at","updated_by","state"] #,"user_id"
    list_display = ["employee","name","phone"]        
    # list_filter = ["category"]
    view_on_site = False
    search_fields = ["employee__name","phone","name"]
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    def has_add_permission(self, request):
        return False

    # def has_change_permission(self, request, obj=None):
    #     return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description=_('Accept'))
    def accept(self, request, queryset):
        for obj in queryset:
            obj.state = STATE_ACCEPTED
            obj.save()

            EmployeeTelegram.objects.update_or_create(
                employee=obj.employee,
                user_id=obj.user_id,
                phone=obj.phone,
                created_by=request.user,
                updated_by=request.user,
            )
            self.message_user(request,_('application accepted!'))

        portal_url = "https://hr1.mineralsgate.com/app/managers/"
        username = obj.employee.email

        if User.objects.filter(username=username).exists():
            # user = User.objects.get(username=username)
            message = f"الآن يمكنك الدخول لبوابة الموارد البشرية عبر الرابط التالي {portal_url} \n باسم المستخدم {username}"

        else:
            password = f"{username}{int(random.random()*10000)}"

            user = User.objects.create_user(username, username, password, is_staff=True)

            employee_group = Group.objects.get(name='hr_employee') 
            employee_group.user_set.add(user)

            message = f"الآن يمكنك الدخول لبوابة الموارد البشرية عبر الرابط التالي {portal_url} \n باسم المستخدم {username} \n وكلمة المرور{password}"

        telegram_url = f"https://api.telegram.org/bot{TOKEN_ID}/sendMessage?chat_id={int(obj.user_id)}&text={message}"
        requests.get(telegram_url)

@admin.register(EmployeeTelegramFamily)
class EmployeeTelegramFamilyAdmin(PermissionMixin,FlowMixin,admin.ModelAdmin):
    model = EmployeeTelegramFamily
    exclude = ["created_at","created_by","updated_at","updated_by","state","tarikh_el2dafa"] #,"user_id"
    list_display = ["name","relation"]        
    # list_filter = ["category"]
    autocomplete_fields = ["employee"]
    view_on_site = False
    search_fields = ["employee__name","employee__code"]

    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

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
                tarikh_el2dafa=timezone.now(),
                attachement_file=obj.attachement_file,

                created_by=request.user,
                updated_by=request.user,
            )
            self.message_user(request,_('application accepted!'))

@admin.register(EmployeeTelegramMoahil)
class EmployeeTelegramMoahilAdmin(PermissionMixin,FlowMixin,admin.ModelAdmin):
    model = EmployeeTelegramMoahil
    exclude = ["created_at","created_by","updated_at","updated_by","state","tarikh_el2dafa"] #,"user_id"
    list_display = ["employee","moahil","university","graduate_dt"]        
    list_filter = ["moahil","university"]
    autocomplete_fields = ["employee"]
    view_on_site = False
    search_fields = ["employee__name","employee__code"]

    # formfield_overrides = {
    #     models.FloatField: {"widget": TextInput},
    # }    

    @admin.action(description=_('Accept'))
    def accept(self, request, queryset):
        for obj in queryset:
            print(f"obj: {obj}")
            obj.state = STATE_ACCEPTED
            obj.save()

            EmployeeMoahil.objects.create(
                employee=obj.employee,
                moahil=obj.moahil,
                university=obj.university,
                takhasos=obj.takhasos,
                graduate_dt=obj.graduate_dt,
                tarikh_el2dafa=timezone.now(),
                attachement_file=obj.attachement_file,

                created_by=request.user,
                updated_by=request.user,
            )
            self.message_user(request,_('application accepted!'))

@admin.register(EmployeeTelegramBankAccount)
class EmployeeTelegramBankAccountAdmin(PermissionMixin,FlowMixin,admin.ModelAdmin):
    model = EmployeeTelegramBankAccount
    exclude = ["created_at","created_by","updated_at","updated_by","state"] #,"user_id"
    list_display = ["employee","bank","account_no","active"]        
    list_filter = ["bank",]
    autocomplete_fields = ["employee"]
    view_on_site = False
    search_fields = ["employee__name","employee__code"]

    # formfield_overrides = {
    #     models.FloatField: {"widget": TextInput},
    # }    

    @admin.action(description=_('Accept'))
    def accept(self, request, queryset):
        for obj in queryset:
            print(f"obj: {obj}")
            obj.state = STATE_ACCEPTED
            obj.save()

            EmployeeBankAccount.objects.create(
                employee=obj.employee,
                bank=obj.bank,
                account_no=obj.account_no,
                active=obj.active,

                created_by=request.user,
                updated_by=request.user,
            )
            self.message_user(request,_('application accepted!'))

class EmployeeBankAccountInline(admin.TabularInline):
    model = EmployeeBankAccountProxy
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 0   

class EmployeeFamilyInline(admin.TabularInline):
    model = EmployeeFamilyProxy
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 0

class EmployeeMoahilInline(admin.TabularInline):
    model = EmployeeMoahilProxy
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 0

class SalafiatInline(admin.TabularInline):
    model = SalafiatProxy
    form = SalafiatForm
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
        models.IntegerField: {"widget": TextInput},
    }    
    extra = 0

class JazaatInline(admin.TabularInline):
    model = JazaatProxy
    exclude = ["created_at","created_by","updated_at","updated_by"]
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
        models.IntegerField: {"widget": TextInput},
    }    
    extra = 0

@admin.register(EmployeeBasicProxy)
class EmployeeBasicProxyAdmin(admin.ModelAdmin):
    model = EmployeeBasicProxy
    inlines = [EmployeeBankAccountInline, EmployeeFamilyInline, EmployeeMoahilInline,SalafiatInline,JazaatInline]
    fields = ["code","name", "draja_wazifia","alawa_sanawia","hikal_wazifi", "edara_3ama_tmp","edara_far3ia_tmp", "mosama_wazifi","sex","tarikh_milad","tarikh_ta3in","tarikh_akhir_targia","phone","email","no3_2lertibat","sanoat_2lkhibra","aadoa","m3ash","status"]        
    list_display = ["code","name", "draja_wazifia","alawa_sanawia", "edara_3ama","edara_far3ia","gisim", "mosama_wazifi","tarikh_ta3in",]        
    view_on_site = False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        email = request.user.email

        return qs.filter(email=email)
