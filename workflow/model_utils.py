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

class WorkFlowModel(LoggingModel):
    """
    Abstract base class for defining workflow logic.

    Subclasses should implement the following methods:
    - get_states(): Returns a list or tuple of available states.
    - get_default_state(): Returns the default initial state.
    - set_states(): Sets the available states for the object.
    - get_next_states(user): Returns the next possible states based on user's permissions.
    - can_transition_to_next_state(user, state): Checks if a user can transition to a specific state.
    - transition_to_next_state(user, state): Transitions the workflow to a new state.

    These methods are required to define the behavior of a workflow system.
    """
    def get_states(self):
        """
        Gets all available states in the workflow.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError
    
    def get_default_state(self):
        """
        Gets the default (initial) state of the workflow.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError
    
    def set_states(self):
        """
        Sets or configures the available states for a specific instance.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError
    
    def get_next_states(self,user):
        """
        Gets the next possible states based on the given user's permissions.

        Args:
            user: The user object for whom to determine the next states.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError
    
    def can_transition_to_next_state(self,user,state):
        """
        Checks if the given user can transition the workflow to the specified state.

        Args:
            user: The user object attempting to make the transition.
            state: The state to transition to.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError
    
    def transition_to_next_state(self,user,state):
        """
        Transitions the workflow to the given state, based on user's permissions.

        Args:
            user: The user object making the transition.
            state: The state to transition to.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError

    class Meta:
        abstract = True