class WorkFlow:
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
