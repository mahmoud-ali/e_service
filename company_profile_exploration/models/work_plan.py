from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from company_profile.models import TblCompanyProduction,LkpMineral
from workflow.model_utils import LoggingModel, WorkFlowModel

class TblCompanyExplorationManager(models.Manager):
    def get_queryset(self):
       return super().get_queryset().filter(company_type=TblCompanyProduction.COMPANY_TYPE_EMTIAZ)

class TblCompanyExploration(TblCompanyProduction):
    objects = TblCompanyExplorationManager()
    default_manager = objects

    class Meta:
        proxy = True
        verbose_name = _("Production Company")
        verbose_name_plural = _("Production Companies")

class AppWorkPlan(WorkFlowModel):
    STATE_DRAFT = 1
    # STATE_APPROVED = 3

    STATE_GM_DECISION = 4
    STATE_REVIEW_CONTRACT= 5
    STATE_REVIEW_TECHNICAL= 6
    STATE_REVIEW_COMPANY= 7
    STATE_RELEASE_CERTIFICATE= 8

    STATE_CHOICES = {
        STATE_DRAFT: _("draft"),
        STATE_GM_DECISION: _("توجيه م.ا.ع"),
        STATE_REVIEW_CONTRACT: _("دراسة اولية"),
        STATE_REVIEW_TECHNICAL: _("دراسة فنية"),
        STATE_REVIEW_COMPANY: _("مراجعة الطلب بواسطة الشركة"),
        STATE_RELEASE_CERTIFICATE: _("تحرير شهادة القبول/الرفض"),
        # STATE_APPROVED:_("approved"),
    }

    company  = models.ForeignKey(TblCompanyExploration, related_name="work_plan", on_delete=models.PROTECT,verbose_name=_("company"))    
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_DRAFT)

    def __str__(self):
        return _("Work Plan") +" ("+str(self.company.name_ar+" - "+str(self.from_dt)+" / "+ str(self.to_dt))+")"
        
    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []
        if 'exploration_gm' in user_groups:
            if self.state == self.STATE_DRAFT:
                states.append((self.STATE_GM_DECISION, self.STATE_CHOICES[self.STATE_GM_DECISION]))

            if self.state == self.STATE_GM_DECISION:
                states.append((self.STATE_REVIEW_CONTRACT, self.STATE_CHOICES[self.STATE_REVIEW_CONTRACT]))
                states.append((self.STATE_REVIEW_TECHNICAL, self.STATE_CHOICES[self.STATE_REVIEW_TECHNICAL]))
                states.append((self.STATE_REVIEW_COMPANY, self.STATE_CHOICES[self.STATE_REVIEW_COMPANY]))
                states.append((self.STATE_RELEASE_CERTIFICATE, self.STATE_CHOICES[self.STATE_RELEASE_CERTIFICATE]))

            if self.state == self.STATE_REVIEW_CONTRACT:
                states.append((self.STATE_GM_DECISION, self.STATE_CHOICES[self.STATE_GM_DECISION]))

            if self.state == self.STATE_REVIEW_TECHNICAL:
                states.append((self.STATE_GM_DECISION, self.STATE_CHOICES[self.STATE_GM_DECISION]))

            if self.state == self.STATE_REVIEW_COMPANY:
                states.append((self.STATE_GM_DECISION, self.STATE_CHOICES[self.STATE_GM_DECISION]))

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
    
    @property
    def from_dt(self):
        try:
            obj = self.phase_set.order_by("from_dt")[0]
            return obj.from_dt        
        except:
            return ""

    @property
    def to_dt(self):
        try:
            obj = self.phase_set.order_by("-to_dt")[0]
            return obj.to_dt
        except:
            return ""
   
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: Work Plan")
        verbose_name_plural = _("Application: Work Plan")

class TargetCommodity(LoggingModel):
    """
    model TargetCommodity with relation one to many with AppWorkPlan has the following fields: mineral(company_profile.models.LkpMineral)
    """
    work_plan = models.ForeignKey(AppWorkPlan, on_delete=models.PROTECT, verbose_name=_("work_plan"))
    mineral = models.ForeignKey(LkpMineral, on_delete=models.PROTECT, verbose_name=_("mineral"))

    class Meta:
        verbose_name = _("Target Commodity")
        verbose_name_plural = _("Target Commodities")
        unique_together = ('work_plan', 'mineral')
        

class Coordinate(LoggingModel):
    """
    model Coordinate with relation one to many with AppWorkPlan has the following fields: Longitude/Easting, Latitude/Northing
    """
    work_plan = models.ForeignKey(AppWorkPlan, on_delete=models.PROTECT, verbose_name=_("work_plan"))
    longitude = models.FloatField(_("Longitude/Easting"))
    latitude = models.FloatField(_("Latitude/Northing"))

    class Meta:
        verbose_name = _("Coordinate")
        verbose_name_plural = _("Coordinates")


class Brief(LoggingModel):
    """
    model Brief with relation one to one with AppWorkPlan has the following fields: "Brief about what has been done"
    """
    work_plan = models.OneToOneField(AppWorkPlan, on_delete=models.PROTECT, verbose_name=_("work_plan"))
    brief = models.TextField(_("Brief about what has been done"))

    class Meta:
        verbose_name = _("Brief")
        verbose_name_plural = _("Briefs")

class LkpPhase(LoggingModel):
    """
    model LkpPhase with relation one to many with Phase has the following fields: name
    """
    name = models.CharField(_("name"), max_length=100)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Phase")
        verbose_name_plural = _("Phases")

class Phase(LoggingModel):
    """
    model Phase with relation one to many with AppWorkPlan has the following fields: phase(foreign from LkpPhase), from_dt, to_dt
    """
    work_plan = models.ForeignKey(AppWorkPlan, on_delete=models.PROTECT, verbose_name=_("work_plan"))
    phase = models.ForeignKey(LkpPhase, on_delete=models.PROTECT, verbose_name=_("phase"))
    from_dt = models.DateField(_("from_dt"))
    to_dt = models.DateField(_("to_dt"))

    class Meta:
        verbose_name = _("Phase")
        verbose_name_plural = _("Phases")

class StaffInformation(LoggingModel):
    work_plan = models.ForeignKey(AppWorkPlan, on_delete=models.PROTECT, verbose_name=_("work_plan"))
    position = models.CharField(_("Position"), max_length=100)
    count = models.IntegerField(_("count"))
    salaries_month = models.FloatField(_("Salaries_month"))
    salaries_year = models.FloatField(_("Salaries_year"))
    remarks = models.TextField(_("Remarks"), blank=True, null=True)

    class Meta:
        verbose_name = _("Staff Information")
        verbose_name_plural = _("Staff Informations")

class LogisticsAdministration(LoggingModel):
    work_plan = models.ForeignKey(AppWorkPlan, on_delete=models.PROTECT, verbose_name=_("work_plan"))
    activity_item = models.CharField(_("Activity/Item"), max_length=100)
    count = models.IntegerField(_("count"))
    unit_cost = models.FloatField(_("Unit cost"))
    total_cost = models.FloatField(_("Total Cost"))

    class Meta:
        verbose_name = _("Logistics Administration")
        verbose_name_plural = _("Logistics Administrations")

class Equipment(LoggingModel):
    work_plan = models.ForeignKey(AppWorkPlan, on_delete=models.PROTECT, verbose_name=_("work_plan"))
    equipment_machine = models.CharField(_("Equipment/Machine"), max_length=100)
    item = models.CharField(_("Item"), max_length=100)
    unit_cost = models.FloatField(_("Unit cost"))
    total_cost = models.FloatField(_("Total cost"))
    remarks = models.TextField(_("Remarks"), blank=True, null=True)

    class Meta:
        verbose_name = _("Equipment")
        verbose_name_plural = _("Equipments")

class SurfaceExplorationActivitie(LoggingModel):
    work_plan = models.ForeignKey(AppWorkPlan, on_delete=models.PROTECT, verbose_name=_("work_plan"))
    activity = models.CharField(_("Activity"), max_length=100)
    unit_cost = models.FloatField(_("Unit cost"))
    total_cost = models.FloatField(_("Total cost"))
    remarks = models.TextField(_("Remarks"), blank=True, null=True)

    class Meta:
        verbose_name = _("Surface Exploration Activitie")
        verbose_name_plural = _("Surface Exploration Activities")

class SubsurfaceExplorationActivitie(LoggingModel):
    work_plan = models.ForeignKey(AppWorkPlan, on_delete=models.PROTECT, verbose_name=_("work_plan"))
    activity = models.CharField(_("Activity"), max_length=100)
    total_depth_length = models.FloatField(_("Total (depth, Length)/m"))
    cost_per_meter = models.FloatField(_("Cost/m"))
    total_cost = models.FloatField(_("Total cost"))
    remarks = models.TextField(_("Remarks"), blank=True, null=True)

    class Meta:
        verbose_name = _("Subsurface Exploration Activitie")
        verbose_name_plural = _("Subsurface Exploration Activities")

class SamplePreparation(LoggingModel):
    work_plan = models.ForeignKey(AppWorkPlan, on_delete=models.PROTECT, verbose_name=_("work_plan"))
    activity = models.CharField(_("Activity"), max_length=100)
    total = models.FloatField(_("Total"))
    unit_cost = models.FloatField(_("Unit cost"))
    total_cost = models.FloatField(_("Total cost"))
    remarks = models.TextField(_("Remarks"), blank=True, null=True)

    class Meta:
        verbose_name = _("Sample Preparation")
        verbose_name_plural = _("Sample Preparations")

#model Others with relation one to many with AppWorkPlan has the following fields: Activity/Item, Total, Unit cost, Total cost
class Other(LoggingModel):
    work_plan = models.ForeignKey(AppWorkPlan, on_delete=models.PROTECT, verbose_name=_("work_plan"))
    activity_item = models.CharField(_("Activity/Item"), max_length=100)
    total = models.FloatField(_("Total"))
    unit_cost = models.FloatField(_("Unit cost"))
    total_cost = models.FloatField(_("Total cost"))

    class Meta:
        verbose_name = _("Other")
        verbose_name_plural = _("Others")
