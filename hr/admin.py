import csv
from django.http import HttpResponse

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from hr.payroll import M2moriaSheet, MobasharaSheet, Payroll

from .models import Drajat3lawat, EmployeeBankAccount, EmployeeFamily, EmployeeM2moria, EmployeeMoahil, EmployeeJazaat, EmployeeMobashra, EmployeeVacation, Gisim, MosamaWazifi,Edara3ama,Edarafar3ia,EmployeeBasic, PayrollDetail, PayrollMaster, EmployeeSalafiat,Settings, Wi7da

class MosamaWazifiAdmin(admin.ModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["name","category"]        
    list_filter = ["category"]
    view_on_site = False
    search_fields = ["name"]

admin.site.register(MosamaWazifi,MosamaWazifiAdmin)

class Edara3amaAdmin(admin.ModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by"]
    list_display = ["name","tab3ia_edaria"]        
    list_filter = ["tab3ia_edaria"] 
    view_on_site = False
    search_fields = ["name"]

admin.site.register(Edara3ama,Edara3amaAdmin)

class Edarafar3iaAdmin(admin.ModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["name"]        
    view_on_site = False
    search_fields = ["name"]

admin.site.register(Edarafar3ia,Edarafar3iaAdmin)

class GisimAdmin(admin.ModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["name","edara_far3ia"]        
    view_on_site = False
    search_fields = ["name"]
    list_filter = ["edara_far3ia"]
    autocomplete_fields = ["edara_far3ia"]

admin.site.register(Gisim,GisimAdmin)

class Wi7daAdmin(admin.ModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["name","gisim"]        
    view_on_site = False
    search_fields = ["name"]
    list_filter = ["gisim"]
    autocomplete_fields = ["gisim"]

admin.site.register(Wi7da,Wi7daAdmin)

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

class EmployeeWifg2lwazaifFilter(admin.SimpleListFilter):
    title = _("wifg 2lwazif")    
    parameter_name = "wifg_2lwazif"
    def lookups(self, request, model_admin):
        return [
            ('1',_('wifg_2lwazif_giadia')),
            ('2',_('wifg_2lwazif_3lia')),
            ('3',_('wifg_2lwazif_okhra')),
        ]
    
    def queryset(self, request, queryset):
        val = self.value()
        if val == '1':
            return queryset.filter(draja_wazifia__lte=1)
        if val == '2': 
            return queryset.filter(draja_wazifia__in=[2,3,4])
        if val == '3':
            return queryset.filter(draja_wazifia__gte=5)
        
        return queryset

class EmployeeWifg2lmostawiatFilter(admin.SimpleListFilter):
    title = _("wifg 2lmostawiat")    
    parameter_name = "wifg_2lmostawiat"
    def lookups(self, request, model_admin):
        return [
            ('1',_('wifg_2lmostawiat_mosa3di_2lmodir')),
            ('2',_('wifg_2lmostawiat_2l2darat_2l3ama')),
            ('3',_('wifg_2lmostawiat_2l2darat_2lmotakhasisa')),
            ('4',_('wifg_2lmostawiat_ro2sa2_2l2gsam')),
            ('5',_('wifg_2lmostawiat_moshrfi_2lwi7dat')),
            ('6',_('wifg_2lmostawiat_mdkhal_khidma')),
            ('7',_('wifg_2lmostawiat_sa2geen_faneen')),
            ('8',_('wifg_2lmostawiat_2mal')),
        ]
    
    def queryset(self, request, queryset):
        val = self.value()
        if val == '1':
            return queryset.filter(draja_wazifia__lte=-2)
        if val == '2':
            return queryset.filter(draja_wazifia__in=[1,-1,-2,-3])
        if val == '3':
            return queryset.filter(draja_wazifia__in=[4,3,2])
        if val == '4':
            return queryset.filter(draja_wazifia__in=[7,5])
        if val == '5':
            return queryset.filter(draja_wazifia=8)
        if val == '6':
            return queryset.filter(draja_wazifia__in=[9,10])
        if val == '7':
            return queryset.filter(draja_wazifia=12)
        if val == '8':
            return queryset.filter(draja_wazifia=15)
        
        return queryset

class EmployeeBankAccountInline(admin.TabularInline):
    model = EmployeeBankAccount
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class EmployeeFamilyInline(admin.TabularInline):
    model = EmployeeFamily
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class EmployeeMoahilInline(admin.TabularInline):
    model = EmployeeMoahil
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class SalafiatInline(admin.TabularInline):
    model = EmployeeSalafiat
    exclude = ["created_at","created_by","updated_at","updated_by","deducted"]
    extra = 1    

class JazaatInline(admin.TabularInline):
    model = EmployeeJazaat
    exclude = ["created_at","created_by","updated_at","updated_by","deducted"]
    extra = 1    

class EmployeeMobashraInline(admin.TabularInline):
    model = EmployeeMobashra
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class EmployeeVacationInline(admin.TabularInline):
    model = EmployeeVacation
    fk_name = "employee"
    exclude = ["created_at","created_by","updated_at","updated_by"]
    autocomplete_fields = ["mokalaf",]
    extra = 1    

class EmployeeM2moriaInline(admin.TabularInline):
    model = EmployeeM2moria
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class EmployeeBasicAdmin(admin.ModelAdmin):
    fields = ["code","name", "draja_wazifia","alawa_sanawia", "edara_3ama","edara_far3ia","gisim","wi7da", "mosama_wazifi","sex","tarikh_milad","tarikh_ta3in","tarikh_akhir_targia","phone","no3_2lertibat","sanoat_2lkhibra","moahil","gasima","atfal","aadoa","m3ash"]        
    inlines = [EmployeeFamilyInline,EmployeeMoahilInline,EmployeeBankAccountInline,SalafiatInline,JazaatInline,EmployeeMobashraInline,EmployeeVacationInline,EmployeeM2moriaInline]
    list_display = ["code","name", "draja_wazifia","alawa_sanawia", "edara_3ama","edara_far3ia","gisim", "mosama_wazifi","tarikh_ta3in","tarikh_akhir_targia","sex","moahil","gasima","atfal","aadoa","m3ash"]    
    list_display_links = ["code","name"]
    list_filter = ["draja_wazifia","alawa_sanawia","edara_3ama","edara_far3ia","mosama_wazifi__category","gasima","atfal",EmployeeTarikhTa3inFilter,EmployeeWifg2lwazaifFilter,EmployeeWifg2lmostawiatFilter,"sex","moahil","aadoa","m3ash"] #
    view_on_site = False
    autocomplete_fields = ["mosama_wazifi", "edara_3ama","edara_far3ia"]
    search_fields = ["name","code"]
    readonly_fields = ["moahil","gasima","atfal"]
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
                    _("edara_far3ia"),_("gisim"),_("wi7da"),_("mosama_wazifi"),_("tarikh_milad"),_("tarikh_ta3in"),_("tarikh_akhir_targia"),_("sex"),_("gasima"),_("atfal"),\
                    _("moahil"),_("m3ash"),_("aadoa"),_("no3_2lertibat"),_("phone"),_("sanoat_2lkhibra")
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
                    emp.edara_3ama.name,emp.edara_far3ia.name,emp.gisim.name,emp.wi7da.name,emp.mosama_wazifi.name,emp.tarikh_milad,emp.tarikh_ta3in,emp.tarikh_akhir_targia,\
                    emp.get_sex_display(),gasima,emp.atfal,emp.get_moahil_display(),emp.m3ash,aadoa,emp.get_no3_2lertibat_display(),\
                    emp.phone,emp.sanoat_2lkhibra
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
    exclude = ["created_at","created_by","updated_at","updated_by","zaka_kafaf","zaka_nisab","confirmed","enable_sandog_kahraba","enable_youm_algoat_almosalaha","daribat_2lmokafa"]
    inlines = [PayrollDetailInline]

    # list_display = ["year","month","confirmed","show_badalat_link","show_khosomat_link","show_mokaf2_link","show_mobashara_link"]
    list_filter = ["year","month","confirmed"]
    view_on_site = False
    list_select_related = True

    actions = ["confirm_payroll"]

    # readonly_fields = ["year","month","confirmed"]

    def get_list_display(self,request):
        if request.user.groups.filter(name="hr_manager").exists():
            return ["year","month","confirmed","show_badalat_link","show_khosomat_link","show_mokaf2_link","show_mobashara_link","show_m2moria_link"]
        else:
            return ["year","month","confirmed","show_badalat_link","show_khosomat_link"]

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
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv&bank_sheet=1">'+_('bank sheet')+'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month)

    @admin.display(description=_('Show mobashara sheet'))
    def show_mobashara_link(self, obj):
        url = reverse('hr:payroll_mobashara')
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}">'+_('Show mobashara sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv&bank_sheet=1">'+_('bank sheet')+'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month)

    @admin.display(description=_('Show mokaf2 sheet'))
    def show_mokaf2_link(self, obj):
        url = reverse('hr:payroll_mokaf2')
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}">'+_('Show mokaf2 sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv&bank_sheet=1">'+_('bank sheet')+'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month)

    @admin.display(description=_('Show m2moria sheet'))
    def show_m2moria_link(self, obj):
        url = reverse('hr:payroll_m2moria')
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}">'+_('Show m2moria sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv&bank_sheet=1">'+_('bank sheet')+'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month)

    def save_model(self, request, obj, form, change):
        payroll = Payroll(obj.year,obj.month)
        payroll.calculate()

        mobashara = MobasharaSheet(obj.year,obj.month)
        mobashara.calculate()

        m2moria = M2moriaSheet(obj.year,obj.month)
        m2moria.calculate()

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.confirmed:
            return False
        
        return True
    
    @admin.action(description=_('Confirm payroll'))
    def confirm_payroll(self, request, queryset):
        queryset.update(confirmed=True)

        for q in queryset:
            mobashara = MobasharaSheet(q.year,q.month)
            mobashara.confirm()

            m2moria = M2moriaSheet(q.year,q.month)
            m2moria.calculate()

admin.site.register(PayrollMaster,PayrollMasterAdmin)

