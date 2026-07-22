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


