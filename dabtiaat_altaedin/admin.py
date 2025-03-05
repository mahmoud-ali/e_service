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
from dabtiaat_altaedin.forms import TblStateRepresentativeForm
from dabtiaat_altaedin.models import AppDabtiaat, RevenueSettlement, SettlementType, TblStateRepresentative2

class LogAdminMixin:
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('source_state')

        if request.user.is_superuser or request.user.groups.filter(name__in=["dabtiaat_altaedin_manager"]).exists():
            return qs

        try:
            state_representative = request.user.state_representative2
            qs = qs.filter(source_state=state_representative.state)
        except:
            qs = qs.none()

        return qs

    def save_model(self, request, obj, form, change):
        try:
            state_representative = request.user.state_representative2
            obj.source_state = state_representative.state

            if obj.pk:
                obj.updated_by = request.user
            else:
                obj.created_by = obj.updated_by = request.user
            super().save_model(request, obj, form, change)                
        except:
            pass

    def has_add_permission(self, request):
        try:
            if request.user.state_representative2.authority==TblStateRepresentative2.AUTHORITY_SMRC:
                return super().has_add_permission(request)
        except:
            pass
        
        return False

    def has_change_permission(self, request, obj=None):
        try:
            if request.user.state_representative2.authority==TblStateRepresentative2.AUTHORITY_SMRC:
                if not obj or obj.state==1:
                    return super().has_change_permission(request,obj)
        except:
            pass
        
        return False

    def has_delete_permission(self, request, obj=None):
        try:
            if request.user.state_representative2.authority==TblStateRepresentative2.AUTHORITY_SMRC:
                if not obj or obj.state==1:
                    return super().has_delete_permission(request,obj)
        except:
            pass
     
        return False

    # def save_model(self, request, obj, form, change):
    #     if obj.pk:
    #         obj.updated_by = request.user
    #     else:
    #         obj.created_by = obj.updated_by = request.user
    #     super().save_model(request, obj, form, change)                

class TblStateRepresentativeAdmin(admin.ModelAdmin):
    model = TblStateRepresentative2
    form = TblStateRepresentativeForm
    list_display = ["name","state","authority","user"]        
    list_filter = ["authority",("state",admin.RelatedOnlyFieldListFilter)]
    view_on_site = False
            
admin.site.register(TblStateRepresentative2, TblStateRepresentativeAdmin)

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

class AppDabtiaatAdmin(LogAdminMixin,admin.ModelAdmin):
    model = AppDabtiaat
    exclude = ["created_at","created_by","updated_at","updated_by","state","source_state"]
    list_display = ["date","gold_weight_in_gram","gold_price","koli_amount","state","source_state","al3wayid_aljalila_amount","alhafiz_amount","alniyaba_amount","smrc_amount","state_amount","police_amount","amn_amount","riasat_alquat_aldaabita_amount","alquat_aldaabita_amount"]        
    list_filter = [("date",DateFieldListFilterWithLast30days),("state",ChoicesFieldListFilterNotEmpty),("source_state",RelatedOnlyFieldListFilterNotEmpty)]
    actions = ['confirm_app','return_to_draft','export_as_csv']

    extra = 1    
    formfield_overrides = {
        models.FloatField: {"widget": TextInput},
    }    

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

    # @admin.action(description=_('state_canceled'))
    # def cancel_app(self, request, queryset):
    #     for obj in queryset:
    #         if obj.state >= AppDabtiaat.STATE_SMRC and obj.state < AppDabtiaat.STATE_SSMO:
    #             obj.state = AppDabtiaat.STATE_CANCELED
    #             obj.save()
    #             self.log_change(request,obj,_('state_canceled'))
    #             self.message_user(request,_('application changed successfully!'))

    @admin.action(description=_('return_to_draft'))
    def return_to_draft(self, request, queryset):
        for obj in queryset:
            if obj.state == AppDabtiaat.STATE_SMRC:
                obj.state = AppDabtiaat.STATE_DRAFT
                obj.save()
                self.log_change(request,obj,_('return_to_draft'))
                self.message_user(request,_('application changed successfully!'))

    @admin.action(description=_('Export data'))
    def export_as_csv(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="dabtiaat_form.csv"'},
        )
        header = [
                    _("date"),_('gold_weight_in_gram'),_('gold_price'),_('koli_amount'),_("record_state"),_("source_state"),_( "al3wayid_aljalila_amount"),\
                    _("alhafiz_amount"),_("alniyaba_amount"),_("smrc_amount"),_("state_amount"),_("police_amount"),_("amn_amount"),_("riasat_alquat_aldaabita_amount"),_("alquat_aldaabita_amount")
        ]

        # BOM
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        writer.writerow(header)

        for obj in queryset.order_by("source_state","-date"):

            row = [
                    obj.date,obj.gold_weight_in_gram,obj.gold_price,obj.koli_amount,obj.get_state_display(),obj.source_state,\
                    obj.al3wayid_aljalila_amount,obj.alhafiz_amount,obj.alniyaba_amount,obj.smrc_amount,obj.state_amount,\
                    obj.police_amount,obj.amn_amount,obj.riasat_alquat_aldaabita_amount,obj.alquat_aldaabita_amount
            ]
            writer.writerow(row)

        return response

    @admin.display(description=_('koli_amount'))
    def koli_amount(self, obj):
        return f'{round(obj.koli_amount):,}'

    @admin.display(description=_('gold_price'))
    def gold_price(self, obj):
        return f'{round(obj.gold_price):,}'

    @admin.display(description=_('gold_weight_in_gram'))
    def gold_weight_in_gram(self, obj):
        return f'{round(obj.gold_weight_in_gram):,}'

    @admin.display(description=_('al3wayid_aljalila_amount'))
    def al3wayid_aljalila_amount(self, obj):
        return f'{round(obj.al3wayid_aljalila_amount):,}'

    @admin.display(description=_('alhafiz_amount'))
    def alhafiz_amount(self, obj):
        return f'{round(obj.alhafiz_amount):,}'

    @admin.display(description=_('alniyaba_amount'))
    def alniyaba_amount(self, obj):
        return f'{round(obj.alniyaba_amount):,}'

    @admin.display(description=_('smrc_amount'))
    def smrc_amount(self, obj):
        return f'{round(obj.smrc_amount):,}'

    @admin.display(description=_('state_amount'))
    def state_amount(self, obj):
        return f'{round(obj.state_amount):,}'

    @admin.display(description=_('police_amount'))
    def police_amount(self, obj):
        return f'{round(obj.police_amount):,}'

    @admin.display(description=_('amn_amount'))
    def amn_amount(self, obj):
        return f'{round(obj.amn_amount):,}'

    @admin.display(description=_('riasat_alquat_aldaabita_amount'))
    def riasat_alquat_aldaabita_amount(self, obj):
        return f'{round(obj.riasat_alquat_aldaabita_amount):,}'

    @admin.display(description=_('alquat_aldaabita_amount'))
    def alquat_aldaabita_amount(self, obj):
        return f'{round(obj.alquat_aldaabita_amount):,}'

admin.site.register(AppDabtiaat, AppDabtiaatAdmin)


class RevenueSettlementAdmin(LogAdminMixin,admin.ModelAdmin):
    model = RevenueSettlement
    exclude = ["created_at","created_by","updated_at","updated_by","state","source_state"]
    # list_display = ["date","gold_weight_in_gram","gold_price","koli_amount","state","source_state","al3wayid_aljalila_amount","alhafiz_amount","alniyaba_amount","smrc_amount","state_amount","police_amount","amn_amount","riasat_alquat_aldaabita_amount","alquat_aldaabita_amount"]        
    list_filter = [("date",DateFieldListFilterWithLast30days),("state",ChoicesFieldListFilterNotEmpty),("source_state",RelatedOnlyFieldListFilterNotEmpty)]

admin.site.register(SettlementType)
admin.site.register(RevenueSettlement, RevenueSettlementAdmin)
