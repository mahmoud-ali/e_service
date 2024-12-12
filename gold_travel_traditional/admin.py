from django.utils.translation import gettext_lazy as _

from django.contrib import admin

from gold_travel_traditional.models import AppMoveGoldTraditional, GoldTravelTraditionalUserDetail, LkpJihatAlaisdar, LkpSoag

class LkpSoagAdmin(admin.ModelAdmin):
    model = LkpSoag
    list_display = ["state","name"]
    list_filter = ["state"]
    search_fields = ["name"]

admin.site.register(LkpSoag, LkpSoagAdmin)

class LkpJihatAlaisdarAdmin(admin.ModelAdmin):
    model = LkpJihatAlaisdar
    list_display = ["state","name"]
    list_filter = ["state"]
    search_fields = ["name"]

admin.site.register(LkpJihatAlaisdar, LkpJihatAlaisdarAdmin)

class GoldTravelTraditionalUserDetailInline(admin.TabularInline):
    model = GoldTravelTraditionalUserDetail
    exclude = ["created_at","created_by","updated_at","updated_by"]
    extra = 1    

class GoldTravelTraditionalUser(admin.ModelAdmin):
    model = AppMoveGoldTraditional
    inlines = [GoldTravelTraditionalUserDetailInline]     

    fields = ["user","name","state"]

class LogAdminMixin:
    def has_add_permission(self, request):
        try:
            request.user.gold_travel_traditional
            return True
        except:
            pass
        
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        try:
            request.user.gold_travel_traditional
            return True
        except:
            pass
        
        return super().has_change_permission(request,obj)

    def has_delete_permission(self, request, obj=None):
        try:
            request.user.gold_travel_traditional
            return True
        except:
            pass
     
        return super().has_delete_permission(request,obj)

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

class AppMoveGoldTraditionalAdmin(LogAdminMixin,admin.ModelAdmin):
    model = AppMoveGoldTraditional

    fieldsets = [
        (
            None,
            {
                'fields': ["code","issue_date","gold_weight_in_gram"]
            },
        ),
        (
            _("almustafid data"),
            {
                'fields': ["almustafid_name","almustafid_phone"]
            },
        ),
        (
            _("others"),
            {
                'fields': ["jihat_alaisdar","wijhat_altarhil"]
            },
        ),
        # (
        #     _("gold data"),
        #     {
        #         'fields': [("gold_weight_in_gram","gold_alloy_count"),"gold_description"]
        #     },
        # ),
    ]

    list_display = ["code","issue_date","gold_weight_in_gram","almustafid_name","almustafid_phone","jihat_alaisdar","wijhat_altarhil","source_state","state"]
    list_filter = ["issue_date",("state",admin.ChoicesFieldListFilter),("source_state",admin.RelatedFieldListFilter),("jihat_alaisdar",admin.RelatedFieldListFilter),("wijhat_altarhil",admin.RelatedFieldListFilter)]
    search_fields = ["code","muharir_alaistimara","almustafid_name","almustafid_phone","almushtari_name"]
    # actions = ['confirm_app','arrived_to_ssmo_app','waived_app','cancel_app','return_to_draft','export_as_csv']
    autocomplete_fields = ["jihat_alaisdar","wijhat_altarhil"]
    # list_editable = ['owner_name_lst']

    view_on_site = False

admin.site.register(AppMoveGoldTraditional, AppMoveGoldTraditionalAdmin)
