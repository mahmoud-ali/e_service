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

class AppMoveGoldTraditionalDetailInline(admin.TabularInline):
    model = AppMoveGoldTraditionalDetail
    min_num = 1


class AppMoveGoldTraditionalAdmin(LogAdminMixin,admin.ModelAdmin):
    form = AppMoveGoldTraditionalAddForm
    inlines = [AppMoveGoldTraditionalDetailInline]
    change_form_template = "admin/gold_travel_traditional/appmovegoldtraditional/change_form.html"

    fieldsets = [
        (
            None,
            {
                'fields': ["code","issue_date"]
            },
        ),
        (
            _("almustafid data",),
            {
                'fields': [("almustafid_identity",), ("almustafid_name",), ("almustafid_identity_type","almustafid_phone"), ("almustafid_identity_attachement",)]
            },
        ),
        (
            _("others"),
            {
                'fields': [("jihat_alaisdar","wijhat_altarhil",),("attachement_file",)]
            },
        ),
    ]
    readonly_fields = ["code"]

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            fieldsets = list(fieldsets) + [
                (
                    _("مراجع اخرى"),
                    {
                        'fields': [
                            ("renew_date", "parent"),
                            ("arrival_attachement", ),
                            ("arrival_time", "arrival_note",),
                            ("melt_batch", "sale", "storage"),
                        ],
                        'classes': ['collapse'],
                    },
                ),
            ]
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:
            readonly_fields = list(readonly_fields) + [
                "renew_date", "parent", "arrival_attachement", "arrival_time", "arrival_note",
                "melt_batch", "melt_date", "melt_workshop", "standardization_lab",
                "sale", "almushtari_name", "storage"
            ]
        return readonly_fields
    # readonly_fields = ["almushtari_name"]
    list_display = ["code","issue_date","total_gold_weight_display","show_actions","almustafid_name","jihat_alaisdar","wijhat_altarhil","source_state","renew_date","arrival_time","state",]
    list_filter = [("state",admin.ChoicesFieldListFilter),("source_state",RelatedOnlyFieldListFilterNotEmpty),("jihat_alaisdar",RelatedOnlyFieldListFilterNotEmpty),("wijhat_altarhil",RelatedOnlyFieldListFilterNotEmpty), HasPhotoFilter]
    date_hierarchy = "issue_date"
    search_fields = ["code","almustafid_name","almustafid_phone","almustafid_identity","almushtari_name"]
    actions = ['export_as_csv']
    # autocomplete_fields = ["jihat_alaisdar","wijhat_altarhil"]
    # list_editable = ['owner_name_lst']
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    view_on_site = False
    class Media:
        css = {
        "all": ["gold_travel_traditional/css/all.css"],
        }

        js = ["admin/js/jquery.init.js"]

    def save_model(self, request, obj, form, change):
        obj.source_state = get_user_state(request)
        if not obj.pk:
            obj.issue_date = timezone.now().date()
            # Set expiry_days from state config on creation
            config = GoldTravelTraditionalState.objects.filter(state=obj.source_state).first()
            obj.expiry_days = config.expiry_days if config else 3

        photo_data = request.POST.get('almustafid_photo_data', '')
        # print(f"DEBUG save_model: photo_data length = {len(photo_data)}")
        if photo_data:
            import base64
            from django.core.files.base import ContentFile
            fmt, imgstr = photo_data.split(';base64,') if ';base64,' in photo_data else ('', photo_data)
            ext = fmt.split('/')[-1] if '/' in fmt else 'jpg'
            filename = f'photo_{obj.code or "new"}.{ext}'
            # print(f"DEBUG save_model: saving photo as {filename}")
            obj.almustafid_photo.save(
                filename,
                ContentFile(base64.b64decode(imgstr)),
                save=False
            )

        result = super().save_model(request, obj, form, change)

        if not change:
            expired_count = AppMoveGoldTraditional.objects.filter(
                almustafid_identity=obj.almustafid_identity,
                state=AppMoveGoldTraditional.STATE_EXPIRED,
            ).exclude(pk=obj.pk).count()
            if expired_count:
                from urllib.parse import quote
                url = reverse("admin:gold_travel_traditional_appmovegoldtraditional_changelist") + f"?q={quote(obj.almustafid_identity)}&state__exact={AppMoveGoldTraditional.STATE_EXPIRED}"
                self.message_user(
                    request,
                    format_html(
                        '{msg} <a href="{url}" target="_blank">{txt}</a>',
                        msg=_('تنبيه: يوجد %(count)d استمارة منتهية الصلاحية لهذا المستفيد.') % {'count': expired_count},
                        url=url,
                        txt=_('عرض الاستمارات المنتهية'),
                    ),
                    level='warning',
                )

        return result

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists():
            return qs

        try:
            gold_travel_traditional_user = request.user.gold_travel_traditional
            
            if gold_travel_traditional_user.is_state_manager or gold_travel_traditional_user.is_state_viewer:
                return qs.filter(
                    models.Q(jihat_alaisdar__state=gold_travel_traditional_user.state) |
                    models.Q(wijhat_altarhil__state=gold_travel_traditional_user.state)
                )

            filters = models.Q()
            if gold_travel_traditional_user.is_alaisdar_user:
                filters |= models.Q(
                    jihat_alaisdar__in=gold_travel_traditional_user.goldtraveltraditionaluserjihatalaisdar_set.values_list('jihat_alaisdar', flat=True),
                    source_state=gold_travel_traditional_user.state,
                )
            if gold_travel_traditional_user.is_tarhil_user:
                filters |= models.Q(
                    wijhat_altarhil__in=gold_travel_traditional_user.goldtraveltraditionaluserjihattarhil_set.filter(can_arrive=True).values_list('wijhat_altarhil', flat=True),
                )
            if filters:
                qs = qs.filter(filters)
            else:
                qs = qs.none()
        except:
            qs = qs.none()

        return qs

    def get_form(self, request, obj=None, **kwargs):
        my_form = self.form
        my_form.user = request.user
        my_form.allowed_state = get_user_state(request)
        kwargs["form"] = my_form
        return super().get_form(request, obj, **kwargs)

    def has_add_permission(self, request):
        try:
            gold_user = request.user.gold_travel_traditional
            if gold_user.is_state_manager or gold_user.is_state_viewer:
                return False
            if not gold_user.is_alaisdar_user:
                return False
            return True
        except:
            pass
        
        return False

    def has_change_permission(self, request, obj=None):            
        if obj:
            if obj.state != AppMoveGoldTraditional.STATE_NEW:
                return False
            
            try:
                gold_user = request.user.gold_travel_traditional
                if gold_user.is_state_viewer:
                    return False
                if gold_user.is_state_manager:
                    return obj.jihat_alaisdar.state_id == gold_user.state_id
                return False
            except:
                return False
        
        return False

    def has_delete_permission(self, request, obj=None):
        if obj:
            if obj.state != AppMoveGoldTraditional.STATE_NEW:
                return False
            
            if request.user.is_superuser or request.user.groups.filter(name="gold_travel_traditional_manager").exists():
                return True
            
            try:
                gold_user = request.user.gold_travel_traditional
                if gold_user.is_state_viewer:
                    return False
                if gold_user.is_state_manager:
                    return obj.jihat_alaisdar.state_id == gold_user.state_id
                return False
            except:
                return False
        
        return False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("dashboard/", self.admin_site.admin_view(self.dashboard_view)),
            path("<int:pk>/renew/", self.admin_site.admin_view(self.renew_view)),
            path("<int:pk>/arrived/", self.admin_site.admin_view(self.arrived_view)),
            path("<int:pk>/print/", self.admin_site.admin_view(self.print_view)),
            path("<int:pk>/cancel/", self.admin_site.admin_view(self.cancel_view)),
            path("<int:pk>/melt/", self.admin_site.admin_view(self.melt_view)),
            path("<int:pk>/melt/print/", self.admin_site.admin_view(self.print_melt_view)),
            path("<int:pk>/sale/", self.admin_site.admin_view(self.sale_view)),
            path("<int:pk>/sale/print/", self.admin_site.admin_view(self.print_sale_view)),
            path("<int:pk>/storage/", self.admin_site.admin_view(self.storage_view)),
            path("<int:pk>/storage/print/", self.admin_site.admin_view(self.print_storage_view)),
            path("identity-lookup/", self.admin_site.admin_view(self.identity_lookup)),
            path("identity-expired-check/", self.admin_site.admin_view(self.identity_expired_check)),
        ]
        return my_urls + urls

    def dashboard_view(self, request):
        from django.db.models import Sum, Count
        from datetime import date, datetime

        today = date.today()
        first_of_month = today.replace(day=1)

        # Parse date range from GET params, default to current month
        date_from_str = request.GET.get('date_from', '')
        date_to_str = request.GET.get('date_to', '')

        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            date_from = first_of_month

        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            date_to = today

        # Base queryset respecting user permissions, excluding canceled
        qs = self.get_queryset(request).exclude(state=AppMoveGoldTraditional.STATE_CANCLED)

        # Filter by date range
        qs_range = qs.filter(issue_date__range=(date_from, date_to))

        # --- Total gold weight in range ---
        total_weight = qs_range.aggregate(
            total=Sum('details__alloy_weight_gram')
        )['total'] or 0.0

        # --- Application count in range ---
        total_count = qs_range.count()

        # --- Top source states (jihat_alaisdar) ---
        top_sources = qs_range.values(
            'jihat_alaisdar__name', 'jihat_alaisdar__state__name'
        ).annotate(
            total_weight=Sum('details__alloy_weight_gram'),
            record_count=Count('id')
        ).order_by('-total_weight')[:10]

        # --- Top destination states (wijhat_altarhil) ---
        top_destinations = qs_range.values(
            'wijhat_altarhil__name', 'wijhat_altarhil__state__name'
        ).annotate(
            total_weight=Sum('details__alloy_weight_gram'),
            record_count=Count('id')
        ).order_by('-total_weight')[:10]

        # --- Per-state breakdown ---
        state_stats = []
        state_colors = {
            AppMoveGoldTraditional.STATE_NEW: '#417690',
            AppMoveGoldTraditional.STATE_EXPIRED: '#ba2121',
            AppMoveGoldTraditional.STATE_RENEW: '#e0a800',
            AppMoveGoldTraditional.STATE_ARRIVED: '#2d8a4e',
        }
        for state_val, state_label in AppMoveGoldTraditional.STATE_CHOICES.items():
            if state_val == AppMoveGoldTraditional.STATE_CANCLED:
                continue
            sub = qs_range.filter(state=state_val)
            w = sub.aggregate(total=Sum('details__alloy_weight_gram'))['total'] or 0.0
            state_stats.append({
                'label': str(state_label),
                'count': sub.count(),
                'weight': round(w, 2),
                'color': state_colors.get(state_val, '#666'),
            })

        context = dict(
            self.admin_site.each_context(request),
            title=_('Dashboard'),
            total_weight=round(total_weight, 2),
            total_count=total_count,
            top_sources=top_sources,
            top_destinations=top_destinations,
            state_stats=state_stats,
            date_from=date_from.isoformat(),
            date_to=date_to.isoformat(),
            opts=AppMoveGoldTraditional._meta,
        )
        return TemplateResponse(request, "admin/gold_travel_traditional/appmovegoldtraditional/dashboard.html", context)

    def melt_view(self, request, pk):
        obj = AppMoveGoldTraditional.objects.get(pk=pk)

        gold_user = None
        try:
            gold_user = request.user.gold_travel_traditional
        except:
            pass

        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            if not gold_user or not gold_user.is_tarhil_user:
                self.message_user(request, _('Only destination users can fill melt details.'), level='error')
                return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        batch_source_state = gold_user.state if gold_user else obj.source_state

        if obj.state != AppMoveGoldTraditional.STATE_ARRIVED:
            self.message_user(request, _('Record must be in arrived state.'), level='error')
            return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        if request.method == "POST":
            my_form = AppMoveGoldTraditionalMeltForm(request.POST)
            my_form.fields['existing_batch'].queryset = MeltBatch.objects.filter(
                source_state=batch_source_state,
                state=MeltBatch.STATE_PENDING
            )
            if my_form.is_valid():
                choice = my_form.cleaned_data['batch_choice']
                if choice == 'new':
                    batch = MeltBatch.objects.create(
                        melt_date=my_form.cleaned_data['melt_date'],
                        melt_workshop=my_form.cleaned_data['melt_workshop'],
                        standardization_lab=my_form.cleaned_data['standardization_lab'],
                        source_state=batch_source_state,
                        created_by=request.user,
                        updated_by=request.user,
                    )
                    obj.melt_batch = batch
                    obj.melt_date = batch.melt_date
                    obj.melt_workshop = batch.melt_workshop
                    obj.standardization_lab = batch.standardization_lab
                    obj.save()
                    self.log_change(request, obj, _('melt_batch_created'))
                else:
                    batch = my_form.cleaned_data['existing_batch']
                    obj.melt_batch = batch
                    obj.melt_date = batch.melt_date
                    obj.melt_workshop = batch.melt_workshop
                    obj.standardization_lab = batch.standardization_lab
                    obj.save()
                    self.log_change(request, obj, _('melt_batch_assigned'))

                self.message_user(request, _('Melt details saved successfully!'))
                return HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_changelist"
                        % (
                            self.admin_site.name,
                            obj._meta.app_label,
                            obj._meta.model_name,
                        )
                    ) + f"{obj.pk}/melt/print/"
                )
        else:
            my_form = AppMoveGoldTraditionalMeltForm()
            # Filter existing batches by source_state and show only pending ones
            my_form.fields['existing_batch'].queryset = MeltBatch.objects.filter(
                source_state=batch_source_state,
                state=MeltBatch.STATE_PENDING
            )

        context = dict(
            self.admin_site.each_context(request),
            object=obj,
            form=my_form,
            opts=AppMoveGoldTraditional._meta,
            title=_("melt_details"),
        )
        return TemplateResponse(request, "admin/gold_travel_traditional/appmovegoldtraditional/melt_form.html", context)

    def print_melt_view(self, request, pk):
        obj = AppMoveGoldTraditional.objects.get(pk=pk)
        batch = obj.melt_batch
        if not batch:
            self.message_user(request, _('No melt batch found.'), level='error')
            return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                gold_user = request.user.gold_travel_traditional
                if not (gold_user.is_tarhil_user or gold_user.is_state_manager):
                    self.message_user(request, _('Only destination users can print this form.'), level='error')
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                if gold_user.is_state_manager and batch.source_state_id != gold_user.state_id:
                    self.message_user(request, _('You can only print batches from your state.'), level='error')
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
            except:
                return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        from itertools import zip_longest

        records = batch.records.all()

        # Aggregate all alloy details from all records
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

    def sale_view(self, request, pk):
        obj = AppMoveGoldTraditional.objects.get(pk=pk)

        gold_user = None
        try:
            gold_user = request.user.gold_travel_traditional
        except:
            pass

        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            if not gold_user or not gold_user.is_tarhil_user:
                self.message_user(request, _('Only destination users can create sales.'), level='error')
                return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        batch_source_state = gold_user.state if gold_user else obj.source_state

        if obj.state not in [AppMoveGoldTraditional.STATE_ARRIVED]:
            self.message_user(request, _('Record must be in arrived state.'), level='error')
            return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        if request.method == "POST":
            my_form = AppMoveGoldTraditionalSaleForm(request.POST)
            my_form.fields['existing_sale'].queryset = Sale.objects.filter(
                source_state=batch_source_state,
                state=Sale.STATE_PENDING
            )
            my_form.fields['buyer_saig'].queryset = LkpSaig.objects.filter(state_id=obj.source_state_id)
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
                    obj.sale = sale
                    obj.almushtari_name = sale.buyer_display
                    obj.save()
                    self.log_change(request, obj, _('sale_created'))
                else:
                    sale = my_form.cleaned_data['existing_sale']
                    obj.sale = sale
                    obj.almushtari_name = sale.buyer_display
                    obj.save()
                    self.log_change(request, obj, _('sale_assigned'))

                self.message_user(request, _('Sale saved successfully!'))
                return HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_changelist"
                        % (
                            self.admin_site.name,
                            obj._meta.app_label,
                            obj._meta.model_name,
                        )
                    ) + f"{obj.pk}/sale/print/"
                )
        else:
            my_form = AppMoveGoldTraditionalSaleForm()
            my_form.fields['existing_sale'].queryset = Sale.objects.filter(
                source_state=batch_source_state,
                state=Sale.STATE_PENDING
            )
            my_form.fields['buyer_saig'].queryset = LkpSaig.objects.filter(state_id=obj.source_state_id)

        context = dict(
            self.admin_site.each_context(request),
            object=obj,
            form=my_form,
            opts=AppMoveGoldTraditional._meta,
            title=_("sale_details"),
        )
        return TemplateResponse(request, "admin/gold_travel_traditional/appmovegoldtraditional/sale_form.html", context)

    def print_sale_view(self, request, pk):
        obj = AppMoveGoldTraditional.objects.get(pk=pk)
        sale = obj.sale
        if not sale:
            self.message_user(request, _('No sale found.'), level='error')
            return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                gold_user = request.user.gold_travel_traditional
                if not (gold_user.is_tarhil_user or gold_user.is_state_manager):
                    self.message_user(request, _('Only destination users can print this form.'), level='error')
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                if gold_user.is_state_manager and sale.source_state_id != gold_user.state_id:
                    self.message_user(request, _('You can only print sales from your state.'), level='error')
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
            except:
                return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        from itertools import zip_longest

        # Collect details from all sources
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
        obj = AppMoveGoldTraditional.objects.get(pk=pk)

        gold_user = None
        try:
            gold_user = request.user.gold_travel_traditional
        except:
            pass

        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            if not gold_user or not gold_user.is_tarhil_user:
                self.message_user(request, _('Only destination users can create storage receipts.'), level='error')
                return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        batch_source_state = gold_user.state if gold_user else obj.source_state

        if obj.state != AppMoveGoldTraditional.STATE_ARRIVED:
            self.message_user(request, _('Record must be in arrived state.'), level='error')
            return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        if request.method == "POST":
            my_form = AppMoveGoldTraditionalStorageForm(request.POST)
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
                    obj.storage = storage
                    obj.save()
                    self.log_change(request, obj, _('storage_created'))
                else:
                    storage = my_form.cleaned_data['existing_storage']
                    obj.storage = storage
                    obj.save()
                    self.log_change(request, obj, _('storage_assigned'))

                self.message_user(request, _('Storage receipt saved successfully!'))
                return HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_changelist"
                        % (
                            self.admin_site.name,
                            obj._meta.app_label,
                            obj._meta.model_name,
                        )
                    ) + f"{obj.pk}/storage/print/"
                )
        else:
            my_form = AppMoveGoldTraditionalStorageForm()
            my_form.fields['existing_storage'].queryset = Storage.objects.filter(
                source_state=batch_source_state,
                state=Storage.STATE_PENDING
            )

        context = dict(
            self.admin_site.each_context(request),
            object=obj,
            form=my_form,
            opts=AppMoveGoldTraditional._meta,
            title=_("تخزين"),
        )
        return TemplateResponse(request, "admin/gold_travel_traditional/appmovegoldtraditional/storage_form.html", context)

    def print_storage_view(self, request, pk):
        obj = AppMoveGoldTraditional.objects.get(pk=pk)
        storage = obj.storage
        if not storage:
            self.message_user(request, _('No storage receipt found.'), level='error')
            return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                gold_user = request.user.gold_travel_traditional
                if not (gold_user.is_tarhil_user or gold_user.is_state_manager):
                    self.message_user(request, _('Only destination users can print this form.'), level='error')
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                if gold_user.is_state_manager and storage.source_state_id != gold_user.state_id:
                    self.message_user(request, _('You can only print storage receipts from your state.'), level='error')
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
            except:
                return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        from itertools import zip_longest

        # Collect details from all sources
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
    def identity_expired_check(self, request):
        from django.http import JsonResponse

        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                request.user.gold_travel_traditional
            except:
                return JsonResponse({'error': 'Unauthorized'}, status=403)

        identity = request.POST.get('identity', '') or request.GET.get('identity', '')
        if not identity:
            return JsonResponse({'error': 'No identity provided'}, status=400)

        # Normalize Arabic digits (matching model.clean)
        arabic_digits = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
        identity = identity.translate(arabic_digits)

        qs = AppMoveGoldTraditional.objects.filter(
            almustafid_identity=identity,
            state=AppMoveGoldTraditional.STATE_EXPIRED,
        )
        return JsonResponse({
            'expired_count': qs.count(),
            'codes': list(qs.values_list('code', flat=True)[:10]),
        })

    def identity_lookup(self, request):
        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                request.user.gold_travel_traditional
            except:
                from django.http import JsonResponse
                return JsonResponse({'error': 'Unauthorized'}, status=403)

        identity = request.POST.get('identity', '') or request.GET.get('identity', '')
        # print(f"DEBUG identity_lookup: identity={identity}")
        if not identity:
            from django.http import JsonResponse
            return JsonResponse({'error': 'No identity provided'}, status=400)

        import requests
        try:
            resp = requests.post(
                'https://baldna.gov.sd/api/v1/validate/data',
                data={'code': 'CIVIL_ROOT_SYSTEM', 'value': identity},
                auth=(settings.BALDNA_API_USER, settings.BALDNA_API_PASS),
                timeout=60
            )
            # print(f"DEBUG API response: status={resp.status_code}, body={resp.text[:500]}")
            resp.raise_for_status()
            from django.http import JsonResponse
            data = resp.json()
            # print(f"DEBUG API json: {data}")
            return JsonResponse(data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            from django.http import JsonResponse
            return JsonResponse({'error': str(e)}, status=500)




    def cancel_view(self, request, pk):
        obj = AppMoveGoldTraditional.objects.get(pk=pk)

        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                gold_user = request.user.gold_travel_traditional
                if gold_user.is_state_viewer:
                    self.message_user(request, _('Only state managers can cancel records.'), level='error')
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                if gold_user.is_state_manager:
                    if obj.jihat_alaisdar.state_id != gold_user.state_id:
                        self.message_user(request, _('You can only cancel records from your state.'), level='error')
                        return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                else:
                    self.message_user(request, _('Only state managers can cancel records.'), level='error')
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
            except:
                return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        if obj.state not in [AppMoveGoldTraditional.STATE_NEW, AppMoveGoldTraditional.STATE_RENEW, AppMoveGoldTraditional.STATE_EXPIRED]:
            self.message_user(request, _('Only new records can be cancelled.'), level='error')
            return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        if request.method == "POST":
            if obj.state in [AppMoveGoldTraditional.STATE_NEW, AppMoveGoldTraditional.STATE_RENEW, AppMoveGoldTraditional.STATE_EXPIRED]:
                obj.state = AppMoveGoldTraditional.STATE_CANCLED
                obj.updated_by = request.user
                obj.save()
                self.log_change(request, obj, _('state_cancled'))
                self.message_user(request, _('application cancelled successfully!'))
            
            return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        context = dict(
            self.admin_site.each_context(request),
            object=obj,
            opts=AppMoveGoldTraditional._meta,
            title=_('تأكيد الإلغاء'),
        )
        return TemplateResponse(request, "admin/gold_travel_traditional/appmovegoldtraditional/cancel_confirm.html", context)

    def print_view(self, request, pk):
        from gold_travel_traditional.models import AppMoveGoldTraditional
        obj = AppMoveGoldTraditional.objects.get(pk=pk)

        # Permission check: Alaisdar user or superuser
        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                gold_user = request.user.gold_travel_traditional
                if gold_user.is_state_viewer:
                    self.message_user(request, _('Only users from the issuing location can print this report.'), level='error')
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                if gold_user.is_state_manager:
                    if obj.jihat_alaisdar.state_id != gold_user.state_id:
                        self.message_user(request, _('Only users from the issuing location can print this report.'), level='error')
                        return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                elif gold_user.is_alaisdar_user:
                    allowed_alaisdar = gold_user.goldtraveltraditionaluserjihatalaisdar_set.values_list('jihat_alaisdar', flat=True)
                    if obj.jihat_alaisdar_id not in allowed_alaisdar:
                        self.message_user(request, _('Only users from the issuing location can print this report.'), level='error')
                        return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                else:
                    self.message_user(request, _('Only users from the issuing location can print this report.'), level='error')
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
            except:
                return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        # Prepare alloy chunks for the template
        details = list(obj.details.all())
        chunk_size = 40
        alloy_chunks = []
        for i in range(0, len(details), chunk_size):
            chunk = details[i:i + chunk_size]
            half = (len(chunk) + 1) // 2
            left_half = chunk[:half]
            right_half = chunk[half:]
            # Zip them together for the template, padding with None if necessary
            from itertools import zip_longest
            rows = list(zip_longest(left_half, right_half))
            alloy_chunks.append({
                'rows': rows,
                'start_index': i + 1,
                'half_offset': half
            })

        # Fetch state expiry config
        expiry_days = obj.expiry_days

        context = {
            'object': obj,
            'alloy_chunks': alloy_chunks,
            'expiry_hours': expiry_days * 24,
            'has_astikhbarat': False, 
        }
        return TemplateResponse(request, "gold_travel_traditional/gold_travel_traditional.html", context)
    
    def arrived_view(self, request, pk):
        obj = AppMoveGoldTraditional.objects.get(pk=pk)

        gold_user = None
        try:
            gold_user = request.user.gold_travel_traditional
        except:
            pass

        # Check if user has permission for this destination
        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                if not gold_user:
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                if gold_user.is_state_viewer:
                    self.message_user(request, _('Only users assigned to the destination location can mark this as arrived.'), level='error')
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                elif gold_user.is_state_manager:
                    if obj.wijhat_altarhil.state_id != gold_user.state_id:
                        self.message_user(request, _('You can only mark records arriving in your state.'), level='error')
                        return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                elif gold_user.is_tarhil_user:
                    if not gold_user.goldtraveltraditionaluserjihattarhil_set.filter(wijhat_altarhil=obj.wijhat_altarhil, can_arrive=True).exists():
                        self.message_user(request, _('Only users assigned to the destination location can mark this as arrived.'), level='error')
                        return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                else:
                    self.message_user(request, _('Only users assigned to the destination location can mark this as arrived.'), level='error')
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
            except:
                 return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        if obj.state not in [AppMoveGoldTraditional.STATE_NEW, AppMoveGoldTraditional.STATE_RENEW, AppMoveGoldTraditional.STATE_EXPIRED]:
            self.message_user(request, _('Record cannot be marked as arrived in its current state.'), level='error')
            return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        is_state_mgr = gold_user.is_state_manager if gold_user else False
        if request.method == "POST":
            my_form = AppMoveGoldTraditionalArriveForm(request.POST, request.FILES, instance=obj)
            if is_state_mgr:
                my_form.fields['arrival_note'].required = True
            if my_form.is_valid():
                if not request.FILES.get('arrival_attachement'):
                    my_form.add_error('arrival_attachement', _('Attachment is required.'))
                else:
                    obj.state = AppMoveGoldTraditional.STATE_ARRIVED
                    obj.arrival_time = timezone.now()
                    obj.updated_by = request.user
                    my_form.save()
                    self.log_change(request, obj, _('state_arrived'))
                    self.message_user(request, _('application marked as arrived successfully!'))
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
        else:
            my_form = AppMoveGoldTraditionalArriveForm(instance=obj)
            if is_state_mgr:
                my_form.fields['arrival_note'].required = True

        context = dict(
            self.admin_site.each_context(request),
            object=obj,
            form=my_form,
            opts=AppMoveGoldTraditional._meta,
            title=_('توصيل'),
        )
        return TemplateResponse(request, "admin/gold_travel_traditional/appmovegoldtraditional/arrive_form.html", context)
    
    def renew_view(self, request, pk):
        obj = AppMoveGoldTraditional.objects.get(pk=pk)

        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                gold_user = request.user.gold_travel_traditional
                if gold_user.is_state_viewer:
                    self.message_user(request, _('Only state managers can renew records.'), level='error')
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                if gold_user.is_state_manager:
                    if obj.jihat_alaisdar.state_id != gold_user.state_id:
                        self.message_user(request, _('You can only renew records from your state.'), level='error')
                        return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                elif gold_user.is_alaisdar_user:
                    allowed = gold_user.goldtraveltraditionaluserjihatalaisdar_set.values_list('jihat_alaisdar', flat=True)
                    if obj.jihat_alaisdar_id not in allowed:
                        self.message_user(request, _('You can only renew records from your issuing location.'), level='error')
                        return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                else:
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
            except:
                return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        if request.method == "POST":
            my_form = AppMoveGoldTraditionalRenewForm(request.POST)

            if my_form.is_valid():
                if obj.state == AppMoveGoldTraditional.STATE_EXPIRED:
                    obj.state = AppMoveGoldTraditional.STATE_RENEW
                    obj.renew_date = my_form.cleaned_data['renew_date']
                    obj.save()
                    self.log_change(request, obj, _('state_renew'))
                    self.message_user(request, _('application changed successfully!'))

                return HttpResponseRedirect(
                    reverse(
                        "%s:%s_%s_changelist"
                        % (
                            self.admin_site.name,
                            obj._meta.app_label,
                            obj._meta.model_name,
                        )
                    )
                )
        else:
            my_form = AppMoveGoldTraditionalRenewForm(initial={'renew_date': timezone.now().date()})

        context = dict(
            self.admin_site.each_context(request),
            object=obj,
            form=my_form,
            opts=AppMoveGoldTraditional._meta,
            title=_("renew_data"),
            add=False,
            change=True,
            is_popup=False,
            save_as=False,
            show_save=True,
            has_add_permission=False,
            has_change_permission=True,
            has_delete_permission=False,
            has_view_permission=True,
            has_editable_inline_admin_formsets=False,
        )
        return TemplateResponse(request, "admin/gold_travel_traditional/appmovegoldtraditional/renew_application.html", context)

    @admin.display(description=_('gold_weight_in_gram'))
    def total_gold_weight_display(self, obj):
        return round(obj.gold_weight_in_gram, 2) if obj.gold_weight_in_gram else 0.0

    @admin.display(description=_('parent'))
    def parent_link(self,obj):
        if obj.parent:
            url = reverse("admin:gold_travel_traditional_appmovegoldtraditional_change", args=(obj.parent.id,))
            return format_html('<a href="{url}">{txt}</a>',url=url,txt=obj.parent.code)
        
        return '-'
    
    @admin.display(description=_('show_actions'))
    def show_actions(self, obj):
        request = self.current_request
        is_manager = request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()

        def get_allowed_actions(obj):
            actions = []
            
            is_alaisdar_user = False
            is_altarhil_user = False
            is_state_manager = False
            is_state_viewer = False
            can_manage = False
            can_manage_dest = False
            try:
                gold_user = request.user.gold_travel_traditional
                if gold_user.is_state_viewer:
                    return format_html('<ul class="actions-list"><li>&nbsp;</li></ul>')
                is_alaisdar_user = gold_user.is_alaisdar_user
                is_altarhil_user = gold_user.is_tarhil_user
                is_state_manager = gold_user.is_state_manager
                can_manage = is_state_manager and obj.jihat_alaisdar.state_id == gold_user.state_id
                can_manage_dest = is_state_manager and obj.wijhat_altarhil.state_id == gold_user.state_id
            except:
                pass

            # Action for Alaisdar users (Renew)
            if obj.state in [AppMoveGoldTraditional.STATE_EXPIRED]:
                if is_alaisdar_user or is_manager or can_manage:
                    actions.append(f'<li><a class="changelink" href="{obj.pk}/renew">{_("state_renew")}</a></li>')                            
            
            # Action for Alaisdar users / State Manager (Print)
            if obj.state in [AppMoveGoldTraditional.STATE_NEW, AppMoveGoldTraditional.STATE_RENEW, ]:
                if is_alaisdar_user or is_manager or can_manage:
                    actions.append(f'<li><a class="changelink" target="_blank" href="{obj.pk}/print">{_("طباعة استمارة ترحيل")}</a></li>')

            # Action for Altarhil users / Destination State Manager (Arrived)
            if obj.state in [AppMoveGoldTraditional.STATE_NEW, AppMoveGoldTraditional.STATE_RENEW, AppMoveGoldTraditional.STATE_EXPIRED, ]:            
                if is_altarhil_user or is_manager or can_manage_dest:
                    try:
                        gold_user = request.user.gold_travel_traditional
                        if is_manager or can_manage_dest or gold_user.goldtraveltraditionaluserjihattarhil_set.filter(wijhat_altarhil=obj.wijhat_altarhil, can_arrive=True).exists():
                            actions.append(f'<li><a class="changelink" href="{obj.pk}/arrived">{_("وصل")}</a></li>')
                    except:
                        pass

            # Action for Altarhil users (Melt) - only on ARRIVED records
            if obj.state == AppMoveGoldTraditional.STATE_ARRIVED:
                if not obj.melt_batch and not obj.sale and not obj.storage and (is_altarhil_user or is_manager):
                    actions.append(f'<li><a class="changelink" href="{obj.pk}/melt">{_("استمارة التسييح والمعايرة")}</a></li>')
                if obj.melt_batch:
                    if is_altarhil_user or is_manager or can_manage_dest:
                        actions.append(f'<li><a class="changelink" target="_blank" href="{obj.pk}/melt/print">{_("طباعة استمارة تسييح ومعاييرة")}</a></li>')
                if not obj.sale and (is_altarhil_user or is_manager):
                    actions.append(f'<li><a class="changelink" href="{obj.pk}/sale">{_("بيع")}</a></li>')
                if obj.sale and (is_altarhil_user or is_manager or can_manage_dest):
                    actions.append(f'<li><a class="changelink" target="_blank" href="{obj.pk}/sale/print">{_("طباعة استمارة بيع")}</a></li>')
                if not obj.storage and (is_altarhil_user or is_manager):
                    actions.append(f'<li><a class="changelink" href="{obj.pk}/storage">{_("تخزين")}</a></li>')
                if obj.storage and (is_altarhil_user or is_manager or can_manage_dest):
                    actions.append(f'<li><a class="changelink" target="_blank" href="{obj.pk}/storage/print">{_("طباعة شهادة تخزين")}</a></li>')

            # Action for State Manager (Cancel) - only on NEW records
            if obj.state in [AppMoveGoldTraditional.STATE_NEW, AppMoveGoldTraditional.STATE_RENEW, AppMoveGoldTraditional.STATE_EXPIRED, ]:
                if can_manage or is_manager:
                    actions.append(f'<li><a class="changelink" href="{obj.pk}/cancel">{_("إلغاء")}</a></li>')

            if not actions:
                return format_html('<ul class="actions-list"><li>&nbsp;</li></ul>')
            
            return format_html('<ul class="actions-list">{links}</ul>', links=format_html(''.join(actions)))

        return get_allowed_actions(obj)

    def changelist_view(self, request, extra_context=None):
        self.current_request = request
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description=_('Export data'))
    def export_as_csv(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="move_gold_form.csv"'},
        )
        header = [
                    _("code"),_("issue_date"),_("renew_date"),_('gold_weight_in_gram'),_("almustafid_name"),_("almustafid_phone"),
                    _("almustafid_identity_type"), _("almustafid_identity"), _( "jihat_alaisdar"),
                    _("wijhat_altarhil"),_("almushtari_name"),_("source_state"),_("record_state"),_("parent"),
                    _("created_at"),_("created_by"),_("updated_at"),_("updated_by")
        ]

        # BOM
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        writer.writerow(header)

        for app in queryset:
            parent_code = None
            if hasattr(app,'parent') and app.parent:
                parent_code = app.parent.code

            row = [
                    app.code,app.issue_date,app.renew_date,app.gold_weight_in_gram,app.almustafid_name,app.almustafid_phone,
                    app.get_almustafid_identity_type_display(), app.almustafid_identity, app.jihat_alaisdar,
                    app.wijhat_altarhil,app.almushtari_name,app.source_state,app.get_state_display(),parent_code,
                    app.created_at,app.created_by,app.updated_at,app.updated_by,
            ]
            writer.writerow(row)

        return response

admin.site.register(AppMoveGoldTraditional, AppMoveGoldTraditionalAdmin)

