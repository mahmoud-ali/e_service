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
from gold_travel_traditional.forms import AppMoveGoldTraditionalAddForm, AppMoveGoldTraditionalArriveForm, AppMoveGoldTraditionalMeltForm, AppMoveGoldTraditionalRenewForm, AppMoveGoldTraditionalSaleForm, AppMoveGoldTraditionalStorageForm, GoldTravelTraditionalUserJihatAlaisdarForm, GoldTravelTraditionalUserJihatTarhilForm, GoldTravelTraditionalUserForm
from gold_travel_traditional.models import AppMoveGoldTraditional, AppMoveGoldTraditionalDetail, GoldTravelTraditionalState, GoldTravelTraditionalUser, GoldTravelTraditionalUserJihatAlaisdar, GoldTravelTraditionalUserJihatTarhil, LkpJihatAlaisdar, LkpJihatAltarhil, LkpSaig, MeltBatch, Sale, Storage

def get_user_state(request):
    try:
        state = request.user.gold_travel_traditional.state
        return state  
    except:
        pass

    return None

class LogAdminMixin:
    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        return super().save_model(request, obj, form, change)                

class LkpJihatAltarhilAdmin(admin.ModelAdmin):
    model = LkpJihatAltarhil
    list_display = ["state","name"]
    list_filter = ["state"]
    search_fields = ["name"]

admin.site.register(LkpJihatAltarhil, LkpJihatAltarhilAdmin)

class LkpJihatAlaisdarAdmin(admin.ModelAdmin):
    model = LkpJihatAlaisdar
    list_display = ["state","name"]
    list_filter = ["state"]
    search_fields = ["name"]

admin.site.register(LkpJihatAlaisdar, LkpJihatAlaisdarAdmin)

class LkpSaigAdmin(admin.ModelAdmin):
    list_display = ["state", "name", "code"]
    list_filter = ["state"]
    search_fields = ["name", "code"]

admin.site.register(LkpSaig, LkpSaigAdmin)

class GoldTravelTraditionalUserJihatAlaisdarInline(admin.TabularInline):
    model = GoldTravelTraditionalUserJihatAlaisdar
    form = GoldTravelTraditionalUserJihatAlaisdarForm
    extra = 1

class GoldTravelTraditionalUserJihatTarhilInline(admin.TabularInline):
    model = GoldTravelTraditionalUserJihatTarhil
    form = GoldTravelTraditionalUserJihatTarhilForm
    fields = ["wijhat_altarhil", "can_arrive"]
    extra = 1

class GoldTravelTraditionalUserAdmin(LogAdminMixin,admin.ModelAdmin):
    form = GoldTravelTraditionalUserForm
    inlines = [GoldTravelTraditionalUserJihatAlaisdarInline, GoldTravelTraditionalUserJihatTarhilInline]     
    list_display = ["name","state","user_type"]
    list_filter = ["state","user_type"]

    fields = ["user","name","state","user_type"]

    def get_readonly_fields(self,request, obj=None):
        if obj:
            return ["user","name","state"]
        
        return super().get_readonly_fields(request,obj)
    
    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            formset = inline.get_formset(request, obj)
            if not obj:
                return formset, None

            if isinstance(inline, GoldTravelTraditionalUserJihatAlaisdarInline):
                formset.form = GoldTravelTraditionalUserJihatAlaisdarForm
                if obj:
                    formset.form.allowed_state = obj.state
            elif isinstance(inline, GoldTravelTraditionalUserJihatTarhilInline):
                formset.form = GoldTravelTraditionalUserJihatTarhilForm
                if obj:
                    formset.form.allowed_state = obj.state
            yield formset,inline

admin.site.register(GoldTravelTraditionalUser, GoldTravelTraditionalUserAdmin)

class AppMoveGoldTraditionalDetailInline(admin.TabularInline):
    model = AppMoveGoldTraditionalDetail
    min_num = 1

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


class HasPhotoFilter(admin.SimpleListFilter):
    title = _('صورة المستفيد')
    parameter_name = 'has_photo'

    def lookups(self, request, model_admin):
        return [
            ('yes', _('يوجد صورة')),
            ('no', _('لا يوجد صورة')),
        ]

    def queryset(self, request, queryset):
        from django.db.models import Q
        if self.value() == 'yes':
            return queryset.exclude(Q(almustafid_photo__isnull=True) | Q(almustafid_photo=''))
        if self.value() == 'no':
            return queryset.filter(Q(almustafid_photo__isnull=True) | Q(almustafid_photo=''))
        return queryset


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
                            ("arrival_attachement",),
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
                "renew_date", "parent", "arrival_attachement",
                "melt_batch", "melt_date", "melt_workshop", "standardization_lab",
                "sale", "almushtari_name", "storage"
            ]
        return readonly_fields
    # readonly_fields = ["almushtari_name"]
    list_display = ["code","issue_date","total_gold_weight_display","show_actions","almustafid_name","jihat_alaisdar","wijhat_altarhil","source_state","renew_date","state",]
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

        return super().save_model(request, obj, form, change)                

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
        ]
        return my_urls + urls

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

        records = sale.records.all()
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

        records = storage.records.all()
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
            'storage': storage,
            'records': records,
            'alloy_chunks': alloy_chunks,
        }
        return TemplateResponse(request, "gold_travel_traditional/gold_travel_traditional_storage.html", context)
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

        if request.method == "POST":
            if obj.state not in [AppMoveGoldTraditional.STATE_CANCLED] and not obj.sale and not obj.storage:
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
        
        # Check if user has permission for this destination
        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                gold_user = request.user.gold_travel_traditional
                if gold_user.is_state_viewer:
                     self.message_user(request, _('Only users assigned to the destination location can mark this as arrived.'), level='error')
                     return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                if not gold_user.is_tarhil_user:
                     self.message_user(request, _('Only users assigned to the destination location can mark this as arrived.'), level='error')
                     return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
                if not gold_user.goldtraveltraditionaluserjihattarhil_set.filter(wijhat_altarhil=obj.wijhat_altarhil, can_arrive=True).exists():
                     self.message_user(request, _('Only users assigned to the destination location can mark this as arrived.'), level='error')
                     return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
            except:
                 return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        if obj.state not in [AppMoveGoldTraditional.STATE_NEW, AppMoveGoldTraditional.STATE_RENEW, AppMoveGoldTraditional.STATE_EXPIRED]:
            self.message_user(request, _('Record cannot be marked as arrived in its current state.'), level='error')
            return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")

        if request.method == "POST":
            my_form = AppMoveGoldTraditionalArriveForm(request.POST, request.FILES, instance=obj)
            if my_form.is_valid():
                if not request.FILES.get('arrival_attachement'):
                    my_form.add_error('arrival_attachement', _('Attachment is required.'))
                else:
                    obj.state = AppMoveGoldTraditional.STATE_ARRIVED
                    obj.updated_by = request.user
                    my_form.save()
                    self.log_change(request, obj, _('state_arrived'))
                    self.message_user(request, _('application marked as arrived successfully!'))
                    return redirect("admin:gold_travel_traditional_appmovegoldtraditional_changelist")
        else:
            my_form = AppMoveGoldTraditionalArriveForm(instance=obj)

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

            # Action for Altarhil users (Arrived)
            if obj.state in [AppMoveGoldTraditional.STATE_NEW, AppMoveGoldTraditional.STATE_RENEW, AppMoveGoldTraditional.STATE_EXPIRED, ]:            
                if is_altarhil_user or is_manager:
                    try:
                        gold_user = request.user.gold_travel_traditional
                        if is_manager or gold_user.goldtraveltraditionaluserjihattarhil_set.filter(wijhat_altarhil=obj.wijhat_altarhil, can_arrive=True).exists():
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

            # Action for State Manager (Cancel)
            if obj.state != AppMoveGoldTraditional.STATE_CANCLED and not obj.sale and not obj.storage:
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

class MeltBatchRecordsInline(admin.TabularInline):
    model = AppMoveGoldTraditional
    fields = ['code', 'almustafid_name', 'jihat_alaisdar', 'gold_weight_in_gram']
    readonly_fields = ['code', 'almustafid_name', 'jihat_alaisdar', 'gold_weight_in_gram']
    can_delete = False
    extra = 0
    max_num = 0

    def has_add_permission(self, request, obj):
        return False

class MeltBatchAdmin(LogAdminMixin, admin.ModelAdmin):
    inlines = [MeltBatchRecordsInline]
    list_display = ['code', 'melt_date', 'melt_workshop', 'standardization_lab', 'record_count', 'total_weight_display', 'state', 'print_button', 'complete_button']
    list_filter = ['melt_date', 'state']
    search_fields = ['code', 'melt_workshop', 'standardization_lab']
    readonly_fields = ['code']
    actions = ['mark_complete', 'print_selected_batches']

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.state == MeltBatch.STATE_COMPLETE:
            readonly_fields = list(set(readonly_fields + [
                'melt_date', 'melt_workshop', 'standardization_lab', 'state'
            ]))
        return readonly_fields

    fieldsets = [
        (None, {'fields': ['code', 'melt_date']}),
        (_('melt_details'), {'fields': [('melt_workshop', 'standardization_lab')]}),
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
                return qs.filter(source_state=gold_user.state, state=MeltBatch.STATE_PENDING)
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

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("<int:pk>/batch-print/", self.admin_site.admin_view(self.batch_print_view), name="gold_travel_traditional_meltbatch_print"),
            path("<int:pk>/complete/", self.admin_site.admin_view(self.complete_view)),
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
            batch.state = MeltBatch.STATE_COMPLETE
            batch.updated_by = request.user
            batch.save()
            self.message_user(request, _('Batch marked as complete.'))
        return redirect(reverse("admin:gold_travel_traditional_meltbatch_changelist"))

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
        queryset.filter(state=MeltBatch.STATE_PENDING).update(state=MeltBatch.STATE_COMPLETE, updated_by=request.user)
        self.message_user(request, _('Selected batches marked as complete.'))

    @admin.action(description=_('طباعة الاستمارات المحددة'))
    def print_selected_batches(self, request, queryset):
        # Redirect to print the first selected batch
        batch = queryset.first()
        if batch:
            return redirect(reverse("admin:gold_travel_traditional_meltbatch_print", args=[batch.pk]))

admin.site.register(MeltBatch, MeltBatchAdmin)

class SaleRecordsInline(admin.TabularInline):
    model = AppMoveGoldTraditional
    fields = ['code', 'almustafid_name', 'gold_weight_in_gram']
    readonly_fields = ['code', 'almustafid_name', 'gold_weight_in_gram']
    can_delete = False
    extra = 0
    max_num = 0

    def has_add_permission(self, request, obj):
        return False

class SaleAdmin(LogAdminMixin, admin.ModelAdmin):
    inlines = [SaleRecordsInline]
    list_display = ['code', 'sale_date', 'buyer_display', 'record_count', 'total_weight_display', 'state', 'print_button', 'complete_button']
    list_filter = ['sale_date', 'state']
    search_fields = ['code', 'buyer_exporter__name', 'buyer_saig__name']
    readonly_fields = ['code']
    actions = ['mark_complete']

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.state == Sale.STATE_COMPLETE:
            readonly_fields = list(set(readonly_fields + [
                'sale_date', 'buyer_type', 'buyer_exporter', 'buyer_saig', 'state'
            ]))
        return readonly_fields

    fieldsets = [
        (None, {'fields': ['code', 'sale_date']}),
        (_('sale_details'), {'fields': [('buyer_type',), ('buyer_exporter', 'buyer_saig')]}),
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

admin.site.register(Sale, SaleAdmin)

class StorageRecordsInline(admin.TabularInline):
    model = AppMoveGoldTraditional
    fields = ['code', 'almustafid_name', 'gold_weight_in_gram']
    readonly_fields = ['code', 'almustafid_name', 'gold_weight_in_gram']
    can_delete = False
    extra = 0
    max_num = 0

    def has_add_permission(self, request, obj):
        return False

class StorageAdmin(LogAdminMixin, admin.ModelAdmin):
    inlines = [StorageRecordsInline]
    list_display = ['code', 'storage_date', 'expiry_date', 'note', 'record_count', 'total_weight', 'state', 'print_button', 'complete_button']
    list_filter = ['storage_date', 'state']
    search_fields = ['code', 'note']
    readonly_fields = ['code']
    actions = ['mark_complete']

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.state == Storage.STATE_COMPLETE:
            readonly_fields = list(set(readonly_fields + [
                'storage_date', 'note', 'state'
            ]))
        return readonly_fields

    fieldsets = [
        (None, {'fields': ['code', 'storage_date']}),
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
                return qs.filter(source_state=gold_user.state, state=Storage.STATE_PENDING)
            return qs.none()
        except:
            return qs.none()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists():
            return True
        if obj and obj.state == Storage.STATE_COMPLETE:
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

    @admin.display(description=_('expiry_date'))
    def expiry_date(self, obj):
        return obj.expiry_date

    def changelist_view(self, request, extra_context=None):
        self.current_request = request
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description=_('print'))
    def print_button(self, obj):
        if not self.has_change_permission(self.current_request, obj):
            return '-'
        record = obj.records.first()
        if record:
            url = reverse("admin:gold_travel_traditional_appmovegoldtraditional_changelist") + f"{record.pk}/storage/print/"
            return format_html('<a class="changelink" target="_blank" href="{url}">{txt}</a>', url=url, txt=_('طباعة'))
        return '-'

    @admin.display(description=_('complete'))
    def complete_button(self, obj):
        if not self.has_change_permission(self.current_request, obj):
            return '-'
        if obj.state == Storage.STATE_PENDING:
            url = reverse("admin:gold_travel_traditional_storage_changelist") + f"{obj.pk}/complete/"
            return format_html('<a class="changelink" href="{url}">{txt}</a>', url=url, txt=_('إكمال'))
        return '-'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("<int:pk>/complete/", self.admin_site.admin_view(self.complete_view)),
        ]
        return my_urls + urls

    def complete_view(self, request, pk):
        storage = Storage.objects.get(pk=pk)
        if not (request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists()):
            try:
                gold_user = request.user.gold_travel_traditional
                if gold_user.user_type not in [GoldTravelTraditionalUser.JIHAT_TARHIL, GoldTravelTraditionalUser.BOTH, GoldTravelTraditionalUser.STATE_MANAGER]:
                    self.message_user(request, _('You do not have permission to complete storage receipts.'), level='error')
                    return redirect(reverse("admin:gold_travel_traditional_storage_changelist"))
                if gold_user.is_state_manager and storage.source_state_id != gold_user.state_id:
                    self.message_user(request, _('You can only complete storage receipts from your state.'), level='error')
                    return redirect(reverse("admin:gold_travel_traditional_storage_changelist"))
            except:
                self.message_user(request, _('You do not have permission to complete storage receipts.'), level='error')
                return redirect(reverse("admin:gold_travel_traditional_storage_changelist"))
        if storage.state == Storage.STATE_PENDING:
            storage.state = Storage.STATE_COMPLETE
            storage.updated_by = request.user
            storage.save()
            self.message_user(request, _('Storage marked as complete.'))
        return redirect(reverse("admin:gold_travel_traditional_storage_changelist"))

    @admin.action(description=_('Mark as Complete'))
    def mark_complete(self, request, queryset):
        queryset.filter(state=Storage.STATE_PENDING).update(state=Storage.STATE_COMPLETE, updated_by=request.user)
        self.message_user(request, _('Selected storage receipts marked as complete.'))

admin.site.register(Storage, StorageAdmin)

class GoldTravelTraditionalStateAdmin(admin.ModelAdmin):
    list_display = ['state', 'expiry_days']
    search_fields = ['state__name']

admin.site.register(GoldTravelTraditionalState, GoldTravelTraditionalStateAdmin)
