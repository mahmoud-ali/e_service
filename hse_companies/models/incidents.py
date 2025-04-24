from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from company_profile.models import TblCompanyProduction
from pa.models import CURRENCY_TYPE_CHOICES, CURRENCY_TYPE_SDG
from workflow.model_utils import LoggingModel

class IncidentInfo(LoggingModel):
    # Incident Category choices
    CATEGORY_CHOICES = [
        ('OCC_HEALTH', 'Occupational Health'),
        ('SAFETY', 'Safety'),
        ('ENVIRONMENT', 'Environment'),
    ]
    
    # Incident Type choices
    TYPE_CHOICES = [
        (1, 'إصابة خطيرة – تطلبت المكوث Serious Injury - Hospitalisation'),
        (2, 'إصابة متوسطة - تطلبت عناية طبية  Moderate Injury - Medical Treated'),
        (3, 'إصابة بسيطة - تطلبت إسعافات أولية Minor Injury - Required First Aid'),
        (4, ' ضرر بالممتلكات Property Damage'),
        (5, 'وفاة Fatality'),
        (6, 'مرض مهني Occupational Illness'),
        (7, 'تلوث بيئي Environmental Contamination'),
        (8, 'حريق/إنفجار Fire/Explosions'),
        (9, 'تسرب مواد / كيماويات خطرة Hazardous Chemicals / Substances'),
        (10, 'حادث مركبة / آلية Vehicle / Equipment Incident'),
        (11, 'بادرة حادث Near Miss'),
        (12, 'اخرى Other'),
    ]
    
    # Incident Classification choices
    CLASSIFICATION_CHOICES = [
        (1, 'جسيم Major'),
        (2, 'متوسط Moderate'),
        (3, 'بسيط Minor'),
    ]
    
    # Location choices
    LOCATION_CHOICES = [
        (1, 'السفر ل/من العمل Travelling To/From Work'),
        (2, 'اثناء العمل On Duty'),
        (3, 'خارج مكان العمل(المعسكر مثلا) Off Duty (E.g. camp)'),
    ]
    
    # Employment Basis choices
    EMPLOYMENT_BASIS_CHOICES = [
        (1, 'دوام كامل Full Time'),
        (2, 'دوام جزئي Part Time'),
        (3, 'يومية Casual'),
        (4, 'متعاقد Contractor'),
    ]
    
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"),related_name="hse_incidents_report")    

    # Category, Type, and Classification
    incident_category = models.SmallIntegerField(choices=CATEGORY_CHOICES, verbose_name=_("فئة الحادث Incident Category"))
    incident_type = models.SmallIntegerField(choices=TYPE_CHOICES, verbose_name=_("نوع الحادث Incident Type"))
    other_type_details = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("في حال اخرى حدد If other specify"))
    classification = models.SmallIntegerField(choices=CLASSIFICATION_CHOICES, verbose_name=_("تصنيف الحادث Classification of Incident"))
    
    # Incident Details
    equipment_vehicle_no = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("رقم الآلية/العربة Equipment/Vehicle No"))
    client_contractor = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("اسم الشركة/المتعاقد Client/Contractor"))
    
    # Dates and Times
    date_time_occurred = models.DateTimeField(verbose_name=_("تاريخ وزمن وقوع الحادث Date & Time of Incident Occurred"))
    date_time_reported = models.DateTimeField(default=timezone.now, verbose_name=_("تاريخ وزمن التبليغ عن الحادث Date & Time of Incident Report"))
    reported_to = models.CharField(max_length=100, verbose_name=_("إسم الشخص المْبلغ له Person Incident Reported to"))
    
    # Location information
    location = models.SmallIntegerField(choices=LOCATION_CHOICES, verbose_name=_("مكان وقوع الحادث Incident Occurred at"))
    
    # Description
    incident_description = models.TextField(verbose_name=_("وصف الحادث Description of the Incident"))
    
    # Injured Person Details
    injured_surname = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("إسم المصاب Injured Surname"))
    injured_position = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("الوظيفة Position"))
    injured_experience_years = models.PositiveIntegerField(blank=True, null=True, verbose_name=_(" الخبرة بالأعوام Experience in Years"))
    injured_date_of_birth = models.DateField(blank=True, null=True, verbose_name=_("تاريخ الميلاد Date of Birth"))
    injured_employment_basis = models.SmallIntegerField(choices=EMPLOYMENT_BASIS_CHOICES, blank=True, null=True, verbose_name=_("نوع التوظيف Basis of Employment"))
    lost_time_injury = models.BooleanField(default=False, verbose_name=_("هل تسببت الإصابة في التغيب عن العمل؟ Did this incident cause of Lost Time of working days?"))
    lost_days = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("في حال كانت الإجابة نعم حدد عدد الأيام حتى تاريخ هذا التقرير If yes, specify Number of lost days up to this report"))
    
    # PPE Used During Incident
    ppe_gloves = models.BooleanField(default=False, verbose_name=_("قفازات Gloves"))
    ppe_helmet = models.BooleanField(default=False, verbose_name=_("خوذة Helmet"))
    ppe_safety_cloth = models.BooleanField(default=False, verbose_name=_("لبس السلامة Safety cloth"))
    ppe_safety_shoes = models.BooleanField(default=False, verbose_name=_("حذاء السلامة Safety Shoes"))
    ppe_face_protection = models.BooleanField(default=False, verbose_name=_("نظارة/واقي وجهGlass/face Protection"))
    ppe_ear_protection = models.BooleanField(default=False, verbose_name=_(" واقي الاذن Ear Protection"))
    ppe_mask = models.BooleanField(default=False, verbose_name=_("كمامة Mask"))
    ppe_other = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("اخرى Other"))
    
    # Injury/Illness Details
    nature_of_injury = models.TextField(blank=True, null=True, verbose_name=_("طبيعة الاصابة او المرض ( مثلا تمزق ، كسر، جرح) Nature of Injury or Illness (e.g. fracture, strain/sprain, bruising)"))
    bodily_location = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("مكان الاصابة بالجسم او المرض(مثلا اليد اليمنى، اسفل الظهر، الرئتين) Bodily Location of Injury or Illness (e.g. right leg, lower back)"))
    first_aid_details = models.TextField(blank=True, null=True, verbose_name=_("تفاصيل الاسعافات الاولية المقدمة للمصاب Details of Any First Aid Treatment Provided"))
    first_aider_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("اسم المسعف Name of First Aider"))
    hospital_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("في حالة تم نقله للمستشفى، اسم المستشفى If admitted to Hospital,hospital name"))
    
    # Property/Equipment Damage Details
    property_description = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("وصف للالية/الملكية المتضررة Description of Property/Equipment Damage"))
    damage_nature = models.TextField(blank=True, null=True, verbose_name=_("طبيعة الضرر للالية/الملكية Nature of Property/Equipment Damage"))
    material_spill_details = models.TextField(blank=True, null=True, verbose_name=_("تفاصيل كمية المواد المتسربة ونوعها Details of materials spill and quantities, its type"))
    
    # Cost Estimation
    control_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], verbose_name=_("تكلفة الاليات/المركبات/الاشخاص المستخدمة في التحكم في الحادث Cost of Equipment's/vehicle’s/human’s used to control Incident"))
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], verbose_name=_("تكلفة الحادث Cost of the accident"))
    other_expenses = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)], verbose_name=_("اي مصاريف اخرى Other expenses"))
    currency = models.CharField(max_length=10, choices=CURRENCY_TYPE_CHOICES, default=CURRENCY_TYPE_SDG, verbose_name=_("currency"))

    # Location and Operation at Time of Incident
    precise_location = models.TextField(verbose_name=_("تحديد موقع وقوع الحادث Precise location at which incident occurred"))
    precise_operation = models.TextField(verbose_name=_("وصف مختصر للعملية/المهمة اثناء وقوع الحادث Brief description of work in progress at time of incident"))

    #Site status
    site_closed_now = models.BooleanField(default=False, verbose_name=_("هل موقع العمل مغلق؟ Site closed now?"))
    site_closed_because_of_incident = models.BooleanField(default=False, verbose_name=_("تم الاغلاق نتيجة الحادث؟ Shutdown because of the incident?"))
    
    def __str__(self):
        return f"Incident {self.company} - {self.get_incident_type_display()} - {self.date_time_occurred}"
    
    class Meta:
        ordering = ['-date_time_occurred']
        verbose_name = 'Incident'
        verbose_name_plural = 'Incidents'

class IncidentWitness(models.Model):
    incident = models.ForeignKey(IncidentInfo, on_delete=models.CASCADE, related_name='incident_witnesses')
    name = models.CharField(max_length=100, verbose_name=_("إسم الشاهد Witness Name")) 
    job_title = models.CharField(max_length=100, verbose_name=_("المهنة Job Title"))
    statement = models.TextField(verbose_name=_("إفادة الشاهد/Witness Statement"))

    class Meta:
        verbose_name = 'إفادة الشاهد/Witness Statement'
        verbose_name_plural = 'إفادة الشهود/Witness Statements'

class IncidentPhoto(models.Model):
    def company_applications_path(instance, filename):
        return "company_{0}/hse/{1}".format(instance.incident.company.id, filename)    

    incident = models.ForeignKey(IncidentInfo, on_delete=models.CASCADE, related_name='incident_photos')
    photo = models.ImageField(upload_to=company_applications_path, verbose_name=_("الصورة Photo"))
    description = models.TextField(blank=True, null=True, verbose_name=_("وصف الصورة photo description"))

    class Meta:
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'

class IncidentAnalysis(LoggingModel):
    """Model for incident analysis and investigation"""
    incident = models.OneToOneField(IncidentInfo, on_delete=models.CASCADE, related_name='analysis')
    
    # Part 2 - Incident Analysis
    # Sequence of Events
    sequence_of_events = models.TextField(help_text="Describe the sequence of events leading to the incident", verbose_name=_("تتابع الاحداث Sequence of Events"))
    
    # Immediate Causes
    unsafe_acts = models.TextField(blank=True, null=True, help_text="مثلاً. السرعة الزائدة، تجاهل علامات السلامة، ... إلخ E.g. Speeding, Ignoring Safety Signs, etc.", verbose_name=_("افعال/تصرفات غير آمنة Unsafe Acts"))
    unsafe_conditions = models.TextField(blank=True, null=True, help_text="طريق رطب، أداة يدوية معابة/ لها عطل، ... إلخ E.g. Wet Road, defected tools, etc.", verbose_name=_("ظروف غير عمل غير آمنة Unsafe Conditions"))
    
    # Repeated Incident
    repeated_incident = models.BooleanField(default=False, verbose_name=_("هل هذا حادث مكرر؟ repeated incident?"))
    repeated_incident_reason = models.TextField(blank=True, null=True, verbose_name=_("في حالة الاجابة بنعم يرجى ذكر إجراءات التحكم الغير مجدية بالحادث السابق If yes, list the control failures at the previous "))
    
    def __str__(self):
        return f"Analysis for Incident {self.incident}"


class ContributingFactor(models.Model):
    """Model for factors that contributed to the incident"""
    FACTOR_CHOICES = [
        (1, 'بيئة العمل Work environment'),
        (2, ' الادوات، الالات او المنشاة Tools, equipment or plant'),
        (3, 'اجراءات العمل/القواعد Work procedures/rules'),
        (4, ' التواصل/المعلومات Communication/information'),

        (5, 'المناولة اليدوية Manual handling'),
        (6, 'النظافة والترتيب Housekeeping'),
        (7, 'اجهزة السلامة/التحذير Warning/safety devices'),
        (8, 'التدريب/مستوى المهارات Training/skill level'),

        (9, 'عوامل شخصية Personal factors'),
        (10, 'عوامل خارجية External factors'),
        (11, 'ادوات السلامة الشخصية Personal protective equipment'),
        (12, 'اخرى Other'),
    ]
    
    incident_analysis = models.ForeignKey(IncidentAnalysis, on_delete=models.CASCADE, related_name='contributing_factors')
    factor_type = models.SmallIntegerField(choices=FACTOR_CHOICES, verbose_name=_("الاسباب المساهمة في الحادث Contributing Causes"))
    description = models.TextField(help_text="Explain how this factor contributed to the incident", verbose_name=_("وصف الاسباب المساهمة في الحادث contributing factors description"))
    
    def __str__(self):
        return f"{self.get_factor_type_display()} - {self.incident_analysis.incident.id}"


class FactorsAssessment(models.Model):
    """Model for assessing various factors related to the incident"""
    incident = models.OneToOneField(IncidentInfo, on_delete=models.CASCADE, related_name='factors_assessment')

    # Documents related to incident
    related_documents_exist = models.BooleanField(default=False, verbose_name=_("هل يوجد وثائق تتعلق بالحادث؟ Were there any documents related to incident?"))
    related_documents_details = models.TextField(blank=True, null=True, 
                                               help_text="Policies, instructions, working procedures, JSA, risk assessment, etc.", verbose_name=_("تفاصيل الوثائق documents details"))
    
    # Control failures
    failed_controls = models.TextField(blank=True, null=True, 
                                     help_text="From Risk Assessment, what were the failed or absent controls?", verbose_name=_('من تقييم درجة المخاطر، ماهي إجراء"ت" التحكم الغائبة او التي فشلت؟ From Risk Assessment, what was the failed or absent control’s?'))
        
    # People/supervision factors
    supervisor_present = models.BooleanField(default=False, verbose_name=_("هل كان يوجد مشرف وردية وقت وقوع الحادث؟ Was there a supervisor on shift at the time of incident?"))
    supervisor_presence_reason = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))
    
    supervisor_hazard_competency = models.BooleanField(default=False, verbose_name=_("هل المشرف ذا كفاءة وقدرة لتمييز المخاطر بمكان العمل؟ Supervisor’s competency of workplace hazards?"))
    supervisor_hazard_reason = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))
    
    supervisor_controls_competency = models.BooleanField(default=False, verbose_name=_("هل المشرف ذا كفاءة باجراءات التحكم؟ Supervisor’s competency in controls? (SOP & procedures)"))
    supervisor_controls_reason = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))
    
    person_hazard_competency = models.BooleanField(default=False, verbose_name=_("هل الشخص المعني بالحادث ذا كفاءة لتمييز المخاطر بمكان العمل؟ Competency of workplace hazards?"))
    person_hazard_reason = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))

    competency_in_controls = models.BooleanField(default=False, verbose_name=_("هل هو ذا كفاءة بإجراءات التحكم؟ Competency in controls? (SOP & procedures)"))
    competency_controls_reason = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))
    
    correct_ppe_worn = models.BooleanField(default=False, verbose_name=_("هل كان يرتدي ادوات السلامة المناسبة للعملية؟ Was the correct PPE worn"))
    ppe_reason = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))
    
    technical_competence = models.BooleanField(default=False, verbose_name=_("هل هو ذا كفاءة فنية لاداء المهمة؟ Was the person technically competent to do the task?"))
    technical_competence_reason = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))
    
    fatigue_factor = models.BooleanField(default=False, verbose_name=_("هل لعب الارهاق دوراً في  الحادث؟ Did fatigue play a role in an incident?"))
    fatigue_reason = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))
    
    substance_abuse_factor = models.BooleanField(default=False, verbose_name=_("هل لعب تناول الكحول/سوء استخدام العقاقير دوراً في الحادث؟ Did alcohol/substance abuse play a role in the incident?"))
    substance_abuse_reason = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))
    
    # Equipment factors
    correct_equipment_used = models.BooleanField(default=False, verbose_name=_("هل تم استخدام الالية المناسبة؟ Was the correct equipment used"))
    equipment_reason = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))
    
    equipment_good_condition = models.BooleanField(default=False, verbose_name=_("هل كانت الآلية بحالة جيدة؟ Was the equipment in good condition"))
    equipment_condition_reason = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))
    
    equipment_inspected = models.BooleanField(default=False, help_text=_("قائمة فحص قبل الاستخدام والفحص الشهري Pre-use checklist & Monthly inspection"), verbose_name=_("هل تم فحص الآلية؟ Was the equipment inspected?"))
    equipment_inspection_reason = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))
    
    # Risk factors
    risk_assessment_conducted = models.BooleanField(default=False, verbose_name=_("هل تم اجراء تقييم مخاطر قبل المهمة؟ Was a pre-task Risk Assessment conducted?"))
    risk_assessment_reason = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))
    
    area_declared_safe = models.BooleanField(default=False, verbose_name=_("هل تم التصريح بان المنطقة امنة؟ او تم اصدار تصريح عمل؟ Was the area declared safe? Or was a permit to work issued?"))
    area_safety_reason = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))
    
    changes_after_declaration = models.BooleanField(default=False, verbose_name=_("هل حدثت اي تغييرات بعد التصريح بان المنطقة امنة/ماقبل المهمة/تصريح العمل حتى وقوع الحادث؟ Did any changes occur after the safe declaration/pre-task/PTW until incident?"))
    changes_details = models.TextField(blank=True, null=True, verbose_name=_("اعطي سبب give reason"))
        
    other_root_causes = models.TextField(blank=True, null=True, verbose_name=_("اي اسباب جذرية اخرى تتعلق بوقوع الحادث؟ Any other root causes?"))
        
    def __str__(self): 
        return f"Factors Assessment for Incident {self.incident}"
    
class LeasonLearnt(models.Model):
    """Model for leason learnt related to the incident"""
    incident = models.OneToOneField(IncidentInfo, on_delete=models.CASCADE, related_name='leasons_learnt')
    leason = models.TextField(verbose_name=_("الدروس المستفادة Lesson Learnt"))

    def __str__(self): 
        return f"Leason learnt for Incident {self.incident}"
