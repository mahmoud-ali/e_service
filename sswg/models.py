from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from gold_travel.models import LkpOwner,AppMoveGold

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

class CompanyDetails(LoggingModel):
    """Stores company and surrogate information"""
    name = models.ForeignKey(LkpOwner, on_delete=models.PROTECT,verbose_name=_("Company Name"))
    surrogate_name = models.CharField(_("Surrogate Name"), max_length=255)
    surrogate_id_type = models.IntegerField(_("ID Type"), choices=AppMoveGold.IDENTITY_CHOICES)
    surrogate_id_val = models.CharField(_("ID Value"), max_length=20)
    surrogate_id_phone = models.CharField(_("Contact Phone"), max_length=20)
    basic_form = models.OneToOneField(
        'BasicForm',
        on_delete=models.PROTECT,
        related_name='company_details',
        verbose_name=_("SSWG Basic Form"),
    )

    def __str__(self):
        return f"{self.name} - {self.surrogate_name}"

    class Meta:
        verbose_name = _("SSWG CompanyDetails")
        verbose_name_plural = _("SSWG CompanyDetails")


class SMRCData(LoggingModel):
    """Stores SMRC-related measurements"""
    def attachment_path(self, filename):
        company = self.form.id
        date = self.created_at.date()
        return "company_{0}/sswg/{1}/{2}".format(company,date, filename)    

    # form_type = models.IntegerField(_("form_type"), choices=AppMoveGold.FORM_TYPE_CHOICES, default=AppMoveGold.FORM_TYPE_GOLD_EXPORT)
    form = models.ForeignKey(AppMoveGold, on_delete=models.PROTECT,verbose_name=_("Move Gold"))

    raw_weight = models.FloatField(_("Raw Weight"), validators=[MinValueValidator(0.0)])
    allow_count = models.PositiveIntegerField(_("Allow Count"))
    basic_form = models.OneToOneField(
        'BasicForm',
        on_delete=models.PROTECT,
        related_name='smrc_data',
        null=True,
        blank=True,
        verbose_name=_("SSWG Basic Form"),
    )

    smrc_file = models.FileField(_("smrc_file"), upload_to=attachment_path)  #,null=True,blank=True

    def __str__(self):
        return f"{self.form}"

    class Meta:
        verbose_name = _("SSWG SMRCData")
        verbose_name_plural = _("SSWG SMRCData")

class SSMOData(LoggingModel):
    """Stores SSMO-related measurements and certificate"""
    def attachment_path(self, filename):
        company = self.form.id
        date = self.created_at.date()
        return "company_{0}/sswg/{1}/{2}".format(company,date, filename)    

    raw_weight = models.FloatField(_("Raw Weight"), validators=[MinValueValidator(0.0)])
    net_weight = models.FloatField(_("Net Weight"), validators=[MinValueValidator(0.0)])
    allow_count = models.PositiveIntegerField(_("Allow Count"))
    certificate_id = models.CharField(_("Certificate ID"), max_length=20) 
    basic_form = models.OneToOneField(
        'BasicForm',
        on_delete=models.PROTECT,
        related_name='ssmo_data',
        verbose_name=_("SSWG Basic Form"),
    )
    ssmo_file = models.FileField(_("ssmo_file"), upload_to=attachment_path)  #,null=True,blank=True

    def __str__(self):
        return f"SSMO-{self.certificate_id}"

    class Meta:
        verbose_name = _("SSWG SSMOData")
        verbose_name_plural = _("SSWG SSMOData")

class SmrcNoObjectionData(LoggingModel):
    """Stores SSMO-related measurements and certificate"""
    def attachment_path(self, filename):
        company = self.form.id
        date = self.created_at.date()
        return "company_{0}/sswg/{1}/{2}".format(company,date, filename)    

    basic_form = models.OneToOneField(
        'BasicForm',
        on_delete=models.PROTECT,
        related_name='smrc_no_objection_data',
        verbose_name=_("SSWG Basic Form"),
    )

    smrc_no_objection_file = models.FileField(
        _("SMRC No Objection File"), 
        upload_to=attachment_path,
    )

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = _("SSWG SmrcNoObjectionData")
        verbose_name_plural = _("SSWG SmrcNoObjectionData")

class MmAceptanceData(LoggingModel):
    """Stores SSMO-related measurements and certificate"""
    def attachment_path(self, filename):
        company = self.form.id
        date = self.created_at.date()
        return "company_{0}/sswg/{1}/{2}".format(company,date, filename)    

    basic_form = models.OneToOneField(
        'BasicForm',
        on_delete=models.PROTECT,
        related_name='mm_aceptance_data',
        verbose_name=_("SSWG Basic Form"),
    )

    mm_aceptance_file = models.FileField(
        _("Ministry of Minerals Acceptance File"), 
        upload_to=attachment_path,
    )

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = _("SSWG MmAceptanceData")
        verbose_name_plural = _("SSWG MmAceptanceData")

class MOCSData(LoggingModel):
    """Stores Ministry of Commerce and Supply related data"""
    def attachment_path(self, filename):
        company = self.form.id
        date = self.created_at.date()
        return "company_{0}/sswg/{1}/{2}".format(company,date, filename)    

    contract_number = models.CharField(_("Contract Number"), max_length=20)
    exporters_importers_registry_number = models.CharField(_("Exporters/Importers Registry Number"), max_length=20)
    unit_price_in_grams = models.FloatField(_("Unit Price (grams)"), validators=[MinValueValidator(0.0)])
    total_contract_value = models.FloatField(_("Total Contract Value"), validators=[MinValueValidator(0.0)])
    port_of_shipment = models.CharField(_("Port of Shipment"), max_length=150)
    port_of_arrival = models.CharField(_("Port of Arrival"), max_length=150)
    main_bank_name = models.CharField(_("Main Bank Name"), max_length=150)
    subsidiary_bank_name = models.CharField(_("Subsidiary Bank Name"), max_length=150)
    contract_expiration_date = models.DateField(_("Contract Expiration Date"))
    basic_form = models.OneToOneField(
        'BasicForm',
        on_delete=models.PROTECT,
        related_name='mocs_data',
        verbose_name=_("SSWG Basic Form"),
    )
    mocs1_file = models.FileField(_("mocs1_file"), upload_to=attachment_path)  #,null=True,blank=True
    mocs2_file = models.FileField(_("mocs2_file"), upload_to=attachment_path)  #,null=True,blank=True

    def __str__(self):
        return f"MOCS-{self.contract_number}"

    class Meta:
        verbose_name = _("SSWG MOCSData")
        verbose_name_plural = _("SSWG MOCSData")

class CBSData(LoggingModel):
    """Stores Central Bank of Sudan related data"""
    def attachment_path(self, filename):
        company = self.form.id
        date = self.created_at.date()
        return "company_{0}/sswg/{1}/{2}".format(company,date, filename)    

    PAYMENT_METHOD_CHOICES = (
        ('cash', _('Cash')),
        ('transfer', _('Bank Transfer')),
        ('cheque', _('Cheque')),
    )

    customer_account_number = models.CharField(_("Customer Account Number"), max_length=20)
    ex_form_number = models.CharField(_("EX-Form Number"), max_length=20)
    commercial_bank_name = models.CharField(_("Commercial Bank Name"), max_length=150)
    issued_amount = models.DateField(_("Issued Amount Date"))
    payment_method = models.CharField(_("Payment Method"), max_length=20, choices=PAYMENT_METHOD_CHOICES)
    basic_form = models.OneToOneField(
        'BasicForm',
        on_delete=models.PROTECT,
        related_name='cbs_data',
        verbose_name=_("SSWG Basic Form"),
    )

    cbs_file = models.FileField(_("cbs_file"), upload_to=attachment_path)  #,null=True,blank=True

    def __str__(self):
        return f"CBS-{self.customer_account_number}"
    
    class Meta:
        verbose_name = _("SSWG CBS")
        verbose_name_plural = _("SSWG CBS")

class BasicForm(LoggingModel):
    """Main form storing all related data"""

    STATE_1 = 1
    STATE_2 = 2
    STATE_3 = 3
    STATE_4 = 4
    STATE_5 = 5
    STATE_6 = 6
    STATE_7 = 7
    STATE_8 = 8
    STATE_9 = 9
    STATE_10 = 10

    STATE_CHOICES = {
        STATE_1:_("SSWG State 1"),
        STATE_2:_("SSWG State 2"), 
        STATE_3:_("SSWG State 3"),
        STATE_4:_("SSWG State 4"),
        STATE_5:_("SSWG State 5"),
        STATE_6:_("SSWG State 6"),
        STATE_7:_("SSWG State 7"),
        STATE_8:_("SSWG State 8"),
        STATE_9:_("SSWG State 9"),
        STATE_10:_("SSWG State 10"),
    }

    date = models.DateField(_("Form Date"))
    sn_no = models.CharField(_("Serial Number"), max_length=15, unique=True)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_1)
    
    def __str__(self):
        return f"{self.sn_no} - {self.date}"

    class Meta:
        verbose_name = _("SSWG Basic Form")
        verbose_name_plural = _("SSWG Basic Forms")
        ordering = ['-date']

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=SMRCData)
def update_smrc_data(sender, instance, **kwargs):
    if instance.form:
        instance.raw_weight = instance.form.gold_weight_in_gram
        instance.allow_count = instance.form.gold_alloy_count

@receiver(post_save, sender=SMRCData)
def create_company_details(sender, instance, **kwargs):
    """Automatically create CompanyDetails when SMRCData is created"""
    if instance.form:
        # Get the owner name from the related AppMoveGold instance
        owner_name = instance.form.owner_name_lst

        obj = None
        try:
            obj = CompanyDetails.objects.get(
                name=owner_name,
                basic_form=instance.basic_form,
            )
        except:
            pass

        if not obj or obj.name != owner_name \
            or obj.basic_form != instance.basic_form \
            or obj.surrogate_name != instance.form.repr_name \
            or obj.surrogate_id_type != instance.form.repr_identity_type \
            or obj.surrogate_id_val != instance.form.repr_identity \
            or obj.surrogate_id_phone != instance.form.repr_phone:

            if obj:
                obj.delete()

            CompanyDetails.objects.create(
                name=owner_name,
                basic_form=instance.basic_form,
                surrogate_name=instance.form.repr_name,
                surrogate_id_type=instance.form.repr_identity_type,
                surrogate_id_val=instance.form.repr_identity,
                surrogate_id_phone=instance.form.repr_phone,
                created_by=instance.created_by,
                updated_by=instance.updated_by,
            )
