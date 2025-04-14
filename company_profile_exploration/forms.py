from django.forms import ModelForm
from company_profile_exploration.models.work_plan import AppWorkPlan, TblCompanyExploration, TblLicenseExploration


class AppWorkPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        company = self.user.pro_company.company
        print("company",company)

        if company:
            self.fields["license"].queryset = TblLicenseExploration.objects.filter(company=company)
        else:
            self.fields["license"].queryset = TblLicenseExploration.objects.none()

    class Meta:
        model = AppWorkPlan     
        fields = ["license","currency"] 
