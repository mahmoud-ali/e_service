import datetime
import codecs
import csv
from django.http import HttpRequest, HttpResponse
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.db import models
from django.forms.widgets import TextInput
from gold_travel.forms import TblStateRepresentativeForm
from gold_travel.models import AppPrepareGold, LkpOwner, LkpStateDetails, TblStateRepresentative,AppMoveGold, AppMoveGoldDetails

class LogAdminMixin:
    def has_add_permission(self, request):
        try:
            if request.user.state_representative.authority==TblStateRepresentative.AUTHORITY_SMRC:
                return super().has_add_permission(request)
        except:
            pass
        
        return False

    def has_change_permission(self, request, obj=None):
        # if request.user.is_superuser:
        #     return True
        
        try:
            if request.user.state_representative.authority==TblStateRepresentative.AUTHORITY_SMRC:
                if not obj or obj.state==1:
                    return super().has_change_permission(request,obj)
        except:
            pass
        
        return False

    def has_delete_permission(self, request, obj=None):
        try:
            if request.user.state_representative.authority==TblStateRepresentative.AUTHORITY_SMRC:
                if not obj or obj.state==1:
                    return super().has_delete_permission(request,obj)
        except:
            pass
     
        return False

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

class LkpStateDetailsAdmin(admin.ModelAdmin):
    model = LkpStateDetails
    list_display = ["state","code","next_serial_no","has_2lestikhbarat_2l3askria"]
    list_filter = ["state","has_2lestikhbarat_2l3askria"]

admin.site.register(LkpStateDetails, LkpStateDetailsAdmin)

class LkpOwnerAdmin(admin.ModelAdmin):
    model = LkpOwner
    list_display = ["name"]
    # list_filter = ["name"]
    search_fields = ["name"]

admin.site.register(LkpOwner, LkpOwnerAdmin)

class TblStateRepresentativeAdmin(admin.ModelAdmin):
    model = TblStateRepresentative
    form = TblStateRepresentativeForm
    list_display = ["name","state","authority","user"]        
    list_filter = ["authority",("state",admin.RelatedOnlyFieldListFilter)]
    view_on_site = False
            
admin.site.register(TblStateRepresentative, TblStateRepresentativeAdmin)

class AppMoveGoldDetailInline(admin.TabularInline):
    model = AppMoveGoldDetails
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

class DateFieldListFilterWithLast30days(admin.DateFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        now = timezone.now()
        # When time zone support is enabled, convert "now" to the user's time
        # zone so Django's definition of "Today" matches what the user expects.
        if timezone.is_aware(now):
            now = timezone.localtime(now)

        if isinstance(field, models.DateTimeField):
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # field is a models.DateField
            today = now.date()
        tomorrow = today + datetime.timedelta(days=1)

        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)

        if today.month == 1:
            last_month = today.replace(year=today.year - 1, month=12, day=1)
        else:
            last_month = today.replace(month=today.month - 1, day=1)

        next_year = today.replace(year=today.year + 1, month=1, day=1)
        last_year = today.replace(year=today.year - 1, month=1, day=1)

        self.lookup_kwarg_since = "%s__gte" % field_path
        self.lookup_kwarg_until = "%s__lt" % field_path

        self.links = (
            (_("Any date"), {}),
            (
                _("Today"),
                {
                    self.lookup_kwarg_since: today,
                    self.lookup_kwarg_until: tomorrow,
                },
            ),
            (
                _("Past 7 days"),
                {
                    self.lookup_kwarg_since: today - datetime.timedelta(days=7),
                    self.lookup_kwarg_until: tomorrow,
                },
            ),
            (
                _("Past 30 days"),
                {
                    self.lookup_kwarg_since: today - datetime.timedelta(days=30),
                    self.lookup_kwarg_until: tomorrow,
                },
            ),
            (
                _("This month"),
                {
                    self.lookup_kwarg_since: today.replace(day=1),
                    self.lookup_kwarg_until: next_month,
                },
            ),
            (
                _("Last month"),
                {
                    self.lookup_kwarg_since: last_month,
                    self.lookup_kwarg_until: today.replace(day=1),
                },
            ),
            (
                _("This year"),
                {
                    self.lookup_kwarg_since: today.replace(month=1, day=1),
                    self.lookup_kwarg_until: next_year,
                },
            ),
            (
                _("Last year"),
                {
                    self.lookup_kwarg_since: last_year,
                    self.lookup_kwarg_until: today.replace(month=1, day=1),
                },
            ),
        )

class ChoicesFieldListFilterNotEmpty(admin.ChoicesFieldListFilter):
    def choices(self, changelist):
        add_facets = changelist.add_facets
        facet_counts = self.get_facet_queryset(changelist)
        yield {
            "selected": self.lookup_val is None,
            "query_string": changelist.get_query_string(
                remove=[self.lookup_kwarg, self.lookup_kwarg_isnull]
            ),
            "display": _("All"),
        }
        none_title = ""
        for i, (lookup, title) in enumerate(self.field.flatchoices):
            count = facet_counts[f"{i}__c"]
            if count == 0:
                continue
            if add_facets:
                title = f"{title} ({count})"
            if lookup is None:
                none_title = title
                continue
            yield {
                "selected": self.lookup_val is not None
                and str(lookup) in self.lookup_val,
                "query_string": changelist.get_query_string(
                    {self.lookup_kwarg: lookup}, [self.lookup_kwarg_isnull]
                ),
                "display": title,
            }
        if none_title:
            yield {
                "selected": bool(self.lookup_val_isnull),
                "query_string": changelist.get_query_string(
                    {self.lookup_kwarg_isnull: "True"}, [self.lookup_kwarg]
                ),
                "display": none_title,
            }

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

class AppMoveGoldAdmin(LogAdminMixin,admin.ModelAdmin):
    model = AppMoveGold
    inlines = [AppMoveGoldDetailInline]     

    fieldsets = [
        (
            None,
            {
                'fields': ["date","destination"]
            },
        ),
        (
            _("owner data"),
            {
                'fields': ["owner_name_lst","owner_address"]
            },
        ),
        (
            _("representative data"),
            {
                'fields': [("repr_name","repr_phone"),"repr_address",("repr_identity_type","repr_identity","repr_identity_issue_date")]
            },
        ),
        # (
        #     _("gold data"),
        #     {
        #         'fields': [("gold_weight_in_gram","gold_alloy_count"),"gold_description"]
        #     },
        # ),
        (
            _("attachments"),
            {
                'fields': ["attachement_file"]
            },
        ),
    ]
    list_filter = [("date",DateFieldListFilterWithLast30days),("state",ChoicesFieldListFilterNotEmpty),("source_state",RelatedOnlyFieldListFilterNotEmpty),("owner_name_lst",RelatedOnlyFieldListFilterNotEmpty)]
    search_fields = ["code","owner_name_lst__name","owner_address","repr_name","repr_phone","repr_identity"]
    actions = ['confirm_app','arrived_to_ssmo_app','cancel_app','export_as_csv']
    autocomplete_fields = ["owner_name_lst"]
    list_display = ["code","date","owner_name_lst","gold_weight_in_gram","gold_alloy_count","state_str","source_state","repr_name"]
    # list_editable = ['owner_name_lst']

    view_on_site = False

    def get_list_display(self,request):
        list_display = self.list_display
        try:
            authority = request.user.state_representative.authority
            if authority == TblStateRepresentative.AUTHORITY_SMRC:
                return  list_display + ["show_certificate_link"]   
        except:
            pass

        return list_display

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('source_state').prefetch_related(models.Prefetch("appmovegolddetails_set"))

        if request.user.is_superuser or request.user.groups.filter(name="gold_travel_manager").exists():
            return qs

        try:
            state_representative = request.user.state_representative
            if state_representative.authority!=TblStateRepresentative.AUTHORITY_SMRC:
                if state_representative.authority==TblStateRepresentative.AUTHORITY_SMRC_NAFIZA:
                    qs = qs.filter(state__gte=AppMoveGold.STATE_SMRC,state__lte=AppMoveGold.STATE_SSMO)
                else:
                    qs = qs.filter(state=(state_representative.authority-1),source_state=state_representative.state)
            else:
                qs = qs.filter(source_state=state_representative.state)
        except:
            qs = qs.none()

        return qs

    def save_model(self, request, obj, form, change):
        try:
            state_representative = request.user.state_representative
            obj.source_state = state_representative.state
            if not obj.code:
                serial_no = state_representative.state.state_gold_travel.next_serial_no
                state_code = state_representative.state.state_gold_travel.code
                obj.code = f"{state_code}/{serial_no:03d}"
                state_representative.state.state_gold_travel.next_serial_no = serial_no+1
                state_representative.state.state_gold_travel.save()
        except Exception as e:
            pass

        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

    def get_actions(self, request):
        actions = super().get_actions(request)

        if request.user.groups.filter(name='gold_travel_manager').count() == 0:
            if "cancel_app" in actions:
                del actions['cancel_app']

        try:
            authority = request.user.state_representative.authority
            if authority!=TblStateRepresentative.AUTHORITY_SMRC:
                if "confirm_app" in actions:
                    del actions['confirm_app']

            if authority!=TblStateRepresentative.AUTHORITY_SMRC_NAFIZA:
                if "arrived_to_ssmo_app" in actions:
                    del actions['arrived_to_ssmo_app']
        except:
            if "confirm_app" in actions:
                del actions['confirm_app']

            if "arrived_to_ssmo_app" in actions:
                del actions['arrived_to_ssmo_app']

        return actions
    
    @admin.action(description=_('Confirm application'))
    def confirm_app(self, request, queryset):
        try:
            authority = request.user.state_representative.authority
            change_flag = False
            for obj in queryset:
                if (obj.state+1)==authority:
                    obj.state = authority
                    obj.save()
                    self.log_change(request,obj,_('state_smrc'))
                    change_flag = True

            if change_flag:
                self.message_user(request,_('application confirmed successfully!'))
        except:
            pass

    @admin.action(description=_('Arrived to SSMO'))
    def arrived_to_ssmo_app(self, request, queryset):
        for obj in queryset:
            if obj.state >= AppMoveGold.STATE_SMRC and obj.state < AppMoveGold.STATE_SSMO:
                obj.state = AppMoveGold.STATE_SSMO
                obj.save()
                self.log_change(request,obj,_('state_ssmo'))

    @admin.action(description=_('state_canceled'))
    def cancel_app(self, request, queryset):
        for obj in queryset:
            if obj.state >= AppMoveGold.STATE_SMRC and obj.state < AppMoveGold.STATE_SSMO:
                obj.state = AppMoveGold.STATE_CANCELED
                obj.save()
                self.log_change(request,obj,_('state_canceled'))

    @admin.action(description=_('Export data'))
    def export_as_csv(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="move_gold_form.csv"'},
        )
        header = [
                    _("code"),_("date"),_('gold_weight_in_gram'),_('gold_alloy_count'),_("destination"),_("owner_name"),_( "owner_address"),\
                    _("repr_name"),_("repr_address"),_("repr_phone"),_("repr_identity_type"),_("repr_identity"),_("repr_identity_issue_date"),_("record_state"),_("source_state")
        ]

        # BOM
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        writer.writerow(header)

        for emp in queryset.order_by("source_state","code"):

            row = [
                    emp.code,emp.date,emp.gold_weight_in_gram,emp.gold_alloy_count,emp.get_destination_display(),emp.owner_name,\
                    emp.owner_address,emp.repr_name,emp.repr_address,emp.repr_phone,emp.get_repr_identity_type_display(),emp.repr_identity,emp.repr_identity_issue_date,emp.get_state_display(),\
                    emp.source_state
            ]
            writer.writerow(row)

        return response

    @admin.display(description=_('owner_name'))
    def owner_name(self, obj):
        return f'{obj.owner_name}'

    @admin.display(description=_('gold_weight_in_gram'))
    def gold_weight_in_gram(self, obj):
        sum = obj.appmovegolddetails_set.aggregate(sum=models.Sum("alloy_weight_in_gram"))['sum'] or 0
        return f'{round(sum,2):,}'

    @admin.display(description=_('gold_alloy_count'))
    def gold_alloy_count(self, obj):
        count = obj.appmovegolddetails_set.count()
        return count

    @admin.display(description=_('Show certificate'))
    def show_certificate_link(self, obj):
        url = reverse('gold_travel:gold_travel_cert')
        return format_html('<a target="_blank" class="viewlink" href="{url}?id={id}">'+_('Show certificate')+'</a>',
                    url=url,id=obj.id
                )

    @admin.display(description=_('record_state'))
    def state_str(self, obj):
        if obj.state == AppMoveGold.STATE_SSMO:
            return format_html(f'<span style="color:green">{obj.get_state_display()}</span>')
        
        return obj.get_state_display()

admin.site.register(AppMoveGold, AppMoveGoldAdmin)

class AppPrepareGoldAdmin(LogAdminMixin,admin.ModelAdmin):
    model = AppPrepareGold
    fields = ["date","owner_name","gold_weight_in_gram","state"] 
    list_filter = ["date","state",("source_state",admin.RelatedOnlyFieldListFilter)]
    search_fields = ["owner_name"]
    view_on_site = False
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

    def get_list_display(self,request):
        list_display = ["date","owner_name","gold_weight_in_gram","state","source_state"]  
        try:
            authority = request.user.state_representative.authority
            if authority == TblStateRepresentative.AUTHORITY_SMRC:
                return  list_display + ["show_certificate_link"]   
        except:
            pass

        return list_display

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser or request.user.groups.filter(name="gold_travel_manager").exists():
            return qs

        try:
            state_representative = request.user.state_representative
            qs = qs.filter(source_state=state_representative.state)
        except:
            qs = qs.none()

        return qs

    def save_model(self, request, obj, form, change):
        try:
            state_representative = request.user.state_representative
            obj.issuer = state_representative
            obj.source_state = state_representative.state
        except Exception as e:
            pass

        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

    @admin.display(description=_('Show certificate'))
    def show_certificate_link(self, obj):
        url = reverse('gold_travel:whom_may_concern')
        return format_html('<a target="_blank" class="viewlink" href="{url}?id={id}">'+_('Show certificate')+'</a>',
                    url=url,id=obj.id
                )

admin.site.register(AppPrepareGold, AppPrepareGoldAdmin)
