from django.contrib import admin
from django import forms
from form15_tra.models import Market, CollectionForm, CollectorAssignment, APILog


@admin.register(CollectorAssignment)
class CollectorAssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'market','is_observer', 'is_collector', 'is_senior_collector')
    search_fields = ('user__username', 'market__market_name')
    readonly_fields = ("esali_password_enc", "esali_service_id") 

    class Form(forms.ModelForm):
        esali_password_plain = forms.CharField(
            required=False,
            widget=forms.PasswordInput(render_value=True),
            help_text="Enter plain Esali password to (re-)encrypt. Leave empty to keep current encrypted value.",
            label="Esali password (plain)",
        )

        class Meta:
            model = CollectorAssignment
            fields = ["user", "market", "is_collector", "is_senior_collector", "is_observer", "esali_username", "esali_password_enc"] #, "esali_service_id"

    form = Form

    def save_model(self, request, obj, form, change):
        plain = str(form.cleaned_data.get("esali_password_plain") or "")
        if plain.strip() != "":
            obj.set_esali_password_plain(plain)
        return super().save_model(request, obj, form, change)


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
        'id','miner_name','total_amount', 'sacks_count', 'phone', 'invoice_id', 'receipt_number', 'rrn_number', 'status',
        
    )
    list_filter = ('status', 'market', 'collector')
    search_fields = ('receipt_number', 'miner_name')
    readonly_fields = [f.name for f in CollectionForm._meta.fields]
    inlines = [APILogInline]
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
