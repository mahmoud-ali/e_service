from django.contrib import admin

from gold_travel_traditional.models import Route


class RouteAdmin(admin.ModelAdmin):
    list_display = ['jihat_alaisdar', 'wijhat_altarhil']
    list_filter = ['jihat_alaisdar__state', 'wijhat_altarhil', 'jihat_alaisdar']
    search_fields = ['jihat_alaisdar__name', 'wijhat_altarhil__name']
    autocomplete_fields = ['jihat_alaisdar', 'wijhat_altarhil']


admin.site.register(Route, RouteAdmin)
