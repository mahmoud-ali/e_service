from django.db import models
from django.db.models import UniqueConstraint
from django.forms import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from company_profile.models import LkpForeignerProcedureType, TblCompanyProduction
from workflow.model_utils import WorkFlowModel

from django.utils import timezone
from datetime import datetime
import calendar

def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return source_date.replace(year=year, month=month, day=day)

def company_applications_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/company_<id>/applications/<filename>
    return "company_{0}/applications/{1}".format(instance.company.id, filename)    

def company_applications_path_certificates(instance, filename):
    # file will be uploaded to MEDIA_ROOT/company_<id>/applications/<filename>
    return "company_{0}/applications/{1}".format(instance.foreigner_record.company.id, filename)    

class TblCompanyEntajManager(models.Manager):
    def get_queryset(self):
       return super().get_queryset().filter(company_type__in=[TblCompanyProduction.COMPANY_TYPE_ENTAJ,TblCompanyProduction.COMPANY_TYPE_MOKHALFAT])

class TblCompanyEntaj(TblCompanyProduction):
    objects = TblCompanyEntajManager()
    default_manager = objects

    class Meta:
        proxy = True
        verbose_name = _("Production Company")
        verbose_name_plural = _("Production Companies")

class ForeignerRecord(WorkFlowModel):
    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED: _("تأكيد الطلب"),
        STATE_APPROVED: _("اعتماد الطلب"),
    }

    EMPLOYMENT_EMPLOYEE = 1
    EMPLOYMENT_CONTRACTOR = 2
    EMPLOYMENT_GUEST = 3

    EMPLOYMENT_CHOICES = {
        EMPLOYMENT_EMPLOYEE: _("موظف دائم"),
        EMPLOYMENT_CONTRACTOR: _("مقاول"),
        EMPLOYMENT_GUEST: _("زيارة"),
    }

    company = models.ForeignKey(TblCompanyEntaj, related_name="foreigner_company", on_delete=models.PROTECT,verbose_name=_("company"))    
    name = models.CharField("الاسم",max_length=150)
    position = models.CharField("الوظيفة",max_length=150)
    department = models.CharField("الادارة",max_length=150)
    salary = models.DecimalField("المرتب",max_digits=10, decimal_places=2,default=0)
    employment_type = models.IntegerField(_("نوع التوظيف"), choices=EMPLOYMENT_CHOICES.items(), default=EMPLOYMENT_EMPLOYEE)
    # employment_history = models.TextField("السجل الوظيفي")
    cv = models.FileField("السيرة الذاتية",upload_to=company_applications_path,null=True,blank=True)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)

    class Meta:
        verbose_name = "سجل اجنبي"
        verbose_name_plural = "سجلات اجانب"

    def __str__(self):
        return f"{self.name}({self.company.name_ar})"

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []

        if 'entaj_section_head' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))

        if 'entaj_department_head' in user_groups:
            if self.state == self.STATE_CONFIRMED:
                states.append((self.STATE_DRAFT, 'إرجاع إلى مسودة'))
                states.append((self.STATE_APPROVED, self.STATE_CHOICES[self.STATE_APPROVED]))

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

class ForeignerPermissionType(models.Model):
    permission_type_choices = [
        ('passport', 'جواز سفر'),
        ('employment_contract', 'عقد عمل'),
        ('experience_certificate', 'شهادة خبرة'),
        ('curriculum_vitae', 'سيرة ذاتية'),
        ('work_card', 'كرت عمل'),
        ('annual_residence', 'إقامة سنوية'),
        ('multiple_visa', 'تأشيرة خروج وعودة متعددة'),
        ('entry_visa', 'تأشيرة دخول'),
        ('movement_permit', 'إذن تحرك'),
    ]

    name =  models.CharField("نوع الوثيقة",max_length=50,choices=permission_type_choices)
    minimum_no_months =  models.IntegerField("عدد الشهور الادنى لتعتبر الوثيقة سارية",default=0,help_text="مثلاً الجواز يعتبر ساري اذا كان عدد الشهور المتبقي اكثر من 8 شهور")

    class Meta:
        verbose_name = "نوع الوثيقة"
        verbose_name_plural = "نوع الوثيقة"

    def __str__(self):
        return f"{self.get_name_display()}"

class ForeignerPermission(WorkFlowModel):
    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED: _("تأكيد الطلب"),
        STATE_APPROVED: _("اعتماد الطلب"),
    }

    foreigner_record = models.ForeignKey(ForeignerRecord, on_delete=models.PROTECT, related_name='permissions',verbose_name="اسم اجنبي")
    permission_type = models.ForeignKey(ForeignerPermissionType, on_delete=models.PROTECT,verbose_name="نوع الوثيقة")
    type_id = models.CharField("رقم الوثيقة",max_length=50)
    validity_due_date = models.DateField("صالحة حتى")
    attachment = models.FileField("مرفق الوثيقة",upload_to=company_applications_path_certificates)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)

    class Meta:
        verbose_name = "وثائق اجنبي"
        verbose_name_plural = "وثائق اجنبي"
        constraints = [
            UniqueConstraint(fields=['permission_type', 'type_id'], name='unique_permission',violation_error_message="الوثيقة بذات الرقم موجودة مسبقاً")
        ]

    def __str__(self):
        return f"{self.foreigner_record.name} - {self.permission_type}"

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []

        if 'entaj_section_head' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))

        if 'entaj_department_head' in user_groups:
            if self.state == self.STATE_CONFIRMED:
                states.append((self.STATE_DRAFT, 'إرجاع إلى مسودة'))
                states.append((self.STATE_APPROVED, self.STATE_CHOICES[self.STATE_APPROVED]))

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

class ForeignerProcedure(WorkFlowModel):
    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED: _("تأكيد الطلب"),
        STATE_APPROVED: _("اعتماد الطلب"),
    }

    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    procedure_type = models.ForeignKey(LkpForeignerProcedureType, on_delete=models.PROTECT,verbose_name=_("procedure_type"))    
    procedure_from = models.DateField(_("procedure_from"), help_text="Ex: 2025-01-31")
    procedure_to = models.DateField(_("procedure_to"), help_text="Ex: 2025-12-31")
    procedure_cause = models.TextField(_("procedure_cause"),max_length=1000)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)

    def __str__(self):
        return _("Foreigner Procedure") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_foreigner_procedure_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Foreigner procedure")
        verbose_name_plural = _("Application: Foreigner procedure")
    
    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []

        # if 'sswg_secretary' in user_groups:
        if self.state == self.STATE_DRAFT:
            states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))

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

class ForeignerProcedurePermanent(models.Model):
    master = models.ForeignKey(ForeignerProcedure, on_delete=models.PROTECT)
    foreigner_record = models.ForeignKey(ForeignerRecord, on_delete=models.PROTECT, verbose_name="الاجنبي")

    def __str__(self):
        return f"{self.id}"
    
    class Meta:
        verbose_name = "اجنبي معتمد"
        verbose_name_plural = "اجانب معتمدين"

    def clean(self):
        try:
            ##### permissions
            errors = []
            now = timezone.now()
            req = ForeignerProcedureRequirements.objects.get(child_procedure_type=self.master.procedure_type)
            for cert in req.cert_type.all():
                permissions = ForeignerPermission.objects.filter(foreigner_record=self.foreigner_record,validity_due_date__gte=add_months(now,cert.minimum_no_months)) 
                # print(cert,permissions)
                if not permissions.filter(permission_type=cert).exists(): # not xxx:
                    errors.append(cert.name)

            ##### procedures
            req = ForeignerProcedureRequirements.objects.get(child_procedure_type=self.master.procedure_type)
            for proc in req.parent_procedure_type.all():
                company_procedures = ForeignerProcedure.objects.filter(procedure_type=proc)
                foreigner_procedures = ForeignerProcedurePermanent.objects.filter(master__in=company_procedures,foreigner_record=self.foreigner_record)
                # print(cert,permissions)
                if proc and not foreigner_procedures.exists(): # not xxx:
                    errors.append(proc.name)

            if len(errors) > 0:
                raise ValidationError(
                    {"foreigner_record":f"الرجاء التحقق من توفر/سريان الاتي: {"، ".join(errors)}"}
                )

        except ForeignerProcedureRequirements.DoesNotExist as e:
            pass

        return super().clean()

class ForeignerProcedureVisitor(models.Model):
    master = models.ForeignKey(ForeignerProcedure, on_delete=models.PROTECT)
    foreigner_record = models.CharField("الاجنبي",max_length=100)
    reason = models.CharField("سبب الطلب",max_length=150)

    def __str__(self):
        return f"{self.id}"
    
    class Meta:
        verbose_name = "اجنبي غير مضاف في السجلات"
        verbose_name_plural = "اجانب غير مضافين في السجلات"

class ForeignerProcedureRequirements(models.Model):
    child_procedure_type = models.ForeignKey(LkpForeignerProcedureType, on_delete=models.PROTECT,verbose_name=_("procedure_type"))    
    cert_type = models.ManyToManyField(ForeignerPermissionType,verbose_name="الوثيقة")
    parent_procedure_type = models.ManyToManyField(LkpForeignerProcedureType,blank=True,related_name="+",verbose_name="الاجراءات اللازمة")

    class Meta:
        verbose_name = "متطلبات اجراء اجنبي"
        verbose_name_plural = "متطلبات اجراء اجنبي"
