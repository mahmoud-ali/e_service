from django.contrib import admin

from hr.models import EmployeeBasic
from sandog.models import EmployeeSolarSystem

class EmployeeSolarSystemMixin:
    def has_add_permission(self, request):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            try:
                employee = EmployeeBasic.objects.get(email=request.user.email)
                print("emp",employee)
                try:
                    employee.solar_system_category_choice
                    return False
                except:
                    print("no solor system")

                    return True
            except Exception as e:
                print("no employee",e)
                return False

        return False

    def has_change_permission(self, request, obj=None):
        if request.user.groups.filter(name__in=["hr_employee",]).exists():
            return True
        
        return False

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
