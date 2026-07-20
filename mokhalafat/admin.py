from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from mokhalafat.forms import AppMokhalafatAdminForm, AppChemicalMaterialsViolationForm, ChemicalViolationStateRepresentativeForm
from mokhalafat.models import (
    AppMokhalafat, 
    AppMokhalafatProcedure, 
    AppMokhalafatRecommendation,
    AppChemicalMaterialsViolation,
    AppChemicalMaterialsViolationItem,
    AppChemicalMaterialsViolationWitness,
    AppChemicalMaterialsViolationAttachment,
    ChemicalViolationStateRepresentative,
)

class AppMokhalafatProcedureInline(admin.TabularInline):
    model = AppMokhalafatProcedure
    extra = 1    

class AppMokhalafatRecommendationInline(admin.TabularInline):
    model = AppMokhalafatRecommendation
    extra = 1    

class AppMokhalafatAdmin(admin.ModelAdmin):
    form = AppMokhalafatAdminForm
    inlines = [AppMokhalafatProcedureInline, AppMokhalafatRecommendationInline]
    fields = ["code", "date", "aism_almukhalafa", "wasf_almukhalafa", "tahlil_almukhalafa"]
    list_display = ["date", "code", "aism_almukhalafa", "tahlil_almukhalafa"]
    list_filter = ["date"]
    search_fields = ["code", "aism_almukhalafa", "wasf_almukhalafa", "tahlil_almukhalafa"]
    view_on_site = False

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(AppMokhalafat, AppMokhalafatAdmin)


GROUP_STATE   = 'mokhalafat_kimyaeya_state'    
GROUP_MANAGER = 'mokhalafat_kimyaeya_manager'  


class ChemicalViolationLogAdminMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        try:
            if request.user.groups.filter(name=GROUP_MANAGER).exists():
                return qs.filter(
                    record_state__in=(
                        AppChemicalMaterialsViolation.STATE_SMRC,
                        AppChemicalMaterialsViolation.STATE_APPROVED,
                        AppChemicalMaterialsViolation.STATE_CANCELED,
                    )
                )

            elif request.user.groups.filter(name=GROUP_STATE).exists():
                if hasattr(request.user, 'chemical_violation_representative'):
                    rep = request.user.chemical_violation_representative
                    return qs.filter(source_state=rep.state)

        except Exception as e:
            print(e)

        return qs.none()

    def save_model(self, request, obj, form, change):
        try:
            if hasattr(request.user, 'chemical_violation_representative'):
                rep = request.user.chemical_violation_representative
                if rep and rep.state:
                    obj.source_state = rep.state

            if obj.pk:
                obj.updated_by = request.user
            else:
                obj.created_by = obj.updated_by = request.user
            super().save_model(request, obj, form, change)
        except Exception as e:
            print(e)
            super().save_model(request, obj, form, change)

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name=GROUP_MANAGER).exists():
            return True
        if request.user.groups.filter(name=GROUP_STATE).exists():
            return True
        return False

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        is_manager = request.user.groups.filter(name=GROUP_MANAGER).exists()
        is_state = request.user.groups.filter(name=GROUP_STATE).exists()

        if is_manager:
            return False

        if is_state:
            return True

        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if request.user.groups.filter(name=GROUP_MANAGER).exists():
            if obj is None or obj.record_state in (
                AppChemicalMaterialsViolation.STATE_SMRC,
                AppChemicalMaterialsViolation.STATE_APPROVED,
            ):
                return True

        if request.user.groups.filter(name=GROUP_STATE).exists():
            return True

        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name=GROUP_STATE).exists():
            if obj is None or obj.record_state == AppChemicalMaterialsViolation.STATE_DRAFT:
                return True
        return False


class ChemicalViolationInlineReadonlyMixin:
    def has_add_permission(self, request, obj=None):
        is_manager = request.user.groups.filter(name=GROUP_MANAGER).exists() and not request.user.is_superuser
        is_state = request.user.groups.filter(name=GROUP_STATE).exists() and not request.user.is_superuser
        if is_manager or (is_state and obj and obj.record_state != AppChemicalMaterialsViolation.STATE_DRAFT):
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        is_manager = request.user.groups.filter(name=GROUP_MANAGER).exists() and not request.user.is_superuser
        is_state = request.user.groups.filter(name=GROUP_STATE).exists() and not request.user.is_superuser
        if is_manager or (is_state and obj and obj.record_state != AppChemicalMaterialsViolation.STATE_DRAFT):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        is_manager = request.user.groups.filter(name=GROUP_MANAGER).exists() and not request.user.is_superuser
        is_state = request.user.groups.filter(name=GROUP_STATE).exists() and not request.user.is_superuser
        if is_manager or (is_state and obj and obj.record_state != AppChemicalMaterialsViolation.STATE_DRAFT):
            return False
        return super().has_delete_permission(request, obj)


class AppChemicalMaterialsViolationItemInline(ChemicalViolationInlineReadonlyMixin, admin.TabularInline):
    model = AppChemicalMaterialsViolationItem
    extra = 1


class AppChemicalMaterialsViolationWitnessInline(ChemicalViolationInlineReadonlyMixin, admin.TabularInline):
    model = AppChemicalMaterialsViolationWitness
    extra = 1


class AppChemicalMaterialsViolationAttachmentInline(ChemicalViolationInlineReadonlyMixin, admin.TabularInline):
    model = AppChemicalMaterialsViolationAttachment
    extra = 1


class ChemicalViolationRecordStateFilter(admin.SimpleListFilter):
    title = _("حالة السجل")
    parameter_name = "record_state"

    def lookups(self, request, model_admin):
        is_manager = request.user.groups.filter(name=GROUP_MANAGER).exists() and not request.user.is_superuser
        if is_manager:
            return [
                (str(AppChemicalMaterialsViolation.STATE_SMRC), _('state_smrc')),
                (str(AppChemicalMaterialsViolation.STATE_APPROVED), _('state_approved')),
                (str(AppChemicalMaterialsViolation.STATE_CANCELED), _('state_canceled')),
            ]
        return [
            (str(AppChemicalMaterialsViolation.STATE_DRAFT), _('state_draft')),
            (str(AppChemicalMaterialsViolation.STATE_SMRC), _('state_smrc')),
            (str(AppChemicalMaterialsViolation.STATE_APPROVED), _('state_approved')),
            (str(AppChemicalMaterialsViolation.STATE_CANCELED), _('state_canceled')),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(record_state=self.value())
        return queryset


class AppChemicalMaterialsViolationAdmin(ChemicalViolationLogAdminMixin, admin.ModelAdmin):
    form = AppChemicalMaterialsViolationForm
    inlines = [
        AppChemicalMaterialsViolationItemInline,
        AppChemicalMaterialsViolationWitnessInline,
        AppChemicalMaterialsViolationAttachmentInline,
    ]
    list_display = ["date", "time", "source_state", "record_state", "officer_name", "incident_type"]
    list_filter = ["date", ChemicalViolationRecordStateFilter, "source_state", "incident_type", "public_health_risk"]
    search_fields = ["officer_name", "city_or_village", "neighborhood", "location_details", "owner_statements"]
    view_on_site = False
    actions = ['confirm_app', 'approve_app']
    change_form_template = 'admin/mokhalafat/appchemicalmaterialsviolation/change_form.html'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None and hasattr(request.user, 'chemical_violation_representative'):
            rep = request.user.chemical_violation_representative
            if rep and rep.state and 'source_state' in form.base_fields:
                form.base_fields['source_state'].initial = rep.state.pk
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        is_manager = request.user.groups.filter(name=GROUP_MANAGER).exists() and not request.user.is_superuser
        is_state = request.user.groups.filter(name=GROUP_STATE).exists() and not request.user.is_superuser

        if is_manager or (is_state and obj and obj.record_state != AppChemicalMaterialsViolation.STATE_DRAFT):
            fields_in_fieldsets = []
            for fs in self.fieldsets:
                for f in fs[1].get('fields', ()):
                    if isinstance(f, (list, tuple)):
                        fields_in_fieldsets.extend(f)
                    else:
                        fields_in_fieldsets.append(f)
            return list(set(fields_in_fieldsets))

        if is_state:
            for field in ('record_state', 'source_state'):
                if field not in readonly_fields:
                    readonly_fields.append(field)

        return readonly_fields

    def get_actions(self, request):
        actions = super().get_actions(request)

        if request.user.groups.filter(name=GROUP_MANAGER).count() > 0:
            if 'confirm_app' in actions:
                del actions['confirm_app']

        elif request.user.groups.filter(name=GROUP_STATE).count() > 0:
            if 'approve_app' in actions:
                del actions['approve_app']

        return actions

    @admin.action(description=_('تأكيد الطلب (إرسال للمدير)'))
    def confirm_app(self, request, queryset):
        try:
            change_flag = False
            for obj in queryset:
                if obj.record_state == AppChemicalMaterialsViolation.STATE_DRAFT:
                    obj.record_state = AppChemicalMaterialsViolation.STATE_SMRC
                    obj.updated_by = request.user
                    obj.save()
                    self.log_change(request, obj, _('state_smrc'))
                    change_flag = True
            if change_flag:
                self.message_user(request, _('تم تأكيد الطلب بنجاح!'))
        except Exception as e:
            print(e)

    @admin.action(description=_('إعتماد الطلب'))
    def approve_app(self, request, queryset):
        try:
            change_flag = False
            for obj in queryset:
                if obj.record_state == AppChemicalMaterialsViolation.STATE_SMRC:
                    obj.record_state = AppChemicalMaterialsViolation.STATE_APPROVED
                    obj.updated_by = request.user
                    obj.save()
                    self.log_change(request, obj, _('state_approved'))
                    change_flag = True
            if change_flag:
                self.message_user(request, _('تم اعتماد الطلب بنجاح!'))
        except Exception as e:
            print(e)

    def response_change(self, request, obj):
        redirect_url = reverse(
            'admin:mokhalafat_appchemicalmaterialsviolation_change',
            args=[obj.pk]
        )

        if '_confirm' in request.POST:
            is_state_or_manager = request.user.is_superuser or request.user.groups.filter(name__in=(GROUP_STATE, GROUP_MANAGER)).exists()
            if is_state_or_manager:
                if obj.record_state == AppChemicalMaterialsViolation.STATE_DRAFT:
                    obj.record_state = AppChemicalMaterialsViolation.STATE_SMRC
                    obj.updated_by = request.user
                    obj.save()
                    self.log_change(request, obj, _('state_smrc'))
                    self.message_user(request, _('تم تأكيد الطلب وإرساله للمدير بنجاح!'), messages.SUCCESS)
                else:
                    self.message_user(request, _('الطلب مؤكد أو معتمد بالفعل.'), messages.WARNING)
            return HttpResponseRedirect(redirect_url)

        if '_approve' in request.POST:
            is_manager = request.user.is_superuser or request.user.groups.filter(name=GROUP_MANAGER).exists()
            if is_manager:
                if obj.record_state == AppChemicalMaterialsViolation.STATE_SMRC:
                    obj.record_state = AppChemicalMaterialsViolation.STATE_APPROVED
                    obj.updated_by = request.user
                    obj.save()
                    self.log_change(request, obj, _('state_approved'))
                    self.message_user(request, _('تم اعتماد الطلب بنجاح!'), messages.SUCCESS)
                else:
                    self.message_user(request, _('لا يمكن الاعتماد إلا في حالة "بانتظار المدير".'), messages.WARNING)
            return HttpResponseRedirect(redirect_url)

        return super().response_change(request, obj)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            obj = self.get_object(request, object_id)
            if obj:
                is_manager = request.user.is_superuser or request.user.groups.filter(name=GROUP_MANAGER).exists()
                is_state = request.user.is_superuser or request.user.groups.filter(name=GROUP_STATE).exists()

                extra_context['show_confirm_btn'] = (
                    is_state and obj.record_state == AppChemicalMaterialsViolation.STATE_DRAFT
                )
                extra_context['show_approve_btn'] = (
                    is_manager and obj.record_state == AppChemicalMaterialsViolation.STATE_SMRC
                )
        return super().changeform_view(request, object_id, form_url, extra_context)

    fieldsets = (
        (_("معلومات الضبط الأساسية والمكان"), {
            'fields': ('date', 'time', 'record_state', 'source_state', 'city_or_village', 'neighborhood', 'house', 'location_details')
        }),
        (_("بيانات القائم بالضبط"), {
            'fields': ('officer_name', 'officer_job', 'officer_org')
        }),
        (_("تفاصيل الواقعة"), {
            'fields': ('incident_type',)
        }),
        (_("حالة التخزين"), {
            'fields': ('is_safely_stored', 'ventilation', 'has_warning_labels', 'near_heat_or_flame')
        }),
        (_("تقييم المخاطر"), {
            'fields': ('public_health_risk', 'fire_explosion_risk', 'environmental_risk')
        }),
        (_("إجراءات أولية يجب اتباعها"), {
            'fields': (
                'proc_secure_site',
                'proc_notify_authorities',
                'proc_prevent_handling',
                'proc_notify_violations',
                'proc_educate_owner'
            )
        }),
        (_("أقوال صاحب الموقع"), {
            'fields': ('owner_statements',)
        }),
        (_("التوقيعات"), {
            'fields': ('officer_signature_name', 'owner_signature_name')
        }),
    )

admin.site.register(AppChemicalMaterialsViolation, AppChemicalMaterialsViolationAdmin)


class ChemicalViolationStateRepresentativeAdmin(admin.ModelAdmin):
    model = ChemicalViolationStateRepresentative
    form = ChemicalViolationStateRepresentativeForm
    list_display = ["name", "state", "user"]
    list_filter = [("state", admin.RelatedOnlyFieldListFilter)]
    view_on_site = False

    def has_module_perms(self, request, app_label):
        return request.user.is_superuser or request.user.groups.filter(name=GROUP_MANAGER).exists()

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name=GROUP_MANAGER).exists()

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name=GROUP_MANAGER).exists()

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name=GROUP_MANAGER).exists()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name=GROUP_MANAGER).exists()


admin.site.register(ChemicalViolationStateRepresentative, ChemicalViolationStateRepresentativeAdmin)
