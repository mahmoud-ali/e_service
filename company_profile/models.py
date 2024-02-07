from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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
        verbose_name = _("Application: BorrowMaterials")
        verbose_name_plural = _("Application: BorrowMaterials")
    
    
class AppBorrowMaterialDetail(models.Model):
    borrow_master  = models.ForeignKey(AppBorrowMaterial, on_delete=models.PROTECT)    
    material = models.CharField(_("borrow_material"),max_length=200)
    quantity = models.IntegerField(_("borrow_quantity"))

    class Meta:
        verbose_name = _("AppBorrowMaterialDetail")
        verbose_name_plural = _("AppBorrowMaterialDetail")
