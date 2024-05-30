import csv
from django.http import HttpResponse

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

class EmployeeBankAccountInline(admin.TabularInline):
    model = EmployeeBankAccount
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class SalafiatInline(admin.TabularInline):
    model = Salafiat
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class JazaatInline(admin.TabularInline):
    model = Jazaat
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class EmployeeBasicAdmin(admin.ModelAdmin):
    fields = ["code","name", "draja_wazifia","alawa_sanawia", "edara_3ama","edara_far3ia", "mosama_wazifi","sex","tarikh_ta3in","moahil","gasima","atfal","aadoa","m3ash"]        
    inlines = [EmployeeBankAccountInline,SalafiatInline,JazaatInline]
    list_display = ["code","name", "draja_wazifia","alawa_sanawia", "edara_3ama","edara_far3ia", "mosama_wazifi","tarikh_ta3in","sex","moahil","gasima","atfal","aadoa","m3ash"]    
    list_display_links = ["code","name"]
    list_filter = ["draja_wazifia","alawa_sanawia","edara_3ama","gasima","atfal",EmployeeTarikhTa3inFilter,"sex","moahil","aadoa","m3ash"] #
    view_on_site = False
    autocomplete_fields = ["mosama_wazifi", "edara_3ama","edara_far3ia"]
    search_fields = ["name","code"]
    actions = ['export_as_csv']

    def has_delete_permission(self, request, obj=None):
        return False
        
    @admin.action(description=_('Export data'))
    def export_as_csv(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="employees.csv"'},
        )
        header = [
                    _("code"),_("name"),_("draja_wazifia"),_("alawa_sanawia"),_( "edara_3ama"),\
                    _("edara_far3ia"),_("mosama_wazifi"),_("tarikh_ta3in"),_("sex"),_("gasima"),_("atfal"),\
                    _("moahil"),_("m3ash"),_("aadoa")
        ]

        writer = csv.writer(response)
        writer.writerow(header)

        for emp in queryset.order_by("draja_wazifia","alawa_sanawia"):
            gasima = _('no')
            if emp.gasima:
                gasima = _('yes')

            aadoa = _('no')
            if emp.aadoa:
                aadoa = _('yes')

            row = [
                    emp.code,emp.name,emp.get_draja_wazifia_display(),emp.get_alawa_sanawia_display(),\
                    emp.edara_3ama.name,emp.edara_far3ia.name,emp.mosama_wazifi.name,emp.tarikh_ta3in,\
                    emp.get_sex_display(),gasima,emp.atfal,emp.get_moahil_display(),emp.m3ash,aadoa
            ]
            writer.writerow(row)

        return response

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

admin.site.register(EmployeeBasic,EmployeeBasicAdmin)

class Drajat3lawatAdmin(admin.ModelAdmin):
    fields = ["draja_wazifia", "alawa_sanawia", "abtdai","galaa_m3isha", "shakhsia","ma3adin"]        
    
    list_display = ["draja_wazifia", "alawa_sanawia", "abtdai","galaa_m3isha", "shakhsia","ma3adin"]
    list_filter = ["draja_wazifia"]
    view_on_site = False

    def has_delete_permission(self, request, obj=None):
        return False

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

# class SalafiatAdmin(admin.ModelAdmin):
#     exclude = ["created_at","created_by","updated_at","updated_by","deducted"]
    
#     list_display = ["employee", "year","month","note","amount","deducted"] 
#     list_filter = ["year","month"]
#     view_on_site = False
#     search_fields = ["employee__name"]
#     autocomplete_fields = ["employee"]

#     def save_model(self, request, obj, form, change):
#         if obj.pk:
#             obj.updated_by = request.user
#         else:
#             obj.created_by = obj.updated_by = request.user
#         super().save_model(request, obj, form, change)                

# admin.site.register(Salafiat,SalafiatAdmin)

# class EmployeeBankAccountAdmin(admin.ModelAdmin):
#     exclude = ["created_at","created_by","updated_at","updated_by"]
    
#     list_display = ["employee", "bank","account_no","active"] 
#     list_filter = ["bank","employee__edara_3ama"]
#     view_on_site = False
#     search_fields = ["employee__name"]
#     autocomplete_fields = ["employee"]

#     def save_model(self, request, obj, form, change):
#         if obj.pk:
#             obj.updated_by = request.user
#         else:
#             obj.created_by = obj.updated_by = request.user
#         super().save_model(request, obj, form, change)                

# admin.site.register(EmployeeBankAccount,EmployeeBankAccountAdmin)

# class JazaatAdmin(admin.ModelAdmin):
#     exclude = ["created_at","created_by","updated_at","updated_by","deducted"]
    
#     list_display = ["employee", "year","month","note","amount","deducted"] 
#     list_filter = ["year","month"]
#     view_on_site = False
#     search_fields = ["employee__name"]
#     autocomplete_fields = ["employee"]

#     def save_model(self, request, obj, form, change):
#         if obj.pk:
#             obj.updated_by = request.user
#         else:
#             obj.created_by = obj.updated_by = request.user
#         super().save_model(request, obj, form, change)                


# admin.site.register(Jazaat,JazaatAdmin)

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

