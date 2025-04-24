from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

from django.db import models

from workflow.model_utils import LoggingModel

from .performance_report import AppHSEPerformanceReport
from .incidents import IncidentInfo

class AppHSECorrectiveAction(LoggingModel):
    STATE_STATE_MNGR_SUBMIT = 1
    STATE_STATE_MNGR_CONFIRM = 2
    STATE_DEPARTMENT_MNGR_CONFIRM = 3
    STATE_GM_APPROVE = 4

    STATE_CHOICES = {
        STATE_STATE_MNGR_SUBMIT: _("تحرير مشرف الولاية"),
        STATE_STATE_MNGR_CONFIRM: _("تأكيد مشرف الولاية"),
        STATE_DEPARTMENT_MNGR_CONFIRM: _("تأكيد مدير الإدارة المختصة "),
        STATE_GM_APPROVE:_("إعتماد مدير الإدارة العامة"),
    }

    report = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT,null=True,blank=True,verbose_name=_("Application: HSE Performance Report"))    
    incident = models.ForeignKey(IncidentInfo, on_delete=models.PROTECT,null=True,blank=True,verbose_name=_("تقرير حادث Incident report"))    
    corrective_action = models.CharField(_("الإجراء التصحيحي"))
    from_dt = models.DateField(_("من"))
    to_dt = models.DateField(_("إلى"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_STATE_MNGR_SUBMIT)

    def __str__(self):
        try:
            return _("إجراء تصحيحي") +" ("+str(self.report.company)+")"
        except:
            return ''
        
    def get_absolute_url(self): 
        return reverse('hse_companies:app_hse_corrective_action_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("الإجراء التصحيحي HSE Corrective Action")
        verbose_name_plural = _("الإجراءات التصحيحية HSE Corrective Actions")

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []

        if 'hse_cmpny_state_mngr' in user_groups:
            if self.state == self.STATE_STATE_MNGR_SUBMIT:
                states.append((self.STATE_STATE_MNGR_CONFIRM, self.STATE_CHOICES[self.STATE_STATE_MNGR_CONFIRM]))

        if 'hse_cmpny_department_mngr' in user_groups:
            if self.state == self.STATE_STATE_MNGR_CONFIRM:
                states.append((self.STATE_DEPARTMENT_MNGR_CONFIRM, self.STATE_CHOICES[self.STATE_DEPARTMENT_MNGR_CONFIRM]))

        if 'hse_cmpny_gm' in user_groups:
            if self.state == self.STATE_DEPARTMENT_MNGR_CONFIRM:
                states.append((self.STATE_GM_APPROVE, self.STATE_CHOICES[self.STATE_GM_APPROVE]))
                states.append((self.STATE_STATE_MNGR_CONFIRM, 'إرجاع إلى مدير الإدارة المختصة '))

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

class AppHSECorrectiveActionFeedback(LoggingModel):
    STATE_SUBMITTED = 1
    STATE_AUDITOR_APPROVAL = 2
    STATE_STATE_MNGR_APPROVAL = 3

    STATE_CHOICES = {
        STATE_SUBMITTED: _("draft"),
        STATE_AUDITOR_APPROVAL: _("تأكيد المشرف"),
        STATE_STATE_MNGR_APPROVAL:_("إعتماد مشرف الولاية"),
    }

    corrective_action = models.ForeignKey(AppHSECorrectiveAction, on_delete=models.PROTECT,null=True,blank=True,verbose_name=_("الإجراء التصحيحي"))    
    percentage = models.IntegerField(_("نسبة التنفيذ"),validators=[MinValueValidator(0), MaxValueValidator(100)])
    company_comment = models.TextField(_("تعليق الشركة"))
    auditor_comment = models.TextField(_("تعليق المشرف الميداني"))
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_SUBMITTED)

    class Meta:
        verbose_name = _("إفادة عن اجراء تصحيحي")
        verbose_name_plural = _("إفادة عن إجراءات تصحيحية")
    def __str__(self):
        try:
            return _("إفادة عن اجراء تصحيحي") +" ("+str(self.corrective_action)+")"
        except:
            return ''
        
    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []

        if 'hse_cmpny_auditor' in user_groups:
            if self.state == self.STATE_SUBMITTED:
                states.append((self.STATE_AUDITOR_APPROVAL, self.STATE_CHOICES[self.STATE_AUDITOR_APPROVAL]))

        if 'hse_cmpny_state_mngr' in user_groups:
            if self.state == self.STATE_AUDITOR_APPROVAL:
                states.append((self.STATE_STATE_MNGR_APPROVAL, self.STATE_CHOICES[self.STATE_STATE_MNGR_APPROVAL]))

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
