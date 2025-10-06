from django.contrib import admin
from django.contrib import messages

from hr.models import EmployeeBasic
from sandog.models import EmployeeSolarSystem, LkpSolarSystemCategory, LkpSolarSystemPaymentMethod

class EmployeeSolarSystemMixin:
    def has_add_permission(self, request):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            return True
        
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            return True
        
        return False

    def get_queryset(self, request):
        messages.warning(request, "يمكن التسجيل لاكثر من  منظومة ولكن يشترط كفاية التمويل وإمكانية سداد الأقساط الشهرية")
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.groups.filter(name__in=["hr_manager","hr_manpower"]).exists():
            return qs #.filter(state=STATE_DRAFT)

        return qs.filter(employee__email=request.user.email)

    def save_model(self, request, obj, form, change):
        if obj.pk:
            obj.updated_by = request.user
        else:
            obj.created_by = obj.updated_by = request.user

        obj.employee = EmployeeBasic.objects.get(email=request.user.email)
        super().save_model(request, obj, form, change)    

@admin.register(EmployeeSolarSystem)
class EmployeeSolarSystemAdmin(EmployeeSolarSystemMixin,admin.ModelAdmin):
    model = EmployeeSolarSystem
    fields = ["payment_method","category",]
    list_display = ["employee","payment_method","category",]

@admin.register(LkpSolarSystemCategory)
class LkpSolarSystemCategoryAdmin(admin.ModelAdmin):
    model = LkpSolarSystemCategory

@admin.register(LkpSolarSystemPaymentMethod)
class LkpSolarSystemPaymentMethodAdmin(admin.ModelAdmin):
    model = LkpSolarSystemPaymentMethod
