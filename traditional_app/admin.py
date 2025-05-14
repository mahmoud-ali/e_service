from django.contrib import admin
# from django.contrib.gis import admin as gis_admin
from leaflet.admin import LeafletGeoAdmin
from company_profile.models import LkpLocality, LkpState
from traditional_app.models import DailyGrabeel, DailyHofrKabira, DailyIncome, DailyReport, DailyGoldMor7ala, DailyKartaMor7ala, DailySmallProcessingUnit, Employee, EmployeeProject, Lkp2bar, Lkp2jhizatBahth, Lkp7ofrKabira, LkpGrabeel, LkpKhalatat, LkpLocalityTmp, LkpMojam3atTawa7in, LkpSaig, LkpSmallProcessingUnit, LkpSoag, LkpSosalGold, DailyTahsilForm, DailyWardHajr, RentedApartment, RentedVehicle, TraditionalAppUser, Vehicle
from workflow.admin_utils import create_main_form

class LogMixin:
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
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
            try:
                state = request.user.traditional_app_user.state
                kwargs["queryset"] = LkpState.objects.filter(id=state.id) #request.user
            except:
                kwargs["queryset"] = LkpState.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
####### Lookups ########
class TraditionalAppUserAdmin(LogMixin, admin.ModelAdmin):
    model = TraditionalAppUser
    list_display = ['name', 'state']
    search_fields = ('name',)
    list_filter = ('state',)

admin.site.register(TraditionalAppUser, TraditionalAppUserAdmin)

class LkpMojam3atTawa7inInline(admin.TabularInline):
    model = LkpMojam3atTawa7in
    exclude = ["geom","created_at","created_by","updated_at","updated_by"]
    min_num = 1

class LkpSaigInline(admin.TabularInline):
    model = LkpSaig
    exclude = ["geom","created_at","created_by","updated_at","updated_by"]
    min_num = 1

class SougAdmin(LogMixin,StateControlMixin, LeafletGeoAdmin):
    model = LkpSoag
    list_display = ['name', 'state','locality']
    search_fields = ('name',)
    list_filter = ('state','locality')

    inlines = [LkpMojam3atTawa7inInline, LkpSaigInline,]

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

class EmployeeProjectAdminInline(admin.StackedInline):
    model = EmployeeProject

class EmployeeAdmin(LogMixin,StateControlMixin, admin.ModelAdmin):
    model = Employee
    list_display = ['state','no3_elta3god', 'name','job']
    search_fields = ('name',)
    list_filter = ('state','no3_elta3god')
    inlines = [EmployeeProjectAdminInline, ]

    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js",)

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

class RentedApartmentAdmin(LogMixin,StateControlMixin, LeafletGeoAdmin):
    model = RentedApartment
    list_display = ['state', 'apartment_type','owner_name']
    search_fields = ('owner_name',)
    list_filter = ('state','apartment_type')

    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js",)

admin.site.register(RentedApartment, RentedApartmentAdmin)

class Lkp7ofrKabiraAdmin(LogMixin,StateControlMixin, LeafletGeoAdmin):
    model = Lkp7ofrKabira

    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js",)

admin.site.register(Lkp7ofrKabira, Lkp7ofrKabiraAdmin)

class Lkp2barAdmin(LogMixin,StateControlMixin, LeafletGeoAdmin):
    model = Lkp2bar
    
    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js",)

admin.site.register(Lkp2bar, Lkp2barAdmin)

class Lkp2jhizatBahthAdmin(LogMixin,StateControlMixin, LeafletGeoAdmin):
    model = Lkp2jhizatBahth
    
    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js",)

admin.site.register(Lkp2jhizatBahth, Lkp2jhizatBahthAdmin)

class LkpSosalGoldAdmin(LogMixin,StateControlMixin, LeafletGeoAdmin):
    model = LkpSosalGold
    
    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js",)

admin.site.register(LkpSosalGold, LkpSosalGoldAdmin)

class LkpGrabeelAdmin(LogMixin,StateControlMixin, LeafletGeoAdmin):
    model = LkpGrabeel
    
    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js",)

admin.site.register(LkpGrabeel, LkpGrabeelAdmin)

class LkpKhalatatAdmin(LogMixin,StateControlMixin, LeafletGeoAdmin):
    model = LkpKhalatat
    
    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js",)

admin.site.register(LkpKhalatat, LkpKhalatatAdmin)

class LkpSmallProcessingUnitAdmin(LogMixin,StateControlMixin, LeafletGeoAdmin):
    model = LkpSmallProcessingUnit
    
    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js",)

admin.site.register(LkpSmallProcessingUnit, LkpSmallProcessingUnitAdmin)

####### Daily Report ##########

class DailyReportMixin:
    def get_formsets_with_inlines(self, request, obj=None):
        super().get_formsets_with_inlines(request, obj)

        state = request.user.traditional_app_user.state

        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
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
        'tra_tahsil_department':{
            'permissions': {
                DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
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
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
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
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
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
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
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
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
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
    'DailyGoldMor7ala': {
        'model': DailyGoldMor7ala,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 1,
            'min_num': 0,
        },
        'groups': {
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
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
    'DailyGrabeel': {
        'model': DailyGrabeel,
        'mixins': [admin.TabularInline],
        'kwargs': {
            'extra': 1,
            'min_num': 0,
        },
        'groups': {
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
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
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
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
            'tra_tahsil_department':{
                'permissions': {
                    DailyReport.STATE_DRAFT: {'add': 1, 'change': 1, 'delete': 1, 'view': 1},
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

@admin.register(LkpLocalityTmp)
class LkpLocalityTmpAdmin(LeafletGeoAdmin):
    model = LkpLocalityTmp
    exclude = ['geom']
    list_display = ['name','city','state_gis'] #, 'state'
    search_fields = ('name',)
    # list_filter = ('state',)
    readonly_fields = ('objectid','name','city','state_gis','shape_leng','shape_area')

    class Media:
        js = ('admin/js/jquery.init.js',"traditional_app/js/lkp_state_change.js",)
