from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from company_profile.models import LkpForeignerProcedureType, TblCompanyProduction
from workflow.model_utils import WorkFlowModel

def company_applications_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/company_<id>/applications/<filename>
    return "company_{0}/applications/{1}".format(instance.company.id, filename)    

class TblCompanyEntajManager(models.Manager):
    def get_queryset(self):
       return super().get_queryset().filter(company_type__in=[TblCompanyProduction.COMPANY_TYPE_ENTAJ,TblCompanyProduction.COMPANY_TYPE_MOKHALFAT])

class TblCompanyEntaj(TblCompanyProduction):
    objects = TblCompanyEntajManager()
    default_manager = objects

    class Meta:
        proxy = True
        verbose_name = _("Production Company")
        verbose_name_plural = _("Production Companies")

class ForeignerRecord(WorkFlowModel):
    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED: _("تأكيد الطلب"),
        STATE_APPROVED: _("اعتماد الطلب"),
    }

    company = models.ForeignKey(TblCompanyEntaj, related_name="foreigner_company", on_delete=models.PROTECT,verbose_name=_("company"))    
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=150)
    department = models.CharField(max_length=150)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    employment_history = models.TextField()
    cv = models.FileField(upload_to=company_applications_path,null=True,blank=True)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)

    def __str__(self):
        return self.name

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []

        # if 'sswg_secretary' in user_groups:
        if self.state == self.STATE_DRAFT:
            states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))

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

class ForeignerPermission(WorkFlowModel):
    foreigner_record = models.ForeignKey(ForeignerRecord, on_delete=models.CASCADE, related_name='permissions')
    permission_type_choices = [
        ('passport', 'Passport'),
        ('visa', 'Visa'),
        ('residence', 'Residence'),
        ('work_permit', 'Work Permit'),
    ]

    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED: _("تأكيد الطلب"),
        STATE_APPROVED: _("اعتماد الطلب"),
    }

    permission_type = models.CharField(max_length=50, choices=permission_type_choices)
    type_id = models.CharField(max_length=50)
    validity_due_date = models.DateField()
    attachment = models.FileField(upload_to=company_applications_path)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)

    def __str__(self):
        return f"{self.foreigner_record.name} - {self.get_permission_type_display()}"

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []

        # if 'sswg_secretary' in user_groups:
        if self.state == self.STATE_DRAFT:
            states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))

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

class AppForeignerProcedure(WorkFlowModel):
    STATE_DRAFT = 1
    STATE_CONFIRMED = 2
    STATE_APPROVED = 3

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_CONFIRMED: _("تأكيد الطلب"),
        STATE_APPROVED: _("اعتماد الطلب"),
    }

    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"))    
    procedure_type = models.ForeignKey(LkpForeignerProcedureType, on_delete=models.PROTECT,verbose_name=_("procedure_type"))    
    procedure_from = models.DateField(_("procedure_from"), help_text="Ex: 2025-01-31")
    procedure_to = models.DateField(_("procedure_to"), help_text="Ex: 2025-01-31")
    procedure_cause = models.TextField(_("procedure_cause"),max_length=1000)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)


    def __str__(self):
        return _("Foreigner Procedure") +" ("+str(self.id)+")"
        
    def get_absolute_url(self): 
        return reverse('profile:app_foreigner_procedure_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Foreigner procedure")
        verbose_name_plural = _("Application: Foreigner procedure")

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []

        # if 'sswg_secretary' in user_groups:
        if self.state == self.STATE_DRAFT:
            states.append((self.STATE_CONFIRMED, self.STATE_CHOICES[self.STATE_CONFIRMED]))

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
