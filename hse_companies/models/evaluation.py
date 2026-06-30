from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from company_profile.models import TblCompanyProduction, LkpState, LkpLocality
from workflow.model_utils import LoggingModel

SCORE_CHOICES = (
    (0, _("المعيار غير موجود أصلاً")),
    (1, _("دون الوسط - غير مقبول (تقل عن 33%)")),
    (2, _("متوسط - مقبول ويحتاج إلى تحسين (34% - 66%)")),
    (3, _("أعلى من الوسط - جيد إلى ممتاز (تزيد عن 67%)")),
)

class TblCompanyEvaluationSession(LoggingModel):
    company = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT, verbose_name=_("company"), related_name="evaluations")
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"), blank=True, null=True)
    locality = models.ForeignKey(LkpLocality, on_delete=models.PROTECT, verbose_name=_("locality"), blank=True, null=True)
    evaluation_date = models.DateField(default=timezone.now, verbose_name=_("تاريخ التقييم"))

    class Meta:
        verbose_name = "تقييم الشركة (HSE)"
        verbose_name_plural = "تقييمات الشركات (HSE)"
        ordering = ['-evaluation_date']

    def __str__(self):
        return f"{self.company} - {self.evaluation_date}"


class TblCompanyEvaluationEnvironment(LoggingModel):
    session = models.OneToOneField(TblCompanyEvaluationSession, on_delete=models.CASCADE, related_name="environment", verbose_name="جلسة التقييم", null=True, blank=True)

    env_mercury_condenser_smelting = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="وجود مكثف زئبق في غرفة الصهر")
    env_mercury_condenser_cell = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="وجود مكثف زئبق في الخلية")
    env_sanitation_system = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="نظام صرف الصحي")
    env_containment_basins = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="أحواض الاحتواء")
    env_cyanide_mixer = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="خلاط السيانيد")
    env_solution_connections_safety = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="سلامة توصيلات المحاليل")
    env_solution_basins_insulation = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="عزل احواض المحاليل")
    env_noise_control_mechanism = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="آلية التحكم في الضوضاء")
    env_dust_control_mechanism = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="آلية التحكم في الغبار")
    env_tailings_storage = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="مخزن الكرته")
    env_basins_fencing = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="تسوير الاحواض")
    env_landfill = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="مكب النفايات")

    class Meta:
        verbose_name = "تقييم البيئة"
        verbose_name_plural = "تقييمات البيئة"

    def __str__(self):
        return f"بيئة - {self.session}"

    def get_average_score(self):
        fields = [
            self.env_mercury_condenser_smelting,
            self.env_mercury_condenser_cell,
            self.env_sanitation_system,
            self.env_containment_basins,
            self.env_cyanide_mixer,
            self.env_solution_connections_safety,
            self.env_solution_basins_insulation,
            self.env_noise_control_mechanism,
            self.env_dust_control_mechanism,
            self.env_tailings_storage,
            self.env_basins_fencing,
            self.env_landfill,
        ]
        valid_scores = [s for s in fields if s > 0]
        if not valid_scores:
            return 0.0
        return round(sum(valid_scores) / len(valid_scores), 2)


class TblCompanyEvaluationSafety(LoggingModel):
    session = models.OneToOneField(TblCompanyEvaluationSession, on_delete=models.CASCADE, related_name="safety", verbose_name="جلسة التقييم", null=True, blank=True)

    safe_mine_barriers = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="حواجز المناجم")
    safe_mine_faces = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="واجهات المناجم")
    safe_mine_lighting = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="إضاءة المناجم")
    safe_food_storage = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="مخزن المواد الغذائية")
    safe_kitchen = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="المطبخ")
    safe_dining_hall = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="صالة الطعام")
    safe_meals = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="الوجبات الغذائية")
    safe_accommodation_rooms = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="غرف السكن")
    safe_accommodation_toilets = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="دورات مياه السكن")
    safe_drinking_water_quality = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="جودة مياه الشرب")
    safe_hcn_detector = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="وجود HCN Dector")
    safe_smelting_room_compliance = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="مطابقة غرفة الصهر")
    safe_chemical_storage_compliance = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="مطابقة مخزن المواد الكيميائية")
    safe_cyanide_storage_compliance = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="مطابقة مخزن السيانيد")
    safe_vehicles_machinery_safety = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="سلامة المركبات والآليات")
    safe_work_environment_quality = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="جودة بيئة العمل")
    safe_specialized_training = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="وجود تدريب مختص")
    safe_electrical_connections_safety = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="سلامة التوصيلات الكهربائية")
    safe_ppe = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="PPE")
    safe_ptw = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="PTW")
    safe_safety_signs = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="علامات السلامة الإرشادية والتحذيرية")
    safe_initial_medical_check = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="الفحص الطبي الأولي")
    safe_periodic_medical_check = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="الفحص الطبي الدوري")
    safe_first_aid_boxes = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="صناديق الاسعافت الأولية")
    safe_firefighting_system = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="نظام مكافحة حرائق")
    safe_health_unit = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="وحدة صحية")

    class Meta:
        verbose_name = "تقييم السلامة"
        verbose_name_plural = "تقييمات السلامة"

    def __str__(self):
        return f"سلامة - {self.session}"

    def get_average_score(self, company_type=None):
        from company_profile.models import TblCompany
        fields = []
        # إضافة حقول المناجم فقط لشركات غير مخلفات
        if company_type is None:
            try:
                company_type = self.session.company.company_type
            except Exception:
                pass
        if company_type != TblCompany.COMPANY_TYPE_MOKHALFAT:
            fields += [
                self.safe_mine_barriers,
                self.safe_mine_faces,
                self.safe_mine_lighting,
            ]
        fields += [
            self.safe_food_storage,
            self.safe_kitchen,
            self.safe_dining_hall,
            self.safe_meals,
            self.safe_accommodation_rooms,
            self.safe_accommodation_toilets,
            self.safe_drinking_water_quality,
            self.safe_hcn_detector,
            self.safe_smelting_room_compliance,
            self.safe_chemical_storage_compliance,
            self.safe_cyanide_storage_compliance,
            self.safe_vehicles_machinery_safety,
            self.safe_work_environment_quality,
            self.safe_specialized_training,
            self.safe_electrical_connections_safety,
            self.safe_ppe,
            self.safe_ptw,
            self.safe_safety_signs,
            self.safe_initial_medical_check,
            self.safe_periodic_medical_check,
            self.safe_first_aid_boxes,
            self.safe_firefighting_system,
            self.safe_health_unit,
        ]
        valid_scores = [s for s in fields if s > 0]
        if not valid_scores:
            return 0.0
        return round(sum(valid_scores) / len(valid_scores), 2)


class TblCompanyEvaluationGeneral(LoggingModel):
    session = models.OneToOneField(TblCompanyEvaluationSession, on_delete=models.CASCADE, related_name="general", verbose_name="جلسة التقييم", null=True, blank=True)

    gen_monthly_reports_commitment = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="الالتزام بالتقارير الشهرية")
    gen_corrective_actions_commitment = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="الإلتزام بتنفيذ الإجراءات التصحيحية")
    gen_company_site_fencing = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="تسوير موقع الشركة")
    gen_waste_management_plan = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="خطة إدارة النفايات")
    gen_emergency_plan = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="خطة طواريء ERP & EAP")
    gen_hse_plan = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="خطة HSE")
    gen_hse_policy = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="سياسة HSE")
    gen_esia = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="ESIA")
    gen_qualified_hse_officer = models.IntegerField(choices=SCORE_CHOICES, default=0, verbose_name="وجود مسؤول بيئة وسلامة مؤهل")

    class Meta:
        verbose_name = "تقييم المطلوبات العامة"
        verbose_name_plural = "تقييمات المطلوبات العامة"

    def __str__(self):
        return f"عام - {self.session}"

    def get_average_score(self):
        fields = [
            self.gen_monthly_reports_commitment,
            self.gen_corrective_actions_commitment,
            self.gen_company_site_fencing,
            self.gen_waste_management_plan,
            self.gen_emergency_plan,
            self.gen_hse_plan,
            self.gen_hse_policy,
            self.gen_esia,
            self.gen_qualified_hse_officer,
        ]
        valid_scores = [s for s in fields if s > 0]
        if not valid_scores:
            return 0.0
        return round(sum(valid_scores) / len(valid_scores), 2)
