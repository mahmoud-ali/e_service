import codecs
import csv
from django.db import models
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import path, reverse

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.template.response import TemplateResponse

from django.contrib import admin

from company_profile.models import LkpState
from gold_travel_traditional.forms import (
    MeltProduceForm, MeltProduceProduceForm
)
from gold_travel_traditional.models import (
    AppMoveGoldTraditional, AppMoveGoldTraditionalDetail,
    GoldTravelTraditionalState, GoldTravelTraditionalUser,
    MeltProduce, MeltProduceDetail
)

from .base import LogAdminMixin, get_user_state, RelatedOnlyFieldListFilterNotEmpty


class MeltProduceDetailInline(admin.TabularInline):
    model = MeltProduceDetail
    fields = ['alloy_weight_gram', 'alloy_shape']

    def _is_complete(self, obj):
        return bool(obj and obj.state in [MeltProduce.STATE_COMPLETE, MeltProduce.STATE_CANCLED])

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if self._is_complete(obj) else 1

    def get_readonly_fields(self, request, obj=None):
        if self._is_complete(obj):
            return ['alloy_weight_gram', 'alloy_shape']
        return []

    def has_add_permission(self, request, obj=None):
        return not self._is_complete(obj)

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return not self._is_complete(obj)


class MeltProduceAdmin(LogAdminMixin, admin.ModelAdmin):
    form = MeltProduceForm
    inlines = [MeltProduceDetailInline]
    change_form_template = "admin/gold_travel_traditional/meltproduce/change_form.html"

    list_display = [
        'code', 'issue_date', 'almustafid_name', 'melt_workshop',
        'alloy_count_display', 'total_weight_display', 'produced_record_display',
        'state', 'print_button', 'produce_button', 'complete_button', 'cancel_button',
    ]
    list_filter = ['state', ('source_state', RelatedOnlyFieldListFilterNotEmpty)]
    date_hierarchy = "issue_date"
    search_fields = ['code', 'almustafid_name', 'almustafid_phone', 'almustafid_identity', 'melt_workshop']
    readonly_fields = ['code', 'state', 'produced_record_display']
    actions = ['export_as_csv']

    fieldsets = [
        (None, {'fields': ['code', 'issue_date']}),
        (_('بيانات المستفيد'), {'fields': [
            ('almustafid_identity',),
            ('almustafid_name',),
            ('almustafid_identity_type', 'almustafid_phone'),
            ('almustafid_identity_attachement',),
        ]}),
        (_('تفاصيل الصهر'), {'fields': ['melt_workshop']}),
        (None, {'fields': ['state', 'produced_record_display']}),
    ]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.state in [MeltProduce.STATE_COMPLETE, MeltProduce.STATE_CANCLED]:
            readonly_fields = list(set(readonly_fields + [
                'issue_date', 'almustafid_name', 'almustafid_phone',
                'almustafid_identity_type', 'almustafid_identity',
                'almustafid_identity_attachement', 'melt_workshop', 'state',
            ]))
        return readonly_fields

    def has_add_permission(self, request):
        try:
            gold_user = request.user.gold_travel_traditional
            return gold_user.user_type in [GoldTravelTraditionalUser.JIHAT_ALAISDAR, GoldTravelTraditionalUser.BOTH]
        except:
            return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager", "gold_travel_traditional_manager_show")).exists():
            return qs
        try:
            gold_user = request.user.gold_travel_traditional
            if gold_user.is_state_manager or gold_user.is_state_viewer or gold_user.user_type in [GoldTravelTraditionalUser.JIHAT_ALAISDAR, GoldTravelTraditionalUser.BOTH]:
                return qs.filter(source_state=gold_user.state)
            return qs.none()
        except:
            return qs.none()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name="gold_travel_traditional_manager").exists():
            return True
        if obj and obj.state in [MeltProduce.STATE_COMPLETE, MeltProduce.STATE_CANCLED]:
            return False
        try:
            gold_user = request.user.gold_travel_traditional
            return gold_user.user_type in [GoldTravelTraditionalUser.JIHAT_ALAISDAR, GoldTravelTraditionalUser.BOTH, GoldTravelTraditionalUser.STATE_MANAGER]
        except:
            return False

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager", "gold_travel_traditional_manager_show")).exists():
            return True
        try:
            gold_user = request.user.gold_travel_traditional
            return gold_user.user_type in [GoldTravelTraditionalUser.JIHAT_ALAISDAR, GoldTravelTraditionalUser.BOTH, GoldTravelTraditionalUser.STATE_MANAGER, GoldTravelTraditionalUser.STATE_VIEWER]
        except:
            return False

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return False
        if obj.state in [MeltProduce.STATE_COMPLETE, MeltProduce.STATE_CANCLED]:
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.source_state = get_user_state(request)
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("<int:pk>/produce/", self.admin_site.admin_view(self.produce_view), name="gold_travel_traditional_meltproduce_produce"),
            path("<int:pk>/print/", self.admin_site.admin_view(self.print_view), name="gold_travel_traditional_meltproduce_print"),
            path("<int:pk>/complete/", self.admin_site.admin_view(self.complete_view), name="gold_travel_traditional_meltproduce_complete"),
            path("<int:pk>/cancel/", self.admin_site.admin_view(self.cancel_view), name="gold_travel_traditional_meltproduce_cancel"),
        ]
        return my_urls + urls

    @admin.display(description=_('عدد السبائك'))
    def alloy_count_display(self, obj):
        return obj.alloy_count

    @admin.display(description=_('total_weight'))
    def total_weight_display(self, obj):
        return round(obj.total_weight, 2) if obj.total_weight else 0.0

    @admin.display(description=_('استمارة الترحيل المنتجة'))
    def produced_record_display(self, obj):
        record = obj.produced_record
        if record:
            url = reverse("admin:gold_travel_traditional_appmovegoldtraditional_change", args=[record.pk])
            return format_html('<a href="{url}">{code}</a>', url=url, code=record.code)
        return '-'

    def changelist_view(self, request, extra_context=None):
        self.current_request = request
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description=_('print'))
    def print_button(self, obj):
        if not self.has_view_permission(self.current_request, obj):
            return '-'
        url = reverse("admin:gold_travel_traditional_meltproduce_print", args=[obj.pk])
        return format_html('<a class="changelink" target="_blank" href="{url}">{txt}</a>', url=url, txt=_('طباعة'))

    @admin.display(description=_('إنتاج استمارة ترحيل'))
    def produce_button(self, obj):
        if not self.has_change_permission(self.current_request, obj):
            return '-'
        if obj.state == MeltProduce.STATE_PENDING and not obj.produced_record:
            url = reverse("admin:gold_travel_traditional_meltproduce_produce", args=[obj.pk])
            return format_html('<a class="changelink" href="{url}">{txt}</a>', url=url, txt=_('إنتاج استمارة ترحيل'))
        return '-'

    @admin.display(description=_('complete'))
    def complete_button(self, obj):
        if not self.has_change_permission(self.current_request, obj):
            return '-'
        if obj.state == MeltProduce.STATE_PENDING:
            url = reverse("admin:gold_travel_traditional_meltproduce_complete", args=[obj.pk])
            return format_html('<a class="changelink" href="{url}">{txt}</a>', url=url, txt=_('إكمال'))
        return '-'

    @admin.display(description=_('cancel'))
    def cancel_button(self, obj):
        if not self.has_change_permission(self.current_request, obj):
            return '-'
        if obj.state == MeltProduce.STATE_PENDING:
            url = reverse("admin:gold_travel_traditional_meltproduce_cancel", args=[obj.pk])
            return format_html('<a class="changelink" href="{url}">{txt}</a>', url=url, txt=_('إلغاء'))
        return '-'

    def _can_manage(self, request, obj):
        if request.user.is_superuser or request.user.groups.filter(name="gold_travel_traditional_manager").exists():
            return True
        try:
            gold_user = request.user.gold_travel_traditional
            if gold_user.user_type not in [GoldTravelTraditionalUser.JIHAT_ALAISDAR, GoldTravelTraditionalUser.BOTH, GoldTravelTraditionalUser.STATE_MANAGER]:
                return False
            if gold_user.is_state_manager and obj.source_state_id != gold_user.state_id:
                return False
            return True
        except:
            return False

    def produce_view(self, request, pk):
        melt = MeltProduce.objects.get(pk=pk)

        if not self._can_manage(request, melt):
            self.message_user(request, _('You do not have permission to produce permits.'), level='error')
            return redirect(reverse("admin:gold_travel_traditional_meltproduce_changelist"))

        if melt.state != MeltProduce.STATE_PENDING:
            self.message_user(request, _('Only pending melt forms can produce permits.'), level='error')
            return redirect(reverse("admin:gold_travel_traditional_meltproduce_changelist"))

        if melt.produced_record:
            self.message_user(request, _('This melt form already produced a permit.'), level='error')
            return redirect(reverse("admin:gold_travel_traditional_meltproduce_changelist"))

        if not melt.details.exists():
            self.message_user(request, _('لا يمكن إنتاج الاستمارة قبل إدخال تفاصيل السبائك الناتجة'), level='error')
            return redirect(reverse("admin:gold_travel_traditional_meltproduce_changelist"))

        if request.method == "POST":
            my_form = MeltProduceProduceForm(request.POST, request.FILES, user=request.user)
            if my_form.is_valid():
                permit = my_form.save(commit=False)
                permit.source_state = melt.source_state
                permit.issue_date = melt.issue_date
                permit.almustafid_name = melt.almustafid_name
                permit.almustafid_phone = melt.almustafid_phone
                permit.almustafid_identity_type = melt.almustafid_identity_type
                permit.almustafid_identity = melt.almustafid_identity
                permit.melt_workshop = melt.melt_workshop
                permit.melt_produce = melt
                permit.state = AppMoveGoldTraditional.STATE_NEW
                permit.created_by = request.user
                permit.updated_by = request.user

                config = GoldTravelTraditionalState.objects.filter(state=melt.source_state).first()
                permit.expiry_days = config.expiry_days if config else 3

                permit.save()
                permit.almustafid_identity_attachement.save(
                    melt.almustafid_identity_attachement.name.split('/')[-1],
                    melt.almustafid_identity_attachement,
                    save=False,
                )
                permit.save()

                for d in melt.details.all():
                    AppMoveGoldTraditionalDetail.objects.create(
                        master=permit,
                        alloy_weight_gram=d.alloy_weight_gram,
                        alloy_shape=d.alloy_shape,
                    )

                melt.state = MeltProduce.STATE_COMPLETE
                melt.updated_by = request.user
                melt.save()
                self.log_change(request, melt, _('produced_permit'))

                self.message_user(request, _('Permit produced successfully!'))
                return redirect(reverse("admin:gold_travel_traditional_appmovegoldtraditional_change", args=[permit.pk]))
        else:
            my_form = MeltProduceProduceForm(user=request.user)

        context = dict(
            self.admin_site.each_context(request),
            object=melt,
            form=my_form,
            opts=MeltProduce._meta,
            title=_('إنتاج استمارة ترحيل'),
        )
        return TemplateResponse(request, "admin/gold_travel_traditional/meltproduce/produce_form.html", context)

    def print_view(self, request, pk):
        from itertools import zip_longest

        melt = MeltProduce.objects.get(pk=pk)
        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager", "gold_travel_traditional_manager_show")).exists()):
            try:
                gold_user = request.user.gold_travel_traditional
                if gold_user.is_state_viewer:
                    self.message_user(request, _('You do not have permission to print melt forms.'), level='error')
                    return redirect(reverse("admin:gold_travel_traditional_meltproduce_changelist"))
                if not (gold_user.user_type in [GoldTravelTraditionalUser.JIHAT_ALAISDAR, GoldTravelTraditionalUser.BOTH] or gold_user.is_state_manager):
                    self.message_user(request, _('You do not have permission to print melt forms.'), level='error')
                    return redirect(reverse("admin:gold_travel_traditional_meltproduce_changelist"))
                if gold_user.is_state_manager and melt.source_state_id != gold_user.state_id:
                    self.message_user(request, _('You can only print melt forms from your state.'), level='error')
                    return redirect(reverse("admin:gold_travel_traditional_meltproduce_changelist"))
            except:
                self.message_user(request, _('You do not have permission to print melt forms.'), level='error')
                return redirect(reverse("admin:gold_travel_traditional_meltproduce_changelist"))

        details = list(melt.details.all())
        chunk_size = 40
        alloy_chunks = []
        for i in range(0, len(details), chunk_size):
            chunk = details[i:i + chunk_size]
            half = (len(chunk) + 1) // 2
            left_half = chunk[:half]
            right_half = chunk[half:]
            rows = list(zip_longest(left_half, right_half))
            alloy_chunks.append({
                'rows': rows,
                'start_index': i + 1,
                'half_offset': half
            })

        context = {
            'melt': melt,
            'details': details,
            'alloy_chunks': alloy_chunks,
        }
        return TemplateResponse(request, "gold_travel_traditional/gold_travel_traditional_melt_produce.html", context)

    def complete_view(self, request, pk):
        melt = MeltProduce.objects.get(pk=pk)

        if not self._can_manage(request, melt):
            self.message_user(request, _('You do not have permission to complete melt forms.'), level='error')
            return redirect(reverse("admin:gold_travel_traditional_meltproduce_changelist"))

        if melt.state == MeltProduce.STATE_PENDING:
            if not melt.details.exists():
                self.message_user(request, _('لا يمكن إكمال الاستمارة قبل إدخال تفاصيل السبائك الناتجة'), level='error')
                return redirect(reverse("admin:gold_travel_traditional_meltproduce_changelist"))
            melt.state = MeltProduce.STATE_COMPLETE
            melt.updated_by = request.user
            melt.save()
            self.log_change(request, melt, _('state_complete'))
            self.message_user(request, _('Melt form marked as complete.'))

        return redirect(reverse("admin:gold_travel_traditional_meltproduce_changelist"))

    def cancel_view(self, request, pk):
        melt = MeltProduce.objects.get(pk=pk)

        if not self._can_manage(request, melt):
            self.message_user(request, _('You do not have permission to cancel melt forms.'), level='error')
            return redirect(reverse("admin:gold_travel_traditional_meltproduce_changelist"))

        if melt.state != MeltProduce.STATE_PENDING:
            self.message_user(request, _('Only pending melt forms can be cancelled.'), level='error')
            return redirect(reverse("admin:gold_travel_traditional_meltproduce_changelist"))

        if request.method == "POST":
            melt.state = MeltProduce.STATE_CANCLED
            melt.updated_by = request.user
            melt.save()
            self.log_change(request, melt, _('state_cancled'))
            self.message_user(request, _('Melt form cancelled successfully!'))
            return redirect(reverse("admin:gold_travel_traditional_meltproduce_changelist"))

        context = dict(
            self.admin_site.each_context(request),
            object=melt,
            opts=MeltProduce._meta,
            title=_('تأكيد الإلغاء'),
        )
        return TemplateResponse(request, "admin/gold_travel_traditional/cancel_confirm.html", context)

    @admin.action(description=_('Export data'))
    def export_as_csv(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="melt_produce_form.csv"'},
        )
        header = [
            "الكود", "تاريخ الاصدار", "اسم المستفيد", "نوع الإثبات", "الرقم الوطني",
            "تلفون المستفيد", "ورشة الصهر", "عدد السبائك", "الوزن (جرام)",
            "استمارة الترحيل", "الولاية", "الحالة",
            "تاريخ الإنشاء", "أنشئ بواسطة", "تاريخ التحديث", "حدث بواسطة"
        ]

        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        writer.writerow(header)

        for obj in queryset:
            record = obj.produced_record
            writer.writerow([
                obj.code,
                obj.issue_date,
                obj.almustafid_name,
                obj.get_almustafid_identity_type_display(),
                obj.almustafid_identity,
                obj.almustafid_phone,
                obj.melt_workshop,
                obj.alloy_count,
                round(obj.total_weight, 2),
                record.code if record else '',
                str(obj.source_state) if obj.source_state else '',
                obj.get_state_display(),
                obj.created_at,
                obj.created_by,
                obj.updated_at,
                obj.updated_by,
            ])

        return response


admin.site.register(MeltProduce, MeltProduceAdmin)
