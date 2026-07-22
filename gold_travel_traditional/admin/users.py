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

