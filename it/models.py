from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from workflow.model_utils import LoggingModel, WorkFlowModel


class DevelopmentRequestForm(WorkFlowModel):
    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3
    STATE_IT_MANAGER_STUDING_APPROVAL = 4
    STATE_IT_MANAGER_STUDING_REJECTION = 5
    STATE_IT_MANAGER_RECOMMENDATION = 6
    STATE_PQI_MANAGER_CHANGE_REQUEST = 7
    STATE_PQI_MANAGER_APPROVAL = 8
    STATE_FINAL_REJECTION = 9

    STATE_CHOICES = {
        STATE_DRAFT:_("IT_STATE_DRAFT"),
        STATE_CONFIRMED:_("IT_STATE_CONFIRMED"),
        STATE_APPROVED:_("IT_STATE_APPROVED"),
        STATE_IT_MANAGER_STUDING_APPROVAL:_("IT_STATE_IT_MANAGER_STUDING_APPROVAL"),
        STATE_IT_MANAGER_STUDING_REJECTION:_("IT_STATE_IT_MANAGER_STUDING_REJECTION"),
        STATE_IT_MANAGER_RECOMMENDATION:_("IT_STATE_IT_MANAGER_RECOMMENDATION"),
        STATE_PQI_MANAGER_CHANGE_REQUEST:_("IT_STATE_PQI_MANAGER_CHANGE_REQUEST"),
        STATE_PQI_MANAGER_APPROVAL:_("IT_STATE_PQI_MANAGER_APPROVAL"),
        STATE_FINAL_REJECTION:_("IT_STATE_FINAL_REJECTION"),
    }

    date = models.DateField(_("date"))
    name = models.CharField(_("name"), max_length=255)
    department = models.CharField(_("department"), max_length=255)
    responsible = models.CharField(_("responsible"), max_length=255)
    requirements_description = models.TextField(_("requirements_description"))
    product_description = models.TextField(_("product_description"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)

    class Meta:
        verbose_name = _("DevelopmentRequestForm") 
        verbose_name_plural = _("DevelopmentRequestForms") 

    def __str__(self):
        return self.name

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []
        if 'department_manager' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))

        if 'general_manager' in user_groups:
            if self.state == self.STATE_CONFIRMED:
                states.append((self.STATE_APPROVED, self.STATE_CHOICES[self.STATE_APPROVED]))
                states.append((self.STATE_FINAL_REJECTION, self.STATE_CHOICES[self.STATE_FINAL_REJECTION]))

        if 'it_manager' in user_groups:
            if self.state == self.STATE_APPROVED:
                states.append((self.STATE_IT_MANAGER_STUDING_APPROVAL, self.STATE_CHOICES[self.STATE_IT_MANAGER_STUDING_APPROVAL]))
                states.append((self.STATE_IT_MANAGER_STUDING_REJECTION, self.STATE_CHOICES[self.STATE_IT_MANAGER_STUDING_REJECTION]))
                
            if self.state == self.STATE_IT_MANAGER_STUDING_APPROVAL:
                states.append((self.STATE_IT_MANAGER_RECOMMENDATION, self.STATE_CHOICES[self.STATE_IT_MANAGER_RECOMMENDATION]))
                
            if self.state == self.STATE_IT_MANAGER_STUDING_REJECTION:
                states.append((self.STATE_IT_MANAGER_RECOMMENDATION, self.STATE_CHOICES[self.STATE_IT_MANAGER_RECOMMENDATION]))
                
        if 'pqi_manager' in user_groups:
            if self.state == self.STATE_IT_MANAGER_RECOMMENDATION:
                states.append((self.STATE_PQI_MANAGER_CHANGE_REQUEST, self.STATE_CHOICES[self.STATE_PQI_MANAGER_CHANGE_REQUEST]))
                states.append((self.STATE_PQI_MANAGER_APPROVAL, self.STATE_CHOICES[self.STATE_PQI_MANAGER_APPROVAL]))

            if self.state == self.STATE_PQI_MANAGER_CHANGE_REQUEST:
                states.append((self.STATE_IT_MANAGER_STUDING_APPROVAL, self.STATE_CHOICES[self.STATE_IT_MANAGER_STUDING_APPROVAL]))

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


class ItRecommendationForm(LoggingModel):
    form = models.OneToOneField(
        'DevelopmentRequestForm',
        on_delete=models.PROTECT,
        related_name='it_recommendation_form',
        verbose_name=_("DevelopmentRequestForm"),
    )

    date = models.DateField()
    priority = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="A small integer between 1 and 10"
    )
    recommendation = models.TextField(_("recommendation"))

    class Meta:
        verbose_name = _("ItRecommendationForm") 
        verbose_name_plural = _("ItRecommendationForms") 

class ItRejectionForm(LoggingModel):
    form = models.OneToOneField(
        'DevelopmentRequestForm',
        on_delete=models.PROTECT,
        related_name='it_rejection_form',
        verbose_name=_("DevelopmentRequestForm"),
    )

    reason = models.TextField(_("reason"))

    class Meta:
        verbose_name = _("ItRejectionForm")
        verbose_name_plural = _("ItRejectionForms")