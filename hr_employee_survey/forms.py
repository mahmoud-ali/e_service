from django import forms
from .models import Employee_Sim_Card,MosamaWazifi,EmergencyEvaluation ,Employee_Data_Emergency,SurveyResponse

class EmergencyEvaluationForm(forms.ModelForm):
    employee_name = forms.ChoiceField(
        label="Employee Name:",
        required=True,
        choices=[('', '')],  
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'employee_name_select'})
    )
    
    employee_code = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'employee_code_hidden'}), 
        required=False 
    )

    direct_manager_email = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'direct_manager_email_hidden'}), 
        required=False 
    )

    job_title = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'job_title_hidden'}), 
        required=False
    )

    class Meta:
        model = EmergencyEvaluation
       
        fields = "__all__" 
        widgets = {
            'period_from': forms.DateInput(attrs={'type': 'date'}),
            'period_to': forms.DateInput(attrs={'type': 'date'}),
            'strengths': forms.Textarea(attrs={'rows': 3}),
            'challenges': forms.Textarea(attrs={'rows': 3}),
            'training_needs': forms.Textarea(attrs={'rows': 3}),
            'manager_notes': forms.Textarea(attrs={'rows': 3}),
            'Substantive_note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        employee_choices = kwargs.pop('employee_choices', None)
        super().__init__(*args, **kwargs)
        if employee_choices is not None:
            self.fields['employee_name'].choices = employee_choices
    def clean_employee_name(self):
        employee_name = self.cleaned_data.get('employee_name')
        
        if EmergencyEvaluation.objects.filter(employee_name=employee_name).exists():
            raise forms.ValidationError("عذراً، تم إدخال تقييم لهذا الموظف مسبقاً.")
            
        return employee_name


class SurveyResponseForm(forms.ModelForm):
    class Meta:
        model = SurveyResponse
        fields = [
            'wilaya','department','position', 'other_position', 'work_duration',
            'clarity_statement',  'roles_responsibilities', 'communication_lines', 'job_title_match',
            'decision_making', 'reduces_overlap', 'coordination', 'service_quality',
            'strategic_alignment', 'adaptability', 'resource_allocation', 'service_delivery',
            'challenges', 'suitability', 'improvements'
        ]
        
        
        widgets = {
            'wilaya': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'ابحث عن القسم'
            }),
            'department': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'ابحث عن القسم'
            }),
            'position': forms.Select(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'ابحث عن القسم'
            }),
            'work_duration': forms.RadioSelect,        
            'clarity_statement': forms.RadioSelect,
            'roles_responsibilities': forms.RadioSelect,
            'communication_lines': forms.RadioSelect,
            'job_title_match': forms.RadioSelect,
            'decision_making': forms.RadioSelect,
            'reduces_overlap': forms.RadioSelect,
            'coordination': forms.RadioSelect,
            'service_quality': forms.RadioSelect,
            'strategic_alignment': forms.RadioSelect,
            'adaptability': forms.RadioSelect,
            'resource_allocation': forms.RadioSelect,
            'service_delivery': forms.RadioSelect,
            
            'challenges': forms.Textarea(attrs={'rows': 4}),
            'suitability': forms.Textarea(attrs={'rows': 4}),
            'improvements': forms.Textarea(attrs={'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['other_position'].required = False
        self.fields['department'].empty_label = 'ابحث أو اختر القسم'
        self.fields['position'].empty_label = 'ابحث أو اختر الوظيفة'    



class EmployeeDataForm(forms.ModelForm):
    class Meta:
        model = Employee_Data_Emergency
        fields = [
            'name', 'email', 'direct_manager_email', 
             'job_title'
        ]
        
        widgets = {
           
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'الاسم الكامل'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'example@company.com'
            }),

            'direct_manager_email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'manager@company.com'
            }),
           
            'job_title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'مثال: محاسب'
            }),
        }
        
        labels = {
            'name': 'اسم الموظف',
            'email': 'البريد الإلكتروني',
            'direct_manager_email': 'بريد المدير المباشر',
            'job_title': 'المسمى الوظيفي',
        }


class EmployeeٍSimCardForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].disabled = True
        self.fields['email'].disabled = True
        self.fields['department'].disabled = True
    class Meta:
        model = Employee_Sim_Card
        fields = [
            'name', 'email', 'department', 
             'sim_number'
        ]
        
        widgets = {
           
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'الاسم الكامل',
                'readonly': 'readonly',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'example@smrc.sd',
                'readonly': 'readonly',
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'الإدارة / القسم',
                'readonly': 'readonly',
            }),
            'sim_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'مثال: 0912345678'
            }),
        }
        
        labels = {
            'name': 'اسم الموظف',
            'email': 'البريد الإلكتروني',
            'department': 'الإدارة / القسم',
            'sim_number': 'رقم الشريحة',
        }

