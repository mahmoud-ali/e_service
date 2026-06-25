from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields

from prices.models import (
    GlobalGoldPrice,
    BankSudanGoldPrice,
    StateGoldPrice,
    DollarPrice,
    PricesStateUser,
)


class LogResourceMixin(resources.ModelResource):
    """Skip created_by/updated_by during import — they are auto-set."""

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        # Remove auto-managed columns from dataset if present
        for col in ('created_by', 'updated_by', 'created_at', 'updated_at', 'id'):
            if col in dataset.headers:
                col_idx = dataset.headers.index(col)
                del dataset[col_idx]
        return dataset


class LogMixin:
    """Sets created_by / updated_by on save."""
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# --- Resource classes for import/export ---

class GlobalGoldPriceResource(LogResourceMixin):
    class Meta:
        model = GlobalGoldPrice
        import_id_fields = []
        fields = ('id', 'karat', 'price_per_gram_usd', 'price_per_ounce_usd', 'created_at')
        export_order = fields


class BankSudanGoldPriceResource(LogResourceMixin):
    class Meta:
        model = BankSudanGoldPrice
        import_id_fields = []
        fields = ('id', 'category', 'price_per_gram_sdg', 'created_at')
        export_order = fields


class StateGoldPriceResource(LogResourceMixin):
    state_name = fields.Field(column_name='state', attribute='state')

    class Meta:
        model = StateGoldPrice
        import_id_fields = []
        fields = ('id', 'state', 'price_per_gram_sdg', 'created_at')
        export_order = fields

    def dehydrate_state_name(self, obj):
        return obj.state.name if obj.state else ''


class DollarPriceResource(LogResourceMixin):
    class Meta:
        model = DollarPrice
        import_id_fields = []
        fields = ('id', 'rate_type', 'price_in_sdg', 'created_at')
        export_order = fields


# --- Admin classes ---

@admin.register(GlobalGoldPrice)
class GlobalGoldPriceAdmin(LogMixin, ImportExportModelAdmin):
    resource_class = GlobalGoldPriceResource
    list_display = ('karat', 'price_per_gram_usd', 'price_per_ounce_usd', 'created_at', 'created_by')
    list_filter = ('karat', 'created_at')
    search_fields = ('price_per_gram_usd',)
    date_hierarchy = 'created_at'


@admin.register(BankSudanGoldPrice)
class BankSudanGoldPriceAdmin(LogMixin, ImportExportModelAdmin):
    resource_class = BankSudanGoldPriceResource
    list_display = ('category', 'price_per_gram_sdg', 'created_at', 'created_by')
    list_filter = ('category', 'created_at')
    search_fields = ('price_per_gram_sdg',)
    date_hierarchy = 'created_at'


@admin.register(StateGoldPrice)
class StateGoldPriceAdmin(LogMixin, ImportExportModelAdmin):
    resource_class = StateGoldPriceResource
    list_display = ('state', 'price_per_gram_sdg', 'created_at', 'created_by')
    list_filter = ('state', 'created_at')
    search_fields = ('state__name', 'price_per_gram_sdg')
    date_hierarchy = 'created_at'
    autocomplete_fields = ('state',)


@admin.register(DollarPrice)
class DollarPriceAdmin(LogMixin, ImportExportModelAdmin):
    resource_class = DollarPriceResource
    list_display = ('rate_type', 'price_in_sdg', 'created_at', 'created_by')
    list_filter = ('rate_type', 'created_at')
    search_fields = ('price_in_sdg',)
    date_hierarchy = 'created_at'


@admin.register(PricesStateUser)
class PricesStateUserAdmin(LogMixin, admin.ModelAdmin):
    list_display = ('user', 'state', 'created_at')
    list_filter = ('state',)
    search_fields = ('user__username', 'state__name')
    autocomplete_fields = ('state',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj=obj, **kwargs)
        form.base_fields['user'].queryset = form.base_fields['user'].queryset.filter(
            groups__name='prices_state_gold'
        ).distinct()
        return form
