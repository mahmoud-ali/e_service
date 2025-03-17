from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from company_profile.models import LkpLocality, LkpState
from workflow.model_utils import LoggingModel, WorkFlowModel

HAJR_TYPE_TOAHIN = 1
HAJR_TYPE_BOLIMAL = 2
HAJR_TYPE_CHOICES = {
    HAJR_TYPE_TOAHIN: _('طواحين'),
    HAJR_TYPE_BOLIMAL: _('بوليمل'),
}

class TraditionalAppUser(LoggingModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="traditional_app_user",verbose_name=_("user"))
    name = models.CharField(_("name"),max_length=100)
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,related_name="traditional_app_state",verbose_name=_("state"))

    def __str__(self):
        return f'{self.user} ({self.name})'

    class Meta:
        verbose_name = _("مستخدم نظام التعدين التقليدي")
        verbose_name_plural = _("مستخدمي نظام التعدين التقليدي")

class Employee(LoggingModel):
    EMPLOYEE_TYPE_EMPLOYEE = 1
    EMPLOYEE_TYPE_T3AGOOD = 2
    EMPLOYEE_TYPE_EL7AG = 3
    EMPLOYEE_TYPE_GOAT_2MNIA = 4
    EMPLOYEE_TYPE_CHOICES = {
        EMPLOYEE_TYPE_EMPLOYEE: _('موظف'),
        EMPLOYEE_TYPE_T3AGOOD: _('متعاقد'),
        EMPLOYEE_TYPE_EL7AG: _('ملحق'),
        EMPLOYEE_TYPE_GOAT_2MNIA: _('قوات أمنية'),
    }

    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    no3_elta3god = models.IntegerField(_("نوع التعاقد"), choices=EMPLOYEE_TYPE_CHOICES, default=EMPLOYEE_TYPE_EMPLOYEE)
    name = models.CharField(_("name"), max_length=100)
    job = models.CharField(_("الوظيفة"), max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("موظف")
        verbose_name_plural = _("الموظفين")

class EmployeeProject(LoggingModel):
    """
    model EmployeeProject with relation one to one with Employee contain work_place, contract_start_date, contract_end_date
    """

    employee = models.OneToOneField(Employee, on_delete=models.PROTECT, verbose_name=_("employee"))
    work_place = models.CharField(_("موقع العمل"), max_length=100)
    contract_start_date = models.DateField(_("تاريخ بداية العقد"))
    contract_end_date = models.DateField(_("تاريخ نهاية العقد"))

    def __str__(self):
        return f"{self.employee.name} ({self.get_no3_elta3god_display()})"

    class Meta:
        verbose_name = _("موظف مشروع")
        verbose_name_plural = _("موظفي المشروع")

class Vehicle(LoggingModel):
    VEHICLE_TYPE_CAR = 1
    VEHICLE_TYPE_MOTOR = 2
    VEHICLE_TYPE_CHOICES = {
        VEHICLE_TYPE_CAR: _('عربة'),
        VEHICLE_TYPE_MOTOR: _('موتر'),
    }

    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    vehicle_type = models.IntegerField(_("نوع المتحرك"), choices=VEHICLE_TYPE_CHOICES, default=VEHICLE_TYPE_CAR)
    plate_no = models.CharField(_("رقم اللوحة"), max_length=100)
    model = models.CharField(_("الموديل"), max_length=100)

    def __str__(self):
        return f"{self.plate_no} ({self.get_vehicle_type_display()})"

    class Meta:
        verbose_name = _("المركبة")
        verbose_name_plural = _("المركبات")

class RentedVehicle(LoggingModel):
    vehicle = models.OneToOneField(Vehicle, on_delete=models.PROTECT, verbose_name=_("vehicle"))
    rented_for = models.ForeignKey(Employee, on_delete=models.PROTECT, verbose_name=_("المستفيد من الاجار"))
    monthly_rent = models.FloatField(_("الاجار الشهري"))
    contract_start_date = models.DateField(_("تاريخ بداية العقد"))
    contract_end_date = models.DateField(_("تاريخ نهاية العقد"))
    contract_attachment = models.FileField(_("صورة من العقد"), upload_to="traditional/rented_vehicles/", blank=True, null=True)

    def __str__(self):
        return f"{self.vehicle.plate_no} ({self.rented_for.name})"

    class Meta:
        verbose_name = _("متحرك مستأجر")
        verbose_name_plural = _("متحركات مستأجرة")

class RentedApartment(LoggingModel):
    RENTED_TYPE_OFFICE = 1
    RENTED_TYPE_2STRA7A = 2
    RENTED_TYPE_SAKAN_MODIR = 3
    RENTED_TYPE_CHOICES = {
        RENTED_TYPE_OFFICE: _('مكتب'),
        RENTED_TYPE_2STRA7A: _('إستراحة'),
        RENTED_TYPE_SAKAN_MODIR: _('سكن المدير'),
    }

    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    apartment_type = models.IntegerField(_("نوع المقر"), choices=RENTED_TYPE_CHOICES, default=RENTED_TYPE_OFFICE)
    monthly_rent = models.FloatField(_("الاجار الشهري"))
    contract_start_date = models.DateField(_("تاريخ بداية العقد"))
    contract_end_date = models.DateField(_("تاريخ نهاية العقد"))
    owner_name = models.CharField(_("اسم مالك العقار"), max_length=100)
    contract_attachment = models.FileField(_("صورة من العقد"), upload_to="traditional/rented_apartments/", blank=True, null=True)

    def __str__(self):
        return f"{self.owner_name} ({self.get_apartment_type_display()})"

    class Meta:
        verbose_name = _("عقار مستأجر")
        verbose_name_plural = _("عقارات مستأجرة")

class LkpSoag(LoggingModel):
    state = models.ForeignKey(LkpState, related_name="traditional_state", on_delete=models.PROTECT,verbose_name=_("state"))
    locality = models.ForeignKey(LkpLocality, related_name="+", on_delete=models.PROTECT,verbose_name=_("Locality"))

    name = models.CharField(_("الاسم"),max_length=100)
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = _("سوق")
        verbose_name_plural = _("أسواق")

class LkpMojam3atTawa7in(LoggingModel):
    """
    model LkpMojam3atTawa7in with relation many to one with LkpSoag contain owner_name, toa7in_jafa_count, toa7in_ratiba_count, pid_attachment
    """

    soag = models.ForeignKey(LkpSoag, on_delete=models.PROTECT, verbose_name=_("السوق"))
    owner_name = models.CharField(_("اسم المالك"),max_length=100)
    toa7in_jafa_count = models.IntegerField(_("عدد الطواحين الجافة"))
    toa7in_ratiba_count = models.IntegerField(_("عدد الطواحين الرطبة"))
    pid_attachment = models.FileField(_("صورة من إثبات الشخصية"), upload_to="traditional/mojam3at_tawa7in/", blank=True, null=True)

    def __str__(self):
        return f"{self.owner_name} ({self.soag.name})"

    class Meta:
        verbose_name = _("مجمع طواحين")
        verbose_name_plural = _("مجمعات طواحين")

class LkpSaig(LoggingModel):
    """
    model Saig with relation many to one with LkpSoag contain name, pid_attachment
    """
    soag = models.ForeignKey(LkpSoag, on_delete=models.PROTECT, verbose_name=_("السوق"))
    name = models.CharField(_("اسم الصائغ"),max_length=100)
    pid_attachment = models.FileField(_("صورة من إثبات الشخصية"), upload_to="traditional/saig/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.soag.name})"

    class Meta:
        verbose_name = _("صائغ")
        verbose_name_plural = _("صاغة")

class Lkp7ofrKabira(LoggingModel):
    """
    model Lkp7ofrKabira with relation many to one with LkpState and LkpLocality contain name,cordinates,state(active/inactive), pid_attachment
    """
    STATE_ACTIVE = 1
    STATE_INACTIVE = 2
    STATE_CHOICES = {
        STATE_ACTIVE: _('منتجة'),
        STATE_INACTIVE: _('غير منتجة'),
    }

    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    locality = models.ForeignKey(LkpLocality, on_delete=models.PROTECT, verbose_name=_("locality"))
    name = models.CharField(_("owner_name"),max_length=100)
    cordinates = models.TextField(_("الإحداثيات"),max_length=256)
    status = models.IntegerField(_("الحالة"), choices=STATE_CHOICES, default=STATE_ACTIVE)
    pid_attachment = models.FileField(_("صورة من إثبات الشخصية"), upload_to="traditional/7ofr_kabira/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.state.name})"

    class Meta:
        verbose_name = _("حفرة كبيرة")
        verbose_name_plural = _("حفر كبيرة")

class Lkp2bar(LoggingModel):
    """
    model Lkp2bar with relation many to one with LkpState and LkpLocality contain name,cordinates, pid_attachment
    """
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    locality = models.ForeignKey(LkpLocality, on_delete=models.PROTECT, verbose_name=_("locality"))
    name = models.CharField(_("owner_name"),max_length=100)
    cordinates = models.TextField(_("الإحداثيات"),max_length=256)
    pid_attachment = models.FileField(_("صورة من إثبات الشخصية"), upload_to="traditional/2bar/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.state.name})"

    class Meta:
        verbose_name = _("بئر/خط انتاج")
        verbose_name_plural = _("ابار/خطوط انتاج")

class Lkp2jhizatBahth(LoggingModel):
    """
    model Lkp2jhizatBahth with relation many to one with LkpState and LkpLocality contain name, pid_attachment
    """
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    locality = models.ForeignKey(LkpLocality, on_delete=models.PROTECT, verbose_name=_("locality"))
    name = models.CharField(_("owner_name"),max_length=100)
    pid_attachment = models.FileField(_("صورة من إثبات الشخصية"), upload_to="traditional/2jhizat_bahth/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.state.name})"

    class Meta:
        verbose_name = _("جهاز بحث/إستكشاف")
        verbose_name_plural = _("اجهزة بحث/استكشاف")

class LkpSosalGold(LoggingModel):
    """
    model LkpSosalGold with relation many to one with LkpState and LkpLocality contain name, pid_attachment
    """
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    locality = models.ForeignKey(LkpLocality, on_delete=models.PROTECT, verbose_name=_("locality"))
    name = models.CharField(_("owner_name"),max_length=100)
    pid_attachment = models.FileField(_("صورة من إثبات الشخصية"), upload_to="traditional/sosl_gold/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.state.name})"

    class Meta:
        verbose_name = _("ذهب صوصال")
        verbose_name_plural = _("ذهب صوصال")

class LkpGrabeel(LoggingModel):
    """
    model LkpGrabeel with relation many to one with LkpState and LkpLocality contain name,type(big/small), pid_attachment
    """
    TYPE_BIG = 1
    TYPE_SMALL = 2
    TYPE_CHOICES = {
        TYPE_BIG: _('كبير'),
        TYPE_SMALL: _('صغير'),
    }

    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    locality = models.ForeignKey(LkpLocality, on_delete=models.PROTECT, verbose_name=_("locality"))
    name = models.CharField(_("owner_name"),max_length=100)
    type = models.IntegerField(_("type"), choices=TYPE_CHOICES, default=TYPE_BIG)
    pid_attachment = models.FileField(_("صورة من إثبات الشخصية"), upload_to="traditional/grabeel/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.state.name})"

    class Meta:
        verbose_name = _("غربال")
        verbose_name_plural = _("غرابيل")

class LkpKhalatat(LoggingModel):
    """
    model LkpKhalatat with relation many to one with LkpState and LkpLocality contain name, pid_attachment
    """
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    locality = models.ForeignKey(LkpLocality, on_delete=models.PROTECT, verbose_name=_("locality"))
    name = models.CharField(_("owner_name"),max_length=100)
    pid_attachment = models.FileField(_("صورة من إثبات الشخصية"), upload_to="traditional/khalatat/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.state.name})"

    class Meta:
        verbose_name = _("خلاط")
        verbose_name_plural = _("خلاطات")

class LkpSmallProcessingUnit(LoggingModel):
    """
    model LkpSmallProcessingUnit with relation many to one with LkpState and LkpLocality contain name, bolimal_count, khalatat_count, kasarat_count pid_attachment
    """
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("state"))
    locality = models.ForeignKey(LkpLocality, on_delete=models.PROTECT, verbose_name=_("locality"))
    name = models.CharField(_("owner_name"),max_length=100)
    bolimal_count = models.IntegerField(_("عدد طواحين البولميل"))
    khalatat_count = models.IntegerField(_("عدد الخلاطات"))
    kasarat_count = models.IntegerField(_("عدد الكسارات"))
    pid_attachment = models.FileField(_("صورة من إثبات الشخصية"), upload_to="traditional/small_processing_unit/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.state.name})"

    class Meta:
        verbose_name = _("وحدة معالجة صغيرة")
        verbose_name_plural = _("وحدات المعالجة الصغيرة")

class DailyReport(WorkFlowModel):
    STATE_DRAFT = 1
    STATE_CONFIRMED1 = 2
    STATE_CONFIRMED2 = 3
    STATE_APPROVED = 4

    STATE_CHOICES = {
        STATE_DRAFT:_("مسودة"),
        STATE_CONFIRMED1:_("تأكيد اولي"),
        STATE_CONFIRMED2:_("تأكيد نهائي"),
        STATE_APPROVED:_("إعتماد"),
    }

    date = models.DateField(_("date"))
    source_state = models.ForeignKey(LkpState,on_delete=models.PROTECT,verbose_name=_("state"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)

    def __str__(self):
        return f"{self.date} ({self.source_state.name})"

    class Meta:
        ordering = ["-date",]
        verbose_name = _("التقرير اليومي")
        verbose_name_plural = _("التقارير اليومية")

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []
        if 'tra_tahsil_department' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_CONFIRMED1, self.STATE_CHOICES[self.STATE_CONFIRMED1]))

        if 'tra_asoag_department' in user_groups:
            if self.state == self.STATE_CONFIRMED1:
                states.append((self.STATE_CONFIRMED2, self.STATE_CHOICES[self.STATE_CONFIRMED2]))
                states.append((self.STATE_DRAFT, self.STATE_CHOICES[self.STATE_DRAFT]))

        if 'tra_state_manager' in user_groups:
            if self.state == self.STATE_CONFIRMED2:
                states.append((self.STATE_APPROVED, self.STATE_CHOICES[self.STATE_APPROVED]))
                states.append((self.STATE_CONFIRMED1, self.STATE_CHOICES[self.STATE_CONFIRMED1]))

        return states

    def can_transition_to_next_state(self, user, state):
        """
        Check if the given user can transition to the specified state.
        """
        if state[0] in map(lambda x: x[0], self.get_next_states(user)):
            return True

        return False

    def transition_to_next_state(self, user, state):
        """
        Transitions the workflow to the given state, after checking user permissions.
        """
        if self.can_transition_to_next_state(user, state):
            self.state = state[0]
            self.updated_by = user
            self.save()
        else:
            raise Exception(f"User {user.username} cannot transition to state {state} from state {self.state}")

        return self

class DailyWardHajr(LoggingModel):
    """
    model WardHajr with relation many to one with DailyReport contain soug, hajr_type, hajr_count
    """

    daily_report = models.ForeignKey(DailyReport, on_delete=models.PROTECT, verbose_name=_("daily_report"))
    soag = models.ForeignKey(LkpSoag, on_delete=models.PROTECT, verbose_name=_("السوق"))
    hajr_type = models.IntegerField(_("نوع الحجر"), choices=HAJR_TYPE_CHOICES,default=HAJR_TYPE_TOAHIN)
    hajr_count = models.IntegerField(_("عدد الجوالات"))

    def __str__(self):
        return f"{self.soag.name} ({self.get_hajr_type_display()})"

    class Meta:
        verbose_name = _("وارد حجر")
        verbose_name_plural = _("وارد حجر")

class DailyIncome(LoggingModel):
    """
    model DailyIncome with relation many to one with DailyReport contain soug, hajr_type, amount
    """

    daily_report = models.ForeignKey(DailyReport, on_delete=models.PROTECT, verbose_name=_("daily_report"))
    soag = models.ForeignKey(LkpSoag, on_delete=models.PROTECT, verbose_name=_("السوق"))
    hajr_type = models.IntegerField(_("نوع الحجر"), choices=HAJR_TYPE_CHOICES,default=HAJR_TYPE_TOAHIN)
    amount = models.FloatField(_("amount"))

    def __str__(self):
        return f"{self.soag.name} ({self.get_hajr_type_display()})"

    class Meta:
        verbose_name = _("الإيراد اليومي")
        verbose_name_plural = _("الإيراد اليومي")

class DailyTahsilForm(LoggingModel):
    """
    model TahsilForm with relation many to one with DailyReport contain soug, form_count, gold_in_gram
    """
    daily_report = models.ForeignKey(DailyReport, on_delete=models.PROTECT, verbose_name=_("daily_report"))
    soag = models.ForeignKey(LkpSoag, on_delete=models.PROTECT, verbose_name=_("السوق"))
    form_count = models.IntegerField(_("عدد الإستمارات"))
    gold_in_gram = models.FloatField(_("كمية الذهب بالجرام"))

    def __str__(self):
        return f"{self.soag.name} ({self.form_count})"

    class Meta:
        verbose_name = _("استمارة تحصيل")
        verbose_name_plural = _("استمارات التحصيل")

class DailyKartaMor7ala(LoggingModel):
    """
    model KartaMor7ala with relation many to one with DailyReport contain soug, galabat_count, destination
    """
    daily_report = models.ForeignKey(DailyReport, on_delete=models.PROTECT, verbose_name=_("daily_report"))
    soag = models.ForeignKey(LkpSoag, on_delete=models.PROTECT, verbose_name=_("السوق"))
    galabat_count = models.IntegerField(_("عدد القلابات"))
    destination = models.CharField(_("destination"),max_length=100)

    def __str__(self):
        return f"{self.soag.name} ({self.galabat_count})"

    class Meta:
        verbose_name = _("الكرتة المرحلة")
        verbose_name_plural = _("الكرتة المرحلة من الاسواق")


class DailyGoldMor7ala(LoggingModel):
    """
    model GoldMor7ala with relation many to one with DailyReport contain soug, weight_in_gram, owner_name, destination
    """
    daily_report = models.ForeignKey(DailyReport, on_delete=models.PROTECT, verbose_name=_("daily_report"))
    soag = models.ForeignKey(LkpSoag, on_delete=models.PROTECT, verbose_name=_("السوق"))
    weight_in_gram = models.FloatField(_("الوزن بالجرام"))
    owner_name = models.CharField(_("owner_name"),max_length=100)
    destination = models.CharField(_("destination"),max_length=100)

    def __str__(self):
        return f"{self.soag.name} ({self.weight_in_gram})"

    class Meta:
        verbose_name = _("الذهب المنتج والمرحل")
        verbose_name_plural = _("الذهب المنتج والمرحل")

class DailyGrabeel(LoggingModel):
    """
    model Grabeel with relation many to one with DailyReport contain grabeel, weight_in_gram, amount
    """
    daily_report = models.ForeignKey(DailyReport, on_delete=models.PROTECT, verbose_name=_("daily_report"))
    grabeel = models.ForeignKey(LkpGrabeel, on_delete=models.PROTECT, verbose_name=_("غربال"))
    weight_in_gram = models.FloatField(_("الوزن بالجرام"))
    amount = models.FloatField(_("amount"))

    def __str__(self):
        return f"{self.grabeel.name} ({self.weight_in_gram})"

    class Meta:
        verbose_name = _("غربال")
        verbose_name_plural = _("غرابيل")

class DailyHofrKabira(LoggingModel):
    """
    model HofrKabira with relation many to one with DailyReport contain 7ofrKabira, weight_in_gram, amount
    """
    daily_report = models.ForeignKey(DailyReport, on_delete=models.PROTECT, verbose_name=_("daily_report"))
    hofr_kabira = models.ForeignKey(Lkp7ofrKabira, on_delete=models.PROTECT, verbose_name=_("حفرة كبيرة"))
    weight_in_gram = models.FloatField(_("الوزن بالجرام"))
    amount = models.FloatField(_("amount"))

    def __str__(self):
        return f"{self.hofr_kabira.name} ({self.weight_in_gram})"

    class Meta:
        verbose_name = _("حفرة كبيرة")
        verbose_name_plural = _("حفر كبيرة")

class DailySmallProcessingUnit(LoggingModel):
    """
    model SmallProcessingUnit with relation many to one with DailyReport contain small_processing_unit, weight_in_gram, amount
    """
    daily_report = models.ForeignKey(DailyReport, on_delete=models.PROTECT, verbose_name=_("daily_report"))
    small_processing_unit = models.ForeignKey(LkpSmallProcessingUnit, on_delete=models.PROTECT, verbose_name=_("وحدة معالجة صغيرة"))
    weight_in_gram = models.FloatField(_("الوزن بالجرام"))
    amount = models.FloatField(_("amount"))

    def __str__(self):
        return f"{self.small_processing_unit.name} ({self.weight_in_gram})"

    class Meta:
        verbose_name = _("وحدة معالجة صغيرة")
        verbose_name_plural = _("وحدات المعالجة الصغيرة")
