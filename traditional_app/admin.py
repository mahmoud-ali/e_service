from django.utils.translation import gettext_lazy as _
from django.urls import reverse, resolve
from django.contrib import admin
from django.utils.html import format_html
# from django.contrib.gis import admin as gis_admin
from leaflet.admin import LeafletGeoAdmin
from company_profile.models import LkpLocality, LkpState
from traditional_app.hr_payroll import T3agoodPayroll
from traditional_app.models import DailyGrabeel, DailyHofrKabira, DailyIncome, DailyReport, DailyGoldMor7ala, DailyKartaMor7ala, DailySmallProcessingUnit, Employee, EmployeeJobData, Lkp2bar, Lkp2jhizatBahth, Lkp7ofrKabira, LkpGrabeel, LkpKhalatat, LkpMojam3atTawa7in, LkpSaig, LkpSmallProcessingUnit, LkpSoag, LkpSosalGold, DailyTahsilForm, DailyWardHajr, PayrollDetail, PayrollMaster, RentedApartment, RentedVehicle, TraditionalAppUser, Vehicle #, LkpLocalityTmp
from workflow.admin_utils import create_main_form
from traditional_app.models import AcademicQualification

class LogMixin:
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        for form in formset.forms:
            if form.cleaned_data.get('DELETE', False):
                if form.instance.pk:
                    form.instance.delete()

        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:  # New inline object
                instance.created_by = request.user
            instance.updated_by = request.user
            instance.save()
        formset.save_m2m()

class StateControlMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser or request.user.groups.filter(name='traditional_hr').exists():
            return qs

        obj = qs.first()

        try:
            state = request.user.traditional_app_user.state

            if hasattr(obj,'source_state'):
                qs = qs.filter(source_state=state)
            elif hasattr(obj,'state'):
                qs = qs.filter(state=state)

            return qs
        except:
            return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "state" or db_field.name == "source_state":
            if request.user.is_superuser or request.user.groups.filter(name='traditional_hr').exists():
                return super().formfield_for_foreignkey(db_field, request, **kwargs)
            try:
                state = request.user.traditional_app_user.state
                kwargs["queryset"] = LkpState.objects.filter(id=state.id) #request.user
            except:
                kwargs["queryset"] = LkpState.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class SoagControlMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser or request.user.groups.filter(name='traditional_hr').exists():
            return qs

        obj = qs.first()

        try:
            state = request.user.traditional_app_user.state

            qs = qs.filter(soag__state=state)

            return qs
        except:
            return qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "soag":
            if request.user.is_superuser or request.user.groups.filter(name='traditional_hr').exists():
                return super().formfield_for_foreignkey(db_field, request, **kwargs)
            try:
                state = request.user.traditional_app_user.state
                kwargs["queryset"] = LkpSoag.objects.filter(state=state) #request.user
            except Exception as e:
                kwargs["queryset"] = LkpSoag.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
class RelatedOnlyFieldListFilterNotEmpty(admin.RelatedOnlyFieldListFilter):
    def choices(self, changelist):
        add_facets = changelist.add_facets
        facet_counts = self.get_facet_queryset(changelist)
        yield {
            "selected": self.lookup_val is None and not self.lookup_val_isnull,
            "query_string": changelist.get_query_string(
                remove=[self.lookup_kwarg, self.lookup_kwarg_isnull]
            ),
            "display": _("All"),
        }
        count = None
        for pk_val, val in self.lookup_choices:
            count = facet_counts[f"{pk_val}__c"]
            if count == 0:
                continue
            if add_facets:
                val = f"{val} ({count})"
            yield {
                "selected": self.lookup_val is not None
                and str(pk_val) in self.lookup_val,
                "query_string": changelist.get_query_string(
                    {self.lookup_kwarg: pk_val}, [self.lookup_kwarg_isnull]
                ),
                "display": val,
            }
        empty_title = self.empty_value_display
        if self.include_empty_choice:
            if add_facets:
                count = facet_counts["__c"]
                empty_title = f"{empty_title} ({count})"
            yield {
                "selected": bool(self.lookup_val_isnull),
                "query_string": changelist.get_query_string(
                    {self.lookup_kwarg_isnull: "True"}, [self.lookup_kwarg]
                ),
                "display": empty_title,
            }

####### Lookups ########
class TraditionalAppUserAdmin(LogMixin, admin.ModelAdmin):
    model = TraditionalAppUser
    list_display = ['name', 'state']
    search_fields = ('name',)
    list_filter = ('state',)

admin.site.register(TraditionalAppUser, TraditionalAppUserAdmin)

class LkpMojam3atTawa7inAdmin(LogMixin,SoagControlMixin, LeafletGeoAdmin):
    model = LkpMojam3atTawa7in
    list_display = ['soag_state','soag_locality','soag', 'owner_name','toa7in_jafa_count','toa7in_ratiba_count']
    list_filter = [('soag',RelatedOnlyFieldListFilterNotEmpty),]
    exclude = ["created_at","created_by","updated_at","updated_by"]

    @admin.display(description=_('الولاية'))
    def soag_state(self, obj):
        return f'{obj.soag.state}'

    @admin.display(description=_('المحلية'))
    def soag_locality(self, obj):
        return f'{obj.soag.locality}'

    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/get_current_location.js",)

admin.site.register(LkpMojam3atTawa7in, LkpMojam3atTawa7inAdmin)

class LkpSaigAdmin(LogMixin,SoagControlMixin, LeafletGeoAdmin):
    model = LkpSaig
    list_display = ['soag_state','soag_locality','soag', 'name']
    list_filter = [('soag',RelatedOnlyFieldListFilterNotEmpty),]
    exclude = ["created_at","created_by","updated_at","updated_by"]

    class Media:
        js = ("traditional_app/js/get_current_location.js",)

    @admin.display(description=_('الولاية'))
    def soag_state(self, obj):
        return f'{obj.soag.state}'

    @admin.display(description=_('المحلية'))
    def soag_locality(self, obj):
        return f'{obj.soag.locality}'

admin.site.register(LkpSaig, LkpSaigAdmin)

# class LkpMojam3atTawa7inInline(admin.TabularInline):
#     model = LkpMojam3atTawa7in
#     exclude = ["geom","created_at","created_by","updated_at","updated_by"]
#     min_num = 1

# class LkpSaigInline(admin.TabularInline):
#     model = LkpSaig
#     exclude = ["geom","created_at","created_by","updated_at","updated_by"]
#     min_num = 1

class SougAdmin(LogMixin,StateControlMixin, LeafletGeoAdmin):
    model = LkpSoag
    list_display = ['name', 'state','locality']
    search_fields = ('name',)
    list_filter = ('state','locality')

    # inlines = [LkpMojam3atTawa7inInline, LkpSaigInline,]

    settings_overrides = {
        # 'TILES': [
        #     ('OpenStreetMap', 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        #         'attribution': '&copy; OpenStreetMap contributors',
        #     }),
        # ],
        # 'MAP_TEMPLATE': 'leaflet/admin/map.html',  
        'PLUGINS': {
            'measure': {
                'css': ['https://cdn.jsdelivr.net/npm/leaflet-measure@3.3.0/dist/leaflet-measure.css'],
                'js': 'https://cdn.jsdelivr.net/npm/leaflet-measure@3.3.0/dist/leaflet-measure.min.js',
                'auto-include': True,
            },
        }        
    }

    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js",)

admin.site.register(LkpSoag, SougAdmin)

from traditional_app.models import (
    AcademicQualification,
    EmployeeJobData, EmployeeStatus, EmployeeBankAccount,
    EmployeeLeave, EmployeePenalty, EmployeeDocument,
)

class AcademicQualificationInline(admin.TabularInline):
    model = AcademicQualification
    extra = 1
    classes = ['tab-academic']

class EmployeeJobDataAdminInline(admin.TabularInline):
    model = EmployeeJobData
    min_num = 1
    classes = ['tab-jobdata']

class EmployeeStatusInline(admin.TabularInline):
    model = EmployeeStatus
    extra = 1
    classes = ['tab-status']

class EmployeeBankAccountInline(admin.TabularInline):
    model = EmployeeBankAccount
    extra = 1
    classes = ['tab-bank']

class EmployeeLeaveInline(admin.TabularInline):
    model = EmployeeLeave
    extra = 1
    fk_name = 'employee'
    classes = ['tab-leave']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "assigned_employee":
            resolved = resolve(request.path_info)
            if resolved.kwargs.get('object_id'):
                try:
                    employee = Employee.objects.get(pk=resolved.kwargs['object_id'])
                    kwargs["queryset"] = Employee.objects.filter(state=employee.state)
                except Employee.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class EmployeePenaltyInline(admin.TabularInline):
    model = EmployeePenalty
    extra = 1
    classes = ['tab-penalty']

class EmployeeDocumentInline(admin.TabularInline):
    model = EmployeeDocument
    extra = 1
    classes = ['tab-document']

class EmployeePayrollHistoryInline(admin.TabularInline):
    model = PayrollDetail
    extra = 0
    can_delete = False
    max_num = 0
    classes = ['tab-salary']
    readonly_fields = [
        'display_year', 'display_month', 'display_asasi', 'display_galaa', 
        'display_sakan', 'display_tar7il', 'display_tabi3at_3amal', 
        'display_laban', 'display_3laj', 'display_damga', 'display_total'
    ]
    fields = readonly_fields

    def display_year(self, obj): return obj.payroll_master.year
    display_year.short_description = _("السنة")
    
    def display_month(self, obj): return obj.payroll_master.get_month_display()
    display_month.short_description = _("الشهر")

    def display_asasi(self, obj): return obj.payroll_master.asasi
    display_asasi.short_description = _("الاساسي")

    def display_galaa(self, obj): return obj.payroll_master.galaa_m3isha
    display_galaa.short_description = _("غلاء معيشة")

    def display_sakan(self, obj): return obj.payroll_master.badel_sakan
    display_sakan.short_description = _("بدل سكن")

    def display_tar7il(self, obj): return obj.payroll_master.badel_tar7il
    display_tar7il.short_description = _("بدل ترحيل")

    def display_tabi3at_3amal(self, obj): return obj.payroll_master.tabi3at_3amal
    display_tabi3at_3amal.short_description = _("طبيعة عمل")

    def display_laban(self, obj): return obj.payroll_master.badel_laban
    display_laban.short_description = _("بدل لبن")

    def display_3laj(self, obj): return obj.payroll_master.badel_3laj
    display_3laj.short_description = _("بدل علاج")

    def display_damga(self, obj): return obj.payroll_master.damga
    display_damga.short_description = _("دمغة")

    def display_total(self, obj):
        m = obj.payroll_master
        return m.asasi + m.galaa_m3isha + m.badel_sakan + m.badel_tar7il + m.tabi3at_3amal + m.badel_laban + m.badel_3laj
    display_total.short_description = _("الإجمالي")

class EmployeeAdmin(LogMixin, StateControlMixin, admin.ModelAdmin):
    model = Employee
    list_display = ['employee_code', 'name', 'state', 'category']
    search_fields = ('employee_code', 'name',)
    list_filter = ('category','state')
    readonly_fields = ('employee_code',)
    fieldsets = (
        (_('البيانات الأساسية'), {
            'fields': (
                'employee_code', 'name', 'birth_date', 'gender', 'phone', 'email', 'category', 'state',
                'id_attachment', 'birth_certificate_attachment'
            )
        }),
    )
    inlines = []

    def get_readonly_fields(self, request, obj=None):
        readonly = super().get_readonly_fields(request, obj)
        if request.user.is_superuser or request.user.groups.filter(name='traditional_hr').exists():
            if 'employee_code' in readonly:
                readonly = list(readonly)
                readonly.remove('employee_code')
                return tuple(readonly)
        return readonly

    def get_inlines(self, request, obj):
        inlines = [
            EmployeeJobDataAdminInline,
            EmployeeStatusInline,
            EmployeeBankAccountInline,
            EmployeeLeaveInline,
            EmployeePenaltyInline,
            EmployeeDocumentInline,
        ]
        
        if not request.user.groups.filter(name='state_hr_traditional').exists():
            inlines.insert(1, EmployeePayrollHistoryInline)

        if request.user.is_superuser or request.user.groups.filter(name='traditional_hr').exists():
            inlines.append(AcademicQualificationInline)
        return tuple(inlines)

    class Media:
        js = ('admin/js/jquery.init.js', "traditional_app/js/lkp_state_change.js", "traditional_app/js/employee_tabs.js")
        css = {'all': ("traditional_app/css/employee_tabs.css",)}

admin.site.register(Employee, EmployeeAdmin)

class RentedVehicleAdminInline(admin.StackedInline):
    model = RentedVehicle

class VehicleAdmin(LogMixin,StateControlMixin, admin.ModelAdmin):
    model = Vehicle
    list_display = ['state','vehicle_type', 'plate_no','model']
    search_fields = ('plate_no',)
    list_filter = ('state','vehicle_type')
    inlines = [RentedVehicleAdminInline,]

    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js",)

admin.site.register(Vehicle, VehicleAdmin)

class RentedApartmentAdmin(LogMixin,StateControlMixin,admin.ModelAdmin):
    model = RentedApartment
    list_display = ['state', 'apartment_type','owner_name']
    search_fields = ('owner_name',)
    list_filter = ('state','apartment_type')

    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js","traditional_app/js/get_current_location.js",)

admin.site.register(RentedApartment, RentedApartmentAdmin)

class Lkp7ofrKabiraAdmin(LogMixin,StateControlMixin, admin.ModelAdmin):
    model = Lkp7ofrKabira

    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js","traditional_app/js/get_current_location.js")

admin.site.register(Lkp7ofrKabira, Lkp7ofrKabiraAdmin)

class Lkp2barAdmin(LogMixin,StateControlMixin, admin.ModelAdmin):
    model = Lkp2bar
    
    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js","traditional_app/js/get_current_location.js")

admin.site.register(Lkp2bar, Lkp2barAdmin)

class Lkp2jhizatBahthAdmin(LogMixin,StateControlMixin, admin.ModelAdmin):
    model = Lkp2jhizatBahth
    
    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js",)

admin.site.register(Lkp2jhizatBahth, Lkp2jhizatBahthAdmin)

class LkpSosalGoldAdmin(LogMixin,StateControlMixin, admin.ModelAdmin):
    model = LkpSosalGold
    
    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js","traditional_app/js/get_current_location.js")

admin.site.register(LkpSosalGold, LkpSosalGoldAdmin)

class LkpGrabeelAdmin(LogMixin,StateControlMixin, admin.ModelAdmin):
    model = LkpGrabeel
    
    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js","traditional_app/js/get_current_location.js")

admin.site.register(LkpGrabeel, LkpGrabeelAdmin)

class LkpKhalatatAdmin(LogMixin,StateControlMixin, admin.ModelAdmin):
    model = LkpKhalatat
    
    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js","traditional_app/js/get_current_location.js")

admin.site.register(LkpKhalatat, LkpKhalatatAdmin)

class LkpSmallProcessingUnitAdmin(LogMixin,StateControlMixin, admin.ModelAdmin):
    model = LkpSmallProcessingUnit
    
    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js","traditional_app/js/get_current_location.js")

admin.site.register(LkpSmallProcessingUnit, LkpSmallProcessingUnitAdmin)

####### Daily Report ##########

class DailyReportMixin:
    def get_formsets_with_inlines(self, request, obj=None):
        super().get_formsets_with_inlines(request, obj)

        bypass_state = request.user.is_superuser or request.user.groups.filter(name='traditional_hr').exists()
        try:
            state = None if bypass_state else request.user.traditional_app_user.state
        except:
            state = None

        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            if state:
                if inline.model == DailyWardHajr:
                    formset.form.base_fields['soag'].queryset = formset.form.base_fields['soag'].queryset.filter(state=state)
                elif inline.model == DailyIncome:
                    formset.form.base_fields['soag'].queryset = formset.form.base_fields['soag'].queryset.filter(state=state)
                elif inline.model == DailyTahsilForm:
                    formset.form.base_fields['soag'].queryset = formset.form.base_fields['soag'].queryset.filter(state=state)
                elif inline.model == DailyKartaMor7ala:
                    formset.form.base_fields['soag'].queryset = formset.form.base_fields['soag'].queryset.filter(state=state)
                elif inline.model == DailyGoldMor7ala:
                    formset.form.base_fields['soag'].queryset = formset.form.base_fields['soag'].queryset.filter(state=state)
                elif inline.model == DailyGrabeel:
                    formset.form.base_fields['grabeel'].queryset = formset.form.base_fields['grabeel'].queryset.filter(state=state)
                elif inline.model == DailyHofrKabira:
                    formset.form.base_fields['hofr_kabira'].queryset = formset.form.base_fields['hofr_kabira'].queryset.filter(state=state)
                elif inline.model == DailySmallProcessingUnit:
                    formset.form.base_fields['small_processing_unit'].queryset = formset.form.base_fields['small_processing_unit'].queryset.filter(state=state)
                
            yield formset,inline

daily_report_main_mixins = [LogMixin,StateControlMixin,DailyReportMixin]
daily_report_main_class = {
    'model': DailyReport,
    'mixins': [],
    'kwargs': {
        'list_display': ('date', 'source_state','state'),
        # 'search_fields': ('department','responsible'),
        'list_filter': ('date', 'source_state','state'),
        'exclude': ('state',),
        'save_as_continue': False,
    },
    'groups': {
        'tra_secruitry':{
            'permissions': {
                DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'tra_tahsil_department':{
            'permissions': {
                DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'tra_asoag_department':{
            'permissions': {
                DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },
        'tra_state_manager':{
            'permissions': {
                DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
            },
        },

    },
}
# inline_mixins = [LogMixin]

daily_report_inline_classes = {
    'DailyWardHajr': {
        'model': DailyWardHajr,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 1,
            'min_num': 0,
        },
        'groups': {
            'tra_secruitry':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_asoag_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_state_manager':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
        }
    },
    'DailyIncome': {
        'model': DailyIncome,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 1,
            'min_num': 0,
        },
        'groups': {
            'tra_secruitry':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_asoag_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_state_manager':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'DailyTahsilForm': {
        'model': DailyTahsilForm,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 1,
            'min_num': 0,
        },
        'groups': {
            'tra_secruitry':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_asoag_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_state_manager':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'DailyKartaMor7ala': {
        'model': DailyKartaMor7ala,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 1,
            'min_num': 0,
        },
        'groups': {
            'tra_secruitry':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_asoag_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_state_manager':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    # 'DailyGoldMor7ala': {
    #     'model': DailyGoldMor7ala,
    #     'mixins': [admin.TabularInline],
    #     'kwargs': {
    #         'extra': 1,
    #         'min_num': 0,
    #     },
    #     'groups': {
    #         'tra_secruitry':{
    #             'permissions': {
    #                 DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
    #                 DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #                 DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #                 DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #             },
    #         },
    #         'tra_tahsil_department':{
    #             'permissions': {
    #                 DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #                 DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #                 DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #                 DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #             },
    #         },
    #         'tra_asoag_department':{
    #             'permissions': {
    #                 DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #                 DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #                 DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #                 DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #             },
    #         },
    #         'tra_state_manager':{
    #             'permissions': {
    #                 DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #                 DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #                 DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #                 DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
    #             },
    #         },

    #     },
    # },
    'DailyGrabeel': {
        'model': DailyGrabeel,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 1,
            'min_num': 0,
        },
        'groups': {
            'tra_secruitry':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_asoag_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_state_manager':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'DailyHofrKabira': {
        'model': DailyHofrKabira,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 1,
            'min_num': 0,
        },
        'groups': {
            'tra_secruitry':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_asoag_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_state_manager':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },
    'DailySmallProcessingUnit': {
        'model': DailySmallProcessingUnit,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 1,
            'min_num': 0,
        },
        'groups': {
            'tra_secruitry':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_asoag_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },
            'tra_state_manager':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED1: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_CONFIRMED2: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                    DailyReport.STATE_APPROVED: {'add': 0, 'change': 0, 'delete': 0, 'view': 1},
                },
            },

        },
    },    
}

model_admin, inlines = create_main_form(daily_report_main_class,daily_report_inline_classes,daily_report_main_mixins)

admin.site.register(model_admin.model,model_admin)

# @admin.register(LkpLocalityTmp)
# class LkpLocalityTmpAdmin(LeafletGeoAdmin):
#     model = LkpLocalityTmp
#     exclude = ['geom']
#     list_display = ['name','city','state_gis'] #, 'state'
#     search_fields = ('name',)
#     # list_filter = ('state',)
#     readonly_fields = ('objectid','name','city','state_gis','shape_leng','shape_area')

#     class Media:
#         js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js",)

class PayrollDetailInline(admin.TabularInline):
    model = PayrollDetail
    #exclude = ["created_at","created_by","updated_at","updated_by"]
    fields = ['employee',]
    extra = 0
    readonly_fields = fields #['employee','abtdai','galaa_m3isha','shakhsia','aadoa','gasima','atfal','moahil','ma3adin','m3ash','salafiat','jazaat','damga','sandog','sandog_kahraba','salafiat_sandog','tarikh_milad','draja_wazifia','alawa_sanawia']
    can_delete = False
    list_select_related = True
    def has_add_permission(self,request, obj):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name='traditional_hr').exists():
            return qs
        try:
            state = request.user.traditional_app_user.state
            return qs.filter(employee__state=state)
        except:
            return qs.none()

class PayrollMasterAdmin(admin.ModelAdmin):
    model = PayrollMaster
    exclude = ["created_at","created_by","updated_at","updated_by","confirmed"]
    inlines = [PayrollDetailInline,]

    # list_display = ["year","month","confirmed","show_badalat_link","show_khosomat_link","show_mokaf2_link","show_mobashara_link"]
    list_filter = ["year","month","confirmed"]
    list_display = ["year","month","confirmed","show_payroll_link"] #
    readonly_fields = ["asasi","galaa_m3isha","badel_sakan","badel_tar7il","tabi3at_3amal","badel_laban","badel_3laj","damga",]
    view_on_site = False
    list_select_related = True
    save_on_top = True

    actions = ["confirm_payroll"]

    # readonly_fields = ["year","month","confirmed"]

    def get_queryset(self, request):
        # Save the current user to the instance (just for this request cycle)
        self._current_user = request.user
        return super().get_queryset(request)
    
    @admin.display(description=_('كشف المرتبات'))
    def show_payroll_link(self, obj):
        url = reverse('traditional_app:payroll_t3agood')

        qs = LkpState.objects.none()
        urls_list = []

        try:
            user = getattr(self, "_current_user", None)
            user_state = user.traditional_app_user.state
            qs = LkpState.objects.filter(id=user_state.id) #request.user
            for state in qs:
                urls_list.append(
                    f'<a target="_blank" class="viewlink" href="{url}?year={obj.year}&month={obj.month}&state={state.id}">'+'مرتب '+state.name+'</a> / '\
                        +f' <a target="_blank" href="{url}?year={obj.year}&month={obj.month}&state={state.id}&format=csv">'+'تصدير '+state.name+'</a>'
                )            
        except:
            pass

        return format_html(" ".join(urls_list))

    def save_model(self, request, obj, form, change):
        # if not obj.pk:  # New object
        #     obj.created_by = request.user
        # obj.updated_by = request.user
        # super().save_model(request, obj, form, change)

        payroll = T3agoodPayroll(obj.year,obj.month)
        payroll.calculate()

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.confirmed:
            return False
        
        return True
    
admin.site.register(PayrollMaster,PayrollMasterAdmin)