from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from company_profile.models import LkpState

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

# class LkpStateDetails(models.Model):
#     state = models.OneToOneField(LkpState, on_delete=models.PROTECT,related_name="state_representative",verbose_name=_("state"))
#     code = models.CharField(_("code"),max_length=4)
#     next_serial_no = models.IntegerField(_("export_next_serial_no"))
    
#     class Meta:
#         verbose_name = _("dabtiaat state detail")
#         verbose_name_plural = _("dabtiaat state details")

class TblStateRepresentative2(models.Model):
    AUTHORITY_SMRC = 2
    AUTHORITY_APPROVED = 3
    # AUTHORITY_SHORTAT_2LM3ADIN = 4
    # AUTHORITY_2LESTIKHBARAT_2L3ASKRIA = 5
    # AUTHORITY_SMRC_NAFIZA = 6

    AUTHORITY_CHOICES = {
        AUTHORITY_SMRC: _('authority_smrc'),
        # AUTHORITY_APPROVED: _('authority_approved'),
        # AUTHORITY_SHORTAT_2LM3ADIN: _('authority_shortat_2lm3adin'),
        # AUTHORITY_2LESTIKHBARAT_2L3ASKRIA: _('authority_2lestikhbarat_2l3askria'),
        # AUTHORITY_SMRC_NAFIZA: _('authority_smrc_nafiza'),
    }

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="state_representative2",verbose_name=_("user"))
    name = models.CharField(_("name"),max_length=100)
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    authority = models.IntegerField(_("authority"), choices=AUTHORITY_CHOICES, default=AUTHORITY_SMRC)

    def __str__(self):
        return f'{self.user} ({self.state.name})'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['state', 'authority'], name='unique_state_authority_dabtiaat')
        ]

        verbose_name = _("state representative")
        verbose_name_plural = _("state representatives")

class AppDabtiaat(LoggingModel):

    STATE_DRAFT = 1
    STATE_SMRC = 2
    STATE_APPROVED = 3
    # STATE_SHORTAT_2LM3ADIN = 4
    # STATE_2LESTIKHBARAT_2L3ASKRIA = 5
    # STATE_SSMO = 6
    # STATE_WAIVED = 7
    STATE_CANCELED = 8

    STATE_CHOICES = {
        STATE_DRAFT: _('state_draft'),
        STATE_SMRC: _('state_smrc'),
        STATE_APPROVED: _('state_approved'),
        # STATE_SHORTAT_2LM3ADIN: _('state_shortat_2lm3adin'),
        # STATE_2LESTIKHBARAT_2L3ASKRIA: _('state_2lestikhbarat_2l3askria'),
        # STATE_SSMO: _('state_ssmo'),
        # STATE_WAIVED: _('state_waived'),
        STATE_CANCELED: _('state_canceled'),
    }

    def attachement_path(self, filename):
        date = self.created_at.date()
        return "dabtiaat/{0}/{1}".format(date, filename)    

    date = models.DateField(_("date"))
    report_number = models.CharField(_("Report number"), max_length=20, null=True, blank=True,default='')
    # gold_weight_in_gram = models.FloatField(_("gold_weight_in_gram"))
    # gold_price = models.FloatField(_("gold_price"))
    # gold_caliber = models.FloatField(_("gold_caliber"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)
    attachement_file = models.FileField(_("attachement_file"),upload_to=attachement_path,null=True,blank=True)
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))

    @property
    def sum_of_weight_in_gram(self):
        total =self.appdabtiaatdetails_set.aggregate(sum=models.Sum("gold_weight_in_gram"))['sum'] or 0

        return total

    @property
    def avg_of_price(self):
        total =self.appdabtiaatdetails_set.aggregate(avg=models.Avg("gold_price"))['avg'] or 0

        return total

    @property
    def sum_of_weight_multiply_price(self):
        qs = self.appdabtiaatdetails_set.all()
        total = 0
        for obj in qs:
            total += obj.gold_weight_in_gram*obj.gold_price
        return total

    @property
    def total_price(self):
        return self.gold_weight_in_gram*self.gold_price

    @property
    def koli_amount(self):
        return self.sum_of_weight_multiply_price*0.22


    @property
    def al3wayid_aljalila_amount(self):
        return self.sum_of_weight_multiply_price*0.10

    @property
    def alhafiz_amount(self):
        return self.sum_of_weight_multiply_price*0.10

    @property
    def alniyaba_amount(self):
        return self.sum_of_weight_multiply_price*0.02

    @property
    def smrc_amount(self):
        return self.alhafiz_amount*0.10

    @property
    def state_amount(self):
        return self.alhafiz_amount*0.10

    @property
    def police_amount(self):
        return self.alhafiz_amount*0.10

    @property
    def amn_amount(self):
        return self.alhafiz_amount*0.10

    @property
    def riasat_alquat_aldaabita_amount(self):
        return self.alhafiz_amount*0.10

    @property
    def alquat_aldaabita_amount(self):
        return self.alhafiz_amount*0.50

    def __str__(self):
        return f'{self.source_state} ({self.sum_of_weight_in_gram} جرام)'

    class Meta:
        ordering = ["-date","-id"]
        verbose_name = _("dabtiaat app")
        verbose_name_plural = _("dabtiaat app")

class AppDabtiaatDetails(models.Model):
    app_dabtiaat = models.ForeignKey(AppDabtiaat, on_delete=models.PROTECT,verbose_name =_("app_dabtiaat"))

    alloy_id = models.CharField(_("alloy_id"),max_length=20,null=True,blank=True, default='')
    gold_weight_in_gram = models.FloatField(_("gold_weight_in_gram"))
    gold_price = models.FloatField(_("gold_price"))
    gold_caliber = models.FloatField(_("gold_caliber"),null=True,blank=True,default=0)

    class Meta:
        verbose_name = _("تفاصيل استمارة ضبطية")
        verbose_name_plural = _("تفاصيل استمارة ضبطية")

class SettlementType(models.Model):
    name = models.CharField(_("name"),max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("settlement type")
        verbose_name_plural = _("settlement types")

class RevenueSettlement(LoggingModel):
    STATE_DRAFT = 1
    STATE_SMRC = 2
    STATE_APPROVED = 3
    STATE_CANCELED = 8

    STATE_CHOICES = {
        STATE_DRAFT: _('state_draft'),
        STATE_SMRC: _('state_smrc'),
        STATE_APPROVED: _('state_approved'),
        STATE_CANCELED: _('state_canceled'),
    }

    settlement_type = models.ForeignKey(SettlementType, on_delete=models.PROTECT,verbose_name=_("settlement_type"))
    date = models.DateField(_("date"))
    amount = models.FloatField(_("amount"))
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)

    def __str__(self):
        return f"{self.settlement_type.name} ({self.date})"

    class Meta:
        ordering = ["-date",]
        verbose_name = _("Revenue Settlement")
        verbose_name_plural = _("Revenue Settlement")
