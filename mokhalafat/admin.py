from django.contrib import admin

from mokhalafat.forms import AppMokhalafatAdminForm
from mokhalafat.models import AppMokhalafat, AppMokhalafatProcedure, AppMokhalafatRecommendation

class LogAdminMixin:
    def has_add_permission(self, request):
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request,obj)

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request,obj)

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user
        super().save_model(request, obj, form, change)                

class AppMokhalafatProcedureInline(admin.TabularInline):
    model = AppMokhalafatProcedure
    extra = 1    

class AppMokhalafatRecommendationInline(admin.TabularInline):
    model = AppMokhalafatRecommendation
    extra = 1    

class AppMokhalafatAdmin(LogAdminMixin,admin.ModelAdmin):
    # model = AppMokhalafat
    form = AppMokhalafatAdminForm
    inlines = [AppMokhalafatProcedureInline,AppMokhalafatRecommendationInline]
    fields = ["code","date","aism_almukhalafa","wasf_almukhalafa","tahlil_almukhalafa"]
    list_display = ["code","date","aism_almukhalafa","tahlil_almukhalafa"]
    list_filter = ["date"]
    search_fields = ["code","aism_almukhalafa","wasf_almukhalafa","tahlil_almukhalafa"]
    view_on_site = False

admin.site.register(AppMokhalafat, AppMokhalafatAdmin)
