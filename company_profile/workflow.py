from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.contrib.auth import get_user_model

from django_fsm import can_proceed,get_available_FIELD_transitions

SUBMITTED = "submitted"
ACCEPTED = "accepted"
APPROVED = "approved"
REJECTED = "rejected"

STATE_CHOICES = { SUBMITTED: _("Submitted state"),
                                        ACCEPTED: _("Accepted state"),
                                        APPROVED: _("Approved state"),
                                        REJECTED: _("Rejected state"),}
                                        
def get_state_choices(state):
    if not state:
        return { SUBMITTED: "Submitted"}

    if state == SUBMITTED:
        return { SUBMITTED: "Submitted", ACCEPTED: "Accepted"}
        
    if state == ACCEPTED:
        return { ACCEPTED: "Accepted",APPROVED: "Approved", REJECTED: "Rejected"}
        
    if state == APPROVED:
        return { APPROVED: "Approved"}
        
    if state == REJECTED:
        return { REJECTED: "Rejected"}
                                        
                                        
def send_transition_email(state,email,url,lang):
    subject = ""
    message = ""

    if state == SUBMITTED:
        subject = _("New application submitted")
        message = render_to_string('company_profile/email/submitted_email_{0}.html'.format(lang),{'url':url}) 
  
    if state == ACCEPTED:
        subject = _("Application accepted")
        message = render_to_string('company_profile/email/accepted_email_{0}.html'.format(lang),{'url':url}) 
            
    if state == APPROVED:
        subject = _("Application approved")
        message = render_to_string('company_profile/email/approved_email_{0}.html'.format(lang),{'url':url}) 
        
    if state == REJECTED:
        subject = _("Application rejected")
        message = render_to_string('company_profile/email/rejected_email_{0}.html'.format(lang),{'url':url}) 
        
    send_mail(
        subject,
        message,
        None,
        [email],
        fail_silently=False,
    )        
        
def get_sumitted_responsible(app):
    User = get_user_model()
    if app == 'pro_company':
        user = User.objects.filter(groups__name="pro_company_application_accept").first()
        return user

def can_do_transition(instance, user):
    ###logic here!
    return True
      
class WorkflowFormMixin:

    def clean(self):
        cleaned_data = super().clean()
        new_state = cleaned_data.get("state")        
        
        self.instance.notify = False        
        
        if not self.instance.id:
            return
                                    
        if self.instance.state == new_state:
            return

        if new_state ==SUBMITTED:                
            if self.instance.pk:        
                self.add_error('state', _('Wrong transition path. You can reach submitted state only when creating a new application.'))      
        elif new_state ==ACCEPTED:
            if not can_proceed(self.instance.accept):
                self.add_error('state', _('Wrong transition path. You can reach accepted state only from submitted state.'))                                
            # elif not has_transition_perm(self.instance.accept, self.request.user):
                # raise PermissionDenied                
        elif new_state ==APPROVED:
            if not can_proceed(self.instance.approve):
                self.add_error('state', _('Wrong transition path. You can reach approved state only from accepted state.'))        
            # elif not has_transition_perm(self.instance.approve, self.request.user):
                # raise PermissionDenied                
        elif new_state ==REJECTED:
            if not can_proceed(self.instance.reject):
                self.add_error('state', _('Wrong transition path. You can reach rejected state only from accepted state.'))        
            # elif not has_transition_perm(self.instance.reject, self.request.user):
                # raise PermissionDenied                
        else:
            self.add_error('state', _('Wrong transition path.'))
            
        self.instance.notify = True        
