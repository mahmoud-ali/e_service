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

class MeltBatchRecordsInline(admin.TabularInline):
    model = AppMoveGoldTraditional
    fields = ['code', 'almustafid_name', 'jihat_alaisdar', 'gold_weight_in_gram']
    readonly_fields = ['code', 'almustafid_name', 'jihat_alaisdar', 'gold_weight_in_gram']
    can_delete = False
    extra = 0
    max_num = 0

    def has_add_permission(self, request, obj):
        return False

class MeltBatchDetailInline(admin.TabularInline):
    model = MeltBatchDetail
    fields = ['alloy_weight_gram', 'alloy_shape']

    def _is_complete(self, obj):
        return bool(obj and obj.state == MeltBatch.STATE_COMPLETE)

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

class MeltBatchAdmin(LogAdminMixin, admin.ModelAdmin):
    inlines = [MeltBatchRecordsInline, MeltBatchDetailInline]
    list_display = ['code', 'melt_date', 'melt_workshop', 'standardization_lab', 'record_count', 'total_weight_display', 'state', 'print_button', 'sale_button', 'storage_button', 'complete_button']
    list_filter = ['state', ]
    date_hierarchy = "melt_date"

    search_fields = ['code', 'melt_workshop', 'standardization_lab']
    readonly_fields = ['code']
    actions = ['mark_complete', 'print_selected_batches', 'export_as_csv']

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.state == MeltBatch.STATE_COMPLETE:
            readonly_fields = list(set(readonly_fields + [
                'melt_date', 'melt_workshop', 'standardization_lab', 'state', 'sale', 'storage'
            ]))
        return readonly_fields

    fieldsets = [
        (None, {'fields': ['code', 'melt_date']}),
        (_('melt_details'), {'fields': [('melt_workshop', 'standardization_lab')]}),
        (None, {'fields': ['state', 'sale', 'storage']}),
    ]

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists():
            return qs
        try:
            gold_user = request.user.gold_travel_traditional
            if gold_user.is_state_manager or gold_user.is_state_viewer or gold_user.user_type in [GoldTravelTraditionalUser.JIHAT_TARHIL, GoldTravelTraditionalUser.BOTH]:
                return qs.filter(source_state=gold_user.state)

            return qs.none()
        except:
            return qs.none()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists():
            return True
        if obj and obj.state == MeltBatch.STATE_COMPLETE:
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
        if obj.state == MeltBatch.STATE_COMPLETE:
            return False
        return super().has_delete_permission(request, obj)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("<int:pk>/batch-print/", self.admin_site.admin_view(self.batch_print_view), name="gold_travel_traditional_meltbatch_print"),
            path("<int:pk>/complete/", self.admin_site.admin_view(self.complete_view)),
            path("<int:pk>/sale/", self.admin_site.admin_view(self.sale_view)),
            path("<int:pk>/sale/print/", self.admin_site.admin_view(self.print_sale_view)),
            path("<int:pk>/storage/", self.admin_site.admin_view(self.storage_view)),
            path("<int:pk>/storage/print/", self.admin_site.admin_view(self.print_storage_view)),
        ]
        return my_urls + urls

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
        url = reverse("admin:gold_travel_traditional_meltbatch_print", args=[obj.pk])
        return format_html('<a class="changelink" target="_blank" href="{url}">{txt}</a>', url=url, txt=_('طباعة'))

    @admin.display(description=_('complete'))
    def complete_button(self, obj):
        if not self.has_change_permission(self.current_request, obj):
            return '-'
        if obj.state == MeltBatch.STATE_PENDING:
            url = reverse("admin:gold_travel_traditional_meltbatch_changelist") + f"{obj.pk}/complete/"
            return format_html('<a class="changelink" href="{url}">{txt}</a>', url=url, txt=_('إكمال'))
        return '-'

    @admin.display(description=_('sale'))
    def sale_button(self, obj):
        if not self.has_view_permission(self.current_request, obj):
            return '-'
        if obj.state == MeltBatch.STATE_COMPLETE and not obj.sale:
            url = reverse("admin:gold_travel_traditional_meltbatch_changelist") + f"{obj.pk}/sale/"
            return format_html('<a class="changelink" href="{url}">{txt}</a>', url=url, txt=_('بيع'))
        if obj.sale:
            url = reverse("admin:gold_travel_traditional_meltbatch_changelist") + f"{obj.pk}/sale/print/"
            return format_html('<a class="changelink" target="_blank" href="{url}">{txt}</a>', url=url, txt=obj.sale.code)
        return '-'

    @admin.display(description=_('storage'))
    def storage_button(self, obj):
        if not self.has_view_permission(self.current_request, obj):
            return '-'
        if obj.state == MeltBatch.STATE_COMPLETE and not obj.storage:
            url = reverse("admin:gold_travel_traditional_meltbatch_changelist") + f"{obj.pk}/storage/"
            return format_html('<a class="changelink" href="{url}">{txt}</a>', url=url, txt=_('تخزين'))
        if obj.storage:
            url = reverse("admin:gold_travel_traditional_meltbatch_changelist") + f"{obj.pk}/storage/print/"
            return format_html('<a class="changelink" target="_blank" href="{url}">{txt}</a>', url=url, txt=obj.storage.code)
        return '-'

    def complete_view(self, request, pk):
        batch = MeltBatch.objects.get(pk=pk)
        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                gold_user = request.user.gold_travel_traditional
                if gold_user.user_type not in [GoldTravelTraditionalUser.JIHAT_TARHIL, GoldTravelTraditionalUser.BOTH, GoldTravelTraditionalUser.STATE_MANAGER]:
                    self.message_user(request, _('You do not have permission to complete batches.'), level='error')
                    return redirect(reverse("admin:gold_travel_traditional_meltbatch_changelist"))
                if gold_user.is_state_manager and batch.source_state_id != gold_user.state_id:
                    self.message_user(request, _('You can only complete batches from your state.'), level='error')
                    return redirect(reverse("admin:gold_travel_traditional_meltbatch_changelist"))
            except:
                self.message_user(request, _('You do not have permission to complete batches.'), level='error')
                return redirect(reverse("admin:gold_travel_traditional_meltbatch_changelist"))
        if batch.state == MeltBatch.STATE_PENDING:
            if not batch.details.exists():
                self.message_user(request, _('لا يمكن إكمال الاستمارة قبل إدخال تفاصيل السبائك الناتجة'), level='error')
                return redirect(reverse("admin:gold_travel_traditional_meltbatch_changelist"))
            batch.state = MeltBatch.STATE_COMPLETE
            batch.updated_by = request.user
            batch.save()
            self.message_user(request, _('Batch marked as complete.'))
        return redirect(reverse("admin:gold_travel_traditional_meltbatch_changelist"))

    def sale_view(self, request, pk):
        batch = MeltBatch.objects.get(pk=pk)

        gold_user = None
        try:
            gold_user = request.user.gold_travel_traditional
        except:
            pass

        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            if not gold_user or not gold_user.is_tarhil_user:
                self.message_user(request, _('Only destination users can create sales.'), level='error')
                return redirect("admin:gold_travel_traditional_meltbatch_changelist")

        batch_source_state = gold_user.state if gold_user else batch.source_state

        if batch.state != MeltBatch.STATE_COMPLETE:
            self.message_user(request, _('Batch must be completed first.'), level='error')
            return redirect("admin:gold_travel_traditional_meltbatch_changelist")

        if request.method == "POST":
            my_form = MeltBatchSaleForm(request.POST)
            my_form.fields['existing_sale'].queryset = Sale.objects.filter(
                source_state=batch_source_state,
                state=Sale.STATE_PENDING
            )
            my_form.fields['buyer_saig'].queryset = LkpSaig.objects.filter(state_id=batch.source_state_id)
            if my_form.is_valid():
                choice = my_form.cleaned_data['batch_choice']
                if choice == 'new':
                    buyer_type = my_form.cleaned_data['buyer_type']
                    buyer_exporter = my_form.cleaned_data.get('buyer_exporter')
                    buyer_saig = my_form.cleaned_data.get('buyer_saig')
                    sale = Sale.objects.create(
                        sale_date=my_form.cleaned_data['sale_date'],
                        buyer_type=buyer_type,
                        buyer_exporter=buyer_exporter,
                        buyer_saig=buyer_saig,
                        source_state=batch_source_state,
                        created_by=request.user,
                        updated_by=request.user,
                    )
                    batch.sale = sale
                    batch.save()
                    self.log_change(request, batch, _('sale_created'))
                else:
                    sale = my_form.cleaned_data['existing_sale']
                    batch.sale = sale
                    batch.save()
                    self.log_change(request, batch, _('sale_assigned'))

                self.message_user(request, _('Sale saved successfully!'))
                return HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_changelist"
                        % (
                            self.admin_site.name,
                            batch._meta.app_label,
                            batch._meta.model_name,
                        )
                    ) + f"{batch.pk}/sale/print/"
                )
        else:
            my_form = MeltBatchSaleForm()
            my_form.fields['existing_sale'].queryset = Sale.objects.filter(
                source_state=batch_source_state,
                state=Sale.STATE_PENDING
            )
            my_form.fields['buyer_saig'].queryset = LkpSaig.objects.filter(state_id=batch.source_state_id)

        context = dict(
            self.admin_site.each_context(request),
            object=batch,
            form=my_form,
            opts=MeltBatch._meta,
            title=_("sale_details"),
        )
        return TemplateResponse(request, "admin/gold_travel_traditional/appmovegoldtraditional/sale_form.html", context)

    def print_sale_view(self, request, pk):
        from itertools import zip_longest

        batch = MeltBatch.objects.get(pk=pk)
        sale = batch.sale
        if not sale:
            self.message_user(request, _('No sale found.'), level='error')
            return redirect("admin:gold_travel_traditional_meltbatch_changelist")

        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                gold_user = request.user.gold_travel_traditional
                if not (gold_user.is_tarhil_user or gold_user.is_state_manager):
                    self.message_user(request, _('Only destination users can print this form.'), level='error')
                    return redirect("admin:gold_travel_traditional_meltbatch_changelist")
                if gold_user.is_state_manager and sale.source_state_id != gold_user.state_id:
                    self.message_user(request, _('You can only print sales from your state.'), level='error')
                    return redirect("admin:gold_travel_traditional_meltbatch_changelist")
            except:
                return redirect("admin:gold_travel_traditional_meltbatch_changelist")

        # Combine all records' AppMoveGoldTraditionalDetail + all melt batches' MeltBatchDetail
        all_details = []
        for record in sale.records.all():
            all_details.extend(record.details.all())
        for mb in sale.melt_batches.all():
            all_details.extend(mb.details.all())

        chunk_size = 40
        alloy_chunks = []
        for i in range(0, len(all_details), chunk_size):
            chunk = all_details[i:i + chunk_size]
            half = (len(chunk) + 1) // 2
            left_half = chunk[:half]
            right_half = chunk[half:]
            rows = list(zip_longest(left_half, right_half))
            alloy_chunks.append({
                'rows': rows,
                'start_index': i + 1,
                'half_offset': half
            })

        class _Row:
            __slots__ = ('code', 'almustafid_name', 'jihat_alaisdar', 'gold_weight_in_gram', 'alloy_count')
            def __init__(self, code, name, source_name, weight, count):
                self.code = code
                self.almustafid_name = name
                self.jihat_alaisdar = type('_', (), {'name': source_name})
                self.gold_weight_in_gram = weight
                self.alloy_count = count

        records = []
        for r in sale.records.all():
            records.append(_Row(r.code, r.almustafid_name, r.jihat_alaisdar.name, r.gold_weight_in_gram, r.alloy_count))
        for mb in sale.melt_batches.all():
            records.append(_Row(mb.code, mb.melt_workshop, mb.source_state.name if mb.source_state else '', mb.output_weight, mb.output_alloy_count))

        context = {
            'sale': sale,
            'records': records,
            'alloy_chunks': alloy_chunks,
        }
        return TemplateResponse(request, "gold_travel_traditional/gold_travel_traditional_sale.html", context)

    def storage_view(self, request, pk):
        batch = MeltBatch.objects.get(pk=pk)

        gold_user = None
        try:
            gold_user = request.user.gold_travel_traditional
        except:
            pass

        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            if not gold_user or not gold_user.is_tarhil_user:
                self.message_user(request, _('Only destination users can create storage receipts.'), level='error')
                return redirect("admin:gold_travel_traditional_meltbatch_changelist")

        batch_source_state = gold_user.state if gold_user else batch.source_state

        if batch.state != MeltBatch.STATE_COMPLETE:
            self.message_user(request, _('Batch must be completed first.'), level='error')
            return redirect("admin:gold_travel_traditional_meltbatch_changelist")

        if request.method == "POST":
            my_form = MeltBatchStorageForm(request.POST)
            my_form.fields['existing_storage'].queryset = Storage.objects.filter(
                source_state=batch_source_state,
                state=Storage.STATE_PENDING
            )
            if my_form.is_valid():
                choice = my_form.cleaned_data['batch_choice']
                if choice == 'new':
                    storage = Storage.objects.create(
                        storage_date=my_form.cleaned_data['storage_date'],
                        note=my_form.cleaned_data.get('note', ''),
                        source_state=batch_source_state,
                        created_by=request.user,
                        updated_by=request.user,
                    )
                    batch.storage = storage
                    batch.save()
                    self.log_change(request, batch, _('storage_created'))
                else:
                    storage = my_form.cleaned_data['existing_storage']
                    batch.storage = storage
                    batch.save()
                    self.log_change(request, batch, _('storage_assigned'))

                self.message_user(request, _('Storage receipt saved successfully!'))
                return HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_changelist"
                        % (
                            self.admin_site.name,
                            batch._meta.app_label,
                            batch._meta.model_name,
                        )
                    ) + f"{batch.pk}/storage/print/"
                )
        else:
            my_form = MeltBatchStorageForm()
            my_form.fields['existing_storage'].queryset = Storage.objects.filter(
                source_state=batch_source_state,
                state=Storage.STATE_PENDING
            )

        context = dict(
            self.admin_site.each_context(request),
            object=batch,
            form=my_form,
            opts=MeltBatch._meta,
            title=_("تخزين"),
        )
        return TemplateResponse(request, "admin/gold_travel_traditional/appmovegoldtraditional/storage_form.html", context)

    def print_storage_view(self, request, pk):
        from itertools import zip_longest

        batch = MeltBatch.objects.get(pk=pk)
        storage = batch.storage
        if not storage:
            self.message_user(request, _('No storage receipt found.'), level='error')
            return redirect("admin:gold_travel_traditional_meltbatch_changelist")

        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                gold_user = request.user.gold_travel_traditional
                if not (gold_user.is_tarhil_user or gold_user.is_state_manager):
                    self.message_user(request, _('Only destination users can print this form.'), level='error')
                    return redirect("admin:gold_travel_traditional_meltbatch_changelist")
                if gold_user.is_state_manager and storage.source_state_id != gold_user.state_id:
                    self.message_user(request, _('You can only print storage receipts from your state.'), level='error')
                    return redirect("admin:gold_travel_traditional_meltbatch_changelist")
            except:
                return redirect("admin:gold_travel_traditional_meltbatch_changelist")

        # Combine all records' AppMoveGoldTraditionalDetail + all melt batches' MeltBatchDetail
        all_details = []
        for record in storage.records.all():
            all_details.extend(record.details.all())
        for mb in storage.melt_batches.all():
            all_details.extend(mb.details.all())

        chunk_size = 40
        alloy_chunks = []
        for i in range(0, len(all_details), chunk_size):
            chunk = all_details[i:i + chunk_size]
            half = (len(chunk) + 1) // 2
            left_half = chunk[:half]
            right_half = chunk[half:]
            rows = list(zip_longest(left_half, right_half))
            alloy_chunks.append({
                'rows': rows,
                'start_index': i + 1,
                'half_offset': half
            })

        class _Row:
            __slots__ = ('code', 'almustafid_name', 'jihat_alaisdar', 'gold_weight_in_gram', 'alloy_count')
            def __init__(self, code, name, source_name, weight, count):
                self.code = code
                self.almustafid_name = name
                self.jihat_alaisdar = type('_', (), {'name': source_name})
                self.gold_weight_in_gram = weight
                self.alloy_count = count

        records = []
        for r in storage.records.all():
            records.append(_Row(r.code, r.almustafid_name, r.jihat_alaisdar.name, r.gold_weight_in_gram, r.alloy_count))
        for mb in storage.melt_batches.all():
            records.append(_Row(mb.code, mb.melt_workshop, mb.source_state.name if mb.source_state else '', mb.output_weight, mb.output_alloy_count))

        context = {
            'storage': storage,
            'records': records,
            'alloy_chunks': alloy_chunks,
        }
        return TemplateResponse(request, "gold_travel_traditional/gold_travel_traditional_storage.html", context)

    def batch_print_view(self, request, pk):
        from itertools import zip_longest

        batch = MeltBatch.objects.get(pk=pk)
        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                gold_user = request.user.gold_travel_traditional
                if gold_user.is_state_viewer:
                    self.message_user(request, _('You do not have permission to print batches.'), level='error')
                    return redirect(reverse("admin:gold_travel_traditional_meltbatch_changelist"))
                if not (gold_user.is_tarhil_user or gold_user.is_state_manager):
                    self.message_user(request, _('You do not have permission to print batches.'), level='error')
                    return redirect(reverse("admin:gold_travel_traditional_meltbatch_changelist"))
                if gold_user.is_state_manager and batch.source_state_id != gold_user.state_id:
                    self.message_user(request, _('You can only print batches from your state.'), level='error')
                    return redirect(reverse("admin:gold_travel_traditional_meltbatch_changelist"))
            except:
                self.message_user(request, _('You do not have permission to print batches.'), level='error')
                return redirect(reverse("admin:gold_travel_traditional_meltbatch_changelist"))

        records = batch.records.all()

        all_details = []
        for record in records:
            all_details.extend(record.details.all())

        chunk_size = 40
        alloy_chunks = []
        for i in range(0, len(all_details), chunk_size):
            chunk = all_details[i:i + chunk_size]
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
            'batch': batch,
            'records': records,
            'alloy_chunks': alloy_chunks,
        }
        return TemplateResponse(request, "gold_travel_traditional/gold_travel_traditional_melt.html", context)

    @admin.action(description=_('مكتمل'))
    def mark_complete(self, request, queryset):
        completed = 0
        skipped = 0
        for batch in queryset.filter(state=MeltBatch.STATE_PENDING):
            if not batch.details.exists():
                skipped += 1
                continue
            batch.state = MeltBatch.STATE_COMPLETE
            batch.updated_by = request.user
            batch.save()
            completed += 1
        if completed:
            self.message_user(request, _('Selected batches marked as complete.'))
        if skipped:
            self.message_user(request, _('تم تجاهل الاستمارات التي لا تحتوي على تفاصيل السبائك الناتجة'), level='warning')

    @admin.action(description=_('طباعة الاستمارات المحددة'))
    def print_selected_batches(self, request, queryset):
        # Redirect to print the first selected batch
        batch = queryset.first()
        if batch:
            return redirect(reverse("admin:gold_travel_traditional_meltbatch_print", args=[batch.pk]))

    @admin.action(description=_('Export data'))
    def export_as_csv(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="melt_batch_form.csv"'},
        )
        header = [
            "الكود", "تاريخ الصهر", "ورشة الصهر", "مختبر المعايرة",
            "عدد الاستمارات", "عدد السبائك (مدخل)", "الوزن (مدخل)",
            "عدد السبائك (ناتج)", "الوزن (ناتج)",
            "فاتورة البيع", "شهادة تخزين", "الولاية", "الحالة",
            "تاريخ الإنشاء", "أنشئ بواسطة", "تاريخ التحديث", "حدث بواسطة"
        ]

        # BOM
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        writer.writerow(header)

        for obj in queryset:
            row = [
                obj.code,
                obj.melt_date,
                obj.melt_workshop,
                obj.standardization_lab,
                obj.record_count,
                obj.total_alloy_count,
                round(obj.total_weight, 2),
                obj.output_alloy_count,
                round(obj.output_weight, 2),
                str(obj.sale) if obj.sale else '',
                str(obj.storage) if obj.storage else '',
                str(obj.source_state) if obj.source_state else '',
                obj.get_state_display(),
                obj.created_at,
                obj.created_by,
                obj.updated_at,
                obj.updated_by,
            ]
            writer.writerow(row)

        return response

admin.site.register(MeltBatch, MeltBatchAdmin)

