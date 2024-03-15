from collections import defaultdict

from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from .models import AppCyanideCertificate, AppExplosivePermission, AppFuelPermission, AppImportPermission, \
                    AppBorrowMaterial,AppWorkPlan,AppTechnicalFinancialReport, \
                    AppChangeCompanyName, AppExplorationTime, AppAddArea,AppRemoveArea, AppTnazolShraka, \
                    AppTajeelTnazol, AppTajmeed,AppTakhali,AppTamdeed,AppTaaweed,AppMda,AppChangeWorkProcedure, \
                    AppExportGold,AppExportGoldRaw,AppSendSamplesForAnalysis,AppForeignerProcedure,AppAifaaJomrki, \
                    AppVisibityStudy,AppReexportEquipments,AppRequirementsList,TblCompany
                    
def get_admin_change_url(object):
    info = (object._meta.app_label, object._meta.model_name)
    url = reverse_lazy('admin:%s_%s_change' % info, args=(object.id,))
    return url

def in_progress_apps(request):
    data = []
    company_count = defaultdict(int)
    app_count = defaultdict(int)

    if request.path == '/managers/company_profile/':
        filter = []
        company_types = []

        if request.user.groups.filter(name="pro_company_application_accept").exists():
            filter += ["submitted"]
        if request.user.groups.filter(name="pro_company_application_approve").exists():
            filter += ["accepted"]

        if request.user.groups.filter(name="company_type_entaj").exists():
            company_types += [TblCompany.COMPANY_TYPE_ENTAJ]
        if request.user.groups.filter(name="company_type_mokhalfat").exists():
            company_types += [TblCompany.COMPANY_TYPE_MOKHALFAT]
        if request.user.groups.filter(name="company_type_emtiaz").exists():
            company_types += [TblCompany.COMPANY_TYPE_EMTIAZ]
        if request.user.groups.filter(name="company_type_sageer").exists():
            company_types += [TblCompany.COMPANY_TYPE_SAGEER]

        models = [
            AppCyanideCertificate, AppExplosivePermission, AppFuelPermission, AppImportPermission, 
            AppBorrowMaterial,AppWorkPlan,AppTechnicalFinancialReport,
            AppChangeCompanyName, AppExplorationTime, AppAddArea,AppRemoveArea, AppTnazolShraka, 
            AppTajeelTnazol, AppTajmeed,AppTakhali,AppTamdeed,AppTaaweed,AppMda,AppChangeWorkProcedure, 
            AppExportGold,AppExportGoldRaw,AppSendSamplesForAnalysis,AppForeignerProcedure,AppAifaaJomrki,
            AppVisibityStudy,AppReexportEquipments,AppRequirementsList
        ]
        for m in models:
            qs = m.objects.filter(state__in=filter,company__company_type__in=company_types).order_by("-updated_at").prefetch_related('company')
            for r in qs:
                key1 = r.company.__str__()
                company_count[key1] += 1 

                key2 = r._meta.verbose_name
                app_count[key2] += 1 

                data.append( {
                    'company': r.company.__str__(),
                    'app': r.__str__(),
                    'updated_at': r.updated_at,
                    'url': get_admin_change_url(r),
                })

        company_count = dict(sorted(company_count.items(),key=lambda x:x[1],reverse=True))
        app_count = dict(sorted(app_count.items(),key=lambda x:x[1],reverse=True))

        if data:
            return {
                'in_progress_apps': {
                    'data':data,
                    'summary':{
                        'company':{
                            'name': list(company_count.keys()),
                            'count': list(company_count.values())
                        },
                        'app':{
                            'name': list(app_count.keys()),
                            'count': list(app_count.values())
                        }
                    }
                }
            }
    
    return {}
