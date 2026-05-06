import codecs
import csv

from django.http import HttpRequest, HttpResponse

from django.contrib import admin
from .models import Employee_Data_Emergency, EmergencyEvaluation, RATING_CHOICES, WARNING_CHOICES, GENERAL_RATING, ASKING_CHOICES, PERCENTAGE_CHOICES, Employee_Sim_Card
from django.utils.translation import gettext_lazy as _

class EmergencyEvaluationAdmin(admin.ModelAdmin):
    
    class Media:
            js = (
                'admin/js/vendor/jquery/jquery.js',
                'admin/js/jquery.init.js',
                'admin/emergency_evaluation_fetch_name.js', 
            )

    readonly_fields = (
                'employee_code',
                'employee_name',
                'job_title',
                'direct_manager',
                'period_from',
                'period_to',
                'attendance_discipline',
                'follow_instructions',
                'task_responsibility',
                'teamwork',
                'communication',
                'main_tasks_quality',
                'extra_tasks',
                'work_pressure',
                'policies_commitment',
                'creativity',
                'overall_performance',
                'emergency_response', 
                'coverage_percentage',
                'strengths',
                'challenges',
                'training_needs',
                'manager_notes'   
                       )
    
    list_display = (
        'employee_code',
        'employee_name',
        'email',
        'job_title',
        'period_from',
        'period_to',
        'overall_performance',
        'recommendations_continue',
        'created_at',
    )

    list_filter = (
        'overall_performance',
        'emergency_response',
        'coverage_percentage',
        'recommendations_continue',
        'period_from',
        'period_to',
    )

    search_fields = (
        'employee_code',
        'employee_name',
        'job_title',
        'direct_manager',
    )

    fieldsets = (
        (_('بيانات الموظف والفترة'), {
            'fields': (
                ('employee_code', 'employee_name'),
                ( 'job_title'),
                ( 'direct_manager'),
                ('period_from', 'period_to'),
            ),
            'classes': ('wide', 'extrapretty'), 
        }),
        
        (_('التقييم السلوكي (1-5)'), {
            'fields': (
                ('attendance_discipline', 'follow_instructions'),
                ('task_responsibility', 'teamwork'),
                'communication',
            ),
        }),
        
        (_('تقييم الأداء والمهام (1-5)'), {
            'fields': (
                ('main_tasks_quality', 'extra_tasks'),
                ('work_pressure', 'policies_commitment'),
                ('creativity',), 
            ),
        }),
        
        (_('التقييمات العامة والملخص'), {
            'fields': (
                ('overall_performance', 'emergency_response', 'coverage_percentage'),
                ('strengths', 'challenges', 'training_needs'),
                ('manager_notes',),
            ),
        }),
        
        (_('الملاحظات الإدارية والسجلات'), {
            'fields': (
                ('average_attendance', 'attendance_punctnality'),
                ('violation_count', 'warnings_count'),
                ('employee_effective', 'recommendations_continue'),
                ('substantive_note',),
            ),
        }),
    )

    ordering = ('-created_at',)

# ---

class Employee_Data_Emergency_admin(admin.ModelAdmin):
    
    class Media:
            js = (
                'admin/js/vendor/jquery/jquery.js',
                'admin/js/jquery.init.js',
                'admin/emergency_evaluation_fetch_name.js', 
            )

    list_display = (
        'name',
        'email',
        'direct_manager_email',
        'job_title',
        'edara_3ama'
    )

    list_filter = (
        'edara_3ama',
    )

    search_fields = (
        'job_title',
        'name',
        'email',
        
    )

    fieldsets = (
          
    )
        
    ordering = ('name',)

    actions = ['export_data']

    @admin.action(description=_('Export data'))
    def export_data(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="employees.csv"'},
        )
        header = [
                    "id","الاسم","الايميل","ايميل المدير المباشر","المسمى الوظيفي","الإدارة العامة"
        ]

        # BOM
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        writer.writerow(header)

        for emp in queryset.all():
            row = [
                    emp.id, emp.name,emp.email,emp.direct_manager_email,emp.job_title,emp.edara_3ama
            ]
            writer.writerow(row)

        return response

admin.site.register(EmergencyEvaluation, EmergencyEvaluationAdmin)
admin.site.register(Employee_Data_Emergency, Employee_Data_Emergency_admin)

class Employee_Sim_Card_admin(admin.ModelAdmin):
    
    list_display = (
        'name',
        'sim_number',
        'department',
        'email',
    )

    list_filter = (
        'department',
    )

    search_fields = (
        'name',
        'sim_number',
        'email',
        
    )

    fieldsets = (
          
    )

admin.site.register(Employee_Sim_Card,Employee_Sim_Card_admin)
