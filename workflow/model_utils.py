from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from auditlog.mixins import LogAccessMixin

class LoggingModel(LogAccessMixin,models.Model):
    """
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
    - get_next_states(user): Returns the next possible states based on user's permissions.
    - can_transition_to_next_state(user, state): Checks if a user can transition to a specific state.
    - transition_to_next_state(user, state): Transitions the workflow to a new state.

    These methods are required to define the behavior of a workflow system.
    """
        
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

    """
        updating ``created_at`` and ``updated_at`` fields for responsable user.
    """
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("created_by")) 
    
    updated_at = models.DateTimeField(_("updated_at"),auto_now=True,editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name="+",editable=False,verbose_name=_("updated_by"))

    class Meta:
        abstract = True