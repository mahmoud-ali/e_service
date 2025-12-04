from django.db import models
from hr.models import EmployeeBasic,MosamaWazifi,HikalWazifi
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
WARNING_CHOICES = [(i, str(i)) for i in range(0, 6)]
GENERAL_RATING = [(i, str(i)) for i in range(0, 6)]
PERCENTAGE_CHOICES= []
RATING_MAPPING = {
    "excellent": 5, "very_good": 4, "good": 3, "acceptable": 2, "weak": 1,
}

ASKING_CHOICES  = [
    ("1", "نعم"),
    ("0", "لا"),
]

RATING_FIELDS = [
    'attendance_discipline', 'follow_instructions', 'task_responsibility',
    'teamwork', 'communication', 'main_tasks_quality', 'extra_tasks',
    'work_pressure', 'policies_commitment', 'creativity'
]

class Employee_Data_Emergency(models.Model):
   
    name = models.CharField(
        max_length=255, 
        verbose_name="اسم الموظف"
    )
    email = models.EmailField(
        unique=True, 
        verbose_name="البريد الإلكتروني"
    )

    direct_manager_email = models.EmailField(
        verbose_name="بريد المدير المباشر",
        null=True, 
        blank=True
    ) 

    job_title = models.CharField(
        max_length=255, 
        verbose_name="المسمى الوظيفي "
    )  

    class Meta:
        verbose_name = "بيانات موظف مستوردة من بيانات المباشرين"



class EmergencyEvaluation(models.Model):
    
    employee_code = models.IntegerField(verbose_name="كود الموظف")
    employee_name = models.CharField(max_length=150,verbose_name="اسم الموظف  ")
    email = models.CharField(max_length=150, verbose_name=" البريد الالكتروني للموظف ")
    
    job_title = models.CharField(max_length=100,verbose_name=" المسمى الوظيفي")
    direct_manager = models.CharField(null=True, blank=True,max_length=100, verbose_name=" المدير المباشر")
    direct_manager_email = models.CharField(null=True, blank=True,max_length=100, verbose_name=" ")
    period_from = models.DateField(verbose_name="من")
    period_to = models.DateField(verbose_name="الي" )
    created_at = models.DateTimeField(auto_now_add=True , verbose_name="تم الانشاء في ",null=True, blank=True)

    attendance_discipline = models.IntegerField(choices=RATING_CHOICES, verbose_name=" الالتزام بالحضور والانضباط")
    follow_instructions = models.IntegerField(choices=RATING_CHOICES, verbose_name="احترام التعليمات ")
    task_responsibility = models.IntegerField(choices=RATING_CHOICES, verbose_name=" تحمل المسؤولية وتعدد المهام")
    teamwork = models.IntegerField(choices=RATING_CHOICES, verbose_name=" التعاون والعمل ضمن فريق")
    communication = models.IntegerField(choices=RATING_CHOICES, verbose_name=" التواصل الفعال")

    main_tasks_quality = models.IntegerField(choices=RATING_CHOICES,verbose_name="انجاز المهام الرئيسية بجودة وكفاءة ")
    extra_tasks = models.IntegerField(choices=RATING_CHOICES,verbose_name=" إنجاز المهام الاضافية خارج التوصيف ")
    work_pressure = models.IntegerField(choices=RATING_CHOICES, verbose_name=" القدرة علي التكيف مع ضغط العمل ")
    policies_commitment = models.IntegerField(choices=RATING_CHOICES, verbose_name=" الالتزام بالاجراءات والسياسات")
    creativity = models.IntegerField(choices=RATING_CHOICES, verbose_name="الابداع في تقديم الحلول ")

    overall_performance = models.CharField(null=True, blank=True,max_length=20 ,verbose_name=" مستوي الانجاز العام")
    emergency_response = models.IntegerField( choices=RATING_CHOICES, verbose_name=" مدي الاستجابة لعمل لطبيعة العمل ")
    coverage_percentage = models.IntegerField( choices=RATING_CHOICES, verbose_name=" نسبة تغطية الفجوة")

    strengths = models.TextField(verbose_name=" نقاط القوة لدى الموظف ")
    challenges = models.TextField(verbose_name=" التحديات")
    training_needs = models.TextField(verbose_name=" الاحتياجات التدريبية ")
    manager_notes = models.TextField(verbose_name="تعليق المدير المباشر")

    average_attendance = models.IntegerField(max_length=20, choices=GENERAL_RATING, null=True, blank=True,verbose_name= "متوسط نسبة الحصور والانصراف")
    attendance_punctnality = models.IntegerField(max_length=20, choices=GENERAL_RATING, null=True, blank=True,verbose_name="الالتزام بمواعيد الدوام")
    violation_count = models.IntegerField(choices=WARNING_CHOICES, null=True, blank=True,verbose_name="عدد المخالفات الادارية المسجلة")
    warnings_count = models.IntegerField(choices=WARNING_CHOICES, null=True, blank=True,verbose_name="عدد الانزارات او التنبيهات الادارية")
        
    employee_effective = models.CharField(null=True, blank=True,max_length=20, choices=ASKING_CHOICES,verbose_name="هل ترى أن الموظف كان فاعلاً ")
    recommendations_continue = models.CharField(null=True, blank=True,max_length=20, choices=ASKING_CHOICES,verbose_name="هل توصي باستمراره ضمن فريق العمل ")
    substantive_note = models.TextField(null=True, blank=True,verbose_name="هل هنالك ملاحظات جوهرية على أدائه ")
    manager_average_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="متوسط تقييم المدير ")
    
    def clean(self):
        super().clean()
        if self.period_from and self.period_to:
            if self.period_to < self.period_from:
                raise ValidationError({
                    'period_to': 'تاريخ النهاية يجب أن يكون مساوياً أو بعد تاريخ البداية.'
                })
                
    def _get_numerical_score_from_hr(self, field_name):
        value = getattr(self, field_name)

        if value is None or value == '':
            return None
            
        if field_name in ['violation_count', 'warnings_count']:
            try:
                val = int(value)
                if val == 0: return 5
                elif val == 1: return 4
                elif val == 2: return 3
                elif val == 3: return 2
                else: return 1
            except:
                return None
        return None

    def _calculate_manager_average(self):
        total_sum = 0
        count = 0
        for field_name in RATING_FIELDS:
            value = getattr(self, field_name)
            if value is not None and value != '':
                try:
                    total_sum += int(value)
                    count += 1
                except ValueError:
                    continue 
        return round( (total_sum / count), 2 ) if count > 0 else None

    def _hr_data_is_complete(self):
        hr_fields = ['average_attendance', 'attendance_punctnality', 'violation_count', 'warnings_count']
        for field in hr_fields:
            value = getattr(self, field)
            if value is None or value == '':
                return False
        return True
    
    def _calculate_combined_average(self):
        total_sum = 0
        count = 0
        
        for field_name in RATING_FIELDS:
            value = getattr(self, field_name)
            if value is not None and value != '':
                try:
                    total_sum += int(value)
                    count += 1
                except ValueError:
                    continue 
                    
        hr_fields = ['average_attendance', 'attendance_punctnality', 'violation_count', 'warnings_count']
        if self._hr_data_is_complete():
            for field_name in hr_fields:
                hr_score = self._get_numerical_score_from_hr(field_name)
                if hr_score is not None:
                    total_sum += hr_score
                    count += 1
        
        return round((total_sum / count), 2) if count > 0 else None


    def _get_overall_rating_key(self, average):
        if average is None: return None
        
        if average >= 4.21:
            return "excellent"
        
        elif average >= 3.41:
            return "very_good"
            
        elif average >= 2.61:
            return "good"
            
        elif average >= 1.81:
            return "acceptable"
            
        elif average >= 1.0:
            return "weak"
        
        else:
            return "weak" 

    def clean(self):
        super().clean()
        if self.period_from and self.period_to:
            if self.period_to < self.period_from:
                raise ValidationError({
                    'period_to': _('تاريخ النهاية يجب أن يكون مساوياً أو بعد تاريخ البداية.')
                })

    def save(self, *args, **kwargs):  
        manager_avg = self._calculate_manager_average()
        if manager_avg is not None:
            self.manager_average_score = manager_avg
            
        final_combined_avg = self._calculate_combined_average()
        if final_combined_avg is not None:
            final_rating_key = self._get_overall_rating_key(final_combined_avg)
            self.overall_performance = final_rating_key
        else:
            self.overall_performance = None 
        
        super().save(*args, **kwargs)

    class Meta:
          verbose_name = "تقييم العاملين فترة الطوارئ"
          verbose_name_plural = "تقييمات العاملين فترة الطوارئ"
          
    def __str__(self):
        return f"استبيان من {self.employee_name}"
    
CHOICES_LIKERT = [
    (1, 'أوافق بشدة'),
    (2, 'أوافق'),
    (3, 'محايد'),
    (4, 'لا أوافق'),
    (5, 'لا أوافق بشدة'),
]

CHOICES_POSITION = [
    ('تنفيذ', 'موظف تنفيذ'),
    ('مشرف', 'مشرف وحدة'),
    ('رئيس_قسم', 'رئيس قسم / مدير الولاية'),
    ('آخر', 'آخر (يرجى التحديد)'),
]

CHOICES_WORK_DURATION = [
    ('Less_than_year', 'أقل من سنة'),
    ('1_3', 'من 1 إلى 3 سنوات'),
    ('3_5', 'من 3 إلى 5 سنوات'),
    ('more_than_5', 'أكثر من 5 سنوات'),
]


CHOICES_WILAYA = [
    ('Blue_Nile',  'النيل الازرق'),
    ('Kassala',  'كسلا'),
    ('Red_Sea',  'البحر الاحمر'),
    ('River_Nile',  'نهر النيل'),
    ('Al_Qadarif',  'القضارف'),
    ('South_Kordofan',  'جنوب كردفان'),
    ('West_Kordofan',  'غرب كردفان'), 
    ('North_Kordofan',  'شمال كردفان'),
    ('White_Nile','النيل الابيض'),
    ('Central_Darfur','وسط دارفور'),
    ('East_Darfur','شرق دارفور'),
    ('South_Darfur','جنوب دارفور'),
    ('West_Darfur','غرب دارفور'),
    ('Northern','الولاية الشمالية'),
]


class SurveyResponse(models.Model):
    wilaya = models.CharField(max_length=100, choices=CHOICES_WILAYA, verbose_name="الولاية")
    department = models.ForeignKey(HikalWazifi,blank=True, null=True, on_delete=models.PROTECT, verbose_name=_("الإدارة / القسم")) 
    position = models.ForeignKey(MosamaWazifi, on_delete=models.PROTECT, verbose_name=_("المسمى الوظيفي"))
    other_position = models.CharField(blank=True, null=True,max_length=100,  verbose_name="تحديد الوظيفة الأخرى")
    work_duration = models.CharField(max_length=50, choices=CHOICES_WORK_DURATION, verbose_name="مدة العمل بالشركة")
    
    clarity_statement = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="الهيكل التنظيمي الجديد واضح ومفهوم لجميع العاملين")
    roles_responsibilities = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="هناك تحديد دقيق للصلاحيات والمسؤوليات لكل وظيفة")
    communication_lines = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="خطوط التواصل الإداري واضحة وسلسة" )
    job_title_match = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="المسمى الوظيفي يتماشى مع طبيعة المهام")
    
    decision_making = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="الهيكل الحالي يسهل اتخاذ القرار الإداري")
    reduces_overlap = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="يقلل من التداخل والازدواجية في المهام")
    coordination = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="يسهل التنسيق والعلاقات بين الإدارات والوحدات")
    service_quality = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="يساهم في تحسين جودة الخدمات المقدمة والإجراءات")
    
    strategic_alignment = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="الهيكل يتماشى مع أهداف الخطة التشغيلية للشركة")
    adaptability = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="قابل للتحديث والتعديل حسب المتغيرات" )
    resource_allocation = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="يسمح بتوزيع الموارد البشرية بكفاءة")
    service_delivery = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="يساعد في تقديم خدمات أكثر فاعلية")

    challenges = models.TextField(blank=True, null=True,verbose_name="1. ما أبرز التحديات التي لاحظتها منذ تطبيق الهيكل الجديد؟" )
    suitability = models.TextField(blank=True, null=True,verbose_name="2. هل ترى أن الهيكل الجديد مناسب لطبيعة العمل في ولايتك / إدارتك؟ ولماذا؟")
    improvements = models.TextField(blank=True, null=True,verbose_name="3. ما التعديلات أو التحسينات التي تقترحها على الهيكل التنظيمي؟")
    
    submission_date = models.DateTimeField(auto_now_add=True)
    overall_evaluation = models.CharField(blank=True, null=True,max_length=20, verbose_name=" التقييم بصورة عامة للهيكل  ")
    average_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="متوسط تقييم")

    def calculate_likert_average(self):

            likert_fields = [
                self.clarity_statement,
                self.roles_responsibilities,
                self.communication_lines,
                self.job_title_match,
                self.decision_making,
                self.reduces_overlap,
                self.coordination,
                self.service_quality,
                self.strategic_alignment,
                self.adaptability,
                self.resource_allocation,
                self.service_delivery,
            ]
            
            if all(field is not None for field in likert_fields):
                total_sum = sum(likert_fields)
                num_fields = len(likert_fields)
                
                average = total_sum / num_fields
                return round(average, 2)
            
            return None 
        
    def get_overall_evaluation_text(self):
     
        average = self.calculate_likert_average()
        self.average_score = average
        print(average)
        if average is None:
            return "بيانات غير مكتملة"

        if 5.00 >= average >= 4.21:
            return "غير فعال"
        elif 4.20 >= average >= 3.41:
            return "ضعيف"
        elif 3.40 >= average >= 2.61:
            return "متوسط"
        elif 2.60 >= average >= 1.81:
            return "فعال"
        elif 1.80 >= average >= 1.00:
            return "فعال جدا"
        else:
            return "خارج النطاق"


    def save(self, *args, **kwargs):
        
        evaluation = self.get_overall_evaluation_text()
        
        if evaluation:
            self.overall_evaluation = evaluation
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"استبيان من {self.wilaya} - {self.department}"