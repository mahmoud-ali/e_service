from django.contrib import admin
from .models import Employee_Data_Emergency, EmergencyEvaluation, RATING_CHOICES, WARNING_CHOICES, GENERAL_RATING, ASKING_CHOICES, PERCENTAGE_CHOICES
from django.utils.translation import gettext_lazy as _

class EmergencyEvaluationAdmin(admin.ModelAdmin):
    
    class Media:
            js = (
                'admin/js/vendor/jquery/jquery.js',
                'admin/js/jquery.init.js',
                'admin/emergency_evaluation_fetch_name.js', 
            )

    readonly_fields = ('employee_name',)
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
        'job_number',
        'job_title',
        'direct_manager',
    )

    fieldsets = (
        (_('بيانات الموظف والفترة'), {
            'fields': (
                ('employee_code', 'employee_name'),
                ('job_number', 'job_title'),
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
        'job_title'
    )

    list_filter = (
        'job_title',
        'name',
        'email',
        'direct_manager_email',
    )

    search_fields = (
        'job_title',
        'name',
        'email',
        'direct_manager_email',
        
    )

    fieldsets = (
          
    )
        
    ordering = ('name',)


admin.site.register(EmergencyEvaluation, EmergencyEvaluationAdmin)
admin.site.register(Employee_Data_Emergency, Employee_Data_Emergency_admin)