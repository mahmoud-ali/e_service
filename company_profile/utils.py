from django.db.models import Value,Count
from django.urls import reverse_lazy

def get_app_metrics(fields={},filter={},related=[],order=[]):
    from .models import AppCyanideCertificate, AppExplosivePermission, AppFuelPermission, AppImportPermission, \
                        AppBorrowMaterial,AppWorkPlan,AppTechnicalFinancialReport, \
                        AppChangeCompanyName, AppExplorationTime, AppAddArea,AppRemoveArea, AppTnazolShraka, \
                        AppTajeelTnazol, AppTajmeed,AppTakhali,AppTamdeed,AppTaaweed,AppMda,AppChangeWorkProcedure, \
                        AppExportGold,AppExportGoldRaw,AppSendSamplesForAnalysis,AppForeignerProcedure,AppAifaaJomrki, \
                        AppVisibityStudy,AppReexportEquipments,AppRequirementsList,TblCompany,AppWhomConcern,AppHSEAccidentReport, AppHSEPerformanceReport

    models = [
        AppCyanideCertificate, AppExplosivePermission, AppFuelPermission, AppImportPermission, 
        AppBorrowMaterial,AppWorkPlan,AppTechnicalFinancialReport,
        AppChangeCompanyName, AppExplorationTime, AppAddArea,AppRemoveArea, AppTnazolShraka, 
        AppTajeelTnazol, AppTajmeed,AppTakhali,AppTamdeed,AppTaaweed,AppMda,AppChangeWorkProcedure, 
        AppExportGold,AppExportGoldRaw,AppSendSamplesForAnalysis,AppForeignerProcedure,AppAifaaJomrki,
        AppVisibityStudy,AppReexportEquipments,AppRequirementsList,AppWhomConcern,AppHSEAccidentReport, AppHSEPerformanceReport
    ]

    qs_list = [
        q.objects \
            .filter(**filter) \
            .select_related(*related) \
            .only(*fields) \
            .annotate(app=Value(q._meta.verbose_name_raw)) \
            .annotate(url=Value('admin:%s_%s_change' % (q._meta.app_label,q._meta.model_name))) \
                for q in models \
    ]
    qs = qs_list[0]
    qs = qs \
        .union(*qs_list[1:]) \
        .order_by(*order)

    return qs