from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

class CompanyDetails(models.Model):
    """Stores company and surrogate information"""
    ID_TYPE_PASSPORT = 1
    ID_TYPE_NATIONAL_ID = 2
    ID_TYPE_DRIVING_LICENSE = 3
    ID_TYPE_BUSINESS_REG = 4
    ID_TYPE_OTHER = 5
    
    ID_TYPE_CHOICES = (
        (ID_TYPE_PASSPORT, _('Passport')),
        (ID_TYPE_NATIONAL_ID, _('National ID')),
        (ID_TYPE_DRIVING_LICENSE, _('Driving License')),
        (ID_TYPE_BUSINESS_REG, _('Business Registration')),
        (ID_TYPE_OTHER, _('Other')),
    )

    name = models.CharField(_("Company Name"), max_length=255)
    surrogate_name = models.CharField(_("Surrogate Name"), max_length=255)
    surrogate_id_type = models.IntegerField(_("ID Type"), choices=ID_TYPE_CHOICES)
    surrogate_id_val = models.CharField(_("ID Value"), max_length=20)
    surrogate_id_phone = models.CharField(_("Contact Phone"), max_length=20)
    basic_form = models.OneToOneField(
        'BasicForm',
        on_delete=models.CASCADE,
        related_name='company_details',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.surrogate_name}"

class SMRCData(models.Model):
    """Stores SMRC-related measurements"""
    raw_weight = models.FloatField(_("Raw Weight"), validators=[MinValueValidator(0.0)])
    allow_count = models.PositiveIntegerField(_("Allow Count"))
    basic_form = models.OneToOneField(
        'BasicForm',
        on_delete=models.CASCADE,
        related_name='smrc_data',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"SMRC-{self.raw_weight}kg/{self.allow_count}"

class SSMOData(models.Model):
    """Stores SSMO-related measurements and certificate"""
    raw_weight = models.FloatField(_("Raw Weight"), validators=[MinValueValidator(0.0)])
    net_weight = models.FloatField(_("Net Weight"), validators=[MinValueValidator(0.0)])
    allow_count = models.PositiveIntegerField(_("Allow Count"))
    certificate_id = models.CharField(_("Certificate ID"), max_length=20) 
    basic_form = models.OneToOneField(
        'BasicForm',
        on_delete=models.CASCADE,
        related_name='ssmo_data',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"SSMO-{self.certificate_id}"

class MOCSData(models.Model):
    """Stores Ministry of Commerce and Supply related data"""
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
        on_delete=models.CASCADE,
        related_name='mocs_data',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"MOCS-{self.contract_number}"

class CBSData(models.Model):
    """Stores Central Bank of Sudan related data"""
    PAYMENT_METHOD_CHOICES = (
        ('cash', _('Cash')),
        ('transfer', _('Bank Transfer')),
        ('cheque', _('Cheque')),
    )

    customer_account_number = models.CharField(_("Customer Account Number"), max_length=20)
    commercial_bank_name = models.CharField(_("Commercial Bank Name"), max_length=150)
    issued_amount = models.DateField(_("Issued Amount Date"))
    payment_method = models.CharField(_("Payment Method"), max_length=20, choices=PAYMENT_METHOD_CHOICES)
    basic_form = models.OneToOneField(
        'BasicForm',
        on_delete=models.CASCADE,
        related_name='cbs_data',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"CBS-{self.customer_account_number}"

class BasicForm(models.Model):
    """Main form storing all related data"""
    date = models.DateField(_("Form Date"))
    sn_no = models.CharField(_("Serial Number"), max_length=15, unique=True)

    def __str__(self):
        return f"{self.sn_no} - {self.date}"

    class Meta:
        verbose_name = _("Basic Form")
        verbose_name_plural = _("Basic Forms")
        ordering = ['-date']
