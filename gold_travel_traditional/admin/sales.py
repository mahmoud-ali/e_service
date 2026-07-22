import codecs
import csv
from django.conf import settings
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import path, reverse

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.forms.widgets import TextInput

from django.contrib import admin

from company_profile.models import LkpState
from gold_travel_traditional.forms import (
    AppMoveGoldTraditionalAddForm, AppMoveGoldTraditionalArriveForm,
    AppMoveGoldTraditionalMeltForm, AppMoveGoldTraditionalRenewForm,
    AppMoveGoldTraditionalSaleForm, AppMoveGoldTraditionalStorageForm,
    GoldTravelTraditionalUserJihatAlaisdarForm, GoldTravelTraditionalUserJihatTarhilForm,
    GoldTravelTraditionalUserForm, MeltBatchSaleForm, MeltBatchStorageForm
)
from gold_travel_traditional.models import (
    AppMoveGoldTraditional, AppMoveGoldTraditionalDetail,
    GoldTravelTraditionalState, GoldTravelTraditionalUser,
    GoldTravelTraditionalUserJihatAlaisdar, GoldTravelTraditionalUserJihatTarhil,
    LkpJihatAlaisdar, LkpJihatAltarhil, LkpSaig, MeltBatch, MeltBatchDetail, Sale, Storage
)

from .base import LogAdminMixin, get_user_state, RelatedOnlyFieldListFilterNotEmpty, HasPhotoFilter

class SaleRecordsInline(admin.TabularInline):
    model = AppMoveGoldTraditional
    fields = ['code', 'almustafid_name', 'gold_weight_in_gram']
    readonly_fields = ['code', 'almustafid_name', 'gold_weight_in_gram']
    can_delete = False
    extra = 0
    max_num = 0

    def has_add_permission(self, request, obj):
        return False

class SaleMeltBatchesInline(admin.TabularInline):
    model = MeltBatch
    fields = ['code', 'melt_workshop', 'total_weight_display']
    readonly_fields = ['code', 'melt_workshop', 'total_weight_display']
    can_delete = False
    extra = 0
    max_num = 0

    @admin.display(description=_('total_weight'))
    def total_weight_display(self, obj):
        return round(obj.total_weight, 2) if obj.total_weight else 0.0

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return True

class SaleAdmin(LogAdminMixin, admin.ModelAdmin):
    inlines = [SaleRecordsInline, SaleMeltBatchesInline]
    list_display = ['code', 'sale_date', 'buyer_display', 'record_count', 'total_weight_display', 'note', 'state', 'print_button', 'complete_button']
    list_filter = ['state','buyer_type', ('buyer_exporter',RelatedOnlyFieldListFilterNotEmpty), ('buyer_saig',RelatedOnlyFieldListFilterNotEmpty)]
    date_hierarchy = "sale_date"

    search_fields = ['code', 'buyer_exporter__name', 'buyer_saig__name', 'note']
    readonly_fields = ['code']
    actions = ['mark_complete', 'export_as_csv']

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.state == Sale.STATE_COMPLETE:
            readonly_fields = list(set(readonly_fields + [
                'sale_date', 'buyer_type', 'buyer_exporter', 'buyer_saig', 'note', 'state'
            ]))
        return readonly_fields

    fieldsets = [
        (None, {'fields': ['code', 'sale_date']}),
        (_('sale_details'), {'fields': [('buyer_type',), ('buyer_exporter', 'buyer_saig')]}),
        (None, {'fields': ['note']}),
        (None, {'fields': ['state']}),
    ]

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists():
            return qs
        try:
            gold_user = request.user.gold_travel_traditional
            if gold_user.is_state_manager or gold_user.is_state_viewer:
                return qs.filter(source_state=gold_user.state)
            if gold_user.user_type in [GoldTravelTraditionalUser.JIHAT_TARHIL, GoldTravelTraditionalUser.BOTH]:
                return qs.filter(source_state=gold_user.state, state=Sale.STATE_PENDING)
            return qs.none()
        except:
            return qs.none()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists():
            return True
        if obj and obj.state == Sale.STATE_COMPLETE:
            return False
        try:
            gold_user = request.user.gold_travel_traditional
            return gold_user.user_type in [GoldTravelTraditionalUser.JIHAT_TARHIL, GoldTravelTraditionalUser.BOTH, GoldTravelTraditionalUser.STATE_MANAGER]
        except:
            return False

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists():
            return True
        try:
            gold_user = request.user.gold_travel_traditional
            return gold_user.user_type in [GoldTravelTraditionalUser.JIHAT_TARHIL, GoldTravelTraditionalUser.BOTH, GoldTravelTraditionalUser.STATE_MANAGER, GoldTravelTraditionalUser.STATE_VIEWER]
        except:
            return False

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return False
        if obj.state == Sale.STATE_COMPLETE:
            return False
        return super().has_delete_permission(request, obj)

    @admin.display(description=_('total_weight'))
    def total_weight_display(self, obj):
        return round(obj.total_weight, 2) if obj.total_weight else 0.0

    def changelist_view(self, request, extra_context=None):
        self.current_request = request
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description=_('print'))
    def print_button(self, obj):
        if not self.has_change_permission(self.current_request, obj):
            return '-'
        record = obj.records.first()
        if record:
            url = reverse("admin:gold_travel_traditional_appmovegoldtraditional_changelist") + f"{record.pk}/sale/print/"
            return format_html('<a class="changelink" target="_blank" href="{url}">{txt}</a>', url=url, txt=_('طباعة'))
        return '-'

    @admin.display(description=_('complete'))
    def complete_button(self, obj):
        if not self.has_change_permission(self.current_request, obj):
            return '-'
        if obj.state == Sale.STATE_PENDING:
            url = reverse("admin:gold_travel_traditional_sale_changelist") + f"{obj.pk}/complete/"
            return format_html('<a class="changelink" href="{url}">{txt}</a>', url=url, txt=_('إكمال'))
        return '-'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("<int:pk>/complete/", self.admin_site.admin_view(self.complete_view)),
        ]
        return my_urls + urls

    def complete_view(self, request, pk):
        sale = Sale.objects.get(pk=pk)
        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                gold_user = request.user.gold_travel_traditional
                if gold_user.user_type not in [GoldTravelTraditionalUser.JIHAT_TARHIL, GoldTravelTraditionalUser.BOTH, GoldTravelTraditionalUser.STATE_MANAGER]:
                    self.message_user(request, _('You do not have permission to complete sales.'), level='error')
                    return redirect(reverse("admin:gold_travel_traditional_sale_changelist"))
                if gold_user.is_state_manager and sale.source_state_id != gold_user.state_id:
                    self.message_user(request, _('You can only complete sales from your state.'), level='error')
                    return redirect(reverse("admin:gold_travel_traditional_sale_changelist"))
            except:
                self.message_user(request, _('You do not have permission to complete sales.'), level='error')
                return redirect(reverse("admin:gold_travel_traditional_sale_changelist"))
        if sale.state == Sale.STATE_PENDING:
            sale.state = Sale.STATE_COMPLETE
            sale.updated_by = request.user
            sale.save()
            self.message_user(request, _('Sale marked as complete.'))
        return redirect(reverse("admin:gold_travel_traditional_sale_changelist"))

    @admin.action(description=_('Mark as Complete'))
    def mark_complete(self, request, queryset):
        queryset.filter(state=Sale.STATE_PENDING).update(state=Sale.STATE_COMPLETE, updated_by=request.user)
        self.message_user(request, _('Selected sales marked as complete.'))

    @admin.action(description=_('Export data'))
    def export_as_csv(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="sale_form.csv"'},
        )
        header = [
            "الكود", "تاريخ البيع", "نوع المشتري", "المشتري",
            "عدد الاستمارات", "عدد السبائك", "الوزن (جرام)",
            "ملاحظات", "الولاية", "الحالة",
            "تاريخ الإنشاء", "أنشئ بواسطة", "تاريخ التحديث", "حدث بواسطة"
        ]

        # BOM
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        writer.writerow(header)

        for obj in queryset:
            row = [
                obj.code,
                obj.sale_date,
                obj.get_buyer_type_display(),
                obj.buyer_display,
                obj.record_count,
                obj.total_alloy_count,
                round(obj.total_weight, 2),
                obj.note,
                str(obj.source_state) if obj.source_state else '',
                obj.get_state_display(),
                obj.created_at,
                obj.created_by,
                obj.updated_at,
                obj.updated_by,
            ]
            writer.writerow(row)

        return response

admin.site.register(Sale, SaleAdmin)

