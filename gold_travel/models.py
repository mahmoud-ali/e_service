from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

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

    STATE_CHOICES = {
        STATE_DRAFT: _('state_draft'),
        STATE_SMRC: _('state_smrc'),
        STATE_2MN_2LM3ADIN: _('state_2mn_2lm3adin'),
        STATE_SHORTAT_2LM3ADIN: _('state_shortat_2lm3adin'),
        STATE_2LESTIKHBARAT_2L3ASKRIA: _('state_2lestikhbarat_2l3askria'),
    }

    def attachement_path(self, filename):
        company = self.owner_name
        date = self.created_at.date()
        return "company_{0}/travel/{1}/{2}".format(company,date, filename)    

    date = models.DateField(_("date"))
    destination = models.IntegerField(_("destination"), choices=DESTINATION_CHOICES, default=DESTINATION_SSMO)
    owner_name = models.CharField(_("owner_name"),max_length=100)
    owner_address = models.CharField(_("owner_address"),max_length=150)
    repr_name = models.CharField(_("repr_name"),max_length=100)
    repr_address = models.CharField(_("repr_address"),max_length=150)
    repr_phone = models.CharField(_("repr_phone"),max_length=30)
    repr_identity = models.CharField(_("repr_identity"),max_length=50)
    repr_identity_issue_date = models.DateField(_("repr_identity_issue_date"))
    gold_weight_in_gram = models.FloatField(_("gold_weight_in_gram"))
    gold_alloy_count = models.IntegerField(_("gold_alloy_count"))
    gold_description = models.CharField(_("gold_description"),max_length=100)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES, default=STATE_DRAFT)
    attachement_file = models.FileField(_("attachement_file"),upload_to=attachement_path)

    def __str__(self):
        return f'{self.owner_name} ({self.gold_weight_in_gram} {_("gram")})'

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Move Gold")
        verbose_name_plural = _("Move Gold")
        indexes = [
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
    alloy_id = models.CharField(_("alloy_id"),max_length=100)
    alloy_weight_in_gram = models.FloatField(_("alloy_weight_in_gram"))
    alloy_shape = models.IntegerField(_("alloy_shape"), choices=ALLOY_SHAPE_CHOICES)
    alloy_note = models.CharField(_("alloy_note"),max_length=150)

    def __str__(self):
        return f'{self.alloy_id}'

    class Meta:
        verbose_name = _("alloy detail")
        verbose_name_plural = _("alloy details")
