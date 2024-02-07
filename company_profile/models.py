from django.db import models
from django.conf import settings
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
    state = FSMField(_("application_state"),default=SUBMITTED, choices=STATE_CHOICES)
    notify = models.BooleanField(_("notify_user"),default=False,editable=False)
           
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
    name_ar = models.CharField(_("name_ar"),max_length=200)
    name_en = models.CharField(_("name_en"),max_length=200)
    nationality = models.ForeignKey(LkpNationality, on_delete=models.PROTECT,verbose_name=_("nationality"))
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    locality = models.ForeignKey(LkpLocality, on_delete=models.PROTECT,verbose_name=_("locality"))
    location = models.TextField(_("location"),max_length=256)
    cordinates = models.TextField(_("cordinates"),max_length=256)
    address = models.TextField(_("address"),max_length=256)
    website = models.URLField(_("website"),max_length=200)
    manager_name = models.CharField(_("manager_name"),max_length=200)
    manager_phone = models.CharField(_("manager_phone"),max_length=20)
    rep_name = models.CharField(_("Representative name"),max_length=200)
    rep_phone = models.CharField(_("Representative phone"),max_length=20)
    email = models.EmailField(_("Official email"),max_length=100,unique=True)
    
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
        verbose_name = _("Production Company")
        verbose_name_plural = _("Production Companies")

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
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    date = models.DateField(_("Sign date"))
    start_date = models.DateField(_("start_date"))
    end_date = models.DateField(_("end_date"))
    sheet_no = models.CharField(_("sheet_no"),max_length=10)
    cordinates = models.TextField(_("cordinates"),max_length=256)
    area = models.FloatField(_("Area in Kilometers"))
    reserve = models.FloatField(_("Reserve in Tones"))
    gov_rep = models.CharField(_("Goverment representative"),max_length=200)
    rep_percent = models.FloatField(_("Representative percentage(%)"))
    com_percent = models.FloatField(_("Company percentage(%)"))
    royalty = models.FloatField(_("royalty"))
    zakat = models.FloatField(_("zakat"))
    annual_rent = models.FloatField(_("company"))
    contract_status  = models.ForeignKey(LkpCompanyProductionLicenseStatus, on_delete=models.PROTECT,verbose_name=_("contract_status"))
    contract_file = models.FileField(_("contract_file"),upload_to=company_contract_path)

    def __str__(self):
        return self.company.name_ar+"( "+str(self.date)+" )"

    class Meta:
        verbose_name = _("Production Company License")
        verbose_name_plural = _("Production Company Licenses")

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
    company_from  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,related_name="borrow_from",verbose_name=_("company_borrow_from"))    
    borrow_date = models.DateField(_("borrow_date"))
    borrow_materials_list_file = models.FileField(_("borrow_materials_list_file"),upload_to=company_applications_path)    
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
    area_percent_from_total = models.IntegerField(_("area_percent_from_total"),validators=[MinValueValidator(limit_value=0),MaxValueValidator(limit_value=100)])

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

    TNAZOL_TYPE_CHOICES = {
        TNAZOL_TYPE_FIRST: _("first"),
        TNAZOL_TYPE_SECOND: _("second"),
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
    tnazol_file = models.FileField(_("tnazol_file"),upload_to=company_applications_path)

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
    arbah_amal_in_gram = models.FloatField(_("arbah_amal_in_gram"))
    sold_for_bank_of_sudan_in_gram = models.FloatField(_("sold_for_bank_of_sudan_in_gram"))
    amount_to_export_in_gram = models.FloatField(_("amount_to_export_in_gram"))
    remain_in_gram = models.FloatField(_("remain_in_gram"))

    f1 = models.FileField(_("f1"),upload_to=company_applications_path)
    f2 = models.FileField(_("f2"),upload_to=company_applications_path)
    f3 = models.FileField(_("f3"),upload_to=company_applications_path)
    f4 = models.FileField(_("f4"),upload_to=company_applications_path)
    f5 = models.FileField(_("f5"),upload_to=company_applications_path)
    f6 = models.FileField(_("f6"),upload_to=company_applications_path)
    f7 = models.FileField(_("f7"),upload_to=company_applications_path)
    f8 = models.FileField(_("f8"),upload_to=company_applications_path)
    f9 = models.FileField(_("f9"),upload_to=company_applications_path)

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

