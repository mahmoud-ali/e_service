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
    month = models.IntegerField(_("month"))
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT,verbose_name=_("state"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)

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

class WasteManagement(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="waste_managements")
    market_name = models.CharField(_("market_name"), max_length=255)
    item_description = models.TextField(_("item_description"))
    material_by_ton = models.FloatField(_("material_by_ton"))
    comment = models.TextField(_("comment"))

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

class ArrangementOfMarkets(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="arrangement_of_markets")
    market_name = models.CharField(_("market_name"), max_length=255)
    percent = models.IntegerField(_("percent"))
    notes = models.TextField(_("notes"))

class EnvironmentalRequirements(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="environmental_requirements")
    market_name = models.CharField(_("market_name"), max_length=255)
    percent = models.FloatField(_("percent"))

class QuickEmergencyTeam(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="quick_emergency_teams")
    issue = models.TextField(_("issue"))
    communication_factors = models.TextField(_("communication_factors"))
    notes = models.TextField(_("notes"))

class Achievement(models.Model):
    report = models.ForeignKey(HseTraditionalReport, on_delete=models.PROTECT, related_name="achievements")
    name = models.CharField(_("name"), max_length=255)
    brief = models.TextField(_("brief"))

class HseTraditionalAccident(LoggingModel):
    ACCIDENT_TYPE_SAFTY = 'safty'
    ACCIDENT_TYPE_ENVIRONMENTAL = 'enviromental'

    ACCIDENT_TYPE_CHOICES = [
        (ACCIDENT_TYPE_SAFTY, _("Safty")),
        (ACCIDENT_TYPE_ENVIRONMENTAL, _("Environmental")),
    ]

    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED: _("confirmed"),
        STATE_APPROVED: _("approved"),
    }

    type = models.CharField(_("accident_type"), max_length=20, choices=ACCIDENT_TYPE_CHOICES)
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("source_state"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)
    what = models.TextField(_("what"))
    when = models.DateTimeField(_("when"))
    where = models.TextField(_("where"))

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

class HseTraditionalAccidentWhy(models.Model):
    accident = models.ForeignKey(HseTraditionalAccident, on_delete=models.PROTECT, related_name="why_list")
    why = models.TextField(_("why"))

class HseTraditionalAccidentInjury(models.Model):
    accident = models.ForeignKey(HseTraditionalAccident, on_delete=models.PROTECT, related_name="injuries_list")
    injuries = models.TextField(_("injuries"))

class HseTraditionalAccidentDamage(models.Model):
    accident = models.ForeignKey(HseTraditionalAccident, on_delete=models.PROTECT, related_name="damages_list")
    damage = models.TextField(_("damage"))

class HseTraditionalNearMiss(LoggingModel):
    ACCIDENT_TYPE_SAFTY = 'safty'
    ACCIDENT_TYPE_ENVIRONMENTAL = 'enviromental'

    ACCIDENT_TYPE_CHOICES = [
        (ACCIDENT_TYPE_SAFTY, _("Safty")),
        (ACCIDENT_TYPE_ENVIRONMENTAL, _("Environmental")),
    ]

    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED: _("confirmed"),
        STATE_APPROVED: _("approved"),
    }

    type = models.CharField(_("accident_type"), max_length=20, choices=ACCIDENT_TYPE_CHOICES)
    source_state = models.ForeignKey(LkpState, on_delete=models.PROTECT, verbose_name=_("source_state"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)
    what = models.TextField(_("what"))
    when = models.DateTimeField(_("when"))
    where = models.TextField(_("where"))

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

class HseTraditionalNearMissWhy(models.Model):
    accident = models.ForeignKey(HseTraditionalNearMiss, on_delete=models.PROTECT, related_name="why_list")
    why = models.TextField(_("why"))

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
