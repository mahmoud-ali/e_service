import sys
from django.db import models
from django.conf import settings
from django.forms import DateInput, ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from django.contrib.gis.db import models as gis_models

# from django_fsm import FSMField, transition
import requests

from workflow.model_utils import WorkFlowModel

from .workflow import REVIEW_ACCEPTANCE, SUBMITTED,ACCEPTED,APPROVED,REJECTED,STATE_CHOICES

MONTH_JAN = 1
MONTH_FEB = 2
MONTH_MAR = 3
MONTH_APR = 4
MONTH_MAY = 5
MONTH_JUN = 6
MONTH_JLY = 7
MONTH_AUG = 8
MONTH_SEP = 9
MONTH_OCT = 10
MONTH_NOV = 11
MONTH_DEC = 12

MONTH_CHOICES = {
    MONTH_JAN: _('MONTH_JAN'),
    MONTH_FEB: _('MONTH_FEB'),
    MONTH_MAR: _('MONTH_MAR'),
    MONTH_APR: _('MONTH_APR'),
    MONTH_MAY: _('MONTH_MAY'),
    MONTH_JUN: _('MONTH_JUN'),
    MONTH_JLY: _('MONTH_JLY'),
    MONTH_AUG: _('MONTH_AUG'),
    MONTH_SEP: _('MONTH_SEP'),
    MONTH_OCT: _('MONTH_OCT'),
    MONTH_NOV: _('MONTH_NOV'),
    MONTH_DEC: _('MONTH_DEC'),
}

class LoggingModel(models.Model):
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))

    class Meta:
        abstract = True
        
class LoggingModelGis(gis_models.Model):
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))

    class Meta:
        abstract = True
    
class WorkflowModel(WorkFlowModel):
    recommendation_comments = models.TextField(_("التوصية"),max_length=256,blank=True)
    reject_comments = models.TextField(_("سبب الرفض/المراجعة"),max_length=256,blank=True)
    state = models.CharField(_("application_state"),max_length=20,default=SUBMITTED, choices=STATE_CHOICES)
    notify = models.BooleanField(_("notify_user"),default=False,editable=False)

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []
        if 'pro_company_application_accept' in user_groups:
            if self.state == SUBMITTED or self.state == REVIEW_ACCEPTANCE:
                states.append((ACCEPTED, STATE_CHOICES[ACCEPTED]))

        if 'pro_company_application_approve' in user_groups:
            if self.state == ACCEPTED:
                states.append((APPROVED, STATE_CHOICES[APPROVED]))
                states.append((REJECTED, STATE_CHOICES[REJECTED]))
                states.append((REVIEW_ACCEPTANCE, STATE_CHOICES[REVIEW_ACCEPTANCE]))

        return states

    def can_transition_to_next_state(self, user, state,obj=None):
        """
        Check if the given user can transition to the specified state.
        """
        
        if state[0] in map(lambda x: x[0], self.get_next_states(user)):
            if obj and state[0] == ACCEPTED and not obj.recommendation_comments:
                raise ValidationError(_("الرجاء كتابة التوصية"))
            
            if obj and (state[0] == REJECTED or state[0] == REVIEW_ACCEPTANCE) and not obj.reject_comments:
                raise ValidationError(_("الرجاء كتابة سبب الرفض/المراجعة"))
            
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

    # def clean(self):
    #     # print("***",self.state,self.recommendation_comments)
    #     if self.id:
    #         if self.state == ACCEPTED and not self.recommendation_comments:
    #             raise ValidationError(
    #                 {"recommendation_comments":_("الرجاء كتابة التوصية")}
    #             )
            
    #         if self.state == REJECTED and not self.reject_comments:
    #             raise ValidationError(
    #                 {"reject_comments":_("reject_comments")}
    #             )
                   
    class Meta:
        abstract = True        
                
class LkpNationality(models.Model):
    name = models.CharField(_("name"),max_length=100)
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = _("Nationality")
        verbose_name_plural = _("Nationalities")

class LkpSector(models.Model):
    name = models.CharField(_("name"),max_length=100)
    
    def __str__(self):
        return self.name    
        
    class Meta:
        verbose_name = _("Sector")
        verbose_name_plural = _("Sectors")

class LkpState(gis_models.Model):
    sector = gis_models.ForeignKey(LkpSector, on_delete=gis_models.PROTECT,verbose_name=_("sector"), null=True, blank=True)
    name = gis_models.CharField(_("name"),max_length=100)
    x = gis_models.FloatField(_("x"))
    y = gis_models.FloatField(_("y"))
    geom = gis_models.MultiPolygonField(srid=4326,null=True)

    def __str__(self):
        return self.name    
        
    class Meta:
        verbose_name = _("State")
        verbose_name_plural = _("States")

class LkpLocality(models.Model):
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    name = models.CharField(_("name"),max_length=100)
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = _("Locality")
        verbose_name_plural = _("Localities")

class LkpMineral(models.Model):
    name = models.CharField(_("name"),max_length=100)
    
    def __str__(self):
        return self.name    
        
    class Meta:
        verbose_name = _("Mineral")
        verbose_name_plural = _("Minerals")        

class TblCompany(LoggingModel):
    COMPANY_TYPE_ENTAJ = "entaj"
    COMPANY_TYPE_MOKHALFAT = "mokhalfat"
    COMPANY_TYPE_EMTIAZ = "emtiaz"
    COMPANY_TYPE_SAGEER = "sageer"

    COMPANY_TYPE_CHOICES = {
        COMPANY_TYPE_ENTAJ: _("entaj"),
        COMPANY_TYPE_MOKHALFAT: _("mokhalfat"),
        COMPANY_TYPE_EMTIAZ: _("emtiaz"),
        COMPANY_TYPE_SAGEER: _("sageer"),
    }

    company_type = models.CharField(_("company_type"),max_length=15, choices=COMPANY_TYPE_CHOICES)
    code = models.CharField(_("code"),max_length=20,blank=True,null=True,default='')
    name_ar = models.CharField(_("name_ar"),max_length=200)
    name_en = models.CharField(_("name_en"),max_length=200)
    nationality = models.ManyToManyField(LkpNationality,verbose_name=_("nationality"),default=[1]) #, on_delete=models.PROTECT
#    cordinates = models.TextField(_("cordinates"),max_length=256)
    address = models.TextField(_("address"),max_length=256,blank=True,null=True)
    website = models.URLField(_("website"),max_length=200,blank=True,null=True)
    manager_name = models.CharField(_("manager_name"),max_length=200)
    manager_phone = models.CharField(_("manager_phone"),max_length=50)
    rep_name = models.CharField(_("Representative name"),max_length=200)
    rep_phone = models.CharField(_("Representative phone"),max_length=50)
    email = models.EmailField(_("Official email"),max_length=100,blank=True,null=True,default='')
    
    class Meta:
        abstract = True    
        
    def __str__(self):
        return f"{self.name_ar} ({self.get_company_type_display()})"
    
class LkpCompanyProductionStatus(models.Model):
    name = models.CharField(_("name"),max_length=100)    
    
    def __str__(self):
        return self.name    
        
    class Meta:
        verbose_name = _("Company Status")
        verbose_name_plural = _("Company Status")
        
    
class TblCompanyProduction(TblCompany):
    status = models.ForeignKey(LkpCompanyProductionStatus, on_delete=models.PROTECT,verbose_name=_("status"))
    
    class Meta:
        ordering = ["name_ar"]
        verbose_name = _("Production Company")
        verbose_name_plural = _("Production Companies")
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["email"]),
            models.Index(fields=["status"]),
        ]

    def get_absolute_url(self): 
        return reverse('profile:pro_company_detail', args=[str(self.id)])        

class TblCompanyProductionUserRole(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="pro_company")
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))

    def __str__(self):
        return self.user.email+" ("+self.company.name_ar+") "        

    class Meta:
        verbose_name = _("Production Company User")
        verbose_name_plural = _("Production Company Users")

class LkpCompanyProductionFactoryType(models.Model):
    name = models.CharField(_("name"),max_length=100)        
    
    def __str__(self):
        return self.name    
        
    class Meta:
        verbose_name = _("Factory Type")
        verbose_name_plural = _("Factory Types")
        
class TblCompanyProductionFactory(LoggingModel): 
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))
    # factory_type  = models.ForeignKey(LkpCompanyProductionFactoryType, on_delete=models.PROTECT,verbose_name=_("factory_type"))
    cil_exists = models.BooleanField(_("CIL?"))
    cil_capacity = models.FloatField(_("السعة التشغيلية بالطن/يوم"),default=0)
    
    heap_exists = models.BooleanField(_("Heap?"))
    heap_capacity = models.FloatField(_("السعة التشغيلية بالطن/يوم"),default=0)

    def clean(self):
        if not self.cil_exists and self.cil_capacity > 0:
            raise ValidationError(
                {"cil_capacity":_("لايمكن اضافة السعة التشغيلية اذا لا يوجد CIL")}
            ) 
        elif self.cil_exists and self.cil_capacity <= 0:
            raise ValidationError(
                {"cil_capacity":_("ادخل سعة تشغيلية أكبر من صفر")}
            ) 
        
        if not self.heap_exists and self.heap_capacity > 0:
            raise ValidationError(
                {"heap_capacity":_("لايمكن اضافة السعة التشغيلية اذا لا يوجد Heap")}
            )
        elif self.heap_exists and self.heap_capacity <= 0:
            raise ValidationError(
                {"heap_capacity":_("ادخل سعة تشغيلية أكبر من صفر")}
            ) 

    def __str__(self):
        return self.company.name_ar
        
    class Meta:
        verbose_name = _("Production Company Factory")
        verbose_name_plural = _("Production Company Factories")

class TblCompanyProductionFactoryVAT(models.Model): 
    factory  = models.ForeignKey(TblCompanyProductionFactory, on_delete=models.PROTECT,verbose_name=_("company"))
    no_sink = models.IntegerField(_("عدد الأحواض"))
    sink_capacity = models.FloatField(_("سعة الحوض"))
    avg_capacity_dimension = models.CharField(_("متوسط ابعاد الحوض"),max_length=100)        

    def __str__(self):
        return f"{self.factory}: {self.no_sink}, {self.sink_capacity}"
        
    class Meta:
        verbose_name = _("حوض")
        verbose_name_plural = _("احواض")

class LkpCompanyProductionLicenseStatus(models.Model):
    name = models.CharField(_("name"),max_length=100)    
    
    def __str__(self):
        return self.name        
        
    class Meta:
        verbose_name = _("License Status")
        verbose_name_plural = _("License Status")
    
def company_contract_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/company_<id>/contract_<id>/<filename>
    return "company_{0}/contract_{1}/{2}".format(instance.company.id,instance.date, filename)    

class TblCompanyProductionLicense(LoggingModelGis):
    LICENSE_TYPE_2TIFAGIA = 1
    LICENSE_TYPE_3AGD = 2
    LICENSE_TYPE_ROKH9A = 3

    LICENSE_TYPE_CHOICES = {
        LICENSE_TYPE_2TIFAGIA: _("license_type_2tifagia"),
        LICENSE_TYPE_3AGD: _("license_type_3agd"),
        LICENSE_TYPE_ROKH9A: _("license_type_rokh9a"),
    }

    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    license_no = models.CharField(_("License no"),max_length=20)
    license_type = models.IntegerField(_("license_type"),choices=LICENSE_TYPE_CHOICES,blank=True,null=True)
    license_count = models.IntegerField(_("License count"),default=1)
    date = models.DateField(_("Sign date"), help_text="Ex: 2025-01-31")
    start_date = models.DateField(_("start_date"), help_text="Ex: 2025-01-31")
    end_date = models.DateField(_("end_date"), help_text="Ex: 2025-01-31")
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    locality = models.ForeignKey(LkpLocality, on_delete=models.PROTECT,verbose_name=_("locality"))
    location = models.CharField(_("location"),max_length=100)
    sheet_no = models.CharField(_("sheet_no"),max_length=20,blank=True,null=True)
    fuel_route = models.CharField("خط سير الوقود",max_length=256,blank=True,null=True)
    cordinates = models.TextField(_("cordinates"),max_length=256)
    mineral = models.ManyToManyField(LkpMineral,verbose_name=_("mineral"),default=[1])
    area = models.FloatField(_("Area in Kilometers"),blank=True,null=True)
    area_initial = models.FloatField(_("Initial area in Kilometers"),blank=True,null=True,default=0)
    reserve = models.FloatField(_("Reserve in Tones"),blank=True,null=True)
    gov_rep = models.CharField(_("Goverment representative"),max_length=200,blank=True,default='',null=True)
    rep_percent = models.FloatField(_("Representative percentage(%)"),blank=True,default=0,null=True)
    com_percent = models.FloatField(_("Company percentage(%)"),blank=True,default=0,null=True)
    royalty = models.FloatField(_("royalty"),default=0)
    zakat = models.FloatField(_("zakat"),default=0)
    annual_rent = models.FloatField(_("annual_rent"),default=0)
    business_profit = models.FloatField(_("Business profit"),blank=True,default=0,null=True)
    social_responsibility = models.FloatField(_("Social responsibility"),blank=True,default=0,null=True)

    contract_status  = models.ForeignKey(LkpCompanyProductionLicenseStatus, on_delete=models.PROTECT,verbose_name=_("contract_status"))
    contract_file = models.FileField(_("contract_file"),upload_to=company_contract_path,blank=True,null=True)

    geom = gis_models.MultiPolygonField(srid=4326,null=True,blank=True)

    def __str__(self):
        return self.company.name_ar+"("+str(self.license_no)+" "+self.location+")"

    class Meta:
        ordering = ["-date"]
        verbose_name = _("Production Company License")
        verbose_name_plural = _("Production Company Licenses")
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["contract_status"]),
        ]

def company_applications_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/company_<id>/applications/<filename>
    return "company_{0}/applications/{1}".format(instance.company.id, filename)    

class AppForignerMovement(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    route_from = models.CharField(_("route_from"),max_length=200)
    route_to = models.CharField(_("route_to"),max_length=200)
    period_from = models.DateField(_("period_from"), help_text="Ex: 2025-01-31")
    period_to = models.DateField(_("period_to"), help_text="Ex: 2025-01-31")
    address_in_sudan = models.TextField(_("address_in_sudan"),max_length=256)
    nationality = models.ForeignKey(LkpNationality, on_delete=models.PROTECT,verbose_name=_("nationality"))
    passport_no = models.CharField(_("passport_no"),max_length=20)
    passport_expiry_date = models.DateField(_("passport_expiry_date"), help_text="Ex: 2025-01-31")
    official_letter_file = models.FileField(_("official_letter_file"),upload_to=company_applications_path)    
    passport_copy_file = models.FileField(_("passport_copy_file"),upload_to=company_applications_path)    
    cv_file = models.FileField(_("cv_file"),upload_to=company_applications_path)    
    experiance_certificates_file = models.FileField(_("experiance_certificates_file"),upload_to=company_applications_path)    
    
    def __str__(self):
        return _("Forigner movement") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_foreigner_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Forigner movement ")
        verbose_name_plural = _("Application: Forigner movement")
    
class AppBorrowMaterial(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,related_name="borrow_to",verbose_name=_("company"))    
    company_from  = models.ForeignKey(TblCompanyProduction,null=True,blank=True, on_delete=models.PROTECT,related_name="borrow_from",verbose_name=_("company_borrow_from"))    
    company_from_str = models.CharField(_("company_borrow_from_str"),max_length=200,default="-")
    borrow_date = models.DateField(_("borrow_date"), help_text="Ex: 2025-01-31")
    borrow_materials_list_file = models.FileField(_("borrow_materials_list_file"),blank=True,upload_to=company_applications_path)    
    borrow_from_approval_file = models.FileField(_("borrow_from_approval_file"),upload_to=company_applications_path)        
    
    def __str__(self):
        return _("Borrow materials") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_borrow_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: BorrowMaterials")
        verbose_name_plural = _("Application: BorrowMaterials")
    
    
class AppBorrowMaterialDetail(models.Model):
    borrow_master  = models.ForeignKey(AppBorrowMaterial, on_delete=models.PROTECT)    
    material = models.CharField(_("borrow_material"),max_length=200)
    quantity = models.IntegerField(_("borrow_quantity"))

    class Meta:
        verbose_name = _("AppBorrowMaterialDetail")
        verbose_name_plural = _("AppBorrowMaterialDetail")

class AppWorkPlan(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    plan_from = models.DateField(_("plan_from"), help_text="Ex: 2025-01-31")
    plan_to = models.DateField(_("plan_to"), help_text="Ex: 2025-01-31")
    plan_comments = models.TextField(_("plan_comments"),max_length=256)
    official_letter_file = models.FileField(_("official_letter_file"),upload_to=company_applications_path)
    work_plan_file = models.FileField(_("work_plan_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Work Plan") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_work_plan_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Work Plan")
        verbose_name_plural = _("Application: Work Plan")

class AppTechnicalFinancialReport(WorkflowModel):
    REPORT_TYPE_TECHNICAL = "technical"
    REPORT_TYPE_FINANCIAL = "financial"

    REPORT_TYPE_CHOICES = {
        REPORT_TYPE_TECHNICAL: _("Technical"),
        REPORT_TYPE_FINANCIAL: _("Financial"),
    }
            
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    report_from = models.DateField(_("report_from"), help_text="Ex: 2025-01-31")
    report_to = models.DateField(_("report_to"))
    report_type = models.CharField(_("report_type"),max_length=15, choices=REPORT_TYPE_CHOICES)
    report_comments = models.TextField(_("Covering letter"),max_length=256) #report_comments

    report_file = models.FileField(_("report_file"),upload_to=company_applications_path)
    other_attachments_file = models.FileField(_("other_attachments_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Technical & Financial Report") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_technical_financial_report_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Technical & Financial Report")
        verbose_name_plural = _("Application: Technical & Financial Reports")

class AppChangeCompanyName(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    new_name = models.CharField(_("new_name"),max_length=200)
    cause_for_change = models.TextField(_("cause_for_change"),max_length=1000)

    tasis_certificate_file = models.FileField(_("tasis_certificate_file"),upload_to=company_applications_path)
    tasis_contract_file = models.FileField(_("tasis_contract_file"),upload_to=company_applications_path)
    sh7_file = models.FileField(_("sh7_file"),upload_to=company_applications_path)
    lahat_tasis_file = models.FileField(_("lahat_tasis_file"),upload_to=company_applications_path)
    name_change_alert_file = models.FileField(_("name_change_alert_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Change Company Name") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_change_company_name_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Company Name Change")
        verbose_name_plural = _("Application: Company Name Changes")

class AppExplorationTime(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    expo_from = models.DateField(_("expo_from"), help_text="Ex: 2025-01-31")
    expo_to = models.DateField(_("expo_to"), help_text="Ex: 2025-01-31")
    expo_cause_for_timing = models.TextField(_("expo_cause_for_timing"),max_length=1000)

    expo_cause_for_change_file = models.FileField(_("expo_cause_for_change_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Exploration Time") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_exploration_time_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Exploration Time")
        verbose_name_plural = _("Application: Exploration Times")

class AppAddArea(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    area_in_km2 = models.IntegerField(_("area_in_km2"))
    cause_for_addition = models.TextField(_("cause_for_addition"),max_length=1000)

    geo_coordination_file = models.FileField(_("geo_coordination_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Add Area") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_add_area_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Add Area")
        verbose_name_plural = _("Application: Add Area")

class AppRemoveArea(WorkflowModel):
    TNAZOL_TYPE_FIRST = "first"
    TNAZOL_TYPE_SECOND = "second"
    TNAZOL_TYPE_EXCEPTIONAL = "exceptional"

    TNAZOL_TYPE_CHOICES = {
        TNAZOL_TYPE_FIRST: _("first"),
        TNAZOL_TYPE_SECOND: _("second"),
        TNAZOL_TYPE_EXCEPTIONAL: _("exceptional"),
    }

    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    remove_type = models.CharField(_("remove_type"),max_length=15, choices=TNAZOL_TYPE_CHOICES)
    area_in_km2 = models.IntegerField(_("area_in_km2"))
    area_percent_from_total = models.FloatField(_("area_percent_from_total"),validators=[MinValueValidator(limit_value=0),MaxValueValidator(limit_value=100)])

    geo_coordinator_for_removed_area_file = models.FileField(_("geo_coordinator_for_removed_area_file"),upload_to=company_applications_path)
    geo_coordinator_for_remain_area_file = models.FileField(_("geo_coordinator_for_remain_area_file"),upload_to=company_applications_path)
    map_for_clarification_file = models.FileField(_("map_for_clarification_file"),upload_to=company_applications_path)
    technical_report_for_removed_area_file = models.FileField(_("technical_report_for_removed_area_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Remove Area") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_remove_area_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Remove Area")
        verbose_name_plural = _("Application: Remove Area")

class AppTnazolShraka(WorkflowModel):
    TNAZOL_TYPE_PARTIAL = "partial"
    TNAZOL_TYPE_COMPLETE = "complete"


    TNAZOL_TYPE_CHOICES = {
        TNAZOL_TYPE_PARTIAL: _("partial"),
        TNAZOL_TYPE_COMPLETE: _("complete"),

    }

    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    tnazol_type = models.CharField(_("tnazol_type"),max_length=15, choices=TNAZOL_TYPE_CHOICES)
    tnazol_for = models.CharField(_("tnazol_for"),max_length=200)
    cause_for_tnazol = models.TextField(_("cause_for_tnazol"),max_length=1000)

    financial_ability_file = models.FileField(_("financial_ability_file"),upload_to=company_applications_path)
    cv_file = models.FileField(_("cv_file"),upload_to=company_applications_path)
    agreement_file = models.FileField(_("agreement_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Tnazol Shraka") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_tnazol_shraka_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Tnazol Shraka")
        verbose_name_plural = _("Application: Tnazol Shraka")

class AppTajeelTnazol(WorkflowModel):
    TNAZOL_TYPE_FIRST = "first"
    TNAZOL_TYPE_SECOND = "second"
    TNAZOL_TYPE_THIRD = "second"
    TNAZOL_TYPE_FOURTH = "second"

    TNAZOL_TYPE_CHOICES = {
        TNAZOL_TYPE_FIRST: _("first"),
        TNAZOL_TYPE_SECOND: _("second"),
        TNAZOL_TYPE_THIRD: _("third"),
        TNAZOL_TYPE_FOURTH: _("fourth"),
    }

    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    tnazol_type = models.CharField(_("tnazol_type"),max_length=15, choices=TNAZOL_TYPE_CHOICES)
    cause_for_tajeel = models.TextField(_("cause_for_tajeel"),max_length=1000)

    cause_for_tajeel_file = models.FileField(_("cause_for_tajeel_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Tajeel Tnazol") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_tajeel_tnazol_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Tajeel Tnazol")
        verbose_name_plural = _("Application: Tajeel Tnazol")

class AppTajmeed(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    tajmeed_from = models.DateField(_("tajmeed_from"), help_text="Ex: 2025-01-31")
    tajmeed_to = models.DateField(_("tajmeed_to"), help_text="Ex: 2025-01-31")
    cause_for_tajmeed = models.TextField(_("cause_for_tajmeed"),max_length=1000)

    cause_for_uncontrolled_force_file = models.FileField(_("cause_for_uncontrolled_force_file"),upload_to=company_applications_path)
    letter_from_jeha_amnia_file = models.FileField(_("letter_from_jeha_amnia_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Tajmeed") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_tajmeed_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Tajmeed")
        verbose_name_plural = _("Application: Tajmeed")

class AppTakhali(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    technical_presentation_date = models.DateField(_("technical_presentation_date"), help_text="Ex: 2025-01-31")
    cause_for_takhali = models.TextField(_("cause_for_takhali"),max_length=1000)

    technical_report_file = models.FileField(_("technical_report_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Takhali") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_takhali_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Takhali")
        verbose_name_plural = _("Application: Takhali")

class AppTamdeed(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    tamdeed_from = models.DateField(_("tamdeed_from"), help_text="Ex: 2025-01-31")
    tamdeed_to = models.DateField(_("tamdeed_to"), help_text="Ex: 2025-01-31")
    cause_for_tamdeed = models.TextField(_("cause_for_tamdeed"),max_length=1000)

    approved_work_plan_file = models.FileField(_("approved_work_plan_file"),upload_to=company_applications_path)
    tnazol_file = models.FileField(_("tnazol_file"),upload_to=company_applications_path,blank=True)

    def __str__(self):
        return _("Tamdeed") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_tamdeed_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Tamdeed")
        verbose_name_plural = _("Application: Tamdeed")

class AppTaaweed(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    taaweed_from = models.DateField(_("taaweed_from"), help_text="Ex: 2025-01-31")
    taaweed_to = models.DateField(_("taaweed_to"), help_text="Ex: 2025-01-31")
    cause_for_taaweed = models.TextField(_("cause_for_taaweed"),max_length=1000)

    def __str__(self):
        return _("Taaweed") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_taaweed_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Taaweed")
        verbose_name_plural = _("Application: Taaweed")

class AppMda(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    mda_from = models.DateField(_("mda_from"), help_text="Ex: 2025-01-31")
    mda_to = models.DateField(_("mda_to"), help_text="Ex: 2025-01-31")
    cause_for_mda = models.TextField(_("cause_for_mda"),max_length=1000)

    approved_work_plan_file = models.FileField(_("approved_work_plan_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("MDA") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_mda_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: MDA")
        verbose_name_plural = _("Application: MDA")

class AppChangeWorkProcedure(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    reason_for_change = models.TextField(_("reason_for_change"),max_length=1000)
    purpose_for_change = models.TextField(_("purpose_for_change"),max_length=1000)
    rational_reason = models.TextField(_("rational_reason"),max_length=1000)

    study_about_change_reason_file = models.FileField(_("study_about_change_reason_file"),upload_to=company_applications_path)
    study_about_new_suggestion_file = models.FileField(_("study_about_new_suggestion_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Change Work Procedure") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_change_work_procedure_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Change Work Procedure")
        verbose_name_plural = _("Application: Change Work Procedure")

class AppExportGold(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    total_in_gram = models.FloatField(_("total_in_gram"))
    net_in_gram = models.FloatField(_("net_in_gram"))
    zakat_in_gram = models.FloatField(_("zakat_in_gram"))
    awaad_jalila_in_gram = models.FloatField(_("awaad_jalila_in_gram"))
    arbah_amal_in_gram = models.FloatField(_("arbah_amal_in_gram"),blank=True,default=0)
    sold_for_bank_of_sudan_in_gram = models.FloatField(_("sold_for_bank_of_sudan_in_gram"))
    amount_to_export_in_gram = models.FloatField(_("amount_to_export_in_gram"))
    remain_in_gram = models.FloatField(_("remain_in_gram"))

    f1 = models.FileField(_("f1"),upload_to=company_applications_path)
    # f2 = models.FileField(_("f2"),upload_to=company_applications_path)
    f3 = models.FileField(_("f3"),upload_to=company_applications_path)
    f4 = models.FileField(_("f4"),upload_to=company_applications_path)
    f6 = models.FileField(_("f6"),upload_to=company_applications_path)
    f7 = models.FileField(_("f7"),upload_to=company_applications_path)
    f8 = models.FileField(_("f8"),upload_to=company_applications_path)
    f9 = models.FileField(_("f9"),upload_to=company_applications_path)
    f5 = models.FileField(_("f5"),upload_to=company_applications_path,blank=True)

    def __str__(self):
        return _("Export Gold") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_export_gold_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Export Gold")
        verbose_name_plural = _("Application: Export Gold")

class AppExportGoldRaw(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))   
    mineral = models.ForeignKey(LkpMineral, on_delete=models.PROTECT,verbose_name=_("mineral"))
    license_type = models.CharField(_("license_type"),max_length=50)
    amount_in_gram = models.FloatField(_("amount_in_gram"))
    sale_price = models.FloatField(_("sale_price"))
    export_country = models.CharField(_("export_country"),max_length=50)
    export_city = models.CharField(_("export_city"),max_length=50)
    export_address = models.TextField(_("export_address"),max_length=200)

    f11 = models.FileField(_("f11"),upload_to=company_applications_path)
    f12 = models.FileField(_("f12"),upload_to=company_applications_path)
    f13 = models.FileField(_("f13"),upload_to=company_applications_path)
    f14 = models.FileField(_("f14"),upload_to=company_applications_path)
    f15 = models.FileField(_("f15"),upload_to=company_applications_path)
    f16 = models.FileField(_("f16"),upload_to=company_applications_path)
    f17 = models.FileField(_("f17"),upload_to=company_applications_path)
    f18 = models.FileField(_("f18"),upload_to=company_applications_path)
    f19 = models.FileField(_("f19"),upload_to=company_applications_path)

    def __str__(self):
        return _("Export Gold") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_export_gold_raw_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Export Gold Raw")
        verbose_name_plural = _("Application: Export Gold Raw")

class AppSendSamplesForAnalysis(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    lab_country = models.CharField(_("lab_country"),max_length=100)
    lab_city = models.CharField(_("lab_city"),max_length=100)
    lab_address = models.TextField(_("lab_address"),max_length=256)
    lab_analysis_cost = models.FloatField(_("lab_analysis_cost"))

    initial_voucher_file = models.FileField(_("initial_voucher_file"),upload_to=company_applications_path)
    sample_description_form_file = models.FileField(_("sample_description_form_file"),upload_to=company_applications_path)
    last_analysis_report_file = models.FileField(_("last_analysis_report_file"),upload_to=company_applications_path,blank=True)

    def __str__(self):
        return _("Send samples for analysis") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_send_samples_for_analysis_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Send samples for analysis")
        verbose_name_plural = _("Application: Send samples for analysis")

class AppSendSamplesForAnalysisDetail(models.Model):
    sample_master = models.ForeignKey(AppSendSamplesForAnalysis, on_delete=models.PROTECT,verbose_name=_("sample_master"))    
    sample_type = models.CharField(_("sample_type"),max_length=100)
    sample_weight = models.FloatField(_("sample_weight"))
    sample_packing_type = models.CharField(_("sample_packing_type"),max_length=100)
    sample_analysis_type = models.CharField(_("sample_analysis_type"),max_length=100)
    sample_analysis_cause = models.TextField(_("sample_analysis_cause"),max_length=256)

    class Meta:
        verbose_name = _("Send Samples For Analysis Detail")
        verbose_name_plural = _("Send Samples For Analysis Detail")

class LkpForeignerProcedureType(models.Model):
    name = models.CharField(_("name"),max_length=50)
    
    def __str__(self):
        return self.name    
        
    class Meta:
        verbose_name = _("Foreigner Procedure Type")
        verbose_name_plural = _("Foreigner Procedure Types")

class AppForeignerProcedure(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    procedure_type = models.ForeignKey(LkpForeignerProcedureType, on_delete=models.PROTECT,verbose_name=_("procedure_type"))    
    procedure_from = models.DateField(_("procedure_from"), help_text="Ex: 2025-01-31")
    procedure_to = models.DateField(_("procedure_to"), help_text="Ex: 2025-01-31")
    procedure_cause = models.TextField(_("procedure_cause"),max_length=1000)

    official_letter_file = models.FileField(_("official_letter_file"),upload_to=company_applications_path)
    passport_file = models.FileField(_("passport_file"),upload_to=company_applications_path)
    cv_file = models.FileField(_("cv_file"),upload_to=company_applications_path)
    experience_certificates_file = models.FileField(_("experience_certificates_file"),upload_to=company_applications_path)
    eqama_file = models.FileField(_("eqama_file"),upload_to=company_applications_path,blank=True)
    dawa_file = models.FileField(_("dawa_file"),upload_to=company_applications_path,blank=True)

    def __str__(self):
        return _("Foreigner Procedure") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_foreigner_procedure_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Foreigner procedure")
        verbose_name_plural = _("Application: Foreigner procedure")

class AppForeignerProcedureDetail(models.Model):
    procedure_master = models.ForeignKey(AppForeignerProcedure, on_delete=models.PROTECT,verbose_name=_("procedure_master"))    
    employee_name = models.CharField(_("employee_name"),max_length=100)
    employee_address = models.TextField(_("employee_address"),max_length=200)

    class Meta:
        verbose_name = _("Foreigner Procedure Detail")
        verbose_name_plural = _("Foreigner Procedure Detail")

class AppAifaaJomrki(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    license_type = models.ForeignKey(TblCompanyProductionLicense, on_delete=models.PROTECT,verbose_name=_("license_type"))    

    approved_requirements_list_file = models.FileField(_("approved_requirements_list_file"),upload_to=company_applications_path)
    approval_from_finance_ministry_file = models.FileField(_("approval_from_finance_ministry_file"),upload_to=company_applications_path)
    final_voucher_file = models.FileField(_("final_voucher_file"),upload_to=company_applications_path)
    shipping_policy_file = models.FileField(_("shipping_policy_file"),upload_to=company_applications_path)
    check_certificate_file = models.FileField(_("check_certificate_file"),upload_to=company_applications_path,blank=True)
    origin_certificate_file = models.FileField(_("origin_certificate_file"),upload_to=company_applications_path,blank=True)
    packing_certificate_file = models.FileField(_("packing_certificate_file"),upload_to=company_applications_path,blank=True)
    specifications_file = models.FileField(_("specifications_file"),upload_to=company_applications_path,blank=True)
    taba_file = models.FileField(_("taba_file"),upload_to=company_applications_path,blank=True)

    def __str__(self):
        return _("Aifaa Jomrki") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_aifaa_jomrki_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Aifaa Jomrki")
        verbose_name_plural = _("Application: Aifaa Jomrki")

class AppAifaaJomrkiDetail(models.Model):
    aifaa_master = models.ForeignKey(AppAifaaJomrki, on_delete=models.PROTECT,verbose_name=_("aifaa_master"))    
    material_name = models.CharField(_("material_name"),max_length=200)

    class Meta:
        verbose_name = _("Aifaa Jomrki Detail")
        verbose_name_plural = _("Aifaa Jomrki Details")

class AppReexportEquipments(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    cause_for_equipments = models.TextField(_("cause_for_equipments"),max_length=1000)

    shipping_policy_file = models.FileField(_("shipping_policy_file"),upload_to=company_applications_path)
    voucher_file = models.FileField(_("voucher_file"),upload_to=company_applications_path)
    specifications_file = models.FileField(_("specifications_file"),upload_to=company_applications_path)
    # momentary_approval_file = models.FileField(_("momentary_approval_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Reexport Equipments") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_reexport_equipments_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Reexport Equipments")
        verbose_name_plural = _("Application: Reexport Equipments")

class AppReexportEquipmentsDetail(models.Model):
    reexport_master = models.ForeignKey(AppReexportEquipments, on_delete=models.PROTECT,verbose_name=_("aifaa_master"))    
    name = models.CharField(_("name"),max_length=50)
    serial_id = models.CharField(_("serial_id"),max_length=50)
    policy_no = models.CharField(_("policy_no"),max_length=50)
    voucher_no = models.CharField(_("voucher_no"),max_length=50)
    insurance_no = models.CharField(_("insurance_no"),max_length=50)
    check_certificate_no = models.CharField(_("check_certificate_no"),max_length=50)

    class Meta:
        verbose_name = _("Reexport Equipments Detail")
        verbose_name_plural = _("Reexport Equipments Details")

class AppRequirementsList(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    

    approved_work_plan_file = models.FileField(_("approved_work_plan_file"),upload_to=company_applications_path)
    initial_voucher_file = models.FileField(_("initial_voucher_file"),upload_to=company_applications_path)
    specifications_file = models.FileField(_("specifications_file"),upload_to=company_applications_path)
    mshobat_jamarik_file = models.FileField(_("mshobat_jamarik_file"),upload_to=company_applications_path,blank=True)
    other_file = models.FileField(_("other_file"),upload_to=company_applications_path,blank=True)

    def __str__(self):
        return _("Requirements List") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_requirements_list_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Requirements List")
        verbose_name_plural = _("Application: Requirements List")

class AppRequirementsListDetail(models.Model):
    requirements_master = models.ForeignKey(AppRequirementsList, on_delete=models.PROTECT,verbose_name=_("requirements_master"))
    item = models.CharField(_("item"),max_length=100)
    description = models.TextField(_("description"),max_length=256)
    qty = models.IntegerField(_("qty"))

    class Meta:
        abstract = True

class AppRequirementsListMangamEquipments(AppRequirementsListDetail):
    class Meta:
        verbose_name = _("Application: Requirements List - Mangam Equipments")
        verbose_name_plural = _("Application: Requirements List - Mangam Equipments")

class AppRequirementsListFactoryEquipments(AppRequirementsListDetail):
    class Meta:
        verbose_name = _("Application: Requirements List - Factory Equipments")
        verbose_name_plural = _("Application: Requirements List - Factory Equipments")

class AppRequirementsListElectricityEquipments(AppRequirementsListDetail):
    class Meta:
        verbose_name = _("Application: Requirements List - Electricity Equipments")
        verbose_name_plural = _("Application: Requirements List - Electricity Equipments")

class AppRequirementsListChemicalLabEquipments(AppRequirementsListDetail):
    class Meta:
        verbose_name = _("Application: Requirements List - Chemical Lab Equipments")
        verbose_name_plural = _("Application: Requirements List - Chemical Lab Equipments")

class AppRequirementsListChemicalEquipments(AppRequirementsListDetail):
    class Meta:
        verbose_name = _("Application: Requirements List - Chemical Equipments")
        verbose_name_plural = _("Application: Requirements List - Chemical Equipments")

class AppRequirementsListMotafjeratEquipments(AppRequirementsListDetail):
    class Meta:
        verbose_name = _("Application: Requirements List - Motafjerat Equipments")
        verbose_name_plural = _("Application: Requirements List - Motafjerat Equipments")

class AppRequirementsListVehiclesEquipments(AppRequirementsListDetail):
    class Meta:
        verbose_name = _("Application: Requirements List - Vehicles Equipments")
        verbose_name_plural = _("Application: Requirements List - Vehicles Equipments")

class AppVisibityStudy(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    license_type = models.ForeignKey(TblCompanyProductionLicense, on_delete=models.PROTECT,verbose_name=_("license_type"))    

    study_area = models.CharField(_("study_area"),max_length=100)
    study_type = models.CharField(_("study_type"),max_length=100)
    study_comment = models.TextField(_("study_comment"),max_length=1000)


    attachement_file = models.FileField(_("attachement_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Visibity Study") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_visibility_study_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Visibity Study")
        verbose_name_plural = _("Application: Visibity Study")

class AppVisibityStudyDetail(models.Model):
    study_master = models.ForeignKey(AppVisibityStudy, on_delete=models.PROTECT)    
    study_point_id = models.IntegerField(_("study_point_id"))
    study_point_long = models.FloatField(_("study_point_long"))
    study_point_lat = models.FloatField(_("study_point_lat"))

    class Meta:
        verbose_name = _("Visibity Study Detail")
        verbose_name_plural = _("Visibity Study Details")

class AppTemporaryExemption(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    

    attachement_file = models.FileField(_("attachement_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Temporary Exemption") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_temporary_exemption_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Temporary Exemption")
        verbose_name_plural = _("Application: Temporary Exemption")

class AppLocalPurchase(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    

    attachement_file = models.FileField(_("local_request_file"),upload_to=company_applications_path)
    attachement_file2 = models.FileField(_("local_purchase_invoice_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Local Purchase") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_local_purchase_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Local Purchase")
        verbose_name_plural = _("Application: Local Purchase")

class AppCyanideCertificate(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    

    attachement_file = models.FileField(_("cyanide_request_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Cyanide Certificate") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_cyanide_certificate_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Cyanide Certificate")
        verbose_name_plural = _("Application: Cyanide Certificate")

class AppExplosivePermission(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    

    attachement_file = models.FileField(_("explosive_request_file"),upload_to=company_applications_path)
    attachement_file2 = models.FileField(_("explosive_amount_file"),upload_to=company_applications_path,blank=True)
    attachement_file3 = models.FileField(_("explosive_last_approved_request_file"),upload_to=company_applications_path,blank=True)

    def __str__(self):
        return _("Explosive Permission") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_explosive_permission_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Explosive Permission")
        verbose_name_plural = _("Application: Explosive Permission")

class AppRestartActivity(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    

    attachement_file = models.FileField(_("restart_activity_reason_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Restart Activity") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_restart_activity_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Restart Activity")
        verbose_name_plural = _("Application: Restart Activity")

class AppRenewalContract(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    

    attachement_file = models.FileField(_("attachement_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Renewal Contract") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_renewal_contract_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Renewal Contract")
        verbose_name_plural = _("Application: Renewal Contract")

class AppImportPermission(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    

    attachement_file = models.FileField(_("import_permission_materials_list_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Import Permission") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_import_permission_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Import Permission")
        verbose_name_plural = _("Application: Import Permission")

class AppImportPermissionDetail(models.Model):
    import_master = models.ForeignKey(AppImportPermission, on_delete=models.PROTECT)    
    import_material_name = models.CharField(_("import_material_name"),max_length=100)
    import_qty = models.FloatField(_("import_qty"))

    class Meta:
        verbose_name = _("Import Permission Detail")
        verbose_name_plural = _("Import Permission Details")

class AppFuelPermission(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    license_type = models.ForeignKey(TblCompanyProductionLicense, on_delete=models.PROTECT,verbose_name=_("license_type"),blank=True,null=True)    

    attachement_file = models.FileField(_("fuel_request_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Fuel Permission") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_fuel_permission_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Fuel Permission")
        verbose_name_plural = _("Application: Fuel Permission")

class AppFuelPermissionDetail(models.Model):
    fuel_master = models.ForeignKey(AppFuelPermission, on_delete=models.PROTECT)    
    fuel_type_name = models.CharField(_("fuel_type_name"),max_length=20)
    fuel_qty = models.FloatField(_("fuel_qty"))
    fuel_actual_qty = models.FloatField(_("fuel_actual_qty"),blank=True,null=True)

    class Meta:
        verbose_name = _("Fuel Permission Detail")
        verbose_name_plural = _("Fuel Permission Details")

class LkpAccidentType(models.Model):
    name = models.CharField(_("name"),max_length=20)
    
    def __str__(self):
        return self.name    
        
    class Meta:
        verbose_name = _("Accident Type")
        verbose_name_plural = _("Accident Types")


class AppHSEAccidentReport(WorkflowModel):
    ACCIDENT_CLASS_MINOR = 'minor'
    ACCIDENT_CLASS_MODERATE = 'moderate'
    ACCIDENT_CLASS_MAJOR = 'major'

    ACCIDENT_CLASS_CHOICES = {
        ACCIDENT_CLASS_MINOR: _("minor"),
        ACCIDENT_CLASS_MODERATE: _("moderate"),
        ACCIDENT_CLASS_MAJOR: _("major"),
    }

    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    accident_place = models.CharField(_("accident_place"),max_length=100)
    accident_dt = models.DateTimeField(_("accident_dt"), help_text="Ex: 2025-01-31")
    accident_type  = models.ForeignKey(LkpAccidentType, on_delete=models.PROTECT,verbose_name=_("accident_type"))    
    accident_class = models.CharField(_("accident_class"),max_length=10, choices=ACCIDENT_CLASS_CHOICES)

    attachement_file = models.FileField(_("attachement_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("HSE Accident Report") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_hse_accident_show',args=[str(self.id)])                

    def send_notifications(self):
        subject = 'بلاغ حادث' 
        url = f"https://mineralsgate.com/app/managers/company_profile/apphseaccidentreport/{self.id}/change/"
        # logo_url = "https://"+Site.objects.get_current().domain+"/app/static/company_profile/img/smrc_logo.png"

        message_html = render_to_string( 
            'hse_companies/telegram/accident.html', 
            { 
                'url':url, 
                # 'logo':logo_url,
                'subject':subject,
                'title':"الإدارة العامة للبيئة والسلامة",
                'sub_title':"إدارة البيئة والسلامة بالتعدين المنظم",
                'data':self,
            },
        ) 

        if 'NotifiedUser' not in sys.modules:
            from hse_traditional.models import NotifiedUser


        for user in NotifiedUser.objects.all():
            telegram_url = f"https://api.telegram.org/bot{settings.TELEGRAM_HSE_ACCIDENTS_ACCESS_KEY}/sendMessage?chat_id={int(user.telegram_user_id)}&text={message_html}&parse_mode=HTML"
            # print(telegram_url)
            requests.get(telegram_url)

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: HSE Accident Report")
        verbose_name_plural = _("Application: HSE Accident Report")

@receiver(pre_save, sender=AppHSEAccidentReport)
def send_notifications_event(sender, instance, **kwargs):
    if not instance.pk:
        instance.send_notifications()

class AppHSEPerformanceReport(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    year = models.PositiveIntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    month = models.PositiveIntegerField(verbose_name=_("month"), choices=MONTH_CHOICES)
    album = models.FileField(_('album'),upload_to=company_applications_path,blank=True,null=True)
    note = models.TextField(verbose_name=_("comment"),blank=True,null=True)

    # attachement_file = models.FileField(_("attachement_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("HSE Performance Report") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_hse_performance_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: HSE Performance Report")
        verbose_name_plural = _("Application: HSE Performance Report")

class AppHSEPerformanceReportManPower(models.Model):
    MAN_POWER_TOTAL = 1
    MAN_POWER_WORK_HOURS = 2

    MAN_POWER_CHOICES = {
        MAN_POWER_TOTAL: _("man_power_total"),
        MAN_POWER_WORK_HOURS: _("man_power_work_hours"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_man_power"), choices=MAN_POWER_CHOICES)
    no_gov = models.PositiveIntegerField(_("no_gov"))
    no_staff = models.PositiveIntegerField(_("no_staff"))
    no_contractor = models.PositiveIntegerField(_("no_contractor"))

    class Meta:
        verbose_name = _("HSE Man power")
        verbose_name_plural = _("HSE Man power")

class AppHSEPerformanceReportFireFighting(models.Model):
    FIRE_FIGHTING_TYPE1 = 1
    FIRE_FIGHTING_TYPE2 = 2
    FIRE_FIGHTING_TYPE3 = 3
    FIRE_FIGHTING_TYPE4 = 4
    FIRE_FIGHTING_TYPE5 = 5

    FIRE_FIGHTING_CHOICES = {
        FIRE_FIGHTING_TYPE1: _("fire_fighting_1"),
        FIRE_FIGHTING_TYPE2: _("fire_fighting_2"),
        FIRE_FIGHTING_TYPE3: _("fire_fighting_3"),
        FIRE_FIGHTING_TYPE4: _("fire_fighting_4"),
        FIRE_FIGHTING_TYPE5: _("fire_fighting_5"),
    }

    SITUATION_TYPE1 = 1
    SITUATION_TYPE2 = 2

    SITUATION_CHOICES = {
        SITUATION_TYPE1: _("situation_ok"),
        SITUATION_TYPE2: _("situation_bad"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_fire_fighting"), choices=FIRE_FIGHTING_CHOICES)
    size = models.PositiveIntegerField(_("size"))
    count = models.PositiveIntegerField(_("count"))
    exam_dt = models.DateField(_("exam_dt"), help_text="Ex: 2025-01-31")
    situation = models.PositiveIntegerField(_("situation"),choices=SITUATION_CHOICES)

    class Meta:
        verbose_name = _("HSE fire fighting")
        verbose_name_plural = _("HSE fire fighting")

class AppHSEPerformanceReportWorkEnvironment(models.Model):
    WORK_ENVIRONMENT_FACTOR1 = 1
    WORK_ENVIRONMENT_FACTOR2 = 2
    WORK_ENVIRONMENT_FACTOR3 = 3
    WORK_ENVIRONMENT_FACTOR4 = 4
    WORK_ENVIRONMENT_FACTOR5 = 5
    WORK_ENVIRONMENT_FACTOR6 = 6
    WORK_ENVIRONMENT_FACTOR7 = 7
    WORK_ENVIRONMENT_FACTOR8 = 8

    WORK_ENVIRONMENT_CHOICES = {
        WORK_ENVIRONMENT_FACTOR1: _("work_environment_factor1"),
        WORK_ENVIRONMENT_FACTOR2: _("work_environment_factor2"),
        WORK_ENVIRONMENT_FACTOR3: _("work_environment_factor3"),
        WORK_ENVIRONMENT_FACTOR4: _("work_environment_factor4"),
        WORK_ENVIRONMENT_FACTOR5: _("work_environment_factor5"),
        WORK_ENVIRONMENT_FACTOR6: _("work_environment_factor6"),
        WORK_ENVIRONMENT_FACTOR7: _("work_environment_factor7"),
        WORK_ENVIRONMENT_FACTOR8: _("work_environment_factor8"),
    }

    RANKING_TYPE1 = 1
    RANKING_TYPE2 = 2
    RANKING_TYPE3 = 3
    RANKING_TYPE4 = 4

    RANKING_CHOICES = {
        RANKING_TYPE1: _("ranking_excellent"),
        RANKING_TYPE2: _("ranking_very_good"),
        RANKING_TYPE3: _("ranking_good"),
        RANKING_TYPE4: _("ranking_bad"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_work_environment"), choices=WORK_ENVIRONMENT_CHOICES)
    offices = models.PositiveIntegerField(_("offices"),choices=RANKING_CHOICES,default=RANKING_TYPE4)
    camp = models.PositiveIntegerField(_("camp"),choices=RANKING_CHOICES,default=RANKING_TYPE4)
    kitchen_dining = models.PositiveIntegerField(_("kitchen_dining"),choices=RANKING_CHOICES,default=RANKING_TYPE4)
    factory = models.PositiveIntegerField(_("factory"),choices=RANKING_CHOICES,default=RANKING_TYPE4)
    stores = models.PositiveIntegerField(_("Stores"),choices=RANKING_CHOICES,default=RANKING_TYPE4)
    lab = models.PositiveIntegerField(_("lab"),choices=RANKING_CHOICES,default=RANKING_TYPE4)
    mines = models.PositiveIntegerField(_("mines"),choices=RANKING_CHOICES,null=True,blank=True)

    class Meta:
        verbose_name = _("HSE work environment")
        verbose_name_plural = _("HSE work environment")

class AppHSEPerformanceReportProactiveIndicators(models.Model):
    PROACTIVE_INDICATORS_TYPE1 = 1
    PROACTIVE_INDICATORS_TYPE2 = 2
    PROACTIVE_INDICATORS_TYPE3 = 3
    PROACTIVE_INDICATORS_TYPE4 = 4

    PROACTIVE_INDICATORS_CHOICES = {
        PROACTIVE_INDICATORS_TYPE1: _("proactive_indicators_type1"),
        PROACTIVE_INDICATORS_TYPE2: _("proactive_indicators_type2"),
        PROACTIVE_INDICATORS_TYPE3: _("proactive_indicators_type3"),
        PROACTIVE_INDICATORS_TYPE4: _("proactive_indicators_type4"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_proactive_indicators"), choices=PROACTIVE_INDICATORS_CHOICES)
    # no_gov = models.PositiveIntegerField(_("no_gov"))
    no_staff = models.PositiveIntegerField(_("no_staff"))
    no_contractor = models.PositiveIntegerField(_("no_contractor"))
    action = models.CharField(_("action"), max_length=100)
    description = models.CharField(_("description"), max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _("HSE proactive indicators")
        verbose_name_plural = _("HSE proactive indicators")

class AppHSEPerformanceReportActivities(models.Model):
    ACTIVITIES_TYPE1 = 1
    ACTIVITIES_TYPE2 = 2
    ACTIVITIES_TYPE3 = 3
    ACTIVITIES_TYPE4 = 4
    ACTIVITIES_TYPE5 = 5
    ACTIVITIES_TYPE6 = 6
    ACTIVITIES_TYPE7 = 7
    ACTIVITIES_TYPE8 = 8
    ACTIVITIES_TYPE9 = 9
    ACTIVITIES_TYPE10 = 10
    ACTIVITIES_TYPE11 = 11

    ACTIVITIES_CHOICES = {
        ACTIVITIES_TYPE1: _("ACTIVITIES_type1"),
        ACTIVITIES_TYPE2: _("ACTIVITIES_type2"),
        ACTIVITIES_TYPE3: _("ACTIVITIES_type3"),
        ACTIVITIES_TYPE4: _("ACTIVITIES_type4"),
        ACTIVITIES_TYPE5: _("ACTIVITIES_type5"),
        ACTIVITIES_TYPE6: _("ACTIVITIES_type6"),
        ACTIVITIES_TYPE7: _("ACTIVITIES_type7"),
        ACTIVITIES_TYPE8: _("ACTIVITIES_type8"),
        ACTIVITIES_TYPE9: _("ACTIVITIES_type9"),
        ACTIVITIES_TYPE10: _("ACTIVITIES_type10"),
        ACTIVITIES_TYPE11: _("ACTIVITIES_type11"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_activities"), choices=ACTIVITIES_CHOICES)
    no_staff = models.PositiveIntegerField(_("no_staff"))
    no_contractor = models.PositiveIntegerField(_("no_contractor"))

    class Meta:
        verbose_name = _("HSE activities")
        verbose_name_plural = _("HSE activities")

class AppHSEPerformanceReportChemicalUsed(models.Model):
    CHEMICAL_USED1 = 1
    CHEMICAL_USED2 = 2
    CHEMICAL_USED3 = 3
    CHEMICAL_USED4 = 4
    CHEMICAL_USED5 = 5

    CHEMICAL_USED_CHOICES = {
        CHEMICAL_USED1: _("CHEMICAL_USED1"),
        CHEMICAL_USED2: _("CHEMICAL_USED2"),
        CHEMICAL_USED3: _("CHEMICAL_USED3"),
        CHEMICAL_USED4: _("CHEMICAL_USED4"),
        CHEMICAL_USED5: _("CHEMICAL_USED5"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_chemical_used"), choices=CHEMICAL_USED_CHOICES)
    qty_used = models.PositiveIntegerField(_("qty_used"))
    qty_in_store = models.PositiveIntegerField(_("qty_in_store"))
    expire_dt = models.DateField(_("expire_dt"), default='',null=True,blank=True, help_text="Ex: 2025-01-31")

    class Meta:
        verbose_name = _("HSE CHEMICAL USED")
        verbose_name_plural = _("HSE CHEMICAL USED")

class AppHSEPerformanceReportOtherChemicalUsed(models.Model):
    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    name = models.CharField(_("hse_chemical_used"), max_length=100,default=_("not exists"))
    qty_used = models.PositiveIntegerField(_("qty_used"),null=True, blank=True)
    qty_in_store = models.PositiveIntegerField(_("qty_in_store"),null=True, blank=True)
    expire_dt = models.DateField(_("expire_dt"), help_text="Ex: 2025-01-31",null=True, blank=True)

    class Meta:
        verbose_name = _("HSE OTHER CHEMICAL USED")
        verbose_name_plural = _("HSE OTHER CHEMICAL USED")

class AppHSEPerformanceReportCyanideTable(models.Model):
    STORAGE_METHOD1 = 1
    STORAGE_METHOD2 = 2

    STORAGE_METHOD_CHOICES = {
        STORAGE_METHOD1: _("STORAGE_METHOD1"),
        STORAGE_METHOD2: _("STORAGE_METHOD2"),
    }

    HANDLING_METHOD1 = 1
    HANDLING_METHOD2 = 2
    HANDLING_METHOD3 = 3

    HANDLING_METHOD_CHOICES = {
        HANDLING_METHOD1: _("HANDLING_METHOD1"),
        HANDLING_METHOD2: _("HANDLING_METHOD2"),
        HANDLING_METHOD3: _("HANDLING_METHOD3"),
    }

    YES = 1
    NO = 2

    YES_NO_CHOICES = {
        YES: _("YES"),
        NO: _("NO"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    storage_method = models.PositiveIntegerField(_("storage_method"), choices=STORAGE_METHOD_CHOICES)
    handling_method = models.PositiveIntegerField(_("handling_method"), choices=HANDLING_METHOD_CHOICES)
    hcn_detector = models.PositiveIntegerField(_("hcn_detector"), choices=YES_NO_CHOICES)
    
    class Meta:
        verbose_name = _("HSE CYANIDE TABLE")
        verbose_name_plural = _("HSE CYANIDE TABLE")

class AppHSEPerformanceReportCyanideCNStorageSpecification(models.Model):
    SPECIFICATION1 = 1
    SPECIFICATION2 = 2
    SPECIFICATION3 = 3
    SPECIFICATION4 = 4

    SPECIFICATION_CHOICES = {
        SPECIFICATION1: _("SPECIFICATION1"),
        SPECIFICATION2: _("SPECIFICATION2"),
        SPECIFICATION3: _("SPECIFICATION3"),
        SPECIFICATION4: _("SPECIFICATION4"),
    }

    YES = 1
    NO = 2

    YES_NO_CHOICES = {
        YES: _("YES"),
        NO: _("NO"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("Specification"), choices=SPECIFICATION_CHOICES)
    choice = models.PositiveIntegerField(_("is_exists"), choices=YES_NO_CHOICES)
    
    class Meta:
        verbose_name = _("HSE CYANIDE CN Storage Specification")
        verbose_name_plural = _("HSE CYANIDE CN Storage Specification")

class AppHSEPerformanceReportWaterUsed(models.Model):
    WATER_USED1 = 1
    WATER_USED2 = 2
    WATER_USED3 = 3
    WATER_USED4 = 4

    WATER_USED_CHOICES = {
        WATER_USED1: _("WATER_USED1"),
        WATER_USED2: _("WATER_USED2"),
        WATER_USED3: _("WATER_USED3"),
        WATER_USED4: _("WATER_USED4"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_water_used"), choices=WATER_USED_CHOICES)
    qty_used = models.FloatField(_("qty_used"))
    source_of_water = models.CharField(_("source_of_water"))
    storage_method = models.CharField(_("storage_method"))

    class Meta:
        verbose_name = _("HSE WATER USED")
        verbose_name_plural = _("HSE WATER USED")

class AppHSEPerformanceReportOilUsed(models.Model):
    OIL_USED1 = 1
    OIL_USED2 = 2
    OIL_USED3 = 3

    OIL_USED_CHOICES = {
        OIL_USED1: _("OIL_USED1"),
        OIL_USED2: _("OIL_USED2"),
        OIL_USED3: _("OIL_USED3"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_oil_used"), choices=OIL_USED_CHOICES)
    qty_used = models.FloatField(_("qty_used"))
    disposal_method = models.CharField(_("disposal_method"))
    storage_method = models.CharField(_("storage_method"))

    class Meta:
        verbose_name = _("HSE OIL USED")
        verbose_name_plural = _("HSE OIL USED")

class AppHSEPerformanceReportWasteDisposal(models.Model):
    WASTE_DISPOSAL1 = 1
    WASTE_DISPOSAL2 = 2
    WASTE_DISPOSAL3 = 3
    WASTE_DISPOSAL4 = 4
    WASTE_DISPOSAL5 = 5
    WASTE_DISPOSAL6 = 6
    WASTE_DISPOSAL7 = 7
    WASTE_DISPOSAL8 = 8
    WASTE_DISPOSAL9 = 9
    WASTE_DISPOSAL10 = 10
    WASTE_DISPOSAL11 = 11
    WASTE_DISPOSAL12 = 12
    WASTE_DISPOSAL13 = 13
    WASTE_DISPOSAL14 = 14
    WASTE_DISPOSAL15 = 15

    WASTE_DISPOSAL_CHOICES = {
        WASTE_DISPOSAL1: _("WASTE_DISPOSAL1"),
        WASTE_DISPOSAL2: _("WASTE_DISPOSAL2"),
        WASTE_DISPOSAL3: _("WASTE_DISPOSAL3"),
        WASTE_DISPOSAL4: _("WASTE_DISPOSAL4"),
        WASTE_DISPOSAL5: _("WASTE_DISPOSAL5"),
        WASTE_DISPOSAL6: _("WASTE_DISPOSAL6"),
        WASTE_DISPOSAL7: _("WASTE_DISPOSAL7"),
        WASTE_DISPOSAL8: _("WASTE_DISPOSAL8"),
        WASTE_DISPOSAL9: _("WASTE_DISPOSAL9"),
        WASTE_DISPOSAL10: _("WASTE_DISPOSAL10"),
        WASTE_DISPOSAL11: _("WASTE_DISPOSAL11"),
        WASTE_DISPOSAL12: _("WASTE_DISPOSAL12"),
        WASTE_DISPOSAL13: _("WASTE_DISPOSAL13"),
        WASTE_DISPOSAL14: _("WASTE_DISPOSAL14"),
        WASTE_DISPOSAL15: _("WASTE_DISPOSAL15"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_WASTE_DISPOSAL"), choices=WASTE_DISPOSAL_CHOICES)
    qty_used = models.FloatField(_("qty_used"))
    disposal_method = models.CharField(_("disposal_method"))

    class Meta:
        verbose_name = _("HSE WASTE DISPOSAL")
        verbose_name_plural = _("HSE WASTE DISPOSAL")

class AppHSEPerformanceReportTherapeuticUnit(models.Model):
    QUALIFICATION1 = 1
    QUALIFICATION2 = 2

    QUALIFICATION_CHOICES = {
        QUALIFICATION1: _("QUALIFICATION1"),
        QUALIFICATION2: _("QUALIFICATION2"),
    }

    AMBULANCE_USED1 = 1
    AMBULANCE_USED2 = 2
    AMBULANCE_USED3 = 3

    AMBULANCE_CHOICES = {
        AMBULANCE_USED1: _("AMBULANCE_USED1"),
        AMBULANCE_USED2: _("AMBULANCE_USED2"),
        AMBULANCE_USED3: _("AMBULANCE_USED3"),
    }

    YES = 1
    NO = 2

    YES_NO_CHOICES = {
        YES: _("YES"),
        NO: _("NO"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    unit_manager = models.CharField(_("unit_manager"), max_length=100)
    unit_phone = models.CharField(_("unit_phone"), max_length=100)
    unit_qualification = models.PositiveIntegerField(_("unit_qualification"), choices=QUALIFICATION_CHOICES)
    aid_qty_used = models.PositiveIntegerField(_("aid_qty_used"))
    ambulance_used = models.PositiveIntegerField(_("ambulance_used"), choices=AMBULANCE_CHOICES)
    periodic_medical_examination  = models.PositiveIntegerField(_("periodic_medical_examination"), choices=YES_NO_CHOICES)
    primary_medical_examination = models.PositiveIntegerField(_("primary_medical_examination"), choices=YES_NO_CHOICES)

    class Meta:
        verbose_name = _("HSE Therapeutic unit")
        verbose_name_plural = _("HSE Therapeutic unit")

class AppHSEPerformanceReportDiseasesForWorkers(models.Model):
    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    disease_dt = models.DateField(_("disease_dt"), help_text="Ex: 2025-01-31")
    disease_type = models.CharField(_("disease_type"), max_length=100)
    no_patients = models.PositiveIntegerField(_("no_patients"))
    patients_career = models.CharField(_("patients_career"), max_length=100)
    patients_worksite = models.CharField(_("patients_worksite"), max_length=100)

    class Meta:
        verbose_name = _("HSE Diseases For Workers")
        verbose_name_plural = _("HSE Diseases For Workers")

class AppHSEPerformanceReportStatisticalData(models.Model):
    STATISTICAL_DATA1 = 1
    STATISTICAL_DATA2 = 2
    STATISTICAL_DATA3 = 3
    STATISTICAL_DATA4 = 4

    STATISTICAL_DATA_CHOICES = {
        STATISTICAL_DATA1: _(" STATISTICAL_DATA1"),
        STATISTICAL_DATA2: _(" STATISTICAL_DATA2"),
        STATISTICAL_DATA3: _(" STATISTICAL_DATA3"),
        STATISTICAL_DATA4: _(" STATISTICAL_DATA4"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_statistical_data"), choices=STATISTICAL_DATA_CHOICES)
    no_staff = models.PositiveIntegerField(_("no_staff"))
    no_contractor = models.PositiveIntegerField(_("no_contractor"))

    class Meta:
        verbose_name = _("HSE STATISTICAL DATA")
        verbose_name_plural = _("HSE STATISTICAL DATA")

class AppHSEPerformanceReportCatering(models.Model):
    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    meal_served_type = models.CharField(_("meal_served"), max_length=100)
    food_sources = models.CharField(_("food_sources"), max_length=100)
    food_transportation = models.CharField(_("food_transportation"), max_length=100)
    food_storage = models.TextField(_("food_storage"))
    kitchen_cleaning = models.TextField(_("kitchen_cleaning"))

    class Meta:
        verbose_name = _("HSE Catering")
        verbose_name_plural = _("HSE Catering")

# class AppHSEPerformanceReportPhotoAlbum(models.Model):
    # master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    # photo = models.ImageField(_('photo'),upload_to=company_applications_path)
    # description = models.TextField(_("description"))

    # class Meta:
    #     verbose_name = _("HSE PHOTO ALBUM")
    #     verbose_name_plural = _("HSE PHOTO ALBUM")

class AppHSEPerformanceReportExplosivesUsed(models.Model):
    EXPLOSIVES_USED1 = 1
    EXPLOSIVES_USED2 = 2
    EXPLOSIVES_USED3 = 3
    EXPLOSIVES_USED4 = 4
    EXPLOSIVES_USED5 = 5
    EXPLOSIVES_USED6 = 6
    EXPLOSIVES_USED7 = 7
    EXPLOSIVES_USED8 = 8
    EXPLOSIVES_USED9 = 9

    EXPLOSIVES_USED_CHOICES = {
        EXPLOSIVES_USED1: _("EXPLOSIVES_USED1"),
        EXPLOSIVES_USED2: _("EXPLOSIVES_USED2"),
        EXPLOSIVES_USED3: _("EXPLOSIVES_USED3"),
        EXPLOSIVES_USED4: _("EXPLOSIVES_USED4"),
        EXPLOSIVES_USED5: _("EXPLOSIVES_USED5"),
        EXPLOSIVES_USED6: _("EXPLOSIVES_USED6"),
        EXPLOSIVES_USED7: _("EXPLOSIVES_USED7"),
        EXPLOSIVES_USED8: _("EXPLOSIVES_USED8"),
        EXPLOSIVES_USED9: _("EXPLOSIVES_USED9"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_explosives_used"), choices=EXPLOSIVES_USED_CHOICES)
    qty_used = models.PositiveIntegerField(_("qty_used"))
    qty_remain = models.PositiveIntegerField(_("qty_remain"))
    expire_dt = models.DateField(_("expire_dt"), help_text="Ex: 2025-01-31")

    class Meta:
        verbose_name = _("HSE EXPLOSIVES USED")
        verbose_name_plural = _("HSE EXPLOSIVES USED")

class AppHSEPerformanceReportExplosivesUsedSpecification(models.Model):
    SPECIFICATION1 = 1
    SPECIFICATION2 = 2
    SPECIFICATION3 = 3
    SPECIFICATION4 = 4
    SPECIFICATION5 = 5

    SPECIFICATION_CHOICES = {
        SPECIFICATION1: _("EXP_SPECIFICATION1"),
        SPECIFICATION2: _("EXP_SPECIFICATION2"),
        SPECIFICATION3: _("EXP_SPECIFICATION3"),
        SPECIFICATION4: _("EXP_SPECIFICATION4"),
        SPECIFICATION5: _("EXP_SPECIFICATION5"),
    }

    YES = 1
    NO = 2

    YES_NO_CHOICES = {
        YES: _("YES"),
        NO: _("NO"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("Specification"), choices=SPECIFICATION_CHOICES)
    choice = models.PositiveIntegerField(_("is_exists"), choices=YES_NO_CHOICES)
    
    class Meta:
        verbose_name = _("HSE Explosive Storage Specification")
        verbose_name_plural = _("HSE Explosive Storage Specification")

class AppHSEPerformanceReportBillsOfQuantities(models.Model):
    BILLS_OF_QUANTITIES1 = 1
    BILLS_OF_QUANTITIES2 = 2
    BILLS_OF_QUANTITIES3 = 3
    BILLS_OF_QUANTITIES4 = 4
    BILLS_OF_QUANTITIES5 = 5
    BILLS_OF_QUANTITIES6 = 6
    BILLS_OF_QUANTITIES7 = 7
    BILLS_OF_QUANTITIES8 = 8
    BILLS_OF_QUANTITIES9 = 9
    BILLS_OF_QUANTITIES10 = 10

    BILLS_OF_QUANTITIES_CHOICES = {
        BILLS_OF_QUANTITIES1: _("BILLS_OF_QUANTITIES1"),
        BILLS_OF_QUANTITIES2: _("BILLS_OF_QUANTITIES2"),
        BILLS_OF_QUANTITIES3: _("BILLS_OF_QUANTITIES3"),
        BILLS_OF_QUANTITIES4: _("BILLS_OF_QUANTITIES4"),
        BILLS_OF_QUANTITIES5: _("BILLS_OF_QUANTITIES5"),
        BILLS_OF_QUANTITIES6: _("BILLS_OF_QUANTITIES6"),
        BILLS_OF_QUANTITIES7: _("BILLS_OF_QUANTITIES7"),
        BILLS_OF_QUANTITIES8: _("BILLS_OF_QUANTITIES8"),
        BILLS_OF_QUANTITIES9: _("BILLS_OF_QUANTITIES9"),
        BILLS_OF_QUANTITIES10: _("BILLS_OF_QUANTITIES10"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_bills_of_quantities"), choices=BILLS_OF_QUANTITIES_CHOICES)
    qty_used = models.PositiveIntegerField(_("qty_used"))

    class Meta:
        verbose_name = _("HSE BILLS OF QUANTITIES")
        verbose_name_plural = _("HSE BILLS OF QUANTITIES")

class AppHSEPerformanceReportCadastralOperations(models.Model):
    SPECIFICATION1 = 1
    SPECIFICATION2 = 2
    SPECIFICATION3 = 3
    SPECIFICATION4 = 4
    SPECIFICATION5 = 5
    SPECIFICATION6 = 6
    SPECIFICATION7 = 7
    SPECIFICATION8 = 8
    SPECIFICATION9 = 9

    SPECIFICATION_CHOICES = {
        SPECIFICATION1: _("CADASTRAL_SPECIFICATION1"),
        SPECIFICATION2: _("CADASTRAL_SPECIFICATION2"),
        SPECIFICATION3: _("CADASTRAL_SPECIFICATION3"),
        SPECIFICATION4: _("CADASTRAL_SPECIFICATION4"),
        SPECIFICATION5: _("CADASTRAL_SPECIFICATION5"),
        SPECIFICATION6: _("CADASTRAL_SPECIFICATION6"),
        SPECIFICATION7: _("CADASTRAL_SPECIFICATION7"),
        SPECIFICATION8: _("CADASTRAL_SPECIFICATION8"),
        SPECIFICATION9: _("CADASTRAL_SPECIFICATION9"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("Specification"), choices=SPECIFICATION_CHOICES)
    value = models.CharField(_("value"), max_length=100)
    
    class Meta:
        verbose_name = _("HSE cadastral operations")
        verbose_name_plural = _("HSE cadastral operations")

class AppHSEPerformanceReportCadastralOperationsTwo(models.Model):
    SPECIFICATION1 = 1
    SPECIFICATION2 = 2
    SPECIFICATION3 = 3
    SPECIFICATION4 = 4
    SPECIFICATION5 = 5
    SPECIFICATION6 = 6
    SPECIFICATION7 = 7

    SPECIFICATION_CHOICES = {
        SPECIFICATION1: _("CADASTRAL2_SPECIFICATION1"),
        SPECIFICATION2: _("CADASTRAL2_SPECIFICATION2"),
        SPECIFICATION3: _("CADASTRAL2_SPECIFICATION3"),
        SPECIFICATION4: _("CADASTRAL2_SPECIFICATION4"),
        SPECIFICATION5: _("CADASTRAL2_SPECIFICATION5"),
        SPECIFICATION6: _("CADASTRAL2_SPECIFICATION6"),
        SPECIFICATION7: _("CADASTRAL2_SPECIFICATION7"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("Specification"), choices=SPECIFICATION_CHOICES)
    observation = models.CharField(_("observation"), max_length=100)
    result = models.CharField(_("result"), max_length=100)
    
    class Meta:
        verbose_name = _("HSE cadastral operations2")
        verbose_name_plural = _("HSE cadastral operations2")

class AppWhomConcern(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    

    whom_reason = models.CharField(_("whom_reason"),max_length=100)
    whom_subject = models.TextField(_("whom_subject"),max_length=256)
    whom_attachement_file = models.FileField(_("whom_attachement_file"),upload_to=company_applications_path,blank=True,null=True)

    def __str__(self):
        return _("Whom may concern") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_whom_concern_show',args=[str(self.id)])                
    
    def clean(self):
        if self.state == APPROVED and not self.whom_attachement_file:
            raise ValidationError(
                {"whom_attachement_file":_("whom_attachement_file")}
            )
        
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Whom may concern request")
        verbose_name_plural = _("Application: Whom may concern requests")

class AppGoldProduction(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    

    form_no = models.CharField(_("form_no"),max_length=20)
    attachement_file = models.FileField(_("gold_production_form_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("Gold Production") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_gold_production_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Gold Production")
        verbose_name_plural = _("Application: Gold Production")

class AppGoldProductionDetail(models.Model):
    melt_master = models.ForeignKey(AppGoldProduction, on_delete=models.PROTECT)    
    melt_dt = models.DateField(_("melt_dt"), help_text="Ex: 2025-01-31")
    melt_bar_no = models.CharField(_("melt_bar_no"),max_length=30)
    melt_bar_weight = models.FloatField(_("melt_bar_weight"))
    melt_jaf = models.FloatField(_("melt_jaf"))
    melt_khabath = models.FloatField(_("melt_khabath"))
    melt_added_gold = models.FloatField(_("melt_added_gold"),blank=True,null=True)
    melt_remaind = models.FloatField(_("melt_remaind"),blank=True,null=True)

    class Meta:
        verbose_name = _("Gold Production Detail")
        verbose_name_plural = _("Gold Production Details")
