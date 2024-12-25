import codecs
import csv
from django.db import models
from django.db.models import Sum
from django.contrib.admin.options import InlineModelAdmin
from django.forms import ModelForm, ValidationError
from django.forms.widgets import TextInput
from django.http import HttpRequest, HttpResponse

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from hr.calculations import PayrollValidation
from hr.payroll import M2moriaSheet, MajlisEl2daraMokaf2Payroll, MobasharaSheet, Mokaf2Sheet, Payroll, Ta3agodMosimiPayroll, TasoiaPayroll, Wi7datMosa3idaMokaf2tFarigMoratabPayroll

from .models import Drajat3lawat, EmployeeBankAccount, EmployeeFamily, EmployeeM2moria, EmployeeM2moriaMonthly, EmployeeMajlisEl2dara, EmployeeMoahil, EmployeeJazaat, EmployeeMobashra, EmployeeTelegram, EmployeeTelegramRegistration, EmployeeVacation, EmployeeWi7datMosa3da, Gisim, HikalWazifi, MosamaWazifi,Edara3ama,Edarafar3ia,EmployeeBasic, PayrollDetail, PayrollDetailMajlisEl2dara, PayrollDetailTa3agodMosimi, PayrollDetailWi7datMosa3ida, PayrollMaster, EmployeeSalafiat, PayrollTasoia,Settings, Wi7da
from mptt.admin import MPTTModelAdmin,TreeRelatedFieldListFilter

class SalafiatMixin(ModelForm):
    def clean_amount(self):
        amount = uploaded_image = self.cleaned_data.get("amount",  0)
        old_month = uploaded_image = self.cleaned_data.get("month",  None)
        old_year = uploaded_image = self.cleaned_data.get("year",  None)
        no3_2lsalafia = uploaded_image = self.cleaned_data.get("no3_2lsalafia",  EmployeeSalafiat.NO3_2LSALAFIA_SANDOG)

        month=old_month
        year = old_year

        if not month or not year:
            raise ValidationError("invalid month or year")

        payroll_curr = Payroll(year,month)

        is_changed = 'amount' in self.changed_data

        if is_changed and payroll_curr.is_calculated():
            raise ValidationError(_("you can not change this record salary already calculated!"))
        
        if month == 1:
            year = year -1
            month = 12
        else:
            month = month -1

        master = PayrollMaster.objects.filter(month__lte=month,year__lte=year,confirmed=True).last()

        emp_payroll = None
        try:
            emp_payroll = master.payrolldetail_set.get(employee=self.instance.employee)
        except:
            pass

        if master and emp_payroll:
            payroll_confirmed = Payroll(master.year,master.month)
            mokaf2_sheet = Mokaf2Sheet(year,month)

            employee,badal,khosomat = payroll_confirmed.employee_payroll_calculated(self.instance.employee)
            mokaf2 = mokaf2_sheet.employee_mokaf2_from_db(emp_payroll)

            # if amount > badal.ajmali_almoratab:
            #     msg = _("Total of deduction more than last employee payroll:")
            #     raise ValidationError(f'{msg} {badal.ajmali_almoratab}')
            
            salafiat_qs = employee.employeesalafiat_set.filter(month=old_month,year=old_year).exclude(pk=self.instance.pk)
            pre_total_all_salafiat = (salafiat_qs.aggregate(total=Sum('amount'))['total'] or 0)
            total_all_salafiat = amount + pre_total_all_salafiat

            # print("****",old_month,old_year,employee,salafiat_qs,pre_total_all_salafiat,total_all_salafiat)
            
            if no3_2lsalafia == EmployeeSalafiat.NO3_2LSALAFIA_3LA_2LMORATAB:
                salafiat_3la_2lmoratab_qs = salafiat_qs.filter(no3_2lsalafia=EmployeeSalafiat.NO3_2LSALAFIA_3LA_2LMORATAB)
                pre_total_3la_2lmoratab_salafiat = (salafiat_3la_2lmoratab_qs.aggregate(total=Sum('amount'))['total'] or 0)
                total_3la_2lmoratab_salafiat = amount + pre_total_3la_2lmoratab_salafiat

                if total_3la_2lmoratab_salafiat > (badal.ajmali_almoratab):
                    msg = _("salafia 3la 2lmoratab more than last employee payroll:")
                    raise ValidationError(f'{msg} {round(badal.ajmali_almoratab,2)}')

            if no3_2lsalafia == EmployeeSalafiat.NO3_2LSALAFIA_3LA_2LMOKAF2:
                salafiat_3la_mokaf2_qs = salafiat_qs.filter(no3_2lsalafia=EmployeeSalafiat.NO3_2LSALAFIA_3LA_2LMOKAF2)
                pre_total_3la_mokaf2_salafiat = (salafiat_3la_mokaf2_qs.aggregate(total=Sum('amount'))['total'] or 0)
                total_3la_mokaf2_salafiat = amount + pre_total_3la_mokaf2_salafiat

                if total_3la_mokaf2_salafiat > (mokaf2.safi_2l2sti7gag_gabl_alsalafiat):
                    msg = _("salafia 3la mokaf2 more than last employee payroll:")
                    raise ValidationError(f'{msg} {round(mokaf2.safi_2l2sti7gag_gabl_alsalafiat,2)}')

            if total_all_salafiat > (badal.ajmali_almoratab + mokaf2.safi_2l2sti7gag_gabl_alsalafiat):
                msg = _("Total of deduction more than last employee payroll:")
                raise ValidationError(f'{msg} {round((badal.ajmali_almoratab+ mokaf2.safi_2l2sti7gag_gabl_alsalafiat),2)}')

        return amount

admin.site.title = _("Site header")
admin.site.site_title = _("Site header")
admin.site.site_header = _("Site header")
admin.site.site_url = None

class MosamaWazifiAdmin(admin.ModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["name","category"]        
    list_filter = ["category"]
    view_on_site = False
    search_fields = ["name"]

admin.site.register(MosamaWazifi,MosamaWazifiAdmin)

# class Edara3amaAdmin(admin.ModelAdmin):
#     exclude = ["created_at","created_by","updated_at","updated_by"]
#     list_display = ["name","tab3ia_edaria"]        
#     list_filter = ["tab3ia_edaria"] 
#     view_on_site = False
#     search_fields = ["name"]

# admin.site.register(Edara3ama,Edara3amaAdmin)

# class Edarafar3iaAdmin(admin.ModelAdmin):
#     exclude = ["created_at","created_by","updated_at","updated_by"]
    
#     list_display = ["edara_3ama","name","hikal_wazifi"]        
#     list_editable = ( 'hikal_wazifi', )
#     ordering = ["edara_3ama","name"]
#     view_on_site = False
#     search_fields = ["name"]

# admin.site.register(Edarafar3ia,Edarafar3iaAdmin)

# class GisimAdmin(admin.ModelAdmin):
#     exclude = ["created_at","created_by","updated_at","updated_by"]
    
#     list_display = ["name","edara_far3ia"]        
#     view_on_site = False
#     search_fields = ["name"]
#     list_filter = ["edara_far3ia"]
#     autocomplete_fields = ["edara_far3ia"]

# admin.site.register(Gisim,GisimAdmin)

# class Wi7daAdmin(admin.ModelAdmin):
#     exclude = ["created_at","created_by","updated_at","updated_by"]
    
#     list_display = ["name","gisim"]        
#     view_on_site = False
#     search_fields = ["name"]
#     list_filter = ["gisim"]
#     autocomplete_fields = ["gisim"]

# admin.site.register(Wi7da,Wi7daAdmin)

class HikalWazifiAdmin(MPTTModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by"]
    
    list_display = ["name","elmostoa_eltanzimi"]        
    view_on_site = False
    search_fields = ["name"]
    mptt_level_indent = 20

admin.site.register(HikalWazifi,HikalWazifiAdmin)

class Edara3amaFilter(admin.SimpleListFilter):
    title = _("Edara 3ama")    
    parameter_name = "edara3ama"
    def lookups(self, request, model_admin):
        org_qs = model_admin.get_queryset(request)
        qs = HikalWazifi.objects.filter(
            elmostoa_eltanzimi=HikalWazifi.ELMOSTOA_ELTANZIMI_2DARA_3AMA,
            id__in=org_qs.order_by("hikal_wazifi").distinct("hikal_wazifi").values_list("hikal_wazifi")
            )\
            .order_by('name')\
            .distinct("name")\
            .values_list("id","name")
        return [(x[0],x[1]) for x in qs]
    
    def queryset(self, request, queryset):
        val = self.value()
        try:
            hikal = HikalWazifi.objects.get(id=int(val))
            if val:
                return queryset.filter(hikal_wazifi__in=hikal.get_descendants(include_self=True))            
        except:
            pass
        
        return queryset

class Edarafar3iaFilter(admin.SimpleListFilter):
    title = _("Edara far3ia")    
    parameter_name = "edarafar3ia"
    def lookups(self, request, model_admin):
        org_qs = model_admin.get_queryset(request)
        qs = HikalWazifi.objects.filter(
            elmostoa_eltanzimi=HikalWazifi.ELMOSTOA_ELTANZIMI_2DARA_FAR3IA,
            id__in=org_qs.order_by("hikal_wazifi").distinct("hikal_wazifi").values_list("hikal_wazifi")
            )\
            .order_by('name')\
            .distinct("name")\
            .values_list("id","name")

        return [(x[0],x[1]) for x in qs]
    
    def queryset(self, request, queryset):
        val = self.value()
        try:
            hikal = HikalWazifi.objects.get(id=int(val))
            if val:
                return queryset.filter(hikal_wazifi__in=hikal.get_descendants(include_self=True))            
        except:
            pass
        
        return queryset

class EmployeeWi7daMosa3daFilter(admin.SimpleListFilter):
    title = _("tajmi3 no3 2lrtibt")    
    parameter_name = "tajmi3_no3_2lrtibt"
    def lookups(self, request, model_admin):
        return [
            ('1',_('wi7dat_mosa3da')),
            ('2',_('ta3agod_kha9')),
            ('3',_('ta3agod_mosimi')),
            ('4',_('mashro3')),
            ('5',_('majlis el2dara')),
            ('6',_('others')),
        ]
    
    def queryset(self, request, queryset):
        val = self.value()
        if val == '1':
            return queryset.filter(no3_2lertibat=EmployeeBasic.NO3_2LERTIBAT_2L7ag)
        if val == '2': 
            return queryset.filter(no3_2lertibat=EmployeeBasic.NO3_2LERTIBAT_TA3AGOD)
        if val == '3': 
            return queryset.filter(no3_2lertibat=EmployeeBasic.NO3_2LERTIBAT_TA3AGOD_MOSIMI)
        if val == '4': 
            return queryset.filter(no3_2lertibat=EmployeeBasic.NO3_2LERTIBAT_MASHRO3)
        if val == '5': 
            return queryset.filter(no3_2lertibat=EmployeeBasic.NO3_2LERTIBAT_MAJLIS_EL2DARA)
        if val == '6': 
            return queryset.exclude(no3_2lertibat__in=[EmployeeBasic.NO3_2LERTIBAT_2L7ag, EmployeeBasic.NO3_2LERTIBAT_TA3AGOD, EmployeeBasic.NO3_2LERTIBAT_TA3AGOD_MOSIMI,EmployeeBasic.NO3_2LERTIBAT_MASHRO3,EmployeeBasic.NO3_2LERTIBAT_MAJLIS_EL2DARA])
        
        return queryset

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

class EmployeeTelegramInline(admin.TabularInline):
    model = EmployeeTelegram
    exclude = ["created_at","created_by","updated_at","updated_by"]
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    extra = 1    

class EmployeeTelegramRegistrationInline(admin.TabularInline):
    model = EmployeeTelegramRegistration
    exclude = ["created_at","created_by","updated_at","updated_by"]
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    extra = 1    

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

class SalafiatForm(SalafiatMixin,ModelForm):
    class Meta:
        model = EmployeeSalafiat
        fields = ['employee','year','month','no3_2lsalafia','note','amount']
 
class SalafiatInline(admin.TabularInline):
    model = EmployeeSalafiat
    form = SalafiatForm
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
        models.IntegerField: {"widget": TextInput},
    }    
    extra = 1    

class JazaatInline(admin.TabularInline):
    model = EmployeeJazaat
    exclude = ["created_at","created_by","updated_at","updated_by"]
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
        models.IntegerField: {"widget": TextInput},
    }    

    extra = 1    

class EmployeeMobashraInline(admin.TabularInline):
    model = EmployeeMobashra
    exclude = ["created_at","created_by","updated_at","updated_by"]
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
        models.IntegerField: {"widget": TextInput},
    }    
    extra = 1    

class EmployeeVacationInline(admin.TabularInline):
    model = EmployeeVacation
    fk_name = "employee"
    exclude = ["created_at","created_by","updated_at","updated_by"]
    autocomplete_fields = ["mokalaf",]
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
        models.IntegerField: {"widget": TextInput},
    }    
    extra = 1    

class EmployeeM2moriaInline(admin.TabularInline):
    model = EmployeeM2moria
    exclude = ["created_at","created_by","updated_at","updated_by"]
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
        models.IntegerField: {"widget": TextInput},
    }    
    extra = 1    

class EmployeeWi7datMosa3daInline(admin.TabularInline):
    model = EmployeeWi7datMosa3da
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1

class EmployeeMajlisEl2daraInline(admin.TabularInline):
    model = EmployeeMajlisEl2dara
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1

class EmployeeBasicAdmin(admin.ModelAdmin):
    fields = ["code","name", "draja_wazifia","alawa_sanawia","hikal_wazifi", "edara_3ama_tmp","edara_far3ia_tmp", "mosama_wazifi","sex","tarikh_milad","tarikh_ta3in","tarikh_akhir_targia","phone","no3_2lertibat","sanoat_2lkhibra","moahil","gasima","atfal","aadoa","m3ash","status"]        
    inlines = [EmployeeTelegramInline,EmployeeTelegramRegistrationInline,EmployeeFamilyInline,EmployeeMoahilInline,EmployeeBankAccountInline,SalafiatInline,JazaatInline,EmployeeMobashraInline,EmployeeVacationInline,EmployeeM2moriaInline]
    list_display = ["code","name", "draja_wazifia","alawa_sanawia", "edara_3ama","edara_far3ia","gisim", "mosama_wazifi","tarikh_ta3in","tarikh_akhir_targia","sex","moahil","gasima","atfal","aadoa","m3ash","status"]    
    list_display_links = ["code","name"]
    list_filter = ["draja_wazifia","alawa_sanawia",Edara3amaFilter,Edarafar3iaFilter,EmployeeWi7daMosa3daFilter,"no3_2lertibat","mosama_wazifi__category","gasima","atfal",EmployeeTarikhTa3inFilter,EmployeeWifg2lwazaifFilter,EmployeeWifg2lmostawiatFilter,"sex","moahil","aadoa","status"] #
    view_on_site = False
    autocomplete_fields = ["mosama_wazifi"] #,"hikal_wazifi"
    search_fields = ["name","code"]
    readonly_fields = ["moahil","gasima","atfal","edara_3ama_tmp","edara_far3ia_tmp"]
    actions = ['export_as_csv']

    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    def get_readonly_fields(self,request,obj):
        if request.user.groups.filter(name="hr_payroll").exists():
            return self.fields
        
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_inlines(self, request, obj):
        inlines = self.inlines
        if obj and obj.no3_2lertibat==EmployeeBasic.NO3_2LERTIBAT_2L7ag:
            return [EmployeeWi7datMosa3daInline] + inlines
        if obj and obj.no3_2lertibat==EmployeeBasic.NO3_2LERTIBAT_MAJLIS_EL2DARA:
            return [EmployeeMajlisEl2daraInline] + inlines

        return inlines
        
    @admin.action(description=_('Export data'))
    def export_as_csv(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="employees.csv"'},
        )
        header = [
                    _("code"),_("name"),_("draja_wazifia"),_("alawa_sanawia"),_( "edara_3ama"),\
                    _("edara_far3ia"),_("gisim"),_("wi7da"),_("mosama_wazifi"),_("tarikh_milad"),_("tarikh_ta3in"),_("tarikh_akhir_targia"),_("sex"),_("gasima"),_("atfal"),\
                    _("moahil"),_("m3ash"),_("aadoa"),_("no3_2lertibat"),_("phone"),_("sanoat_2lkhibra"),_("bank"),_("account_no"),_("status")
        ]

        # BOM
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        writer.writerow(header)

        for emp in queryset.order_by("draja_wazifia","alawa_sanawia"):
            gasima = _('no')
            if emp.gasima:
                gasima = _('yes')

            aadoa = _('no')
            if emp.aadoa:
                aadoa = _('yes')

            account = emp.employeebankaccount_set.filter(active=True).first()
            bank_name = ''
            account_no = ''
            if account:
                bank_name = account.get_bank_display()
                account_no = account.account_no

            row = [
                    emp.code,emp.name,emp.get_draja_wazifia_display(),emp.get_alawa_sanawia_display(),\
                    emp.edara_3ama,emp.edara_far3ia,emp.gisim,emp.wi7da,emp.mosama_wazifi.name,emp.tarikh_milad,emp.tarikh_ta3in,emp.tarikh_akhir_targia,\
                    emp.get_sex_display(),gasima,emp.atfal,emp.get_moahil_display(),emp.m3ash,aadoa,emp.get_no3_2lertibat_display(),\
                    emp.phone,emp.sanoat_2lkhibra,bank_name,account_no,emp.get_status_display()
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

class SalafiatSandogForm(SalafiatMixin,ModelForm):
    class Meta:
        model = EmployeeSalafiat
        fields = ['employee','year','month','note','amount']

class SalafiatAdmin(admin.ModelAdmin):
    form = SalafiatSandogForm
    
    list_display = ["code","employee", "year","month","note","amount","deducted"] 
    list_filter = ["year","month"]
    view_on_site = False
    search_fields = ["employee__code","employee__name"]
    ordering =  ["employee__code"]
    autocomplete_fields = ["employee"]
    actions = ['export_as_csv']

    @admin.display(description=_("code"))
    def code(self, obj):
        return obj.employee.code
    @admin.action(description=_('Export data'))
    def export_as_csv(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="employees.csv"'},
        )
        header = [
                    _("code"),_("name"),_("year"),_("month"),_( "note"),_( "amount")
        ]

        # BOM
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        writer.writerow(header)

        for salafia in queryset.order_by("employee__code"):
            row = [
                    salafia.employee.code,salafia.employee.name,salafia.year,salafia.get_month_display(),\
                    salafia.note,salafia.amount
            ]
            writer.writerow(row)

        return response


    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # if request.user.is_superuser:
        #     return qs
        return qs.filter(no3_2lsalafia=EmployeeSalafiat.NO3_2LSALAFIA_SANDOG)
    
admin.site.register(EmployeeSalafiat,SalafiatAdmin)

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
    #exclude = ["created_at","created_by","updated_at","updated_by"]
    fields = ['employee','draja_wazifia','alawa_sanawia','bank','account_no','abtdai','galaa_m3isha','shakhsia','aadoa','gasima','atfal','moahil','ma3adin','m3ash','salafiat','jazaat','damga','sandog','sandog_kahraba','salafiat_sandog','salafiat_3la_2lmoratab','salafiat_3la_2lmokaf2','tarikh_milad']
    extra = 0
    readonly_fields = fields #['employee','abtdai','galaa_m3isha','shakhsia','aadoa','gasima','atfal','moahil','ma3adin','m3ash','salafiat','jazaat','damga','sandog','sandog_kahraba','salafiat_sandog','tarikh_milad','draja_wazifia','alawa_sanawia']
    can_delete = False
    list_select_related = True
    def has_add_permission(self,request, obj):
        return False
    
class PayrollDetailWi7datMosa3idaInline(admin.TabularInline):
    model = PayrollDetailWi7datMosa3ida
    #exclude = ["created_at","created_by","updated_at","updated_by"]
    fields = ['employee','draja_wazifia','alawa_sanawia','bank','account_no','abtdai','galaa_m3isha','ma3adin','payroll_2ljiha_2l2om','payroll_2lsharika','has_diff','salafiat','jazaat','damga','sandog','sandog_kahraba','salafiat_sandog','salafiat_3la_2lmoratab','salafiat_3la_2lmokaf2','tarikh_milad']
    extra = 0
    readonly_fields = fields
    can_delete = False
    list_select_related = True
    def has_add_permission(self,request, obj):
        return False
    
class PayrollDetailTa3agodMosimiInline(admin.TabularInline):
    model = PayrollDetailTa3agodMosimi
    #exclude = ["created_at","created_by","updated_at","updated_by"]
    fields = ['employee','draja_wazifia','alawa_sanawia','bank','account_no','payroll_ajmali','payroll_mokaf2','salafiat','jazaat','damga','sandog','sandog_kahraba','salafiat_sandog','salafiat_3la_2lmoratab','salafiat_3la_2lmokaf2','tarikh_milad']
    extra = 0
    readonly_fields = fields
    can_delete = False
    list_select_related = True
    def has_add_permission(self,request, obj):
        return False

class PayrollDetailMajlisEl2daraInline(admin.TabularInline):
    model = PayrollDetailMajlisEl2dara
    #exclude = ["created_at","created_by","updated_at","updated_by"]
    fields = ['employee','draja_wazifia','alawa_sanawia','bank','account_no','payroll_mokaf2','payroll_asasi','gasima','atfal','moahil','salafiat','jazaat','damga','sandog','sandog_kahraba','salafiat_sandog','salafiat_3la_2lmoratab','salafiat_3la_2lmokaf2','tarikh_milad']
    extra = 0
    readonly_fields = fields
    can_delete = False
    list_select_related = True
    def has_add_permission(self,request, obj):
        return False

class EmployeeM2moriaMonthlyInline(admin.TabularInline):
    model = EmployeeM2moriaMonthly
    #exclude = ["created_at","created_by","updated_at","updated_by"]
    fields = ['employee','ajmali_2lmoratab','no_days','damga','safi_2l2sti7gag']
    extra = 0
    readonly_fields = fields #['employee','abtdai','galaa_m3isha','shakhsia','aadoa','gasima','atfal','moahil','ma3adin','m3ash','salafiat','jazaat','damga','sandog','sandog_kahraba','salafiat_sandog','tarikh_milad','draja_wazifia','alawa_sanawia']
    can_delete = False
    list_select_related = True
    def has_add_permission(self,request, obj):
        return False
    
class PayrollTasoiaInline(admin.TabularInline):
    model = PayrollTasoia


class PayrollMasterAdmin(admin.ModelAdmin):
    exclude = ["created_at","created_by","updated_at","updated_by","zaka_kafaf","zaka_nisab","confirmed","enable_sandog_kahraba","enable_youm_algoat_almosalaha","daribat_2lmokafa","m3ash_age","khasm_salafiat_elsandog_min_elomoratab"]
    inlines = [PayrollDetailInline,PayrollDetailWi7datMosa3idaInline,PayrollDetailTa3agodMosimiInline,PayrollDetailMajlisEl2daraInline,EmployeeM2moriaMonthlyInline,PayrollTasoiaInline]

    # list_display = ["year","month","confirmed","show_badalat_link","show_khosomat_link","show_mokaf2_link","show_mobashara_link"]
    list_filter = ["year","month","confirmed"]
    view_on_site = False
    list_select_related = True
    save_on_top = True

    actions = ["confirm_payroll"]

    # readonly_fields = ["year","month","confirmed"]

    def get_list_display(self,request):
        links = ["year","month","confirmed","show_badalat_link","cmp_badalat_prev_month_link","show_khosomat_link","cmp_khosomat_prev_month_link","show_mokaf2_link","show_wi7dat_mosa3ida_farig_moratab_link","show_wi7dat_mosa3ida_mokaf2_link","show_ta3agod_mosimi_moratab_link","show_ta3agod_mosimi_mokaf2_link","show_majlis_el2dara_link","show_modir_3am_badalat_link","show_modir_3am_khosomat_link","show_modir_3am_mokaf2_link"]
        if request.user.groups.filter(name="hr_manager").exists():
            return links + ["show_mobashara_link","show_m2moria_link"]
        else:
            return links

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
        url_tasoia = reverse('hr:payroll_tasoia')
        check_payroll_url = reverse('hr:payroll_check')
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}">'+_('Show khosomat sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url_tasoia}?year={year}&month={month}">'+_('tasoia sheet')+'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv&bank_sheet=1">'+_('bank sheet')+'</a> / '\
                               +'<a target="_blank" href="{check_payroll_url}?year={year}&month={month}">'+_('check payroll')+'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,url_tasoia=url_tasoia,check_payroll_url=check_payroll_url,year=obj.year,month=obj.month)

    @admin.display(description=_('Diff badalat sheet'))
    def cmp_badalat_prev_month_link(self, obj):
        url = reverse('hr:payroll_diff_badalat')
        prev_year = obj.year
        prev_month = int(obj.month) -1
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}&cmp_year={cmp_year}&cmp_month={cmp_month}">'+_('Diff badalat sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&cmp_year={cmp_year}&cmp_month={cmp_month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month,cmp_year=prev_year,cmp_month=prev_month)

    @admin.display(description=_('Diff khosomat sheet'))
    def cmp_khosomat_prev_month_link(self, obj):
        url = reverse('hr:payroll_diff_khosomat')
        prev_year = obj.year
        prev_month = int(obj.month) -1
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}&cmp_year={cmp_year}&cmp_month={cmp_month}">'+_('Diff khosomat sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&cmp_year={cmp_year}&cmp_month={cmp_month}&bank_sheet=1">'+_('diff bank sheet')+'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&cmp_year={cmp_year}&cmp_month={cmp_month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month,cmp_year=prev_year,cmp_month=prev_month)

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

    @admin.display(description=_('Show wi7dat mosa3ida farig moratab sheet'))
    def show_wi7dat_mosa3ida_farig_moratab_link(self, obj):
        url = reverse('hr:payroll_wi7dat_mosa3ida_farg_moratab')
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}">'+_('Show wi7dat mosa3ida farig moratab sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv&bank_sheet=1">'+_('bank sheet')+'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month)

    @admin.display(description=_('Show wi7dat mosa3ida mokaf2 sheet'))
    def show_wi7dat_mosa3ida_mokaf2_link(self, obj):
        url = reverse('hr:payroll_wi7dat_mosa3ida_mokaf2')
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}">'+_('Show wi7dat mosa3ida mokaf2 sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv&bank_sheet=1">'+_('bank sheet')+'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month)


    @admin.display(description=_('Show ta3agod mosimi moratab sheet'))
    def show_ta3agod_mosimi_moratab_link(self, obj):
        url = reverse('hr:payroll_ta3agod_mosimi_moratab')
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}">'+_('Show ta3agod mosimi moratab sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv&bank_sheet=1">'+_('bank sheet')+'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month)

    @admin.display(description=_('Show ta3agod mosimi mokaf2 sheet'))
    def show_ta3agod_mosimi_mokaf2_link(self, obj):
        url = reverse('hr:payroll_ta3agod_mosimi_mokaf2')
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}">'+_('Show ta3agod mosimi mokaf2 sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv&bank_sheet=1">'+_('bank sheet')+'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month)

    @admin.display(description=_('Show majlis el2dara sheet'))
    def show_majlis_el2dara_link(self, obj):
        url = reverse('hr:payroll_majlis_el2dara_mokaf2')
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}">'+_('Show majlis el2dara sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv&bank_sheet=1">'+_('bank sheet')+'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month)

    @admin.display(description=_('Show modir 3am badalat sheet'))
    def show_modir_3am_badalat_link(self, obj):
        url = reverse('hr:payroll_modir_3am_badalat')
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}">'+_('Show modir 3am badalat sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month)

    @admin.display(description=_('Show modir 3am khosomat sheet'))
    def show_modir_3am_khosomat_link(self, obj):
        url = reverse('hr:payroll_modir_3am_khosomat')
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}">'+_('Show modir 3am khosomat sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv&bank_sheet=1">'+_('bank sheet')+'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month)

    @admin.display(description=_('Show modir 3am mokaf2 sheet'))
    def show_modir_3am_mokaf2_link(self, obj):
        url = reverse('hr:payroll_modir_3am_mokaf2')
        return format_html('<a target="_blank" class="viewlink" href="{url}?year={year}&month={month}">'+_('Show modir 3am mokaf2 sheet')\
                               +'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv&bank_sheet=1">'+_('bank sheet')+'</a> / '\
                               +'<a target="_blank" href="{url}?year={year}&month={month}&format=csv">CSV</a>',
                           url=url,year=obj.year,month=obj.month)

    def save_model(self, request, obj, form, change):
        payroll = Payroll(obj.year,obj.month)
        payroll.calculate()

        tasoia = TasoiaPayroll(obj.year,obj.month)
        tasoia.calculate()

        mobashara = MobasharaSheet(obj.year,obj.month)
        mobashara.calculate()

        m2moria = M2moriaSheet(obj.year,obj.month)
        m2moria.calculate()

        wi7dat_mosa3da = Wi7datMosa3idaMokaf2tFarigMoratabPayroll(obj.year,obj.month)
        wi7dat_mosa3da.calculate()

        ta3agod_mosimi = Ta3agodMosimiPayroll(obj.year,obj.month)
        ta3agod_mosimi.calculate()

        majlis_el2dara = MajlisEl2daraMokaf2Payroll(obj.year,obj.month)
        majlis_el2dara.calculate()

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.confirmed:
            return False
        
        return True
    
    @admin.action(description=_('Confirm payroll'))
    def confirm_payroll(self, request, queryset):
        # queryset.update(confirmed=True)

        for q in queryset:
            payroll = Payroll(q.year,q.month)

            payroll_validation = PayrollValidation(payroll,Drajat3lawat)

            if payroll_validation.is_all_khosomat_valid():
                payroll.confirm()

                mobashara = MobasharaSheet(q.year,q.month)
                mobashara.confirm()

            else:
                self.message_user(request, f'الرجاء التأكد من صحة بيانات {q.get_month_display()} {q.year} اولاً.',messages.ERROR)

            # EmployeeSalafiat.objects.filter(year=q.year,month=q.month).update(deducted=True)

            # EmployeeJazaat.objects.filter(year=q.year,month=q.month).update(deducted=True)

admin.site.register(PayrollMaster,PayrollMasterAdmin)

