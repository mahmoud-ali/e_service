from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from django.contrib import admin

from .models import (
    Application,
    ComputerTemplate,
    Computer,
    NetworkAdapter,
    Peripheral,
    AccessPoint,
    EmployeeComputer,
)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "version")
    search_fields = ("name", "version")


class ApplicationInline(admin.TabularInline):
    model = ComputerTemplate.applications.through
    extra = 1


@admin.register(ComputerTemplate)
class ComputerTemplateAdmin(admin.ModelAdmin):
    list_display = ("os_type",)
    inlines = [ApplicationInline]
    exclude = ("applications",)  # handled by inline


class NetworkAdapterInline(admin.TabularInline):
    model = NetworkAdapter
    extra = 1


class PeripheralInline(admin.TabularInline):
    model = Peripheral
    extra = 1


class AccessPointInline(admin.TabularInline):
    model = AccessPoint
    extra = 1


class EmployeeComputerInline(admin.TabularInline):
    model = EmployeeComputer
    extra = 1
    max_num = 1


@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    list_display = ("code", "type", "template") #
    list_filter = ("type", "template__os_type")
    search_fields = ("code",)
    inlines = [EmployeeComputerInline,NetworkAdapterInline, PeripheralInline, AccessPointInline]

# @admin.register(NetworkAdapter)
# class NetworkAdapterAdmin(admin.ModelAdmin):
#     list_display = ("model", "connectivity_type", "computer")
#     list_filter = ("connectivity_type",)
#     search_fields = ("model",)


# @admin.register(Peripheral)
# class PeripheralAdmin(admin.ModelAdmin):
#     list_display = ("name", "type", "connectivity_type", "model", "computer")
#     list_filter = ("type", "connectivity_type")
#     search_fields = ("name", "model")


# @admin.register(AccessPoint)
# class AccessPointAdmin(admin.ModelAdmin):
#     list_display = ("name", "model", "computer")
#     search_fields = ("name", "model")


@admin.register(EmployeeComputer)
class EmployeeComputerAdmin(admin.ModelAdmin):
    list_display = ("employee","computer","ask_ai_link")
    list_filter = ("employee", )
    autocomplete_fields = ["employee","computer"]

    @admin.display(description=_('Ask AI'))
    def ask_ai_link(self, obj):
        url = reverse('it:ai_prompt',args=[obj.id])
        return format_html('<a target="_blank" class="viewlink" href="{url}">'+_('Ask AI')+'</a>',
                    url=url
                )
