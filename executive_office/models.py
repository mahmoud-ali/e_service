from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from company_profile.models import LkpState

STATE_DRAFT = 1
STATE_CONFIRMED = 2
STATE_EXPIRED = 3

STATE_CHOICES = {
    STATE_DRAFT: _('state_draft'),
    STATE_CONFIRMED: _('state_confirmed'),
    STATE_EXPIRED: _('state_expired'),
}

ORDER_PROCEDURE = 1
ORDER_FOLLOWUP = 2

ORDER_CHOICES = {
    ORDER_PROCEDURE: _('order_procedure'),
    ORDER_FOLLOWUP: _('order_followup'),
}

class LoggingModel(models.Model):
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))
    
    class Meta:
        abstract = True

class Contact(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="executive_user",verbose_name=_("user"))
    name = models.CharField(_("name"),max_length=100)

    def __str__(self):
        return f'{self.name} ({self.user})'

    class Meta:
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")

class ProcedureType(models.Model):
    name = models.CharField(_("name"),max_length=100)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _("procedure_type")
        verbose_name_plural = _("procedure_types")

class ProcedureTypeTasksTemplate(models.Model):
    procedure_type = models.ForeignKey(ProcedureType, on_delete=models.PROTECT,verbose_name=_("procedure_type"))
    title = models.CharField(_("title"),max_length=200)
    order = models.IntegerField(_("order"),choices=ORDER_CHOICES)
    assign_to = models.ForeignKey(Contact, on_delete=models.PROTECT,verbose_name=_("assign_to"))

    def __str__(self):
        return f'{self.procedure_type} ({self.title}/{self.assign_to})'

    class Meta:
        verbose_name = _("procedure type task template")
        verbose_name_plural = _("procedure type task templates")

class SenderEntity(models.Model):
    name = models.CharField(_("name"),max_length=100)

    def __str__(self):
        return f'{self.name} ({self.user})'

    class Meta:
        verbose_name = _("contact")
        verbose_name_plural = _("contacts")

class Inbox(LoggingModel):
    procedure_type = models.ForeignKey(ProcedureType, on_delete=models.PROTECT,verbose_name=_("procedure_type"))
    sender_entity = models.ForeignKey(SenderEntity, on_delete=models.PROTECT,verbose_name=_("sender_entity"))
    start_date = models.DateTimeField(_("start_date"))
    expected_due_date = models.DateTimeField(_("expected_due_date"))
    finish_date = models.DateTimeField(_("finish_date"),null=True)

    def __str__(self):
        return f'{self.procedure_type} ({self.sender_entity})'

    class Meta:
        verbose_name = _("inbox")
        verbose_name_plural = _("inbox")

def inbox_path(instance, filename):
    return "executive_office/{0}/{1}".format(instance.inbox.sender_entity, filename)    

class InboxAttachment(models.Model):
    inbox = models.ForeignKey(Inbox, on_delete=models.PROTECT,verbose_name=_("inbox"))
    attachment_file = models.FileField(_("attachment_file"),upload_to=inbox_path)

    class Meta:
        verbose_name = _("inbox attachment")
        verbose_name_plural = _("inbox attachments")

class InboxTasks(models.Model):
    inbox = models.ForeignKey(Inbox, on_delete=models.PROTECT,verbose_name=_("inbox"))
    title = models.CharField(_("title"),max_length=200)
    order = models.IntegerField(_("order"),choices=ORDER_CHOICES)
    assign_to = models.ForeignKey(Contact, on_delete=models.PROTECT,verbose_name=_("assign_to"))

    def __str__(self):
        return f'{self.inbox} ({self.title}/{self.assign_to})'

    class Meta:
        verbose_name = _("inbox task")
        verbose_name_plural = _("inbox tasks")
