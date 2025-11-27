from django import forms
from .models import MosamaWazifi,EmergencyEvaluation ,Employee_Data_Emergency,SurveyResponse

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



class SurveyResponseForm(forms.ModelForm):
    class Meta:
        model = SurveyResponse
        fields = [
            'wilaya','position', 'other_position', 'work_duration',
            'clarity_statement', 'roles_responsibilities', 'communication_lines', 'job_title_match',
            'decision_making', 'reduces_overlap', 'coordination', 'service_quality',
            'strategic_alignment', 'adaptability', 'resource_allocation', 'service_delivery',
            'challenges', 'suitability', 'improvements'
        ]
        
        
        widgets = {
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

