from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from form15_tra.models import (
    Market,
    CollectionForm,
    CollectorAssignmentCollector,
    CollectorAssignmentSeniorCollector,
    CollectorAssignmentObserver,
    APILog,
)


class BaseCollectorAssignmentProxyAdmin(admin.ModelAdmin):
    list_display = ("market", "user", "is_observer", "is_collector", "is_senior_collector")
    search_fields = ("user__username", "market__market_name")

    def apply_role_flags(self, obj):
        """
        Force a single role for each proxy model.
        """
        return obj

    def save_model(self, request, obj, form, change):
        self.apply_role_flags(obj)
        return super().save_model(request, obj, form, change)


@admin.register(CollectorAssignmentCollector)
class CollectorAssignmentCollectorAdmin(BaseCollectorAssignmentProxyAdmin):
    readonly_fields = ("esali_password_enc", "esali_service_id")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        User = get_user_model()
        # `get_form()` returns a Form *class*, not an instance.
        # Adjust the declared field via `base_fields`.
        if "user" in getattr(form, "base_fields", {}):
            form.base_fields["user"].queryset = User.objects.filter(groups__name="التحصيل الإلكتروني/متحصل")
        return form

    def apply_role_flags(self, obj):
        obj.is_collector = True
        obj.is_senior_collector = False
        obj.is_observer = False
        return obj

    class Form(forms.ModelForm):
        esali_password_plain = forms.CharField(
            required=False,
            widget=forms.PasswordInput(render_value=True),
            help_text="Enter plain Esali password to (re-)encrypt. Leave empty to keep current encrypted value.",
            label="Esali password (plain)",
        )

        class Meta:
            model = CollectorAssignmentCollector
            fields = [
                "user",
                "market",
                "esali_username",
                "esali_password_enc",
            ]  # `is_*` flags are enforced by the proxy admin.

    form = Form

    def save_model(self, request, obj, form, change):
        self.apply_role_flags(obj)
        plain = str(form.cleaned_data.get("esali_password_plain") or "")
        if plain.strip() != "":
            obj.set_esali_password_plain(plain)
        return super().save_model(request, obj, form, change)


@admin.register(CollectorAssignmentSeniorCollector)
class CollectorAssignmentSeniorCollectorAdmin(BaseCollectorAssignmentProxyAdmin):
    fields = ("user", "market")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        User = get_user_model()
        # `get_form()` returns a Form *class*, not an instance.
        # Adjust the declared field via `base_fields`.
        if "user" in getattr(form, "base_fields", {}):
            form.base_fields["user"].queryset = User.objects.filter(groups__name="التحصيل الإلكتروني/كبير متحصلين")
        return form

    def apply_role_flags(self, obj):
        obj.is_collector = False
        obj.is_senior_collector = True
        obj.is_observer = False
        return obj


@admin.register(CollectorAssignmentObserver)
class CollectorAssignmentObserverAdmin(BaseCollectorAssignmentProxyAdmin):
    fields = ("user", "market")

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        User = get_user_model()
        # `get_form()` returns a Form *class*, not an instance.
        # Adjust the declared field via `base_fields`.
        if "user" in getattr(form, "base_fields", {}):
            form.base_fields["user"].queryset = User.objects.filter(groups__name="التحصيل الإلكتروني/مراقب")
        return form

    def apply_role_flags(self, obj):
        obj.is_collector = False
        obj.is_senior_collector = False
        obj.is_observer = True
        return obj


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ('market_name', 'location')
    search_fields = ('market_name',)


class APILogInline(admin.TabularInline):
    model = APILog
    extra = 0
    readonly_fields = (
        'action', 'user', 'request_data', 'response_data', 
        'status_code', 'ip_address', 'created_at'
    )
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(CollectionForm)
class CollectionFormAdmin(admin.ModelAdmin):
    list_display = (
        'id','miner_name','arrival_source','vehicle_plate','total_amount', 'sacks_count', 'phone', 'invoice_id', 'receipt_number', 'rrn_number', 'status',
        
    )
    list_filter = ('status', 'market',)
    search_fields = ('phone', 'invoice_id', 'receipt_number', 'rrn_number', 'miner_name', 'arrival_source', 'vehicle_plate')
    readonly_fields = [f.name for f in CollectionForm._meta.fields]
    inlines = [APILogInline]
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
