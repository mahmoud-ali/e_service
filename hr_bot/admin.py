import random
from django.db import IntegrityError, models
from django.forms.widgets import TextInput
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django.contrib import admin
from django.contrib.auth.models import  Group
from django.contrib.auth import get_user_model

from hr.admin import SalafiatForm
from hr.models import EmployeeBankAccount, EmployeeFamily, EmployeeMoahil
from hr_bot.management.commands._telegram_main import TOKEN_ID
from hr_bot.models import STATE_ACCEPTED, STATE_DRAFT, STATE_REJECTED, ApplicationRequirement, EmployeeBankAccountProxy, EmployeeBasicProxy, EmployeeFamilyProxy, EmployeeMoahilProxy, EmployeeTelegram, EmployeeTelegramBankAccount, EmployeeTelegramFamily, EmployeeTelegramMoahil, EmployeeTelegramRegistration, JazaatProxy, SalafiatProxy
from hr_bot.utils import create_user, reject_cause, reset_user_password, send_message

User = get_user_model()

portal_url = "https://hr1.mineralsgate.com/app/managers/"

class PermissionMixin:
    def has_add_permission(self, request):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            return True
        
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            return False
        
        if obj and obj.state == STATE_DRAFT:
            return True
        
        return False


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

        obj.employee = EmployeeTelegram.objects.filter(employee__email=request.user.email).first().employee
        super().save_model(request, obj, form, change)    

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name__in=["hr_manager","hr_manpower"]).exists():
            return qs #.filter(state=STATE_DRAFT)

        return qs.filter(employee__email=request.user.email)
    
    def get_exclude(self,request, obj=None):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            return self.exclude+['employee']

        return self.exclude
    
    def get_readonly_fields(self,request, obj=None):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            return []

        return ["employee",]

    def get_actions(self, request):
        if not request.user.groups.filter(name__in=["hr_manager","hr_manpower",]).exists():
            return []

        return super().get_actions(request)

    @admin.action(description=_('Accept'))
    def accept(self, request, queryset):
        raise NotImplementedError
    
    @admin.action(description=_('Reject'))
    def reject(self, request, queryset):
        for obj in queryset:
            if obj.state ==STATE_DRAFT:
                obj.state = STATE_REJECTED
                obj.save()
                self.log_change(request,obj,"تحويل الطلب إلى "+"مرفوض")
                self.message_user(request,_('application rejected!'))

                message = f"تم رفض طلبك: {obj}. الرجاء مراجعة البيانات.\n\n{reject_cause(self.model,obj)}"

                try:
                    user_id = obj.employee.employeetelegramregistration_set.first().user_id
                    send_message(TOKEN_ID, user_id, message)

                    obj.delete()
                except:
                    pass
            

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
    list_display = ["employee","name","phone","state"]        
    list_filter = ["created_at","state"]
    actions = ['accept','reject','reset_password']
    view_on_site = False
    search_fields = ["employee__name","phone","name"]
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if obj and obj.state == STATE_DRAFT:
            return super().has_change_permission(request, obj)

        return False

    def has_delete_permission(self, request, obj=None):
        if obj and obj.state == STATE_DRAFT:
            return super().has_delete_permission(request, obj)
        
        return False

    @admin.action(description=_('Accept'))
    def accept(self, request, queryset):
        for obj in queryset:
            obj.state = STATE_ACCEPTED
            obj.save()
            self.log_change(request,obj,"تحويل الطلب إلى "+"مقبول")


            try:
                emp, bool =EmployeeTelegram.objects.update_or_create(
                    employee=obj.employee,
                    user_id=obj.user_id,
                    phone=obj.phone,
                    created_by=request.user,
                    updated_by=request.user,
                )
                self.message_user(request,_('application accepted!'))
            except IntegrityError:
                obj.state = STATE_REJECTED
                obj.save()
                self.message_user(request,_('تم رفض الطلب لأن الهاتف موجود مسبقاً'))
                self.log_change(request,obj,'تم رفض الطلب لأن الهاتف موجود مسبقاً')

            username = obj.employee.email

            if not username:
                message = f"لاتمتلك بريداً إلكترونياً. الرجاء مراجعة إدارة الموارد البشرية لتخصيص بريد إلكتروني لك."
                send_message(TOKEN_ID, obj.user_id, message)
                return

            obj.employee.phone = obj.phone
            obj.employee.save()

            if User.objects.filter(username=username).exists():
                # user = User.objects.get(username=username)
                message = f"الآن يمكنك الدخول لبوابة الموارد البشرية عبر الرابط التالي\n {portal_url} \n باسم المستخدم {username}"

            else:
                password = f"{int(random.random()*1000000)}"

                user = create_user(username, username, password)

                message = f"الآن يمكنك الدخول لبوابة الموارد البشرية عبر الرابط التالي\n {portal_url} \n باسم المستخدم {username} \n وكلمة المرور {password}"
                self.log_change(request,obj,"اعتماد مستخدم جديد")

            send_message(TOKEN_ID, obj.user_id, message)

    @admin.action(description=_('إعادة تعيين كلمة مرور الموظف'))
    def reset_password(self, request, queryset):
        for obj in queryset:
            password = f"{int(random.random()*1000000)}"
            message = f"تم إعادة تعيين كلمة المرور الخاصة بك.\nالآن يمكنك الدخول لبوابة الموارد البشرية عبر الرابط التالي {portal_url} \n باسم المستخدم {obj.employee.email} \n وكلمة المرور {password}"
            reset_user_password(obj.employee.email,password)
            send_message(TOKEN_ID, obj.user_id, message)

            self.message_user(request,_('password reset!'))
            self.log_change(request,obj,"إعادة تعيين كلمة مرور الموظف")

@admin.register(EmployeeTelegramFamily)
class EmployeeTelegramFamilyAdmin(PermissionMixin,FlowMixin,admin.ModelAdmin):
    model = EmployeeTelegramFamily
    exclude = ["created_at","created_by","updated_at","updated_by","state"] #,"user_id"
    list_display = ["employee","name","relation","attachement_file","state"]        
    list_filter = ["created_at","state"]
    autocomplete_fields = ["employee"]
    view_on_site = False
    search_fields = ["employee__name","employee__code"]

    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    @admin.action(description=_('Accept'))
    def accept(self, request, queryset):
        for obj in queryset:
            if obj.state ==STATE_DRAFT:
                obj.state = STATE_ACCEPTED
                obj.save()
                self.log_change(request,obj,"تحويل الطلب إلى "+"مقبول")

                EmployeeFamily.objects.create(
                    employee=obj.employee,
                    relation=obj.relation,
                    name=obj.name,
                    tarikh_el2dafa=obj.tarikh_el2dafa,
                    attachement_file=obj.attachement_file,

                    created_by=request.user,
                    updated_by=request.user,
                )
                self.message_user(request,_('application accepted!'))

                message = f"تم قبول طلبك: {obj}."

                try:
                    user_id = obj.employee.employeetelegramregistration_set.first().user_id
                    send_message(TOKEN_ID, user_id, message)
                except:
                    pass

@admin.register(EmployeeTelegramMoahil)
class EmployeeTelegramMoahilAdmin(PermissionMixin,FlowMixin,admin.ModelAdmin):
    model = EmployeeTelegramMoahil
    exclude = ["created_at","created_by","updated_at","updated_by","state","tarikh_el2dafa"] #,"user_id"
    list_display = ["employee","moahil","university","graduate_dt","state"]        
    list_filter = ["created_at","moahil","state"]
    autocomplete_fields = ["employee"]
    view_on_site = False
    search_fields = ["employee__name","employee__code"]

    # formfield_overrides = {
    #     models.FloatField: {"widget": TextInput},
    # }    

    @admin.action(description=_('Accept'))
    def accept(self, request, queryset):
        for obj in queryset:
            if obj.state ==STATE_DRAFT:
                obj.state = STATE_ACCEPTED
                obj.save()
                self.log_change(request,obj,"تحويل الطلب إلى "+"مقبول")

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

                message = f"تم قبول طلبك: {obj}."

                try:
                    user_id = obj.employee.employeetelegramregistration_set.first().user_id
                    send_message(TOKEN_ID, user_id, message)
                except:
                    pass

@admin.register(EmployeeTelegramBankAccount)
class EmployeeTelegramBankAccountAdmin(PermissionMixin,FlowMixin,admin.ModelAdmin):
    model = EmployeeTelegramBankAccount
    exclude = ["created_at","created_by","updated_at","updated_by","state"] #,"user_id"
    list_display = ["employee","bank","account_no","active","state"]        
    list_filter = ["created_at","bank","state"]
    autocomplete_fields = ["employee"]
    view_on_site = False
    search_fields = ["employee__name","employee__code"]

    # formfield_overrides = {
    #     models.FloatField: {"widget": TextInput},
    # }    

    @admin.action(description=_('Accept'))
    def accept(self, request, queryset):
        for obj in queryset:
            if obj.state ==STATE_DRAFT:
                try:
                    EmployeeBankAccount.objects.update_or_create(
                        employee=obj.employee,
                        bank=obj.bank,
                        branch_code=obj.branch_code,
                        account_type=obj.account_type,
                        account_no=obj.account_no,
                        active=obj.active,

                        created_by=request.user,
                        updated_by=request.user,
                    )
                    self.message_user(request,_('application accepted!'))
                    self.log_change(request,obj,"تحويل الطلب إلى "+"مقبول")

                    message = f"تم قبول طلبك: {obj}."

                    obj.state = STATE_ACCEPTED
                    obj.save()

                    try:
                        user_id = obj.employee.employeetelegramregistration_set.first().user_id
                        send_message(TOKEN_ID, user_id, message)
                    except:
                        pass

                except IntegrityError:
                    obj.state = STATE_REJECTED
                    obj.save()
                    self.message_user(request,_('تم رفض الطلب لأن رقم الحساب موجود مسبقاً'))
                    self.log_change(request,obj,'تم رفض الطلب لأن رقم الحساب موجود مسبقاً')

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
    fields = ["code","name", "draja_wazifia","alawa_sanawia","hikal_wazifi", "mosama_wazifi","sex","tarikh_milad","tarikh_ta3in","tarikh_akhir_targia","gasima","atfal","moahil","phone","email","no3_2lertibat","sanoat_2lkhibra","aadoa","m3ash","status"]        
    readonly_fields = ["code","name", "draja_wazifia","alawa_sanawia","hikal_wazifi", "mosama_wazifi","sex","tarikh_milad","tarikh_ta3in","tarikh_akhir_targia","gasima","atfal","phone","email","no3_2lertibat","sanoat_2lkhibra","aadoa","m3ash","status"]        
    list_display_links = ["code","name"]
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

@admin.register(EmployeeBankAccountProxy)
class EmployeeBankAccountProxyAdmin(admin.ModelAdmin):
    model = EmployeeBankAccountProxy
    fields = ["bank","branch_code", "account_type","account_no","active", ]        
    readonly_fields = ["bank","branch_code", "account_type","account_no",]        
    list_display_links = ["bank","branch_code"]
    list_display = ["bank","branch_code", "account_type","account_no","active"]        
    view_on_site = False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        email = request.user.email

        return qs.filter(email=email)
@admin.register(ApplicationRequirement)
class ApplicationRequirementAdmin(admin.ModelAdmin):
    model = ApplicationRequirement
    list_display = ["app","requirement"]
    list_filter = ["app"]
    view_on_site = False

@admin.register(EmployeeBankAccountProxy)
class EmployeeBankAccountAdmin(admin.ModelAdmin):
    model = EmployeeBankAccountProxy
    list_display = ('bank', 'account_no','active')
    fields = ('employee','bank','account_no','active')
    exclude = ["created_at","created_by","updated_at","updated_by"]
    readonly_fields = ('employee','bank','account_no',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # if request.user.is_superuser or request.user.groups.filter(name__in=["hr_manager","hr_manpower"]).exists():
        #     return qs #.filter(state=STATE_DRAFT)

        return qs.filter(employee__email=request.user.email)
    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False
