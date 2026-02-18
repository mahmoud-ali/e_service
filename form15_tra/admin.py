from django.contrib import admin
from form15_tra.models import Market, CollectionForm, CollectorAssignment, APILog


@admin.register(CollectorAssignment)
class CollectorAssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'market','is_observer', 'is_collector', 'is_senior_collector')
    search_fields = ('user__username', 'market__market_name')


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
        'receipt_number', 'miner_name', 'status', 
        'collector', 'market', 'created_at'
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
