from django.db import models
from django.conf import settings
from django.forms import DateInput, ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

from django_fsm import FSMField, transition

from .workflow import *

class LoggingModel(models.Model):
    """
    An abstract base class model that provides self-
    updating ``created_at`` and ``updated_at`` fields for responsable user.
    """
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))
    
    class Meta:
        abstract = True
        
class WorkflowModel(LoggingModel):
    reject_comments = models.TextField(_("reject_comments"),max_length=256,blank=True)
    state = FSMField(_("application_state"),default=SUBMITTED, choices=STATE_CHOICES)
    notify = models.BooleanField(_("notify_user"),default=False,editable=False)

    def clean(self):
        if self.state == REJECTED and not self.reject_comments:
            raise ValidationError(
                {"reject_comments":_("reject_comments")}
            )
           
    def can_accept(instance):
        return True
        
    @transition(field=state, source=SUBMITTED, target=ACCEPTED, permission=can_do_transition, conditions=[can_accept])
    def accept(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        The return value will be discarded.
        """
        pass
        
    @transition(field=state, source=ACCEPTED, target=APPROVED)
    def approve(self):
        pass

    @transition(field=state, source=ACCEPTED, target=REJECTED)
    def reject(self):
        pass
        
    class Meta:
        abstract = True        
                
class LkpNationality(models.Model):
    name = models.CharField(_("name"),max_length=100)
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = _("Nationality")
        verbose_name_plural = _("Nationalities")

class LkpState(models.Model):
    name = models.CharField(_("name"),max_length=100)
    
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
        return self.name_ar        
    
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
    factory_type  = models.ForeignKey(LkpCompanyProductionFactoryType, on_delete=models.PROTECT,verbose_name=_("factory_type"))
    capacity = models.FloatField(_("Capacity (Tones per day)"))
    
    def __str__(self):
        return self.company.name_ar+" - "+self.factory_type.name
        
    class Meta:
        verbose_name = _("Production Company Factory")
        verbose_name_plural = _("Production Company Factories")
    
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

class TblCompanyProductionLicense(LoggingModel):
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
    date = models.DateField(_("Sign date"))
    start_date = models.DateField(_("start_date"))
    end_date = models.DateField(_("end_date"))
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    locality = models.ForeignKey(LkpLocality, on_delete=models.PROTECT,verbose_name=_("locality"))
    location = models.CharField(_("location"),max_length=100)
    sheet_no = models.CharField(_("sheet_no"),max_length=20,blank=True,null=True)
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

    def __str__(self):
        return self.company.name_ar+"("+str(self.license_no)+")"

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
    period_from = models.DateField(_("period_from"))
    period_to = models.DateField(_("period_to"))
    address_in_sudan = models.TextField(_("address_in_sudan"),max_length=256)
    nationality = models.ForeignKey(LkpNationality, on_delete=models.PROTECT,verbose_name=_("nationality"))
    passport_no = models.CharField(_("passport_no"),max_length=20)
    passport_expiry_date = models.DateField(_("passport_expiry_date"))
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
    borrow_date = models.DateField(_("borrow_date"))
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
    plan_from = models.DateField(_("plan_from"))
    plan_to = models.DateField(_("plan_to"))
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
    report_from = models.DateField(_("report_from"))
    report_to = models.DateField(_("report_to"))
    report_type = models.CharField(_("report_type"),max_length=15, choices=REPORT_TYPE_CHOICES)
    report_comments = models.TextField(_("report_comments"),max_length=256)

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
    expo_from = models.DateField(_("expo_from"))
    expo_to = models.DateField(_("expo_to"))
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
    tajmeed_from = models.DateField(_("tajmeed_from"))
    tajmeed_to = models.DateField(_("tajmeed_to"))
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
    technical_presentation_date = models.DateField(_("technical_presentation_date"))
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
    tamdeed_from = models.DateField(_("tamdeed_from"))
    tamdeed_to = models.DateField(_("tamdeed_to"))
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
    taaweed_from = models.DateField(_("taaweed_from"))
    taaweed_to = models.DateField(_("taaweed_to"))
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
    mda_from = models.DateField(_("mda_from"))
    mda_to = models.DateField(_("mda_to"))
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
    procedure_from = models.DateField(_("procedure_from"))
    procedure_to = models.DateField(_("procedure_to"))
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
    accident_dt = models.DateTimeField(_("accident_dt"))
    accident_type  = models.ForeignKey(LkpAccidentType, on_delete=models.PROTECT,verbose_name=_("accident_type"))    
    accident_class = models.CharField(_("accident_class"),max_length=10, choices=ACCIDENT_CLASS_CHOICES)

    attachement_file = models.FileField(_("attachement_file"),upload_to=company_applications_path)

    def __str__(self):
        return _("HSE Accident Report") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_hse_accident_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: HSE Accident Report")
        verbose_name_plural = _("Application: HSE Accident Report")

class AppHSEPerformanceReport(WorkflowModel):
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    

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

    FIRE_FIGHTING_CHOICES = {
        FIRE_FIGHTING_TYPE1: _("fire_fighting_1"),
        FIRE_FIGHTING_TYPE2: _("fire_fighting_2"),
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
    exam_dt = models.DateField(_("exam_dt"))
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
    mines = models.PositiveIntegerField(_("mines"),choices=RANKING_CHOICES,default=RANKING_TYPE4)

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
    no_gov = models.PositiveIntegerField(_("no_gov"))
    no_staff = models.PositiveIntegerField(_("no_staff"))
    no_contractor = models.PositiveIntegerField(_("no_contractor"))

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
    CHEMICAL_USED6 = 6

    CHEMICAL_USED_CHOICES = {
        CHEMICAL_USED1: _("CHEMICAL_USED1"),
        CHEMICAL_USED2: _("CHEMICAL_USED2"),
        CHEMICAL_USED3: _("CHEMICAL_USED3"),
        CHEMICAL_USED4: _("CHEMICAL_USED4"),
        CHEMICAL_USED5: _("CHEMICAL_USED5"),
        CHEMICAL_USED6: _("CHEMICAL_USED6"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_chemical_used"), choices=CHEMICAL_USED_CHOICES)
    qty_used = models.PositiveIntegerField(_("qty_used"))
    qty_in_store = models.PositiveIntegerField(_("qty_in_store"))
    expire_dt = models.DateField(_("expire_dt"))

    class Meta:
        verbose_name = _("HSE CHEMICAL USED")
        verbose_name_plural = _("HSE CHEMICAL USED")

# class AppHSEPerformanceReportCyanideTable(models.Model):
#     CYANIDE_TABLE1 = 1
#     CYANIDE_TABLE2 = 2
#     CYANIDE_TABLE3 = 3
#     CYANIDE_TABLE4 = 4

#     CYANIDE_TABLE_CHOICES = {
#         CYANIDE_TABLE1: _("CYANIDE_TABLE1"),
#         CYANIDE_TABLE2: _("CYANIDE_TABLE2"),
#         CYANIDE_TABLE3: _("CYANIDE_TABLE3"),
#         CYANIDE_TABLE4: _("CYANIDE_TABLE4"),
#     }

#     master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
#     factor = models.PositiveIntegerField(_("hse_cyanide_table"), choices=CYANIDE_TABLE_CHOICES)
#     choices = models.PositiveIntegerField(_("cyanide_choices"))

#     class Meta:
#         verbose_name = _("HSE CYANIDE TABLE")
#         verbose_name_plural = _("HSE CYANIDE TABLE")

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
    OIL_USED4 = 4

    OIL_USED_CHOICES = {
        OIL_USED1: _("OIL_USED1"),
        OIL_USED2: _("OIL_USED2"),
        OIL_USED3: _("OIL_USED3"),
        OIL_USED4: _("OIL_USED4"),
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
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_WASTE_DISPOSAL"), choices=WASTE_DISPOSAL_CHOICES)
    qty_used = models.FloatField(_("qty_used"))
    disposal_method = models.CharField(_("disposal_method"))

    class Meta:
        verbose_name = _("HSE WASTE DISPOSAL")
        verbose_name_plural = _("HSE WASTE DISPOSAL")

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
    melt_dt = models.DateField(_("melt_dt"))
    melt_bar_no = models.CharField(_("melt_bar_no"),max_length=30)
    melt_bar_weight = models.FloatField(_("melt_bar_weight"))
    melt_jaf = models.FloatField(_("melt_jaf"))
    melt_khabath = models.FloatField(_("melt_khabath"))
    melt_added_gold = models.FloatField(_("melt_added_gold"),blank=True,null=True)
    melt_remaind = models.FloatField(_("melt_remaind"),blank=True,null=True)

    class Meta:
        verbose_name = _("Gold Production Detail")
        verbose_name_plural = _("Gold Production Details")
