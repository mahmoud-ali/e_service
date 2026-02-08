from datetime import date

from django.conf import settings
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

from django.db import models

from workflow.model_utils import LoggingModel

from company_profile.models import MONTH_CHOICES, TblCompanyProduction, TblCompanyProductionLicense

def get_previous_month(report_date):
    year, month = report_date.year, report_date.month

    if month == 1:  # If current month is January, go to December of previous year
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    return prev_year, prev_month

def company_applications_path(instance, filename):
    return "company_{0}/hse/{1}".format(instance.company.id, filename)    

class AppHSEPerformanceReport(LoggingModel):
    STATE_SUBMITTED = 1
    STATE_AUDITOR_APPROVAL = 2
    STATE_STATE_MNGR_APPROVAL = 3

    STATE_CHOICES = {
        STATE_SUBMITTED: _("draft"),
        STATE_AUDITOR_APPROVAL: _("تأكيد المشرف"),
        STATE_STATE_MNGR_APPROVAL:_("إعتماد مشرف الولاية"),
    }
   
    company  = models.ForeignKey(TblCompanyProduction, on_delete=models.PROTECT,verbose_name=_("company"),related_name="hse_performance_report") 
    license  = models.ForeignKey(TblCompanyProductionLicense, on_delete=models.PROTECT,verbose_name=_("license"),null=True,blank=True)       
    year = models.PositiveIntegerField(_("year"), validators=[MinValueValidator(limit_value=2015),MaxValueValidator(limit_value=2100)])
    month = models.PositiveIntegerField(verbose_name=_("month"), choices=MONTH_CHOICES)
    album = models.FileField(_('album'),upload_to=company_applications_path,blank=True,null=True)
    note = models.TextField(verbose_name=_("comment"),blank=True,null=True)
    state = models.IntegerField(_("record_state"), choices=STATE_CHOICES.items(), default=STATE_SUBMITTED)

    def __str__(self):
        return _("HSE Performance Report") +" ("+str(self.company)+")"
        
    def get_absolute_url(self): 
        return reverse('hse_companies:app_hse_performance_show',args=[str(self.id)])                
    
    class Meta:
        ordering = ["-id"]
        verbose_name = _("Application: HSE Performance Report")
        verbose_name_plural = _("Application: HSE Performance Report")
        constraints = [
            models.UniqueConstraint(fields=['year', 'month','company','license'], name='unique_report_per_month')
        ]

    def clean(self):
        report_count = AppHSEPerformanceReport.objects.filter(year=self.year,month=self.month,license=self.license,).count()
        # print("count: ",report_count,"-",self.pk)
        if (not self.pk and report_count >0) or (self.pk and report_count >1):
            raise ValidationError({
                'month':_("يوجد تقرير لنفس السنة، الشهر "),
            })
        
        
        return super().clean()
    
    def save(self, *args,**kwargs):
        report_dt = date.today()
        if self.created_at:
            report_dt = self.created_at

        self.year, self.month = get_previous_month(report_dt)
        return super().save(args,kwargs)

    def get_next_states(self, user):
        """
        Determine the next possible states based on the current state and user's role.
        """
        # user = self.updated_by
        user_groups = list(user.groups.values_list('name', flat=True))

        states = []

        if 'production_control_auditor' in user_groups:
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

class AppHSEPerformanceReportManPower(models.Model):
    MAN_POWER_TOTAL = 1
    MAN_POWER_WORK_HOURS = 2

    MAN_POWER_CHOICES = {
        MAN_POWER_TOTAL: _("man_power_total"),
        MAN_POWER_WORK_HOURS: _("man_power_work_hours"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_man_power"), choices=MAN_POWER_CHOICES)
    no_gov = models.PositiveIntegerField(_("no_gov"))
    no_staff = models.PositiveIntegerField(_("no_staff"))
    no_contractor = models.PositiveIntegerField(_("no_contractor"))

    class Meta:
        verbose_name = _("HSE Man power")
        verbose_name_plural = _("HSE Man power")

class AppHSEPerformanceReportFireFighting(models.Model):
    FIRE_FIGHTING_TYPE1 = 1
    FIRE_FIGHTING_TYPE2 = 2
    FIRE_FIGHTING_TYPE3 = 3
    FIRE_FIGHTING_TYPE4 = 4
    FIRE_FIGHTING_TYPE5 = 5

    FIRE_FIGHTING_CHOICES = {
        FIRE_FIGHTING_TYPE1: _("fire_fighting_1"),
        FIRE_FIGHTING_TYPE2: _("fire_fighting_2"),
        FIRE_FIGHTING_TYPE3: _("fire_fighting_3"),
        FIRE_FIGHTING_TYPE4: _("fire_fighting_4"),
        FIRE_FIGHTING_TYPE5: _("fire_fighting_5"),
    }

    SITUATION_TYPE1 = 1
    SITUATION_TYPE2 = 2

    SITUATION_CHOICES = {
        SITUATION_TYPE1: _("situation_ok"),
        SITUATION_TYPE2: _("situation_bad"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_fire_fighting"), choices=FIRE_FIGHTING_CHOICES)
    size = models.PositiveIntegerField(_("size"))
    count = models.PositiveIntegerField(_("count"))
    exam_dt = models.DateField(_("exam_dt"), help_text="Ex: 2025-01-31")
    situation = models.PositiveIntegerField(_("situation"),choices=SITUATION_CHOICES)

    class Meta:
        verbose_name = _("HSE fire fighting")
        verbose_name_plural = _("HSE fire fighting")

class AppHSEPerformanceReportWorkEnvironment(models.Model):
    WORK_ENVIRONMENT_FACTOR1 = 1
    WORK_ENVIRONMENT_FACTOR2 = 2
    WORK_ENVIRONMENT_FACTOR3 = 3
    WORK_ENVIRONMENT_FACTOR4 = 4
    WORK_ENVIRONMENT_FACTOR5 = 5
    WORK_ENVIRONMENT_FACTOR6 = 6
    WORK_ENVIRONMENT_FACTOR7 = 7
    WORK_ENVIRONMENT_FACTOR8 = 8

    WORK_ENVIRONMENT_CHOICES = {
        WORK_ENVIRONMENT_FACTOR1: _("work_environment_factor1"),
        WORK_ENVIRONMENT_FACTOR2: _("work_environment_factor2"),
        WORK_ENVIRONMENT_FACTOR3: _("work_environment_factor3"),
        WORK_ENVIRONMENT_FACTOR4: _("work_environment_factor4"),
        WORK_ENVIRONMENT_FACTOR5: _("work_environment_factor5"),
        WORK_ENVIRONMENT_FACTOR6: _("work_environment_factor6"),
        WORK_ENVIRONMENT_FACTOR7: _("work_environment_factor7"),
        WORK_ENVIRONMENT_FACTOR8: _("work_environment_factor8"),
    }

    RANKING_TYPE1 = 1
    RANKING_TYPE2 = 2
    RANKING_TYPE3 = 3
    RANKING_TYPE4 = 4

    RANKING_CHOICES = {
        RANKING_TYPE1: _("ranking_excellent"),
        RANKING_TYPE2: _("ranking_very_good"),
        RANKING_TYPE3: _("ranking_good"),
        RANKING_TYPE4: _("ranking_bad"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_work_environment"), choices=WORK_ENVIRONMENT_CHOICES)
    offices = models.PositiveIntegerField(_("offices"),choices=RANKING_CHOICES,default=RANKING_TYPE4)
    camp = models.PositiveIntegerField(_("camp"),choices=RANKING_CHOICES,default=RANKING_TYPE4)
    kitchen_dining = models.PositiveIntegerField(_("kitchen_dining"),choices=RANKING_CHOICES,default=RANKING_TYPE4)
    factory = models.PositiveIntegerField(_("factory"),choices=RANKING_CHOICES,default=RANKING_TYPE4)
    stores = models.PositiveIntegerField(_("Stores"),choices=RANKING_CHOICES,default=RANKING_TYPE4)
    lab = models.PositiveIntegerField(_("lab"),choices=RANKING_CHOICES,default=RANKING_TYPE4)
    mines = models.PositiveIntegerField(_("mines"),choices=RANKING_CHOICES,null=True,blank=True)

    class Meta:
        verbose_name = _("HSE work environment")
        verbose_name_plural = _("HSE work environment")

class AppHSEPerformanceReportProactiveIndicators(models.Model):
    PROACTIVE_INDICATORS_TYPE1 = 1
    PROACTIVE_INDICATORS_TYPE2 = 2
    PROACTIVE_INDICATORS_TYPE3 = 3
    PROACTIVE_INDICATORS_TYPE4 = 4

    PROACTIVE_INDICATORS_CHOICES = {
        PROACTIVE_INDICATORS_TYPE1: _("proactive_indicators_type1"),
        PROACTIVE_INDICATORS_TYPE2: _("proactive_indicators_type2"),
        PROACTIVE_INDICATORS_TYPE3: _("proactive_indicators_type3"),
        PROACTIVE_INDICATORS_TYPE4: _("proactive_indicators_type4"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_proactive_indicators"), choices=PROACTIVE_INDICATORS_CHOICES)
    # no_gov = models.PositiveIntegerField(_("no_gov"))
    no_staff = models.PositiveIntegerField(_("no_staff"))
    no_contractor = models.PositiveIntegerField(_("no_contractor"))
    action = models.CharField(_("action"), max_length=100)
    description = models.CharField(_("description"), max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _("HSE proactive indicators")
        verbose_name_plural = _("HSE proactive indicators")

class AppHSEPerformanceReportActivities(models.Model):
    ACTIVITIES_TYPE1 = 1
    ACTIVITIES_TYPE2 = 2
    ACTIVITIES_TYPE3 = 3
    ACTIVITIES_TYPE4 = 4
    ACTIVITIES_TYPE5 = 5
    ACTIVITIES_TYPE6 = 6
    ACTIVITIES_TYPE7 = 7
    ACTIVITIES_TYPE8 = 8
    ACTIVITIES_TYPE9 = 9
    ACTIVITIES_TYPE10 = 10
    ACTIVITIES_TYPE11 = 11

    ACTIVITIES_CHOICES = {
        ACTIVITIES_TYPE1: _("ACTIVITIES_type1"),
        ACTIVITIES_TYPE2: _("ACTIVITIES_type2"),
        ACTIVITIES_TYPE3: _("ACTIVITIES_type3"),
        ACTIVITIES_TYPE4: _("ACTIVITIES_type4"),
        ACTIVITIES_TYPE5: _("ACTIVITIES_type5"),
        ACTIVITIES_TYPE6: _("ACTIVITIES_type6"),
        ACTIVITIES_TYPE7: _("ACTIVITIES_type7"),
        ACTIVITIES_TYPE8: _("ACTIVITIES_type8"),
        ACTIVITIES_TYPE9: _("ACTIVITIES_type9"),
        ACTIVITIES_TYPE10: _("ACTIVITIES_type10"),
        ACTIVITIES_TYPE11: _("ACTIVITIES_type11"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_activities"), choices=ACTIVITIES_CHOICES)
    no_staff = models.PositiveIntegerField(_("no_staff"))
    no_contractor = models.PositiveIntegerField(_("no_contractor"))

    class Meta:
        verbose_name = _("HSE activities")
        verbose_name_plural = _("HSE activities")

class AppHSEPerformanceReportChemicalUsed(models.Model):
    CHEMICAL_USED1 = 1
    CHEMICAL_USED2 = 2
    CHEMICAL_USED3 = 3
    CHEMICAL_USED4 = 4
    CHEMICAL_USED5 = 5

    CHEMICAL_USED_CHOICES = {
        CHEMICAL_USED1: _("CHEMICAL_USED1"),
        CHEMICAL_USED2: _("CHEMICAL_USED2"),
        CHEMICAL_USED3: _("CHEMICAL_USED3"),
        CHEMICAL_USED4: _("CHEMICAL_USED4"),
        CHEMICAL_USED5: _("CHEMICAL_USED5"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_chemical_used"), choices=CHEMICAL_USED_CHOICES)
    qty_used = models.PositiveIntegerField(_("qty_used"))
    qty_in_store = models.PositiveIntegerField(_("qty_in_store"))
    expire_dt = models.DateField(_("expire_dt"), default='',null=True,blank=True, help_text="Ex: 2025-01-31")

    class Meta:
        verbose_name = _("HSE CHEMICAL USED")
        verbose_name_plural = _("HSE CHEMICAL USED")

class AppHSEPerformanceReportOtherChemicalUsed(models.Model):
    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    name = models.CharField(_("hse_chemical_used"), max_length=100,default=_("not exists"))
    qty_used = models.PositiveIntegerField(_("qty_used"),null=True, blank=True)
    qty_in_store = models.PositiveIntegerField(_("qty_in_store"),null=True, blank=True)
    expire_dt = models.DateField(_("expire_dt"), help_text="Ex: 2025-01-31",null=True, blank=True)

    class Meta:
        verbose_name = _("HSE OTHER CHEMICAL USED")
        verbose_name_plural = _("HSE OTHER CHEMICAL USED")

class AppHSEPerformanceReportCyanideTable(models.Model):
    STORAGE_METHOD1 = 1
    STORAGE_METHOD2 = 2

    STORAGE_METHOD_CHOICES = {
        STORAGE_METHOD1: _("STORAGE_METHOD1"),
        STORAGE_METHOD2: _("STORAGE_METHOD2"),
    }

    HANDLING_METHOD1 = 1
    HANDLING_METHOD2 = 2
    HANDLING_METHOD3 = 3

    HANDLING_METHOD_CHOICES = {
        HANDLING_METHOD1: _("HANDLING_METHOD1"),
        HANDLING_METHOD2: _("HANDLING_METHOD2"),
        HANDLING_METHOD3: _("HANDLING_METHOD3"),
    }

    YES = 1
    NO = 2

    YES_NO_CHOICES = {
        YES: _("YES"),
        NO: _("NO"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    storage_method = models.PositiveIntegerField(_("storage_method"), choices=STORAGE_METHOD_CHOICES)
    handling_method = models.PositiveIntegerField(_("handling_method"), choices=HANDLING_METHOD_CHOICES)
    hcn_detector = models.PositiveIntegerField(_("hcn_detector"), choices=YES_NO_CHOICES)
    
    class Meta:
        verbose_name = _("HSE CYANIDE TABLE")
        verbose_name_plural = _("HSE CYANIDE TABLE")

class AppHSEPerformanceReportCyanideCNStorageSpecification(models.Model):
    SPECIFICATION1 = 1
    SPECIFICATION2 = 2
    SPECIFICATION3 = 3
    SPECIFICATION4 = 4

    SPECIFICATION_CHOICES = {
        SPECIFICATION1: _("SPECIFICATION1"),
        SPECIFICATION2: _("SPECIFICATION2"),
        SPECIFICATION3: _("SPECIFICATION3"),
        SPECIFICATION4: _("SPECIFICATION4"),
    }

    YES = 1
    NO = 2

    YES_NO_CHOICES = {
        YES: _("YES"),
        NO: _("NO"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("Specification"), choices=SPECIFICATION_CHOICES)
    choice = models.PositiveIntegerField(_("is_exists"), choices=YES_NO_CHOICES)
    
    class Meta:
        verbose_name = _("HSE CYANIDE CN Storage Specification")
        verbose_name_plural = _("HSE CYANIDE CN Storage Specification")

class AppHSEPerformanceReportWaterUsed(models.Model):
    WATER_USED1 = 1
    WATER_USED2 = 2
    WATER_USED3 = 3
    WATER_USED4 = 4

    WATER_USED_CHOICES = {
        WATER_USED1: _("WATER_USED1"),
        WATER_USED2: _("WATER_USED2"),
        WATER_USED3: _("WATER_USED3"),
        WATER_USED4: _("WATER_USED4"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_water_used"), choices=WATER_USED_CHOICES)
    qty_used = models.FloatField(_("qty_used"))
    source_of_water = models.CharField(_("source_of_water"))
    storage_method = models.CharField(_("storage_method"))

    class Meta:
        verbose_name = _("HSE WATER USED")
        verbose_name_plural = _("HSE WATER USED")

class AppHSEPerformanceReportOilUsed(models.Model):
    OIL_USED1 = 1
    OIL_USED2 = 2
    OIL_USED3 = 3

    OIL_USED_CHOICES = {
        OIL_USED1: _("OIL_USED1"),
        OIL_USED2: _("OIL_USED2"),
        OIL_USED3: _("OIL_USED3"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_oil_used"), choices=OIL_USED_CHOICES)
    qty_used = models.FloatField(_("qty_used"))
    disposal_method = models.CharField(_("disposal_method"))
    storage_method = models.CharField(_("storage_method"))

    class Meta:
        verbose_name = _("HSE OIL USED")
        verbose_name_plural = _("HSE OIL USED")

class AppHSEPerformanceReportWasteDisposal(models.Model):
    WASTE_DISPOSAL1 = 1
    WASTE_DISPOSAL2 = 2
    WASTE_DISPOSAL3 = 3
    WASTE_DISPOSAL4 = 4
    WASTE_DISPOSAL5 = 5
    WASTE_DISPOSAL6 = 6
    WASTE_DISPOSAL7 = 7
    WASTE_DISPOSAL8 = 8
    WASTE_DISPOSAL9 = 9
    WASTE_DISPOSAL10 = 10
    WASTE_DISPOSAL11 = 11
    WASTE_DISPOSAL12 = 12
    WASTE_DISPOSAL13 = 13
    WASTE_DISPOSAL14 = 14
    WASTE_DISPOSAL15 = 15

    WASTE_DISPOSAL_CHOICES = {
        WASTE_DISPOSAL1: _("WASTE_DISPOSAL1"),
        WASTE_DISPOSAL2: _("WASTE_DISPOSAL2"),
        WASTE_DISPOSAL3: _("WASTE_DISPOSAL3"),
        WASTE_DISPOSAL4: _("WASTE_DISPOSAL4"),
        WASTE_DISPOSAL5: _("WASTE_DISPOSAL5"),
        WASTE_DISPOSAL6: _("WASTE_DISPOSAL6"),
        WASTE_DISPOSAL7: _("WASTE_DISPOSAL7"),
        WASTE_DISPOSAL8: _("WASTE_DISPOSAL8"),
        WASTE_DISPOSAL9: _("WASTE_DISPOSAL9"),
        WASTE_DISPOSAL10: _("WASTE_DISPOSAL10"),
        WASTE_DISPOSAL11: _("WASTE_DISPOSAL11"),
        WASTE_DISPOSAL12: _("WASTE_DISPOSAL12"),
        WASTE_DISPOSAL13: _("WASTE_DISPOSAL13"),
        WASTE_DISPOSAL14: _("WASTE_DISPOSAL14"),
        WASTE_DISPOSAL15: _("WASTE_DISPOSAL15"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_WASTE_DISPOSAL"), choices=WASTE_DISPOSAL_CHOICES)
    qty_used = models.FloatField(_("qty_used"))
    disposal_method = models.CharField(_("disposal_method"))

    class Meta:
        verbose_name = _("HSE WASTE DISPOSAL")
        verbose_name_plural = _("HSE WASTE DISPOSAL")

class AppHSEPerformanceReportTherapeuticUnit(models.Model):
    QUALIFICATION1 = 1
    QUALIFICATION2 = 2

    QUALIFICATION_CHOICES = {
        QUALIFICATION1: _("QUALIFICATION1"),
        QUALIFICATION2: _("QUALIFICATION2"),
    }

    AMBULANCE_USED1 = 1
    AMBULANCE_USED2 = 2
    AMBULANCE_USED3 = 3

    AMBULANCE_CHOICES = {
        AMBULANCE_USED1: _("AMBULANCE_USED1"),
        AMBULANCE_USED2: _("AMBULANCE_USED2"),
        AMBULANCE_USED3: _("AMBULANCE_USED3"),
    }

    YES = 1
    NO = 2

    YES_NO_CHOICES = {
        YES: _("YES"),
        NO: _("NO"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    unit_manager = models.CharField(_("unit_manager"), max_length=100)
    unit_phone = models.CharField(_("unit_phone"), max_length=100)
    unit_qualification = models.PositiveIntegerField(_("unit_qualification"), choices=QUALIFICATION_CHOICES)
    aid_qty_used = models.PositiveIntegerField(_("aid_qty_used"))
    ambulance_used = models.PositiveIntegerField(_("ambulance_used"), choices=AMBULANCE_CHOICES)
    periodic_medical_examination  = models.PositiveIntegerField(_("periodic_medical_examination"), choices=YES_NO_CHOICES)
    primary_medical_examination = models.PositiveIntegerField(_("primary_medical_examination"), choices=YES_NO_CHOICES)

    class Meta:
        verbose_name = _("HSE Therapeutic unit")
        verbose_name_plural = _("HSE Therapeutic unit")

class AppHSEPerformanceReportDiseasesForWorkers(models.Model):
    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    disease_dt = models.DateField(_("disease_dt"), help_text="Ex: 2025-01-31")
    disease_type = models.CharField(_("disease_type"), max_length=100)
    no_patients = models.PositiveIntegerField(_("no_patients"))
    patients_career = models.CharField(_("patients_career"), max_length=100)
    patients_worksite = models.CharField(_("patients_worksite"), max_length=100)

    class Meta:
        verbose_name = _("HSE Diseases For Workers")
        verbose_name_plural = _("HSE Diseases For Workers")

class AppHSEPerformanceReportStatisticalData(models.Model):
    STATISTICAL_DATA1 = 1
    STATISTICAL_DATA2 = 2
    STATISTICAL_DATA3 = 3
    STATISTICAL_DATA4 = 4

    STATISTICAL_DATA_CHOICES = {
        STATISTICAL_DATA1: _(" STATISTICAL_DATA1"),
        STATISTICAL_DATA2: _(" STATISTICAL_DATA2"),
        STATISTICAL_DATA3: _(" STATISTICAL_DATA3"),
        STATISTICAL_DATA4: _(" STATISTICAL_DATA4"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_statistical_data"), choices=STATISTICAL_DATA_CHOICES)
    no_staff = models.PositiveIntegerField(_("no_staff"))
    no_contractor = models.PositiveIntegerField(_("no_contractor"))

    class Meta:
        verbose_name = _("HSE STATISTICAL DATA")
        verbose_name_plural = _("HSE STATISTICAL DATA")

class AppHSEPerformanceReportCatering(models.Model):
    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    meal_served_type = models.CharField(_("meal_served"), max_length=100)
    food_sources = models.CharField(_("food_sources"), max_length=100)
    food_transportation = models.CharField(_("food_transportation"), max_length=100)
    food_storage = models.TextField(_("food_storage"))
    kitchen_cleaning = models.TextField(_("kitchen_cleaning"))

    class Meta:
        verbose_name = _("HSE Catering")
        verbose_name_plural = _("HSE Catering")

# class AppHSEPerformanceReportPhotoAlbum(models.Model):
    # master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    # photo = models.ImageField(_('photo'),upload_to=company_applications_path)
    # description = models.TextField(_("description"))

    # class Meta:
    #     verbose_name = _("HSE PHOTO ALBUM")
    #     verbose_name_plural = _("HSE PHOTO ALBUM")

class AppHSEPerformanceReportExplosivesUsed(models.Model):
    EXPLOSIVES_USED1 = 1
    EXPLOSIVES_USED2 = 2
    EXPLOSIVES_USED3 = 3
    EXPLOSIVES_USED4 = 4
    EXPLOSIVES_USED5 = 5
    EXPLOSIVES_USED6 = 6
    EXPLOSIVES_USED7 = 7
    EXPLOSIVES_USED8 = 8
    EXPLOSIVES_USED9 = 9

    EXPLOSIVES_USED_CHOICES = {
        EXPLOSIVES_USED1: _("EXPLOSIVES_USED1"),
        EXPLOSIVES_USED2: _("EXPLOSIVES_USED2"),
        EXPLOSIVES_USED3: _("EXPLOSIVES_USED3"),
        EXPLOSIVES_USED4: _("EXPLOSIVES_USED4"),
        EXPLOSIVES_USED5: _("EXPLOSIVES_USED5"),
        EXPLOSIVES_USED6: _("EXPLOSIVES_USED6"),
        EXPLOSIVES_USED7: _("EXPLOSIVES_USED7"),
        EXPLOSIVES_USED8: _("EXPLOSIVES_USED8"),
        EXPLOSIVES_USED9: _("EXPLOSIVES_USED9"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_explosives_used"), choices=EXPLOSIVES_USED_CHOICES)
    qty_used = models.PositiveIntegerField(_("qty_used"))
    qty_remain = models.PositiveIntegerField(_("qty_remain"))
    expire_dt = models.DateField(_("expire_dt"), help_text="Ex: 2025-01-31")

    class Meta:
        verbose_name = _("HSE EXPLOSIVES USED")
        verbose_name_plural = _("HSE EXPLOSIVES USED")

class AppHSEPerformanceReportExplosivesUsedSpecification(models.Model):
    SPECIFICATION1 = 1
    SPECIFICATION2 = 2
    SPECIFICATION3 = 3
    SPECIFICATION4 = 4
    SPECIFICATION5 = 5

    SPECIFICATION_CHOICES = {
        SPECIFICATION1: _("EXP_SPECIFICATION1"),
        SPECIFICATION2: _("EXP_SPECIFICATION2"),
        SPECIFICATION3: _("EXP_SPECIFICATION3"),
        SPECIFICATION4: _("EXP_SPECIFICATION4"),
        SPECIFICATION5: _("EXP_SPECIFICATION5"),
    }

    YES = 1
    NO = 2

    YES_NO_CHOICES = {
        YES: _("YES"),
        NO: _("NO"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("Specification"), choices=SPECIFICATION_CHOICES)
    choice = models.PositiveIntegerField(_("is_exists"), choices=YES_NO_CHOICES)
    
    class Meta:
        verbose_name = _("HSE Explosive Storage Specification")
        verbose_name_plural = _("HSE Explosive Storage Specification")

class AppHSEPerformanceReportBillsOfQuantities(models.Model):
    BILLS_OF_QUANTITIES1 = 1
    BILLS_OF_QUANTITIES2 = 2
    BILLS_OF_QUANTITIES3 = 3
    BILLS_OF_QUANTITIES4 = 4
    BILLS_OF_QUANTITIES5 = 5
    BILLS_OF_QUANTITIES6 = 6
    BILLS_OF_QUANTITIES7 = 7
    BILLS_OF_QUANTITIES8 = 8
    BILLS_OF_QUANTITIES9 = 9
    BILLS_OF_QUANTITIES10 = 10

    BILLS_OF_QUANTITIES_CHOICES = {
        BILLS_OF_QUANTITIES1: _("BILLS_OF_QUANTITIES1"),
        BILLS_OF_QUANTITIES2: _("BILLS_OF_QUANTITIES2"),
        BILLS_OF_QUANTITIES3: _("BILLS_OF_QUANTITIES3"),
        BILLS_OF_QUANTITIES4: _("BILLS_OF_QUANTITIES4"),
        BILLS_OF_QUANTITIES5: _("BILLS_OF_QUANTITIES5"),
        BILLS_OF_QUANTITIES6: _("BILLS_OF_QUANTITIES6"),
        BILLS_OF_QUANTITIES7: _("BILLS_OF_QUANTITIES7"),
        BILLS_OF_QUANTITIES8: _("BILLS_OF_QUANTITIES8"),
        BILLS_OF_QUANTITIES9: _("BILLS_OF_QUANTITIES9"),
        BILLS_OF_QUANTITIES10: _("BILLS_OF_QUANTITIES10"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("hse_bills_of_quantities"), choices=BILLS_OF_QUANTITIES_CHOICES)
    qty_used = models.PositiveIntegerField(_("qty_used"))

    class Meta:
        verbose_name = _("HSE BILLS OF QUANTITIES")
        verbose_name_plural = _("HSE BILLS OF QUANTITIES")

class AppHSEPerformanceReportCadastralOperations(models.Model):
    SPECIFICATION1 = 1
    SPECIFICATION2 = 2
    SPECIFICATION3 = 3
    SPECIFICATION4 = 4
    SPECIFICATION5 = 5
    SPECIFICATION6 = 6
    SPECIFICATION7 = 7
    SPECIFICATION8 = 8
    SPECIFICATION9 = 9

    SPECIFICATION_CHOICES = {
        SPECIFICATION1: _("CADASTRAL_SPECIFICATION1"),
        SPECIFICATION2: _("CADASTRAL_SPECIFICATION2"),
        SPECIFICATION3: _("CADASTRAL_SPECIFICATION3"),
        SPECIFICATION4: _("CADASTRAL_SPECIFICATION4"),
        SPECIFICATION5: _("CADASTRAL_SPECIFICATION5"),
        SPECIFICATION6: _("CADASTRAL_SPECIFICATION6"),
        SPECIFICATION7: _("CADASTRAL_SPECIFICATION7"),
        SPECIFICATION8: _("CADASTRAL_SPECIFICATION8"),
        SPECIFICATION9: _("CADASTRAL_SPECIFICATION9"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("Specification"), choices=SPECIFICATION_CHOICES)
    value = models.CharField(_("value"), max_length=100)
    
    class Meta:
        verbose_name = _("HSE cadastral operations")
        verbose_name_plural = _("HSE cadastral operations")

class AppHSEPerformanceReportCadastralOperationsTwo(models.Model):
    SPECIFICATION1 = 1
    SPECIFICATION2 = 2
    SPECIFICATION3 = 3
    SPECIFICATION4 = 4
    SPECIFICATION5 = 5
    SPECIFICATION6 = 6
    SPECIFICATION7 = 7

    SPECIFICATION_CHOICES = {
        SPECIFICATION1: _("CADASTRAL2_SPECIFICATION1"),
        SPECIFICATION2: _("CADASTRAL2_SPECIFICATION2"),
        SPECIFICATION3: _("CADASTRAL2_SPECIFICATION3"),
        SPECIFICATION4: _("CADASTRAL2_SPECIFICATION4"),
        SPECIFICATION5: _("CADASTRAL2_SPECIFICATION5"),
        SPECIFICATION6: _("CADASTRAL2_SPECIFICATION6"),
        SPECIFICATION7: _("CADASTRAL2_SPECIFICATION7"),
    }

    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    factor = models.PositiveIntegerField(_("Specification"), choices=SPECIFICATION_CHOICES)
    observation = models.CharField(_("observation"), max_length=100)
    result = models.CharField(_("result"), max_length=100)
    
    class Meta:
        verbose_name = _("HSE cadastral operations2")
        verbose_name_plural = _("HSE cadastral operations2")

class AppHSEPerformanceReportAuditorComment(models.Model):
    master = models.ForeignKey(AppHSEPerformanceReport, on_delete=models.PROTECT)    
    comment = models.TextField(_("comment"))

    class Meta:
        verbose_name = _("ملاحظات المراقب")
        verbose_name_plural = _("ملاحظات المراقب")
