import sys
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.core.mail import EmailMessage
import threading

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

from django_fsm import can_proceed,get_available_FIELD_transitions

SUBMITTED = "submitted"
ACCEPTED = "accepted"
REVIEW_ACCEPTANCE = "review_accept"
APPROVED = "approved"
REJECTED = "rejected"

STATE_CHOICES = { 
    SUBMITTED: _("Submitted state"),
    ACCEPTED: _("Accepted state"),
    REVIEW_ACCEPTANCE: _("Review acceptance state"),
    APPROVED: _("Approved state"),
    REJECTED: _("Rejected state"),
}

def send_async_email(subject, message, from_email, recipient_list):
    email = EmailMessage(subject, message, from_email, recipient_list)
    threading.Thread(target=email.send).start()

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
    logo_url = "https://"+Site.objects.get_current().domain+"/app/static/company_profile/img/smrc_logo.png"
    
    if state == SUBMITTED:
        subject = _("New application submitted")
        message = render_to_string('company_profile/email/submitted_email_{0}.html'.format(lang),{'url':url,'logo':logo_url}) 
  
    if state == ACCEPTED:
        subject = _("Application accepted")
        message = render_to_string('company_profile/email/accepted_email_{0}.html'.format(lang),{'url':url,'logo':logo_url}) 
            
    if state == APPROVED:
        subject = _("Application approved")
        message = render_to_string('company_profile/email/approved_email_{0}.html'.format(lang),{'url':url,'logo':logo_url}) 
        
    if state == REJECTED:
        subject = _("Application rejected")
        message = render_to_string('company_profile/email/rejected_email_{0}.html'.format(lang),{'url':url,'logo':logo_url}) 
        
    try:
        # send_mail(
        send_async_email(
            subject,
            # strip_tags(message),
            message,
            None,
            [email],
            # html_message=message,
            # fail_silently=False,
        )
    except:
        print("Error sending email",sys.stderr)
        
def get_sumitted_responsible(app,company_type):
    User = get_user_model()
    if app == 'pro_company':
        qs = User.objects.filter(
            groups__name="company_type_"+company_type,
        ).filter(
            groups__name="pro_company_application_accept",
        )

        return qs.last()

def can_do_transition(instance, user):
    ###logic here!
    return True
      
class WorkflowFormMixin:
    pass

    # def clean(self):
    #     cleaned_data = super().clean()
    #     new_state = cleaned_data.get("state")        
        
    #     self.instance.notify = False        
        
    #     if not self.instance.id:
    #         return
                                    
    #     if self.instance.state == new_state:
    #         return

    #     if new_state ==SUBMITTED:                
    #         if self.instance.pk:        
    #             self.add_error('state', _('Wrong transition path. You can reach submitted state only when creating a new application.'))      
    #     elif new_state ==ACCEPTED:
    #         if not can_proceed(self.instance.accept):
    #             self.add_error('state', _('Wrong transition path. You can reach accepted state only from submitted state.'))                                
    #         # elif not has_transition_perm(self.instance.accept, self.request.user):
    #             # raise PermissionDenied                
    #     elif new_state ==APPROVED:
    #         if not can_proceed(self.instance.approve):
    #             self.add_error('state', _('Wrong transition path. You can reach approved state only from accepted state.'))        
    #         # elif not has_transition_perm(self.instance.approve, self.request.user):
    #             # raise PermissionDenied                
    #     elif new_state ==REJECTED:
    #         if not can_proceed(self.instance.reject):
    #             self.add_error('state', _('Wrong transition path. You can reach rejected state only from accepted state.'))        
    #         # elif not has_transition_perm(self.instance.reject, self.request.user):
    #             # raise PermissionDenied                
    #     else:
    #         self.add_error('state', _('Wrong transition path.'))
            
    #     self.instance.notify = True        
