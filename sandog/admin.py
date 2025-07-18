from django.contrib import admin

from hr.models import EmployeeBasic
from sandog.models import EmployeeSolarSystem, LkpSolarSystemCategory

class EmployeeSolarSystemMixin:
    def has_add_permission(self, request):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            try:
                employee = EmployeeBasic.objects.get(email=request.user.email)
                print("***",employee)
                if EmployeeSolarSystem.objects.filter(employee=employee).count() > 0:
                    return False
                
                return True
                # print("emp",employee)
                # try:
                #     employee.solar_system_category_choice
                #     return False
                # except:
                #     print("no solor system")
                #     return True
                
            except Exception as e:
                print("not an employee",e)
                return False

        return False

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            return True
        
        return False

    def get_queryset(self, request):
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
    fields = ["category",]
    list_display = ["employee","category",]

@admin.register(LkpSolarSystemCategory)
class LkpSolarSystemCategoryAdmin(admin.ModelAdmin):
    model = LkpSolarSystemCategory
    def has_add_permission(self, request):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            return False
        
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            return False

        return super().has_change_permission(request,obj)
