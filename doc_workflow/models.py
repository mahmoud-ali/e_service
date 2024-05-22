from django.db import models
from django.db.models import CheckConstraint, Q, F
from django.conf import settings
from django.forms import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from company_profile.models import TblCompany,TblCompanyProduction

STATE_TYPE_DRAFT = 'draft'
STATE_TYPE_CONFIRM = 'confirm'

STATE_TYPE_CHOICES = {
    STATE_TYPE_DRAFT: _("draft"),
    STATE_TYPE_CONFIRM: _("confirm"),
}

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

class ApplicationType(models.Model):
    name = models.CharField(_("name"),max_length=50)

    class Meta:
        ordering = ["id"]
        verbose_name = _("Application type")
        verbose_name_plural = _("Application types")

    def __str__(self):
        return str(self.name)

class ActionType(models.Model):
    name = models.CharField(_("name"),max_length=50)

    class Meta:
        ordering = ["id"]
        verbose_name = _("Action type")
        verbose_name_plural = _("Action types")

    def __str__(self):
        return str(self.name)

class Department(models.Model):
    name = models.CharField(_("name"),max_length=50)
    group = models.ForeignKey(Group,null=True,blank=True,on_delete=models.CASCADE)

    class Meta:
        ordering = ["id"]
        verbose_name = _("department")
        verbose_name_plural = _("departments")

    def __str__(self):
        return str(self.name)

class Destination(models.Model):
    name = models.CharField(_("name"),max_length=50)

    class Meta:
        ordering = ["id"]
        verbose_name = _("destination")
        verbose_name_plural = _("destinations")

    def __str__(self):
        return str(self.name)

class ApplicationRecord(LoggingModel):
    STATE_TYPE_NEW = 'new'
    STATE_TYPE_PROCESSING_DEPARTMENT = 'processing_department'
    STATE_TYPE_PROCESSING_EXECUTIVE = 'processing_executive'
    STATE_TYPE_DELIVERY_READY = 'delivery_ready'
    STATE_TYPE_DELIVERY_PARTIAL = 'delivery_partial'
    STATE_TYPE_DELIVERY_COMPLETE = 'delivery_complete'

    STATE_TYPE_CHOICES = {
        STATE_TYPE_NEW: _("new"),
        STATE_TYPE_PROCESSING_DEPARTMENT: _("processing_department"),
        STATE_TYPE_PROCESSING_EXECUTIVE: _("processing_executive"),
        STATE_TYPE_DELIVERY_READY: _("delivery_ready"),
        STATE_TYPE_DELIVERY_PARTIAL: _("delivery_partial"),
        STATE_TYPE_DELIVERY_COMPLETE: _("delivery_completed"),
    }

    def attachement_path(self, filename):
        company = self.company
        date = self.created_at.date()
        return "company_{0}/app/{1}/{2}".format(company.id,date, filename)    

    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    app_type = models.ForeignKey(ApplicationType, on_delete=models.PROTECT,verbose_name=_("app_type"))    
    attachement_file = models.FileField(_("main_attachement_file"),upload_to=attachement_path)
    state = models.CharField(_("record_state"),max_length=25, choices=STATE_TYPE_CHOICES, default=STATE_TYPE_NEW)

    def __str__(self):
        return self.company.__str__()+"/"+self.app_type.name
        
    def get_absolute_url(self): 
        return reverse('doc_workflow:app_record_show',args=[str(self.id)])                

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application record")
        verbose_name_plural = _("Application records")
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["app_type"]),
            models.Index(fields=["state"]),
        ]

    def goto_processing_executive(self):
        qs = ApplicationDepartmentProcessing.objects.filter(app_record=self.id)
        count_all = qs.count()
        count_confirmed = qs.filter(action_state=STATE_TYPE_CONFIRM).count()
        if(count_all == count_confirmed):
            self.state = self.STATE_TYPE_PROCESSING_EXECUTIVE
            self.save()

    def goto_delivery_ready(self):
        qs = ApplicationExectiveProcessing.objects.filter(department_processing__app_record=self.id)
        count_all = qs.count()
        count_confirmed = qs.filter(action_state=STATE_TYPE_CONFIRM).count()
        if(count_all == count_confirmed):
            self.state = self.STATE_TYPE_DELIVERY_READY
            self.save()

    def goto_delivery_complete(self):
        qs = ApplicationDelivery.objects.filter(app_record=self.id)
        count_all = qs.count()
        count_confirmed = qs.filter(delivery_state=STATE_TYPE_CONFIRM).count()
        
        if(count_all == count_confirmed):
            self.state = self.STATE_TYPE_DELIVERY_COMPLETE
            self.save()
        elif(count_confirmed > 0):
            self.state = self.STATE_TYPE_DELIVERY_PARTIAL
            self.save()

    def clean(self):
        pass

    def execution_time(self):
        delta = self.updated_at - self.created_at
        print(delta.microseconds.__repr__())
        delta.microseconds.__repr__()
        return delta

class ApplicationDepartmentProcessing(LoggingModel):
    def attachement_path(self, filename):
        company = self.app_record.company
        date = self.created_at.date()
        return "company_{0}/app/{1}/{2}".format(company.id,date, filename)    

    app_record  = models.ForeignKey(ApplicationRecord, on_delete=models.PROTECT)    
    department = models.ForeignKey(Department, on_delete=models.PROTECT,verbose_name=_("department"))    
    action_type = models.ForeignKey(ActionType, on_delete=models.PROTECT,verbose_name=_("action_type"))    
    attachement_file = models.FileField(_("attachement_file"),upload_to=attachement_path,blank=True)
    action_state = models.CharField(_("action_state"),max_length=10, choices=STATE_TYPE_CHOICES, default=STATE_TYPE_DRAFT) 
    
    def __str__(self):
        return self.app_record.__str__()+"/"+self.department.name
        
    def get_absolute_url(self): 
        return reverse('doc_workflow:app_department_processing_show',args=[str(self.id)])                

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application department processing")
        verbose_name_plural = _("Application department processing")
        indexes = [
            models.Index(fields=["department"]),
            models.Index(fields=["action_type"]),
        ]

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
    def add_executive_processing_record(self):
        if self.action_state == STATE_TYPE_CONFIRM and not hasattr(self,'exective_processing'):
            ApplicationExectiveProcessing.objects.create(
                department_processing=self, \
                created_by=self.created_by, \
                updated_by=self.updated_by, \
                app_record=self.app_record, \
                department=self.department, \
                action_type=self.action_type
            )

    def clean(self):
        if self.action_state == STATE_TYPE_CONFIRM and not self.attachement_file:
            raise ValidationError(
                {"attachement_file":_("field is required")}
            )

class ApplicationExectiveProcessing(LoggingModel):
    def attachement_path(self, filename):
        company = self.department_processing.app_record.company
        date = self.created_at.date()
        return "company_{0}/app/{1}/{2}".format(company.id,date, filename)    

    department_processing = models.OneToOneField(ApplicationDepartmentProcessing, on_delete=models.PROTECT,related_name="exective_processing")
    attachement_file = models.FileField(_("attachement_file"),upload_to=attachement_path,blank=True)
    action_state = models.CharField(_("action_state"),max_length=10, choices=STATE_TYPE_CHOICES, default=STATE_TYPE_DRAFT) 
    
    #duplicated to UI
    app_record  = models.ForeignKey(ApplicationRecord, on_delete=models.PROTECT)    
    department = models.ForeignKey(Department, on_delete=models.PROTECT,verbose_name=_("department"))    
    action_type = models.ForeignKey(ActionType, on_delete=models.PROTECT,verbose_name=_("action_type"))    

    def __str__(self):
        return self.department_processing.__str__()+"/executive"
        
    def get_absolute_url(self): 
        return reverse('doc_workflow:app_executive_processing_show',args=[str(self.id)])                

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application executive processing")
        verbose_name_plural = _("Application executive processing")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.action_state == STATE_TYPE_CONFIRM and not self.attachement_file:
            raise ValidationError(
                {"attachement_file":_("field is required")}
            )
        
        if self.department_processing.app_record != self.app_record:
            raise ValidationError(
                {"app_record":_("field not match relation")}
            )

        if self.department_processing.department != self.department:
            raise ValidationError(
                {"department":_("field not match relation")}
            )

        if self.department_processing.action_type != self.action_type:
            raise ValidationError(
                {"action_type":_("field not match relation")}
            )

class ApplicationDelivery(LoggingModel):
    app_record  = models.ForeignKey(ApplicationRecord, on_delete=models.PROTECT)    
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT,verbose_name=_("destination"))    
    delivery_state = models.CharField(_("delivery_state"),max_length=10, choices=STATE_TYPE_CHOICES, default=STATE_TYPE_DRAFT) 
    
    def __str__(self):
        return self.app_record.__str__()+"/"+self.destination.name+"/"+self.delivery_state
        
    def get_absolute_url(self): 
        return reverse('doc_workflow:app_delivery_show',args=[str(self.id)])                

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application delivery")
        verbose_name_plural = _("Application delivery")

    def clean(self):
        pass

