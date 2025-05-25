from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from gold_travel.models import LkpOwner,AppMoveGold

class LoggingModel(models.Model):
    """
    An abstract base class model that provides self-
    updating ``created_at`` and ``updated_at`` fields for respons959034able user.
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
    surrogate_id_val = models.CharField(_("ID Value"), max_length=50)
    surrogate_id_phone = models.CharField(_("Contact Phone"), max_length=50)
    total_weight = models.FloatField(_("الوزن الكلي"),default=0)
    total_count = models.IntegerField(_("عدد السبائك"),default=0)
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


class TransferRelocationFormData(LoggingModel):
    """Stores SMRC-related measurements"""
    def attachment_path(self, filename):
        company = self.basic_form.id
        date = self.created_at.date()
        return "company_{0}/sswg/{1}/{2}".format(company,date, filename)    

    # form_type = models.IntegerField(_("form_type"), choices=AppMoveGold.FORM_TYPE_CHOICES, default=AppMoveGold.FORM_TYPE_GOLD_EXPORT)
    form = models.ForeignKey(AppMoveGold, on_delete=models.PROTECT,verbose_name=_("Move Gold"))

    raw_weight = models.FloatField(_("Raw Weight"), validators=[MinValueValidator(0.0)])
    allow_count = models.PositiveIntegerField(_("Allow Count"))
    basic_form = models.ForeignKey(
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
        company = self.basic_form.id
        date = self.created_at.date()
        return "company_{0}/sswg/{1}/{2}".format(company,date, filename)    

    raw_weight = models.FloatField(_("Raw Weight"), validators=[MinValueValidator(0.0)])
    net_weight = models.FloatField(_("Net Weight"), validators=[MinValueValidator(0.0)])
    allow_count = models.PositiveIntegerField(_("Allow Count"))
    certificate_id = models.CharField(_("Certificate ID"), max_length=20) 
    return_weight = models.FloatField(_("الذهب الراجع"),help_text=_("في حال التصنيع والإعادة"),default=0, validators=[MinValueValidator(0.0)])

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
        company = self.basic_form.id
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
        return str(self.id)

    class Meta:
        verbose_name = _("SSWG SmrcNoObjectionData")
        verbose_name_plural = _("SSWG SmrcNoObjectionData")

class MmAceptanceData(LoggingModel):
    """Stores SSMO-related measurements and certificate"""
    def attachment_path(self, filename):
        company = self.basic_form.id
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
        return str(self.id)

    class Meta:
        verbose_name = _("SSWG MmAceptanceData")
        verbose_name_plural = _("SSWG MmAceptanceData")

class MOCSData(LoggingModel):
    """Stores Ministry of Commerce and Supply related data"""
    def attachment_path(self, filename):
        company = self.basic_form.id
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
    # mocs2_file = models.FileField(_("mocs2_file"), upload_to=attachment_path)  #,null=True,blank=True

    def __str__(self):
        return f"MOCS-{self.contract_number}"

    class Meta:
        verbose_name = _("SSWG MOCSData")
        verbose_name_plural = _("SSWG MOCSData")

class COCSData(LoggingModel):
    """Stores Chamber of Commerce related data"""
    def attachment_path(self, filename):
        company = self.basic_form.id
        date = self.created_at.date()
        return "company_{0}/sswg/{1}/{2}".format(company,date, filename)    

    basic_form = models.OneToOneField(
        'BasicForm',
        on_delete=models.PROTECT,
        related_name='coc_data',
        verbose_name=_("SSWG Basic Form"),
    )
    cocs_file = models.FileField(_("mocs2_file"), upload_to=attachment_path)

    def __str__(self):
        return f"COC-{self.id}"

    class Meta:
        verbose_name = _("الغرفة التجارية")
        verbose_name_plural = _("الغرفة التجارية")

class CBSData(LoggingModel):
    """Stores Central Bank of Sudan related data"""
    def attachment_path(self, filename):
        company = self.basic_form.id
        date = self.created_at.date()
        return "company_{0}/sswg/{1}/{2}".format(company,date, filename)    

    PAYMENT_METHOD_CHOICES = (
        ('cash', _('دفع مقدم')),
        ('transfer', _('تحويل انصبة')),
        # ('cheque', _('Cheque')),
    )

    customer_account_number = models.CharField(_("Customer Account Number"), max_length=20)
    ex_form_number = models.CharField(_("EX-Form Number"), max_length=20)
    commercial_bank_name = models.CharField(_("Commercial Bank Name"), max_length=150)
    issued_amount = models.FloatField(_("Issued Amount"))
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
    STATE_11 = 11

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
        STATE_11:_("SSWG State 11"),
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

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []

        if 'sswg_secretary' in user_groups:
            if self.state == self.STATE_1:
                states.append((self.STATE_2, self.STATE_CHOICES[self.STATE_2]))

        if 'sswg_economic_security' in user_groups:
            if self.state == self.STATE_2:
                states.append((self.STATE_3, self.STATE_CHOICES[self.STATE_3]))

        if 'sswg_ssmo' in user_groups:
            if self.state == self.STATE_3:
                states.append((self.STATE_4, self.STATE_CHOICES[self.STATE_4]))

        if 'sswg_smrc' in user_groups:
            if self.state == self.STATE_4:
                states.append((self.STATE_5, self.STATE_CHOICES[self.STATE_5]))

        if 'sswg_mm' in user_groups:
            if self.state == self.STATE_5:
                states.append((self.STATE_6, self.STATE_CHOICES[self.STATE_6]))

        if 'sswg_military_intelligence' in user_groups:
            if self.state == self.STATE_6:
                states.append((self.STATE_7, self.STATE_CHOICES[self.STATE_7]))

        if 'sswg_moc' in user_groups:
            if self.state == self.STATE_7:
                states.append((self.STATE_8, self.STATE_CHOICES[self.STATE_8]))

        if 'sswg_cbs' in user_groups:
            if self.state == self.STATE_8:
                states.append((self.STATE_9, self.STATE_CHOICES[self.STATE_9]))

        if 'sswg_coc' in user_groups:
            if self.state == self.STATE_9:
                states.append((self.STATE_10, self.STATE_CHOICES[self.STATE_10]))

        if 'sswg_custom_force' in user_groups:
            if self.state == self.STATE_10:
                states.append((self.STATE_11, self.STATE_CHOICES[self.STATE_11]))

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


    # def get_next_state(self):
    #     if self.state < len(self.STATE_CHOICES):
    #         return self.state + 1
        
    #     # return self.state
    
    # def get_next_state_display(self):
    #     curr_index = self.get_next_state()

    #     if curr_index:
    #         return self.STATE_CHOICES[curr_index]

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=BasicForm)
def update_basic_form_state(sender, instance, **kwargs):
    if instance.pk:
        obj = BasicForm.objects.get(pk=instance.pk)

        if obj.state != instance.state and instance.state == BasicForm.STATE_2:
            # update state
            for t in obj.smrc_data.all():
                t.form.state = AppMoveGold.STATE_SSMO
                t.form.save()

@receiver(pre_save, sender=TransferRelocationFormData)
def update_smrc_data(sender, instance, **kwargs):
    """Automatically update SMRCData with values from related AppMoveGold form before saving.
    
    Triggers when SMRCData is saved:
    - Copies gold_weight_in_gram from AppMoveGold to raw_weight
    - Copies gold_alloy_count from AppMoveGold to allow_count
    - Only operates when form relation is set
    """
    if instance.form:
        instance.raw_weight = instance.form.gold_weight_in_gram
        instance.allow_count = instance.form.gold_alloy_count

@receiver(post_save, sender=TransferRelocationFormData)
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

        # if obj and (obj.name != owner_name \
        #     or obj.basic_form != instance.basic_form \
        #     or obj.surrogate_name != instance.form.repr_name \
        #     or obj.surrogate_id_type != instance.form.repr_identity_type \
        #     or obj.surrogate_id_val != instance.form.repr_identity \
        #     or obj.surrogate_id_phone != instance.form.repr_phone):

        #     if obj:
        #         obj.delete()

        try:
            obj,_ = CompanyDetails.objects.get_or_create(
                name=owner_name,
                basic_form=instance.basic_form,
                surrogate_name=instance.form.repr_name,
                surrogate_id_type=instance.form.repr_identity_type,
                surrogate_id_val=instance.form.repr_identity,
                surrogate_id_phone=instance.form.repr_phone,
                created_by=instance.created_by,
                updated_by=instance.updated_by,
            )
        except:
            pass

        ##### update totals
        if obj:
            all_forms = obj.basic_form.smrc_data.all()
            total_weight = all_forms.aggregate(sum=models.Sum('raw_weight'))['sum']
            total_count = all_forms.aggregate(sum=models.Sum('allow_count'))['sum']

            obj.total_weight=total_weight
            obj.total_count=total_count
            obj.save()
