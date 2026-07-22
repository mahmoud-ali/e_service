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

    def _gold_user(self, request):
        try:
            return request.user.gold_travel_traditional
        except:
            return None

    def _state_manager(self, request):
        gold_user = self._gold_user(request)
        if gold_user and gold_user.is_state_manager:
            return gold_user
        return None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists():
            return qs
        gold_user = self._gold_user(request)
        if gold_user:
            return qs.filter(state=gold_user.state)
        return qs

    def has_view_permission(self, request, obj=None):
        if super().has_view_permission(request, obj):
            return True
        return self._gold_user(request) is not None

    def has_add_permission(self, request):
        if super().has_add_permission(request):
            return True
        return self._state_manager(request) is not None

    def has_change_permission(self, request, obj=None):
        if super().has_change_permission(request, obj):
            return True
        gold_user = self._state_manager(request)
        if not gold_user:
            return False
        if obj:
            return obj.state_id == gold_user.state_id
        return True

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if self._state_manager(request) and not request.user.is_superuser:
            fields = [f for f in fields if f != 'state']
        return fields

    def save_model(self, request, obj, form, change):
        gold_user = self._state_manager(request)
        if gold_user and not request.user.is_superuser:
            obj.state = gold_user.state
        return super().save_model(request, obj, form, change)

admin.site.register(LkpJihatAlaisdar, LkpJihatAlaisdarAdmin)

class LkpSaigAdmin(admin.ModelAdmin):
    list_display = ["state", "name", "code"]
    list_filter = ["state"]
    search_fields = ["name", "code"]

    def _state_manager(self, request):
        try:
            gold_user = request.user.gold_travel_traditional
            if gold_user.is_state_manager:
                return gold_user
        except:
            pass
        return None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name__in=("gold_travel_traditional_manager","gold_travel_traditional_manager_show")).exists():
            return qs
        gold_user = self._state_manager(request)
        if gold_user:
            return qs.filter(state=gold_user.state)
        return qs

    def has_view_permission(self, request, obj=None):
        if super().has_view_permission(request, obj):
            return True
        return self._state_manager(request) is not None

    def has_add_permission(self, request):
        if super().has_add_permission(request):
            return True
        return self._state_manager(request) is not None

    def has_change_permission(self, request, obj=None):
        if super().has_change_permission(request, obj):
            return True
        gold_user = self._state_manager(request)
        if not gold_user:
            return False
        if obj:
            return obj.state_id == gold_user.state_id
        return True

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if self._state_manager(request) and not request.user.is_superuser:
            fields = [f for f in fields if f != 'state']
        return fields

    def save_model(self, request, obj, form, change):
        gold_user = self._state_manager(request)
        if gold_user and not request.user.is_superuser:
            obj.state = gold_user.state
        return super().save_model(request, obj, form, change)

admin.site.register(LkpSaig, LkpSaigAdmin)


class GoldTravelTraditionalStateAdmin(admin.ModelAdmin):
    list_display = ['state', 'expiry_days']
    search_fields = ['state__name']

admin.site.register(GoldTravelTraditionalState, GoldTravelTraditionalStateAdmin)
