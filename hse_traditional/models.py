from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from company_profile.models import LkpState

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

class HseTraditionalReport(LoggingModel):
    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED: _("confirmed"),
        STATE_APPROVED:_("IT_STATE_APPROVED"),
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
        if 'it_manager' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))

        if 'pqi_manager' in user_groups:
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
    what = models.TextField(_("what"))
    who = models.CharField(_("who"), max_length=255)
    hazard_identified = models.TextField(_("hazard_identified"))
    closed_date = models.DateField(_("closed_date"))

    class Meta:
        verbose_name = _("Environmental Inspection")
        verbose_name_plural = _("Environmental Inspections")

class WasteManagement(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="waste_managements")
    market_name = models.CharField(_("market_name"), max_length=255)
    item_description = models.TextField(_("item_description"))
    material_by_ton = models.FloatField(_("material_by_ton"))
    comment = models.TextField(_("comment"))

    class Meta:
        verbose_name = _("Waste Management")
        verbose_name_plural = _("Waste Managements")

class TrainingAwareness(models.Model):
    TRAINING_TYPE1 = 1
    TRAINING_TYPE2 = 2

    TRAINING_CHOICES = {
        TRAINING_TYPE1: _("Training"),
        TRAINING_TYPE2: _("Awareness"),
    }

    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="training_awarenesses")
    market_name = models.CharField(_("market_name"), max_length=255)
    traning_type = models.IntegerField(_("training_type"), choices=TRAINING_CHOICES.items())
    training_id = models.CharField(_("training_id"), max_length=255)
    subject = models.TextField(_("subject"))
    attendees = models.IntegerField(_("attendees"))
    notes = models.TextField(_("notes"))

    class Meta:
        verbose_name = _("Training Awareness")
        verbose_name_plural = _("Training Awareness")

class ArrangementOfMarkets(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="arrangement_of_markets")
    market_name = models.CharField(_("market_name"), max_length=255)
    percent = models.IntegerField(_("percent"))
    notes = models.TextField(_("notes"))

    class Meta:
        verbose_name = _("Arrangement Of Market")
        verbose_name_plural = _("Arrangement Of Markets")

class EnvironmentalRequirements(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="environmental_requirements")
    market_name = models.CharField(_("market_name"), max_length=255)
    percent = models.FloatField(_("percent"))

    class Meta:
        verbose_name = _("Environmental Requirement")
        verbose_name_plural = _("Environmental Requirements")

class QuickEmergencyTeam(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="quick_emergency_teams")
    issue = models.TextField(_("issue"))
    communication_factors = models.TextField(_("communication_factors"))
    notes = models.TextField(_("notes"))

    class Meta:
        verbose_name = _("Quick Emergency Team")
        verbose_name_plural = _("Quick Emergency Teams")

class Achievement(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="achievements")
    name = models.CharField(_("name"), max_length=255)
    brief = models.TextField(_("brief"))

    class Meta:
        verbose_name = _("Achievement")
        verbose_name_plural = _("Achievements")

class HseTraditionalAccident(LoggingModel):
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
        verbose_name = _("Hse Traditional Accident")
        verbose_name_plural = _("Hse Traditional Accidents")

    def __str__(self):
        return f"{self.ACCIDENT_TYPE_CHOICES[self.type]}/{self.what}"

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []
        if 'it_manager' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))

        if 'pqi_manager' in user_groups:
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
        if 'it_manager' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))

        if 'pqi_manager' in user_groups:
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
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED: _("confirmed"),
        STATE_APPROVED: _("approved"),
    }

    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("source_state"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)
    source_accident = models.ForeignKey(HseTraditionalAccident, on_delete=models.PROTECT, null=True, blank=True, related_name="corrective_actions", verbose_name=_("source_accident"))
    source_near_miss = models.ForeignKey(HseTraditionalNearMiss, on_delete=models.PROTECT, null=True, blank=True, related_name="corrective_actions", verbose_name=_("source_near_miss"))
    what = models.TextField(_("what"))
    where = models.TextField(_("where"))
    corrective_action = models.TextField(_("corrective_action"))

    class Meta:
        verbose_name = _("Hse Traditional Corrective Action")
        verbose_name_plural = _("Hse Traditional Corrective Action")

    def __str__(self):
        return f"{self.what}/{self.where}"

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []
        if 'it_manager' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))

        if 'pqi_manager' in user_groups:
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
