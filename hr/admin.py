from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from hr.payroll import Payroll

from .models import Drajat3lawat, EmployeeBankAccount, Jazaat, MosamaWazifi,Edara3ama,Edarafar3ia,EmployeeBasic, PayrollDetail, PayrollMaster, Salafiat,Settings

class MosamaWazifiAdmin(admin.ModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by","deducted"]
    
    list_display = ["name"]        
    view_on_site = False
    search_fields = ["name"]

admin.site.register(MosamaWazifi,MosamaWazifiAdmin)

class Edara3amaAdmin(admin.ModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by","deducted"]
    
    list_display = ["name"]        
    view_on_site = False
    search_fields = ["name"]

admin.site.register(Edara3ama,Edara3amaAdmin)

class Edarafar3iaAdmin(admin.ModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by","deducted"]
    
    list_display = ["name"]        
    view_on_site = False
    search_fields = ["name"]

admin.site.register(Edarafar3ia,Edarafar3iaAdmin)

class EmployeeTarikhTa3inFilter(admin.SimpleListFilter):
    title = _("tarikh_ta3in")    
    parameter_name = "year"
    def lookups(self, request, model_admin):
        qs = EmployeeBasic.objects.order_by('tarikh_ta3in__year').distinct("tarikh_ta3in__year").values_list("tarikh_ta3in__year")
        return [(x[0],x[0]) for x in qs]
    
    def queryset(self, request, queryset):
        year = self.value()
        if year:
            return queryset.filter(tarikh_ta3in__year=int(year))
        
        return queryset
    
class EmployeeBasicAdmin(admin.ModelAdmin):
    fields = ["code","name", "mosama_wazifi", "edara_3ama","edara_far3ia", "draja_wazifia","alawa_sanawia","tarikh_ta3in","gasima","atfal","moahil","m3ash"]        
    
    list_display = ["code","name", "mosama_wazifi", "edara_3ama","edara_far3ia", "draja_wazifia","alawa_sanawia","tarikh_ta3in"]    
    list_display_links = ["code","name"]
    list_filter = ["edara_3ama","draja_wazifia","alawa_sanawia","gasima","atfal","moahil","m3ash",EmployeeTarikhTa3inFilter] #
    view_on_site = False
    autocomplete_fields = ["mosama_wazifi", "edara_3ama","edara_far3ia"]
    search_fields = ["name","code"]

admin.site.register(EmployeeBasic,EmployeeBasicAdmin)

class Drajat3lawatAdmin(admin.ModelAdmin):
    fields = ["draja_wazifia", "alawa_sanawia", "abtdai","galaa_m3isha", "shakhsia","ma3adin","aadoa"]        
    
    list_display = ["draja_wazifia", "alawa_sanawia", "abtdai","galaa_m3isha", "shakhsia","ma3adin","aadoa"]
    list_filter = ["draja_wazifia"]
    view_on_site = False

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

admin.site.register(Drajat3lawat,Drajat3lawatAdmin)

class SettingsAdmin(admin.ModelAdmin):
    fields = ["code", "value"]        
    
    list_display = ["code", "value"] 
    list_filter = ["code"]
    view_on_site = False

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

admin.site.register(Settings,SettingsAdmin)

class SalafiatAdmin(admin.ModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by","deducted"]
    
    list_display = ["employee", "year","month","note","amount","deducted"] 
    list_filter = ["year","month"]
    view_on_site = False
    search_fields = ["employee__name"]
    autocomplete_fields = ["employee"]

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

admin.site.register(Salafiat,SalafiatAdmin)

class EmployeeBankAccountAdmin(admin.ModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["employee", "bank","account_no","active"] 
    list_filter = ["bank","employee__edara_3ama"]
    view_on_site = False
    search_fields = ["employee__name"]
    autocomplete_fields = ["employee"]

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

admin.site.register(EmployeeBankAccount,EmployeeBankAccountAdmin)

class JazaatAdmin(admin.ModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by","deducted"]
    
    list_display = ["employee", "year","month","note","amount","deducted"] 
    list_filter = ["year","month"]
    view_on_site = False
    search_fields = ["employee__name"]
    autocomplete_fields = ["employee"]

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                


admin.site.register(Jazaat,JazaatAdmin)

class PayrollDetailInline(admin.TabularInline):
    model = PayrollDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 0
    readonly_fields = ['employee','abtdai','galaa_m3isha','shakhsia','aadoa','gasima','atfal','moahil','ma3adin','m3ash','salafiat','jazaat','damga','sandog','sandog_kahraba']
    can_delete = False
    list_select_related = True
    def has_add_permission(self,request, obj):
        return False
    
class PayrollMasterAdmin(admin.ModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by","zaka_kafaf","zaka_nisab"]
    inlines = [PayrollDetailInline]

    list_display = ["year","month","confirmed","show_badalat_link","show_khosomat_link"] 
    list_filter = ["year","month","confirmed"]
    view_on_site = False
    list_select_related = True

    actions = ["confirm_payroll"]

    # readonly_fields = ["year","month","confirmed"]

    @admin.display(description=_('Show badalat sheet'))
    def show_badalat_link(self, obj):
        url = reverse('hr:payroll_badalat')
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}">'+_('Show badalat sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month)

    @admin.display(description=_('Show khosomat sheet'))
    def show_khosomat_link(self, obj):
        url = reverse('hr:payroll_khosomat')
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}">'+_('Show khosomat sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month)

    def save_model(self, request, obj, form, change):
        payroll = Payroll(obj.year,obj.month)
        payroll.calculate()

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.confirmed:
            return False
        
        return True
    
    @admin.action(description=_('Confirm payroll'))
    def confirm_payroll(self, request, queryset):
        queryset.update(confirmed=True)

admin.site.register(PayrollMaster,PayrollMasterAdmin)

