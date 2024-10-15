from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from company_profile.models import TblCompany
from pa.models import TblCompanyCommitmentMaster
from company_profile.models import TblCompanyProductionLicense

class LkpSelectView(LoginRequiredMixin,TemplateView):
    template_name = 'pa/select.html'
    kwargs = None

    def get_queryset(self):
        return None #not implemented

    def dispatch(self, *args, **kwargs):
        self.kwargs = kwargs
        self.extra_context = {
                            "options":self.get_queryset(), 
                            "old_value":self.kwargs['dependent_id']
         }
        return super().dispatch(*args, **kwargs)                    

    def get(self, request, *args, **kwargs):                   
        return render(request, self.template_name, self.extra_context)    

class LkpLicenseSelectView(LkpSelectView):
    def get_queryset(self):
        qs = TblCompanyProductionLicense.objects.filter(company__id = self.kwargs['master_id'])
        return qs

def get_company_details(commitment:TblCompanyCommitmentMaster):
    dict = {
        "name":commitment.company.name_ar,
        "address":commitment.company.address,
        "company_type":commitment.company.company_type,
    }

    if hasattr(commitment,'license'):
        dict['license'] = commitment.license

    if commitment.company.company_type == 'sageer':
        dict['license_count'] = commitment.company.tblcompanyproductionlicense_set.count()

    return dict

