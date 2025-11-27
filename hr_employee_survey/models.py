from django.db import models
from hr.models import EmployeeBasic,MosamaWazifi,HikalWazifi
from django.utils.translation import gettext_lazy as _

RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
WARNING_CHOICES = [(i, str(i)) for i in range(0, 6)]
GENERAL_RATING = [
    ("excellent", "ممتاز"),
    ("very_good", "جيد جدًا"),
    ("good", "جيد"),
    ("acceptable", "مقبول"),
    ("weak", "ضعيف"),
]

ASKING_CHOICES  = [
    ("yes", "نعم"),
    ("no", "لا"),
]

PERCENTAGE_CHOICES = [
    ("high", "عالية"),
    ("medium", "متوسطة"),
    ("low", "ضعيفة"),
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
    
    employee_code = models.IntegerField(verbose_name="كود الموظف",null=True, blank=True,)
    employee_name = models.CharField(max_length=150,null=True, blank=True,verbose_name="اسم الموظف  ")
    email = models.CharField(max_length=150,null=True, blank=True, verbose_name=" البريد الالكتروني للموظف ")
    
    job_number = models.CharField(max_length=50,null=True, blank=True, verbose_name="رقم الموظف")  
    job_title = models.CharField(max_length=100,null=True, blank=True,verbose_name=" المسمى الوظيفي")
    direct_manager = models.CharField(max_length=100,null=True, blank=True, verbose_name=" المدير المباشر")
    direct_manager_email = models.CharField(max_length=100, null=True, blank=True,verbose_name=" ")
    period_from = models.DateField(verbose_name="من",null=True, blank=True)
    period_to = models.DateField(verbose_name="الي" , null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True , null=True, blank=True,verbose_name="تم الانشاء في ")

    attendance_discipline = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True,verbose_name=" الالتزام بالحضور والانضباط")
    follow_instructions = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True,verbose_name="احترام التعليمات ")
    task_responsibility = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True,verbose_name=" تحمل المسؤولية وتعدد المهام")
    teamwork = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True,verbose_name=" التعاون والعمل ضمن فريق")
    communication = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True,verbose_name=" التواصل الفعال")

    main_tasks_quality = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True,verbose_name="انجاز المهام الرئيسية بجودة وكفاءة ")
    extra_tasks = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True,verbose_name=" إنجاز المهام الاضافية خارج التوصيف ")
    work_pressure = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True,verbose_name=" القدرة علي التكيف مع ضغط العمل ")
    policies_commitment = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True,verbose_name=" الالتزام بالاجراءات والسياسات")
    creativity = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True,verbose_name="الابداع في تقديم الحلول ")

    overall_performance = models.CharField(max_length=20, choices=GENERAL_RATING, null=True, blank=True,verbose_name=" مستوي الانجاز العام")
    emergency_response = models.CharField(max_length=20, choices=GENERAL_RATING, null=True, blank=True,verbose_name=" مدي الاستجابة لعمل لطبيعة العمل ")
    coverage_percentage = models.CharField(max_length=20, choices=PERCENTAGE_CHOICES, null=True, blank=True,verbose_name=" نسبة تغطية الفجوة")

    strengths = models.TextField( null=True, blank=True,verbose_name=" نقاط القوة لدى الموظف ")
    challenges = models.TextField( null=True, blank=True,verbose_name=" التحديات")
    training_needs = models.TextField(null=True, blank=True,verbose_name=" الاحتياجات التدريبية ")
    manager_notes = models.TextField(null=True, blank=True,verbose_name="تعليق المدير المباشر")

    average_attendance = models.CharField(max_length=20, choices=GENERAL_RATING, null=True, blank=True,verbose_name= "متوسط نسبة الحصور والانصراف")
    attendance_punctnality = models.CharField(max_length=20, choices=GENERAL_RATING, null=True, blank=True,verbose_name="الالتزام بمواعيد الدوام")
    violation_count = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True,verbose_name="عدد المخالفات الادارية المسجلة")
    warnings_count = models.IntegerField(choices=WARNING_CHOICES, null=True, blank=True,verbose_name="عدد الانزارات او التنبيهات الادارية")
        
    employee_effective = models.CharField(max_length=20, choices=ASKING_CHOICES, null=True, blank=True,verbose_name="هل ترى أن الموظف كان فاعلاً ")
    recommendations_continue = models.CharField(max_length=20, choices=ASKING_CHOICES, null=True, blank=True,verbose_name="هل توصي باستمراره ضمن فريق العمل ")
    substantive_note = models.TextField(null=True, blank=True,verbose_name="هل هنالك ملاحظات جوهرية على أدائه ")

    class Meta:
          verbose_name = "تقييم العاملين فترة الطوارئ"
    def __str__(self):
        return f"استبيان من {self.employee_name} "
    


CHOICES_LIKERT = [
    (5, 'أوافق بشدة'),
    (4, 'أوافق'),
    (3, 'محايد'),
    (2, 'لا أوافق'),
    (1, 'لا أوافق بشدة'),
]

CHOICES_POSITION = [
    ('تنفيذ', 'موظف تنفيذ'),
    ('مشرف', 'مشرف وحدة'),
    ('رئيس_قسم', 'رئيس قسم / مدير الولاية'),
    ('آخر', 'آخر (يرجى التحديد)'),
]

CHOICES_WORK_DURATION = [
    ('اقل_سنةmi', 'أقل من سنة'),
    ('1_3', 'من 1 إلى 3 سنوات'),
    ('3_5', 'من 3 إلى 5 سنوات'),
    ('more_5', 'أكثر من 5 سنوات'),
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
    department = models.ForeignKey(HikalWazifi, on_delete=models.PROTECT, verbose_name=_("الإدارة / القسم"), blank=True, null=True) 
    position = models.ForeignKey(MosamaWazifi, on_delete=models.PROTECT, verbose_name=_("المسمى الوظيفي"), blank=True, null=True)
    other_position = models.CharField(max_length=100,  verbose_name="تحديد الوظيفة الأخرى", blank=True, null=True)
    work_duration = models.CharField(max_length=50, choices=CHOICES_WORK_DURATION, verbose_name="مدة العمل بالشركة", blank=True, null=True)
    
    clarity_statement = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="الهيكل التنظيمي الجديد واضح ومفهوم لجميع العاملين", blank=True, null=True)
    roles_responsibilities = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="هناك تحديد دقيق للصلاحيات والمسؤوليات لكل وظيفة", blank=True, null=True)
    communication_lines = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="خطوط التواصل الإداري واضحة وسلسة" , blank=True, null=True)
    job_title_match = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="المسمى الوظيفي يتماشى مع طبيعة المهام", blank=True, null=True)
    
    decision_making = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="الهيكل الحالي يسهل اتخاذ القرار الإداري", blank=True, null=True)
    reduces_overlap = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="يقلل من التداخل والازدواجية في المهام", blank=True, null=True)
    coordination = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="يسهل التنسيق والعلاقات بين الإدارات والوحدات", blank=True, null=True)
    service_quality = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="يساهم في تحسين جودة الخدمات المقدمة والإجراءات", blank=True, null=True)
    
    strategic_alignment = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="الهيكل يتماشى مع أهداف الخطة التشغيلية للشركة", blank=True, null=True)
    adaptability = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="قابل للتحديث والتعديل حسب المتغيرات" , blank=True, null=True)
    resource_allocation = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="يسمح بتوزيع الموارد البشرية بكفاءة", blank=True, null=True)
    service_delivery = models.IntegerField(choices=CHOICES_LIKERT, verbose_name="يساعد في تقديم خدمات أكثر فاعلية", blank=True, null=True)

    challenges = models.TextField(verbose_name="1. ما أبرز التحديات التي لاحظتها منذ تطبيق الهيكل الجديد؟" , blank=True, null=True)
    suitability = models.TextField(verbose_name="2. هل ترى أن الهيكل الجديد مناسب لطبيعة العمل في ولايتك / إدارتك؟ ولماذا؟", blank=True, null=True)
    improvements = models.TextField(verbose_name="3. ما التعديلات أو التحسينات التي تقترحها على الهيكل التنظيمي؟", blank=True, null=True)
    
    submission_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"استبيان من {self.wilaya} - {self.department}"