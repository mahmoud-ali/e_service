from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from company_profile.models import TblCompanyProduction

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

class ForeignerRecord(models.Model):
    company = models.ForeignKey(TblCompanyEntaj, related_name="foreigner_company", on_delete=models.PROTECT,verbose_name=_("company"))    
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    employment_history = models.TextField()

    def __str__(self):
        return self.name

class ForeignerPermission(models.Model):
    foreigner_record = models.ForeignKey(ForeignerRecord, on_delete=models.CASCADE, related_name='permissions')
    permission_type_choices = [
        ('passport', 'Passport'),
        ('visa', 'Visa'),
        ('residence', 'Residence'),
        ('work_permit', 'Work Permit'),
    ]

    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED: _("تأكيد الطلب"),
        STATE_APPROVED: _("اعتماد الطلب"),
    }

    permission_type = models.CharField(max_length=50, choices=permission_type_choices)
    type_id = models.CharField(max_length=50)
    validity_due_date = models.DateField()
    attachment = models.FileField(upload_to='foreigner_permissions/')
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)

    def __str__(self):
        return f"{self.foreigner_record.name} - {self.get_permission_type_display()}"

class ForeignerApplication(models.Model):
    procedure_type = models.CharField(max_length=255)
    cause = models.TextField()
    address = models.TextField()
    foreigners = models.ManyToManyField(ForeignerRecord, related_name='applications')

    def __str__(self):
        return self.procedure_type
