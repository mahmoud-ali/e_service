from django.db import models
from django.utils.translation import gettext_lazy as _

from workflow.model_utils import WorkFlowModel

class DevelopmentRequestForm(WorkFlowModel):
    STATE_DRAFT = 1 
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3
    STATE_IT_MANAGER_RECOMMENDATION = 4
    STATE_PCI_MANAGER_APPROVAL = 5

    STATE_CHOICES = {
        STATE_DRAFT:_("IT State 1"), 
        STATE_CONFIRMED:_("IT State 2"), 
        STATE_APPROVED:_("IT State 3"),
        STATE_IT_MANAGER_RECOMMENDATION:_("IT State 4"),
        STATE_PCI_MANAGER_APPROVAL:_("IT State 5"),
    }

    date = models.DateField()
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    responsible = models.CharField(max_length=255)
    requirements_description = models.TextField()
    product_description = models.TextField()
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)

    def __str__(self):
        return self.name

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        next_states = []
        if 'department_manager' in user_groups and self.state == self.STATE_DRAFT:
            next_states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))
        if 'department_manager' in user_groups and self.state == self.STATE_CONFIRMED:
            next_states.append((self.STATE_APPROVED, self.STATE_CHOICES[self.STATE_APPROVED]))
        if 'department_manager' in user_groups and self.state == self.STATE_APPROVED:
            next_states.append((self.STATE_IT_MANAGER_RECOMMENDATION, self.STATE_CHOICES[self.STATE_IT_MANAGER_RECOMMENDATION]))
        if '' in user_groups and self.state == self.STATE_IT_MANAGER_RECOMMENDATION:
            next_states.append((self.STATE_PCI_MANAGER_APPROVAL, self.STATE_CHOICES[self.STATE_PCI_MANAGER_APPROVAL]))
        
        return next_states

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