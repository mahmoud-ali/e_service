from django.shortcuts import render, redirect
from .forms import (
    EmergencyEvaluationForm,
    SurveyResponseForm, 
    EmployeeDataForm, 
)
from django.http import JsonResponse
from .models import Employee_Data_Emergency,EmergencyEvaluation,SurveyResponse
from django.contrib.auth.decorators import login_required
import json 
from django.contrib import messages
import traceback
from django.db import transaction, IntegrityError 
@login_required
def get_employees_under_manager(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated"}, status=401)
    
    manager_email = request.user.email    
    
    try:
        manager_employee = Employee_Data_Emergency.objects.get(email=manager_email)
        manager_name = manager_employee.name
    except Employee_Data_Emergency.DoesNotExist:
        return JsonResponse({"error": "Manager employee not found in Employee_Data_Emergency model."}, status=404)        
    employees_under_manager = Employee_Data_Emergency.objects.filter(
        direct_manager_email=manager_email
    ).exclude(
        email=manager_email  
    ).values('id','name','email','job_title') 
    employee_list = []
    for emp in employees_under_manager:
        employee_list.append({
            "code": emp['id'], 
            "name": emp['name'],
            "email": emp['email'],
            "job": emp['job_title']
        })
        
    data = {
        "manager_name": manager_name,
        "employees_count": len(employee_list),
        "employees": employee_list
    }
    
    return JsonResponse(data)


def emergency_form_list(request):
    employees = EmergencyEvaluation.objects.all()
    context = {
        'employees': employees,
        'title': 'قائمة الموظفين'
    }
    return render(request, 'hr_survey/employee_list.html', context)

@login_required
def emergency_form(request):
    employees_data_response = get_employees_under_manager(request)
    employees_data = json.loads(employees_data_response.content)
    employee_list = employees_data.get('employees', [])   
    employee_choices = [('', 'اختر الموظف...')]
    employee_choices.extend([(emp['name'], emp['name']) for emp in employee_list])

    if request.method == "POST":
        
        form = EmergencyEvaluationForm(request.POST, employee_choices=employee_choices )

        if form.is_valid():
            try:
                with transaction.atomic():
                    emergency_evaluation_instance = form.save(commit=False)
                    manager_name = employees_data.get('manager_name') 
                    manager_email=  request.user.email if request.user.is_authenticated else ''

                    emergency_evaluation_instance.direct_manager = manager_name 
                    emergency_evaluation_instance.direct_manager_email = manager_email 
                    employee_code = form.cleaned_data.get('employee_code') 
                    if employee_code:
                        emergency_evaluation_instance.job_number = str(employee_code)
                    employee_email_from_form = form.cleaned_data.get('email')
                    
                    if employee_email_from_form:
                        emergency_evaluation_instance.email = str(employee_email_from_form)
                                        
                    emergency_evaluation_instance.save()
                    return redirect('/surveys/survey_thank_you/')

            except Exception as e:
                        print(f"Error saving Emergency Evaluation: {e}") 
                        print(f"Form non-field errors: {form.errors}")
                        traceback.print_exc() 
    else:
        form = EmergencyEvaluationForm(employee_choices=employee_choices)

    employees_json = json.dumps(employee_list)

    context = {
        "form": form,
        "employees_json": employees_json, 
        "manager_name": employees_data.get('manager_name'),
        "direct_manager_email": request.user.email
    }
    
    return render(request, "hr_survey/form.html", context)




def employee_list(request):
    employees = Employee_Data_Emergency.objects.all()
    context = {
        'employees': employees,
        'title': 'قائمة الموظفين'
    }
    return render(request, 'hr_survey/employee_list.html', context)

def employee_create(request):
    if request.method == 'POST':
        form = EmployeeDataForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الموظف بنجاح!')
            return redirect('employee_list/')
    else:
        form = EmployeeDataForm()
    
    context = {
        'form': form,
        'title': 'إضافة موظف جديد'
    }
    return render(request, 'hr_survey/employee_form.html', context)


def survey_view(request):
    if request.method == 'POST':
        form = SurveyResponseForm(request.POST)

        if form.is_valid():
            try:
                
                with transaction.atomic():
                    form.save()
                
                return render(request, 'hr_survey/thank_you.html')

            except IntegrityError as e:
                print(f"Database Integrity Error: {e}")
                form.add_error(None, "حدث خطأ في البيانات المدخلة. يرجى التأكد من اختيار جميع الخيارات المطلوبة.")
                
            except Exception as e:
                print(f"General Error saving survey: {e}")
                form.add_error(None, "حدث خطأ غير متوقع أثناء حفظ الاستبيان.")
                
       
    else:
        form = SurveyResponseForm()

    context = {
        'form': form, 
        'title': 'استبيان تقييم فاعلية الهيكل التنظيمي',
    }
    
    return render(request, 'hr_survey/survey_structure.html', context)

def survey_thank_you(request):
    return render(request, 'hr_survey/thank_you.html')



def survey_list_view(request):
    all_surveys = SurveyResponse.objects.all().order_by('-submission_date') 
    
    context = {
        'surveys': all_surveys,
    }
    return render(request, 'hr_survey/survey_list.html', context)


@login_required
def submission_list_view(request):
    manager_name=request.user.get_full_name()
    user_submissions = EmergencyEvaluation.objects.filter(direct_manager_email = request.user.email).order_by('created_at')
    
    context = {
        'user_submissions': user_submissions
    }
    return render(request, 'hr_survey/submission_list.html', context)