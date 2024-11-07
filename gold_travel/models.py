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

class LkpStateDetails(models.Model):
    state = models.OneToOneField(LkpState, on_delete=models.PROTECT,related_name="state_gold_travel",verbose_name=_("state"))
    code = models.CharField(_("code"),max_length=4)
    next_serial_no = models.IntegerField(_("next_serial_no"))
    has_2lestikhbarat_2l3askria = models.BooleanField(_("has_2lestikhbarat_2l3askria"))
    
    class Meta:
        verbose_name = _("gold travel state detail")
        verbose_name_plural = _("gold travel state details")

class TblStateRepresentative(models.Model):
    AUTHORITY_SMRC = 2
    AUTHORITY_2MN_2LM3ADIN = 3
    AUTHORITY_SHORTAT_2LM3ADIN = 4
    AUTHORITY_2LESTIKHBARAT_2L3ASKRIA = 5
    AUTHORITY_SMRC_NAFIZA = 6

    AUTHORITY_CHOICES = {
        AUTHORITY_SMRC: _('authority_smrc'),
        AUTHORITY_2MN_2LM3ADIN: _('authority_2mn_2lm3adin'),
        AUTHORITY_SHORTAT_2LM3ADIN: _('authority_shortat_2lm3adin'),
        AUTHORITY_2LESTIKHBARAT_2L3ASKRIA: _('authority_2lestikhbarat_2l3askria'),
        AUTHORITY_SMRC_NAFIZA: _('authority_smrc_nafiza'),
    }

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="state_representative",verbose_name=_("user"))
    name = models.CharField(_("name"),max_length=100)
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    authority = models.IntegerField(_("authority"), choices=AUTHORITY_CHOICES, default=AUTHORITY_SMRC)

    def __str__(self):
        return f'{self.user} ({self.state.name})'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['state', 'authority'], name='unique_state_authority ')
        ]

        verbose_name = _("state representative")
        verbose_name_plural = _("state representatives")

class AppMoveGold(LoggingModel):
    DESTINATION_SSMO = 1
    DESTINATION_CHOICES = {
        DESTINATION_SSMO: _('ssmo_name'),
    }

    STATE_DRAFT = 1
    STATE_SMRC = 2
    STATE_2MN_2LM3ADIN = 3
    STATE_SHORTAT_2LM3ADIN = 4
    STATE_2LESTIKHBARAT_2L3ASKRIA = 5
    STATE_SSMO = 6

    STATE_CHOICES = {
        STATE_DRAFT: _('state_draft'),
        STATE_SMRC: _('state_smrc'),
        STATE_2MN_2LM3ADIN: _('state_2mn_2lm3adin'),
        STATE_SHORTAT_2LM3ADIN: _('state_shortat_2lm3adin'),
        STATE_2LESTIKHBARAT_2L3ASKRIA: _('state_2lestikhbarat_2l3askria'),
        STATE_SSMO: _('state_ssmo'),
    }

    IDENTITY_PASSPORT = 1
    IDENTITY_PERSONAL = 2
    IDENTITY_NATIONAL_ID = 3
    IDENTITY_DRIVING_LICENSE = 4

    IDENTITY_CHOICES = {
        IDENTITY_PASSPORT: _('identity_passport'),
        IDENTITY_PERSONAL: _('identity_personal'),
        IDENTITY_NATIONAL_ID: _('identity_national_id'),
        IDENTITY_DRIVING_LICENSE: _('identity_driving_license'),
    }

    def attachement_path(self, filename):
        company = self.owner_name
        date = self.created_at.date()
        return "company_{0}/travel/{1}/{2}".format(company,date, filename)    
    
    code = models.CharField(_("code"),max_length=20, default='')
    date = models.DateField(_("date"))
    destination = models.IntegerField(_("destination"), choices=DESTINATION_CHOICES, default=DESTINATION_SSMO)
    owner_name = models.CharField(_("owner_name"),max_length=100)
    owner_address = models.CharField(_("owner_address"),max_length=150)
    repr_name = models.CharField(_("repr_name"),max_length=100)
    repr_address = models.CharField(_("repr_address"),max_length=150)
    repr_phone = models.CharField(_("repr_phone"),max_length=30)
    repr_identity_type = models.IntegerField(_("repr_identity_type"), choices=IDENTITY_CHOICES, default=IDENTITY_PASSPORT)
    repr_identity = models.CharField(_("repr_identity"),max_length=50)
    repr_identity_issue_date = models.DateField(_("repr_identity_issue_date"))
    # gold_weight_in_gram = models.FloatField(_("gold_weight_in_gram"))
    # gold_alloy_count = models.IntegerField(_("gold_alloy_count"))
    # gold_description = models.CharField(_("gold_description"),max_length=100)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)
    attachement_file = models.FileField(_("attachement_file"),upload_to=attachement_path,null=True,blank=True)
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))

    @property
    def gold_weight_in_gram(self):
        sum = self.appmovegolddetails_set.aggregate(sum=models.Sum("alloy_weight_in_gram"))['sum'] or 0
        return f'{sum:.2f}'

    def gold_alloy_count_per_shape(self,shape=None):
        if(not shape):
            return self.appmovegolddetails_set.count()
        else:
            return self.appmovegolddetails_set.filter(alloy_shape=shape).count()
    @property        
    def gold_alloy_count(self):
        return self.gold_alloy_count_per_shape()
    
    @property
    def gold_description(self):
        arr = []
        for shape,shape_desc in AppMoveGoldDetails.ALLOY_SHAPE_CHOICES.items():
            count = self.gold_alloy_count_per_shape(shape=shape)
            if count > 0:
                arr.append(f"عدد ({count}) سبيكة {shape_desc} الشكل")

        return '، '.join(arr)+'.'

    def __str__(self):
        return f'{self.owner_name} ({self.gold_weight_in_gram} {_("gram")})'

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Move Gold")
        verbose_name_plural = _("Move Gold")
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["owner_name"]),
        ]

class AppMoveGoldDetails(models.Model):
    ALLOY_SHAPE_RECTANGULAR = 1
    ALLOY_SHAPE_CIRCULAR = 2
    ALLOY_SHAPE_CHOICES = {
        ALLOY_SHAPE_RECTANGULAR: _('alloy_shape_rectangular'),
        ALLOY_SHAPE_CIRCULAR: _('alloy_shape_circular'),
    }

    master  = models.ForeignKey(AppMoveGold, on_delete=models.PROTECT)
    alloy_id = models.CharField(_("alloy_id"),max_length=20, default='')
    alloy_weight_in_gram = models.FloatField(_("alloy_weight_in_gram"))
    alloy_shape = models.IntegerField(_("alloy_shape"), choices=ALLOY_SHAPE_CHOICES)
    alloy_note = models.CharField(_("alloy_note"),max_length=150,null=True,blank=True)

    def __str__(self):
        return f"{_('alloy_id')} {self.alloy_id}"

    class Meta:
        verbose_name = _("alloy detail")
        verbose_name_plural = _("alloy details")

class AppPrepareGold(LoggingModel):
    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_CHOICES = {
        STATE_DRAFT: _('state_draft'),
        STATE_CONFIRMED: _('state_confirmed'),
    }

    date = models.DateField(_("date"))
    owner_name = models.CharField(_("owner_name"),max_length=100)
    gold_weight_in_gram = models.FloatField(_("gold_weight_in_gram"))
    issuer = models.ForeignKey(TblStateRepresentative, on_delete=models.PROTECT,verbose_name=_("issuer"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))

    def __str__(self):
        return f'{self.owner_name} ({self.gold_weight_in_gram})'

    class Meta:
        verbose_name = _("prepare gold")
        verbose_name_plural = _("prepare gold")
