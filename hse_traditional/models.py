import sys
from django.db import models
from django.conf import settings
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.utils.html import strip_tags

from company_profile.models import LkpState
from hse_traditional.utils import get_user_emails_by_groups

MONTH_JAN = 1
MONTH_FEB = 2
MONTH_MAR = 3
MONTH_APR = 4
MONTH_MAY = 5
MONTH_JUN = 6
MONTH_JLY = 7
MONTH_AUG = 8
MONTH_SEP = 9
MONTH_OCT = 10
MONTH_NOV = 11
MONTH_DEC = 12

MONTH_CHOICES = {
    MONTH_JAN: _('MONTH_JAN'),
    MONTH_FEB: _('MONTH_FEB'),
    MONTH_MAR: _('MONTH_MAR'),
    MONTH_APR: _('MONTH_APR'),
    MONTH_MAY: _('MONTH_MAY'),
    MONTH_JUN: _('MONTH_JUN'),
    MONTH_JLY: _('MONTH_JLY'),
    MONTH_AUG: _('MONTH_AUG'),
    MONTH_SEP: _('MONTH_SEP'),
    MONTH_OCT: _('MONTH_OCT'),
    MONTH_NOV: _('MONTH_NOV'),
    MONTH_DEC: _('MONTH_DEC'),
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

class TblStateRepresentative(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="hse_tra_state",verbose_name=_("user"))
    name = models.CharField(_("name"),max_length=100)
    state = models.ForeignKey(LkpState, on_delete=models.PROTECT, related_name="hse_tra_state",verbose_name=_("state"))

    def __str__(self):
        return f'{self.user} ({self.state.name})'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'state'], name='unique_user_state')
        ]

        verbose_name = _("state representative")
        verbose_name_plural = _("state representatives")

class HseTraditionalReport(LoggingModel):
    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED: _("confirmed"),
        STATE_APPROVED:_("approved"),
    }

    year = models.IntegerField(_("year"))
    month = models.IntegerField(_("month"), choices=MONTH_CHOICES.items())
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)

    class Meta:
        verbose_name = _("Hse Traditional Monthly Report")
        verbose_name_plural = _("Hse Traditional Monthly Reports")

    def __str__(self):
        return f"{MONTH_CHOICES[self.month]}/{self.year}"

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []
        if 'hse_tra_state_employee' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))

        if 'hse_tra_manager' in user_groups:
            if self.state == self.STATE_CONFIRMED:
                states.append((self.STATE_APPROVED, self.STATE_CHOICES[self.STATE_APPROVED]))
                states.append((self.STATE_DRAFT, self.STATE_CHOICES[self.STATE_DRAFT]))

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

class EnvironmentalInspection(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="environmental_inspections")
    market_name = models.CharField(_("market_name"), max_length=255)
    what = models.TextField(_("What ماذا"))
    who = models.CharField(_("Who من"), max_length=255)
    hazard_identified = models.TextField(_("Hazard identified تحديد المخاطر"))
    closed_date = models.DateField(_("Closed date الاغلاق"))

    class Meta:
        verbose_name = _("Environmental Inspection")
        verbose_name_plural = _("Environmental Inspections")

class WasteManagement(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="waste_managements")
    market_name = models.CharField(_("Market name / اسم السوق"), max_length=255)
    item_description = models.TextField(_("Item description وصف"))
    material_by_ton = models.FloatField(_("Material by ton الخام بالطن"))
    comment = models.TextField(_("Comment تعليق"))

    class Meta:
        verbose_name = _("Waste Management")
        verbose_name_plural = _("Waste Managements")

class TrainingAwareness(models.Model):
    TRAINING_TYPE1 = 1
    TRAINING_TYPE2 = 2

    TRAINING_CHOICES = {
        TRAINING_TYPE1: _("Training - تدريب"),
        TRAINING_TYPE2: _("Awareness - إرشاد"),
    }

    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="training_awarenesses")
    market_name = models.CharField(_("Market name / اسم السوق"), max_length=255)
    traning_type = models.IntegerField(_("نوع التدريب -  type of training"), choices=TRAINING_CHOICES.items())
    subject = models.TextField(_("Subject الموضوع"))
    attendees = models.IntegerField(_("Attendees الحضور"))
    notes = models.TextField(_("Notes ملاحظات"))

    class Meta:
        verbose_name = _("Training Awareness")
        verbose_name_plural = _("Training Awareness")

class ArrangementOfMarkets(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="arrangement_of_markets")
    market_name = models.CharField(_("Market name / اسم السوق"), max_length=255)
    percent = models.IntegerField(_("Percent % النسبة"))
    notes = models.TextField(_("Notes ملاحظات"))

    class Meta:
        verbose_name = _("Arrangement Of Market")
        verbose_name_plural = _("Arrangement Of Markets")

class EnvironmentalRequirements(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="environmental_requirements")
    market_name = models.CharField(_("Market name / اسم السوق"), max_length=255)
    percent = models.FloatField(_("Percent % النسبة"))

    class Meta:
        verbose_name = _("Environmental Requirement")
        verbose_name_plural = _("Environmental Requirements")

class QuickEmergencyTeam(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="quick_emergency_teams")
    issue = models.TextField(_("issue"))
    communication_factors = models.TextField(_("Communication factors"))
    notes = models.TextField(_("Notes ملاحظات"))

    class Meta:
        verbose_name = _("Quick Emergency Team")
        verbose_name_plural = _("Quick Emergency Teams")

class Achievement(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="achievements")
    name = models.CharField(_("Achievements   الإنجازات"), max_length=255)
    brief = models.TextField(_("Describe briefly , وصف مختصر"))

    class Meta:
        verbose_name = _("Achievement")
        verbose_name_plural = _("Achievements")

class HseTraditionalAccident(LoggingModel):
    ACCIDENT_TYPE_SAFTY = 'safty'
    ACCIDENT_TYPE_ENVIRONMENTAL = 'enviromental'

    ACCIDENT_TYPE_CHOICES = {
        ACCIDENT_TYPE_SAFTY: _("Safty - سلامة"),
        ACCIDENT_TYPE_ENVIRONMENTAL: _("Environmental - بيئي"),
    }

    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED: _("confirmed"),
        STATE_APPROVED: _("approved"),
    }

    type = models.CharField(_("accident_type"), max_length=20, choices=ACCIDENT_TYPE_CHOICES.items())
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("source_state"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)
    what = models.TextField(_("what - ماذا"))
    when = models.DateTimeField(_("when - متى"))
    where = models.TextField(_("where - اين"))

    class Meta:
        verbose_name = _("Hse Traditional Accident")
        verbose_name_plural = _("Hse Traditional Accidents")

    def __str__(self):
        return f"{self.ACCIDENT_TYPE_CHOICES[self.type]}/{self.what}"

    def send_notifications(self):
        subject = 'تقرير حادث' #f"{self.ACCIDENT_TYPE_CHOICES[self.type]}/{self.what}"
        message = f"""
            الإدارة العامة للبيئة والسلامة / إدارة التعدين التقليدي
            الولاية: {self.source_state}
            ماذا حدث: {self.what}
            متى حدث: {self.when}
            اين حدث: {self.where}

            رابط التفاصيل: https://mineralsgate.com/app/managers/hse_traditional/hsetraditionalaccident/{self.id}/change/

        """
        emails = get_user_emails_by_groups(['hse_tra_manager','hse_tra_gm']) + ['omer.awad@smrc.sd',]
        try:
            send_mail(
                subject,
                strip_tags(message),
                None,
                emails,
                html_message=message,
                fail_silently=False,
            )        
        except:
            print("Error sending email",sys.stderr)

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []
        if 'hse_tra_state_employee' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))

        if 'hse_tra_manager' in user_groups:
            if self.state == self.STATE_CONFIRMED:
                states.append((self.STATE_APPROVED, self.STATE_CHOICES[self.STATE_APPROVED]))
                states.append((self.STATE_DRAFT, self.STATE_CHOICES[self.STATE_DRAFT]))

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
    
class HseTraditionalAccidentWho(models.Model):
    accident = models.ForeignKey(HseTraditionalAccident, on_delete=models.PROTECT, related_name="who_list")
    who = models.CharField(_("who"), max_length=150)

    class Meta:
        verbose_name = _("Hse Traditional Accident Who")
        verbose_name_plural = _("Hse Traditional Accident Whos")

class HseTraditionalAccidentWhy(models.Model):
    accident = models.ForeignKey(HseTraditionalAccident, on_delete=models.PROTECT, related_name="why_list")
    why = models.TextField(_("why"))

    class Meta:
        verbose_name = _("Hse Traditional Accident Why")
        verbose_name_plural = _("Hse Traditional Accident Whys")

class HseTraditionalAccidentInjury(models.Model):
    accident = models.ForeignKey(HseTraditionalAccident, on_delete=models.PROTECT, related_name="injuries_list")
    injuries = models.TextField(_("injuries"))

    class Meta:
        verbose_name = _("Hse Traditional Accident injury")
        verbose_name_plural = _("Hse Traditional Accident injuries")

class HseTraditionalAccidentDamage(models.Model):
    accident = models.ForeignKey(HseTraditionalAccident, on_delete=models.PROTECT, related_name="damages_list")
    damage = models.TextField(_("damage"))

    class Meta:
        verbose_name = _("Hse Traditional Accident damage")
        verbose_name_plural = _("Hse Traditional Accident damages")

class ImmediateAction(models.Model):
    accident = models.ForeignKey(HseTraditionalAccident, on_delete=models.PROTECT, related_name="immediate_actions")
    description = models.TextField(_("description"))

    class Meta:
        verbose_name = _("Immediate Action")
        verbose_name_plural = _("Immediate Actions")

class HseTraditionalAccidentManagerComment(models.Model):
    accident = models.ForeignKey(HseTraditionalAccident, on_delete=models.PROTECT, related_name="manager_comments")    
    comment = models.TextField(_("comment"))

    class Meta:
        verbose_name = _("ملاحظات مدير الإدارة")
        verbose_name_plural = _("ملاحظات مدير الإدارة")

class HseTraditionalNearMiss(LoggingModel):
    ACCIDENT_TYPE_SAFTY = 'safty'
    ACCIDENT_TYPE_ENVIRONMENTAL = 'enviromental'

    ACCIDENT_TYPE_CHOICES = {
        ACCIDENT_TYPE_SAFTY: _("Safty"),
        ACCIDENT_TYPE_ENVIRONMENTAL: _("Environmental"),
    }

    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED: _("confirmed"),
        STATE_APPROVED: _("approved"),
    }

    type = models.CharField(_("accident_type"), max_length=20, choices=ACCIDENT_TYPE_CHOICES.items())
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("source_state"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)
    what = models.TextField(_("what"))
    when = models.DateTimeField(_("when"))
    where = models.TextField(_("where"))

    class Meta:
        verbose_name = _("Hse Traditional Near Miss")
        verbose_name_plural = _("Hse Traditional Near Miss")

    def __str__(self):
        return f"{self.ACCIDENT_TYPE_CHOICES[self.type]}/{self.what}"

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []
        if 'hse_tra_state_employee' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))

        if 'hse_tra_manager' in user_groups:
            if self.state == self.STATE_CONFIRMED:
                states.append((self.STATE_APPROVED, self.STATE_CHOICES[self.STATE_APPROVED]))
                states.append((self.STATE_DRAFT, self.STATE_CHOICES[self.STATE_DRAFT]))

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
    
class HseTraditionalNearMissWho(models.Model):
    accident = models.ForeignKey(HseTraditionalNearMiss, on_delete=models.PROTECT, related_name="who_list")
    who = models.CharField(_("who"), max_length=150)

    class Meta:
        verbose_name = _("Hse Traditional Near Miss Who")
        verbose_name_plural = _("Hse Traditional Near Miss Whos")

class HseTraditionalNearMissWhy(models.Model):
    accident = models.ForeignKey(HseTraditionalNearMiss, on_delete=models.PROTECT, related_name="why_list")
    why = models.TextField(_("why"))

    class Meta:
        verbose_name = _("Hse Traditional Near Miss why")
        verbose_name_plural = _("Hse Traditional Near Miss whys")

class HseTraditionalCorrectiveAction(LoggingModel):
    STATE_DRAFT = 1
    STATE_CONFIRMED1 = 2
    STATE_CONFIRMED2 = 22
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED1: _("confirmed_emp"),
        STATE_CONFIRMED2: _("confirmed_mngr"),
        STATE_APPROVED: _("approved"),
    }

    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("source_state"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)
    source_accident = models.ForeignKey(HseTraditionalAccident, on_delete=models.PROTECT, null=True, blank=True, related_name="corrective_actions", verbose_name=_("source_accident"))
    source_near_miss = models.ForeignKey(HseTraditionalNearMiss, on_delete=models.PROTECT, null=True, blank=True, related_name="corrective_actions", verbose_name=_("source_near_miss"))
    # what = models.TextField(_("what"))
    when = models.DateField(_("when"))
    corrective_action = models.TextField(_("corrective_action"))

    class Meta:
        verbose_name = _("Hse Traditional Corrective Action")
        verbose_name_plural = _("Hse Traditional Corrective Action")

    def clean(self):
        if not self.source_accident and not self.source_near_miss:
            raise ValidationError(_(f"Either source_accident or source_near_miss must be provided."))

    def __str__(self):
        return f"{self.corrective_action}"

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []
        if 'hse_tra_state_employee' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_CONFIRMED1, self.STATE_CHOICES[self.STATE_CONFIRMED1]))

        if 'hse_tra_manager' in user_groups:
            if self.state == self.STATE_CONFIRMED1:
                states.append((self.STATE_CONFIRMED2, self.STATE_CHOICES[self.STATE_CONFIRMED2]))
                states.append((self.STATE_DRAFT, self.STATE_CHOICES[self.STATE_DRAFT]))

        if 'hse_tra_gm' in user_groups:
            if self.state == self.STATE_CONFIRMED2:
                states.append((self.STATE_APPROVED, self.STATE_CHOICES[self.STATE_APPROVED]))
                states.append((self.STATE_CONFIRMED1, self.STATE_CHOICES[self.STATE_CONFIRMED1]))

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

class HseTraditionalCorrectiveActionReccomendation(models.Model):
    action = models.OneToOneField(HseTraditionalCorrectiveAction, on_delete=models.PROTECT, related_name="corrective_action_reccomendation")
    description = models.TextField(_("description"))

    class Meta:
        verbose_name = _("Hse Traditional Corrective Action Reccomendation")
        verbose_name_plural = _("Hse Traditional Corrective Action Reccomendations")

class HseTraditionalCorrectiveActionFinalDecision(models.Model):
    action = models.OneToOneField(HseTraditionalCorrectiveAction, on_delete=models.PROTECT, related_name="corrective_action_final_decision")
    description = models.TextField(_("description"))

    class Meta:
        verbose_name = _("Hse Traditional Corrective Action Final Decision")
        verbose_name_plural = _("Hse Traditional Corrective Action Final Decisions")

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=HseTraditionalAccident)
def send_notifications(sender, instance, **kwargs):
    if instance.state:
        obj = HseTraditionalAccident.objects.get(pk=instance.pk)

        if obj.state != instance.state and instance.state == HseTraditionalAccident.STATE_CONFIRMED:
            instance.send_notifications()
