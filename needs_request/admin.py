from django.contrib import admin
from .models import NeedsRequest, Item, SuggestedItem, Department
from django.contrib.auth.models import Group, User

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'executive_manager', 'department_manager')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "executive_manager":
            try:
                eom_pub_group = Group.objects.get(name='eom_pub')
                kwargs["queryset"] = eom_pub_group.user_set.all()
            except Group.DoesNotExist:
                kwargs["queryset"] = User.objects.none()

        if db_field.name == "department_manager":
            try:
                eom_pub_group = Group.objects.get(name='dga_pub')
                kwargs["queryset"] = eom_pub_group.user_set.all()
            except Group.DoesNotExist:
                kwargs["queryset"] = User.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ItemInline(admin.TabularInline):
    model = Item
    extra = 1

@admin.register(NeedsRequest)
class NeedsRequestAdmin(admin.ModelAdmin):
    list_display = ('department', 'date', 'approval_status')
    inlines = [ItemInline]

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('requested_item','needs_request')

@admin.register(SuggestedItem)
class SuggestedItemAdmin(admin.ModelAdmin):
    list_display = ('name', )
