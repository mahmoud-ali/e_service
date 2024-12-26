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
        AppVisibityStudy,AppReexportEquipments,AppRequirementsList,AppWhomConcern,AppHSEAccidentReport, AppHSEPerformanceReport, AppLocalPurchase
    ]

    profile_show_urls = {
        "appcyanidecertificate":"app_cyanide_certificate_show",
        "appexplosivepermission":"app_explosive_permission_show",
        "appfuelpermission":"app_fuel_permission_show",
        "appimportpermission":"app_import_permission_show",
        "appborrowmaterial":"app_borrow_show",
        "appworkplan":"app_work_plan_show",
        "apptechnicalfinancialreport":"app_technical_financial_report_show",
        "appchangecompanyname":"app_change_company_name_show",
        "appexplorationtime":"app_exploration_time_show",
        "appaddarea":"app_add_area_show",
        "appremovearea":"app_remove_area_show",
        "apptnazolshraka":"app_tnazol_shraka_show",
        "apptajeeltnazol":"app_tajeel_tnazol_show",
        "apptajmeed":"app_tajmeed_show",
        "apptakhali":"app_takhali_show",
        "apptamdeed":"app_tamdeed_show",
        "apptaaweed":"app_taaweed_show",
        "appmda":"app_mda_show",
        "appchangeworkprocedure":"app_change_work_procedure_show",
        "appexportgold":"app_export_gold_show",
        "appexportgoldraw":"app_export_gold_raw_show",
        "appsendsamplesforanalysis":"app_send_samples_for_analysis_show",
        "appforeignerprocedure":"app_foreigner_procedure_show",
        "appaifaajomrki":"app_aifaa_jomrki_show",
        "appvisibitystudy":"app_visibility_study_show",
        "appreexportequipments":"app_reexport_equipments_show",
        "apprequirementslist":"app_requirements_list_show",
        "appwhomconcern":"app_whom_concern_show",
        "apphseaccidentreport":"app_hse_accident_show",
        "apphseperformancereport":"app_hse_performance_show",
        "applocalpurchase":"app_local_purchase_show",
    }

    qs_list = [
        q.objects \
            .filter(**filter) \
            .select_related(*related) \
            .only(*fields) \
            .annotate(app=Value(q._meta.verbose_name_raw)) \
            .annotate(admin_url=Value('admin:%s_%s_change' % (q._meta.app_label,q._meta.model_name))) \
            .annotate(app_url=Value('profile:%s' % (profile_show_urls[q._meta.model_name],))) \
                for q in models \
    ]
    qs = qs_list[0]
    qs = qs \
        .union(*qs_list[1:]) \
        .order_by(*order)

    return qs
