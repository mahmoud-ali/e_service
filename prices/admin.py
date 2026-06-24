from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from prices.models import (
    GlobalGoldPrice,
    BankSudanGoldPrice,
    StateGoldPrice,
    DollarPrice,
)


class LogMixin:
    """Sets created_by / updated_by on save."""
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(GlobalGoldPrice)
class GlobalGoldPriceAdmin(LogMixin, admin.ModelAdmin):
    list_display = ('karat', 'price_per_gram_usd', 'price_per_ounce_usd', 'created_at', 'created_by')
    list_filter = ('karat', 'created_at')
    search_fields = ('price_per_gram_usd',)
    date_hierarchy = 'created_at'


@admin.register(BankSudanGoldPrice)
class BankSudanGoldPriceAdmin(LogMixin, admin.ModelAdmin):
    list_display = ('category', 'price_per_gram_sdg', 'created_at', 'created_by')
    list_filter = ('category', 'created_at')
    search_fields = ('price_per_gram_sdg',)
    date_hierarchy = 'created_at'


@admin.register(StateGoldPrice)
class StateGoldPriceAdmin(LogMixin, admin.ModelAdmin):
    list_display = ('state', 'price_per_gram_sdg', 'created_at', 'created_by')
    list_filter = ('state', 'created_at')
    search_fields = ('state__name', 'price_per_gram_sdg')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('state',)


@admin.register(DollarPrice)
class DollarPriceAdmin(LogMixin, admin.ModelAdmin):
    list_display = ('rate_type', 'price_in_sdg', 'created_at', 'created_by')
    list_filter = ('rate_type', 'created_at')
    search_fields = ('price_in_sdg',)
    date_hierarchy = 'created_at'
