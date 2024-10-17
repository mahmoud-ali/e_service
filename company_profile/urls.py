from django.urls import path
from django.conf.urls.static import static

from django.conf import settings

from company_profile.views.pa_request import AppRequestListView, AppRequestReadonlyView

from .views import CompanySummaryView,SetLanguageView, HomePageView, \
                   AppForignerMovementListView,AppForignerMovementCreateView,AppForignerMovementReadonlyView, \
                   AppBorrowMaterialListView,AppBorrowMaterialCreateView,AppBorrowMaterialReadonlyView, \
                   LkpLocalitySelectView,AppWorkPlanListView,AppWorkPlanCreateView,AppWorkPlanReadonlyView, \
                   AppTechnicalFinancialReportListView, AppTechnicalFinancialReportCreateView, AppTechnicalFinancialReportReadonlyView, \
                   AppChangeCompanyNameListView, AppChangeCompanyNameCreateView, AppChangeCompanyNameReadonlyView, \
                   AppExplorationTimeListView, AppExplorationTimeCreateView, AppExplorationTimeReadonlyView, \
                   AppAddAreaListView, AppAddAreaCreateView, AppAddAreaReadonlyView, \
                   AppRemoveAreaListView, AppRemoveAreaCreateView, AppRemoveAreaReadonlyView, \
                   AppTnazolShrakaListView, AppTnazolShrakaCreateView, AppTnazolShrakaReadonlyView, \
                   AppTajeelTnazolListView, AppTajeelTnazolCreateView, AppTajeelTnazolReadonlyView, \
                   AppTajmeedListView, AppTajmeedCreateView, AppTajmeedReadonlyView, \
                   AppTakhaliListView, AppTakhaliCreateView, AppTakhaliReadonlyView, \
                   AppTamdeedListView, AppTamdeedCreateView, AppTamdeedReadonlyView, \
                   AppTaaweedListView, AppTaaweedCreateView, AppTaaweedReadonlyView, \
                   AppMdaListView, AppMdaCreateView, AppMdaReadonlyView, \
                   AppChangeWorkProcedureListView, AppChangeWorkProcedureCreateView, AppChangeWorkProcedureReadonlyView, \
                   AppExportGoldListView, AppExportGoldCreateView, AppExportGoldReadonlyView, \
                   AppExportGoldRawListView, AppExportGoldRawCreateView, AppExportGoldRawReadonlyView, \
                   AppSendSamplesForAnalysisListView, AppSendSamplesForAnalysisCreateView, AppSendSamplesForAnalysisReadonlyView, \
                   AppForeignerProcedureListView, AppForeignerProcedureCreateView, AppForeignerProcedureReadonlyView, \
                   AppAifaaJomrkiListView, AppAifaaJomrkiCreateView, AppAifaaJomrkiReadonlyView, \
                   AppReexportEquipmentsListView, AppReexportEquipmentsCreateView, AppReexportEquipmentsReadonlyView, \
                   AppRequirementsListListView, AppRequirementsListCreateView, AppRequirementsListReadonlyView, \
                   AppVisibityStudyListView, AppVisibityStudyCreateView, AppVisibityStudyReadonlyView, \
                   AppTemporaryExemptionCreateView, AppTemporaryExemptionListView, AppTemporaryExemptionReadonlyView, \
                   AppLocalPurchaseListView,AppLocalPurchaseCreateView,AppLocalPurchaseReadonlyView, \
                   AppCyanideCertificateListView,AppCyanideCertificateCreateView,AppCyanideCertificateReadonlyView, \
                   AppExplosivePermissionListView,AppExplosivePermissionCreateView,AppExplosivePermissionReadonlyView, \
                   AppRestartActivityListView,AppRestartActivityCreateView,AppRestartActivityReadonlyView, \
                   AppRenewalContractListView,AppRenewalContractCreateView,AppRenewalContractReadonlyView, \
                   AppImportPermissionListView,AppImportPermissionCreateView,AppImportPermissionReadonlyView, \
                   AppFuelPermissionListView,AppFuelPermissionCreateView,AppFuelPermissionReadonlyView, \
                   AppHSEAccidentReportListView,AppHSEAccidentReportCreateView,AppHSEAccidentReportReadonlyView, \
                   AppHSEPerformanceReportListView,AppHSEPerformanceReportCreateView,AppHSEPerformanceReportReadonlyView, \
                   AppWhomConcernListView,AppWhomConcernCreateView,AppWhomConcernReadonlyView, \
                   AppGoldProductionListView,AppGoldProductionCreateView,AppGoldProductionReadonlyView

app_name = "profile"
urlpatterns = [                                                        
    path('', HomePageView.as_view(), name='home'),
    path('set_lang', SetLanguageView.as_view(), name='set_lang'),
    path('summary',CompanySummaryView.as_view(),name='summary'),

    path('lkp_locality/<int:master_id>/<int:dependent_id>/', LkpLocalitySelectView.as_view(), name='lkp_locality_select'),
    
    path('app_foreigner/', AppForignerMovementListView.as_view(), name='app_foreigner_list'),
    path('app_foreigner/<int:type>/', AppForignerMovementListView.as_view(), name='app_foreigner_list'),
    path('app_foreigner/<int:pk>/show/', AppForignerMovementReadonlyView.as_view(), name='app_foreigner_show'),
    path('app_foreigner/add/', AppForignerMovementCreateView.as_view(), name='app_foreigner_add'),
    
    path('app_borrow_materials/', AppBorrowMaterialListView.as_view(), name='app_borrow_list'),
    path('app_borrow_materials/<int:type>/', AppBorrowMaterialListView.as_view(), name='app_borrow_list'),
    path('app_borrow_materials/<int:pk>/show/', AppBorrowMaterialReadonlyView.as_view(), name='app_borrow_show'),    
    path('app_borrow_materials/add/', AppBorrowMaterialCreateView.as_view(), name='app_borrow_add'),

    path('app_work_plan/', AppWorkPlanListView.as_view(), name='app_work_plan_list'),
    path('app_work_plan/<int:type>/', AppWorkPlanListView.as_view(), name='app_work_plan_list'),
    path('app_work_plan/<int:pk>/show/', AppWorkPlanReadonlyView.as_view(), name='app_work_plan_show'),    
    path('app_work_plan/add/', AppWorkPlanCreateView.as_view(), name='app_work_plan_add'),

    path('app_technical_financial_report/', AppTechnicalFinancialReportListView.as_view(), name='app_technical_financial_report_list'),
    path('app_technical_financial_report/<int:type>/', AppTechnicalFinancialReportListView.as_view(), name='app_technical_financial_report_list'),
    path('app_technical_financial_report/<int:pk>/show/', AppTechnicalFinancialReportReadonlyView.as_view(), name='app_technical_financial_report_show'),    
    path('app_technical_financial_report/add/', AppTechnicalFinancialReportCreateView.as_view(), name='app_technical_financial_report_add'),

    path('app_change_company_name/', AppChangeCompanyNameListView.as_view(), name='app_change_company_name_list'),
    path('app_change_company_name/<int:type>/', AppChangeCompanyNameListView.as_view(), name='app_change_company_name_list'),
    path('app_change_company_name/<int:pk>/show/', AppChangeCompanyNameReadonlyView.as_view(), name='app_change_company_name_show'),    
    path('app_change_company_name/add/', AppChangeCompanyNameCreateView.as_view(), name='app_change_company_name_add'),

    path('app_exploration_time/', AppExplorationTimeListView.as_view(), name='app_exploration_time_list'),
    path('app_exploration_time/<int:type>/', AppExplorationTimeListView.as_view(), name='app_exploration_time_list'),
    path('app_exploration_time/<int:pk>/show/', AppExplorationTimeReadonlyView.as_view(), name='app_exploration_time_show'),    
    path('app_exploration_time/add/', AppExplorationTimeCreateView.as_view(), name='app_exploration_time_add'),

    path('app_add_area/', AppAddAreaListView.as_view(), name='app_add_area_list'),
    path('app_add_area/<int:type>/', AppAddAreaListView.as_view(), name='app_add_area_list'),
    path('app_add_area/<int:pk>/show/', AppAddAreaReadonlyView.as_view(), name='app_add_area_show'),    
    path('app_add_area/add/', AppAddAreaCreateView.as_view(), name='app_add_area_add'),

    path('app_remove_area/', AppRemoveAreaListView.as_view(), name='app_remove_area_list'),
    path('app_remove_area/<int:type>/', AppRemoveAreaListView.as_view(), name='app_remove_area_list'),
    path('app_remove_area/<int:pk>/show/', AppRemoveAreaReadonlyView.as_view(), name='app_remove_area_show'),    
    path('app_remove_area/add/', AppRemoveAreaCreateView.as_view(), name='app_remove_area_add'),

    path('app_tnazol_shraka/', AppTnazolShrakaListView.as_view(), name='app_tnazol_shraka_list'),
    path('app_tnazol_shraka/<int:type>/', AppTnazolShrakaListView.as_view(), name='app_tnazol_shraka_list'),
    path('app_tnazol_shraka/<int:pk>/show/', AppTnazolShrakaReadonlyView.as_view(), name='app_tnazol_shraka_show'),    
    path('app_tnazol_shraka/add/', AppTnazolShrakaCreateView.as_view(), name='app_tnazol_shraka_add'),

    path('app_tajeel_tnazol/', AppTajeelTnazolListView.as_view(), name='app_tajeel_tnazol_list'),
    path('app_tajeel_tnazol/<int:type>/', AppTajeelTnazolListView.as_view(), name='app_tajeel_tnazol_list'),
    path('app_tajeel_tnazol/<int:pk>/show/', AppTajeelTnazolReadonlyView.as_view(), name='app_tajeel_tnazol_show'),    
    path('app_tajeel_tnazol/add/', AppTajeelTnazolCreateView.as_view(), name='app_tajeel_tnazol_add'),

    path('app_tajmeed/', AppTajmeedListView.as_view(), name='app_tajmeed_list'),
    path('app_tajmeed/<int:type>/', AppTajmeedListView.as_view(), name='app_tajmeed_list'),
    path('app_tajmeed/<int:pk>/show/', AppTajmeedReadonlyView.as_view(), name='app_tajmeed_show'),    
    path('app_tajmeed/add/', AppTajmeedCreateView.as_view(), name='app_tajmeed_add'),

    path('app_takhali/', AppTakhaliListView.as_view(), name='app_takhali_list'),
    path('app_takhali/<int:type>/', AppTakhaliListView.as_view(), name='app_takhali_list'),
    path('app_takhali/<int:pk>/show/', AppTakhaliReadonlyView.as_view(), name='app_takhali_show'),    
    path('app_takhali/add/', AppTakhaliCreateView.as_view(), name='app_takhali_add'),

    path('app_tamdeed/', AppTamdeedListView.as_view(), name='app_tamdeed_list'),
    path('app_tamdeed/<int:type>/', AppTamdeedListView.as_view(), name='app_tamdeed_list'),
    path('app_tamdeed/<int:pk>/show/', AppTamdeedReadonlyView.as_view(), name='app_tamdeed_show'),    
    path('app_tamdeed/add/', AppTamdeedCreateView.as_view(), name='app_tamdeed_add'),
    
    path('app_taaweed/', AppTaaweedListView.as_view(), name='app_taaweed_list'),
    path('app_taaweed/<int:type>/', AppTaaweedListView.as_view(), name='app_taaweed_list'),
    path('app_taaweed/<int:pk>/show/', AppTaaweedReadonlyView.as_view(), name='app_taaweed_show'),    
    path('app_taaweed/add/', AppTaaweedCreateView.as_view(), name='app_taaweed_add'),

    path('app_mda/', AppMdaListView.as_view(), name='app_mda_list'),
    path('app_mda/<int:type>/', AppMdaListView.as_view(), name='app_mda_list'),
    path('app_mda/<int:pk>/show/', AppMdaReadonlyView.as_view(), name='app_mda_show'),    
    path('app_mda/add/', AppMdaCreateView.as_view(), name='app_mda_add'),

    path('app_change_work_procedure/', AppChangeWorkProcedureListView.as_view(), name='app_change_work_procedure_list'),
    path('app_change_work_procedure/<int:type>/', AppChangeWorkProcedureListView.as_view(), name='app_change_work_procedure_list'),
    path('app_change_work_procedure/<int:pk>/show/', AppChangeWorkProcedureReadonlyView.as_view(), name='app_change_work_procedure_show'),    
    path('app_change_work_procedure/add/', AppChangeWorkProcedureCreateView.as_view(), name='app_change_work_procedure_add'),

    path('app_export_gold/', AppExportGoldListView.as_view(), name='app_export_gold_list'),
    path('app_export_gold/<int:type>/', AppExportGoldListView.as_view(), name='app_export_gold_list'),
    path('app_export_gold/<int:pk>/show/', AppExportGoldReadonlyView.as_view(), name='app_export_gold_show'),    
    path('app_export_gold/add/', AppExportGoldCreateView.as_view(), name='app_export_gold_add'),

    path('app_export_gold_raw/', AppExportGoldRawListView.as_view(), name='app_export_gold_raw_list'),
    path('app_export_gold_raw/<int:type>/', AppExportGoldRawListView.as_view(), name='app_export_gold_raw_list'),
    path('app_export_gold_raw/<int:pk>/show/', AppExportGoldRawReadonlyView.as_view(), name='app_export_gold_raw_show'),    
    path('app_export_gold_raw/add/', AppExportGoldRawCreateView.as_view(), name='app_export_gold_raw_add'),

    path('app_send_samples_for_analysis/', AppSendSamplesForAnalysisListView.as_view(), name='app_send_samples_for_analysis_list'),
    path('app_send_samples_for_analysis/<int:type>/', AppSendSamplesForAnalysisListView.as_view(), name='app_send_samples_for_analysis_list'),
    path('app_send_samples_for_analysis/<int:pk>/show/', AppSendSamplesForAnalysisReadonlyView.as_view(), name='app_send_samples_for_analysis_show'),    
    path('app_send_samples_for_analysis/add/', AppSendSamplesForAnalysisCreateView.as_view(), name='app_send_samples_for_analysis_add'),

    path('app_foreigner_procedure/', AppForeignerProcedureListView.as_view(), name='app_foreigner_procedure_list'),
    path('app_foreigner_procedure/<int:type>/', AppForeignerProcedureListView.as_view(), name='app_foreigner_procedure_list'),
    path('app_foreigner_procedure/<int:pk>/show/', AppForeignerProcedureReadonlyView.as_view(), name='app_foreigner_procedure_show'),    
    path('app_foreigner_procedure/add/', AppForeignerProcedureCreateView.as_view(), name='app_foreigner_procedure_add'),

    path('app_aifaa_jomrki/', AppAifaaJomrkiListView.as_view(), name='app_aifaa_jomrki_list'),
    path('app_aifaa_jomrki/<int:type>/', AppAifaaJomrkiListView.as_view(), name='app_aifaa_jomrki_list'),
    path('app_aifaa_jomrki/<int:pk>/show/', AppAifaaJomrkiReadonlyView.as_view(), name='app_aifaa_jomrki_show'),    
    path('app_aifaa_jomrki/add/', AppAifaaJomrkiCreateView.as_view(), name='app_aifaa_jomrki_add'),

    path('app_reexport_equipments/', AppReexportEquipmentsListView.as_view(), name='app_reexport_equipments_list'),
    path('app_reexport_equipments/<int:type>/', AppReexportEquipmentsListView.as_view(), name='app_reexport_equipments_list'),
    path('app_reexport_equipments/<int:pk>/show/', AppReexportEquipmentsReadonlyView.as_view(), name='app_reexport_equipments_show'),    
    path('app_reexport_equipments/add/', AppReexportEquipmentsCreateView.as_view(), name='app_reexport_equipments_add'),

    path('app_requirements_list/', AppRequirementsListListView.as_view(), name='app_requirements_list_list'),
    path('app_requirements_list/<int:type>/', AppRequirementsListListView.as_view(), name='app_requirements_list_list'),
    path('app_requirements_list/<int:pk>/show/', AppRequirementsListReadonlyView.as_view(), name='app_requirements_list_show'),    
    path('app_requirements_list/add/', AppRequirementsListCreateView.as_view(), name='app_requirements_list_add'),

    path('app_visibility_study/', AppVisibityStudyListView.as_view(), name='app_visibility_study_list'),
    path('app_visibility_study/<int:type>/', AppVisibityStudyListView.as_view(), name='app_visibility_study_list'),
    path('app_visibility_study/<int:pk>/show/', AppVisibityStudyReadonlyView.as_view(), name='app_visibility_study_show'),    
    path('app_visibility_study/add/', AppVisibityStudyCreateView.as_view(), name='app_visibility_study_add'),

    path('app_temporary_exemption/', AppTemporaryExemptionListView.as_view(), name='app_temporary_exemption_list'),
    path('app_temporary_exemption/<int:type>/', AppTemporaryExemptionListView.as_view(), name='app_temporary_exemption_list'),
    path('app_temporary_exemption/<int:pk>/show/', AppTemporaryExemptionReadonlyView.as_view(), name='app_temporary_exemption_show'),    
    path('app_temporary_exemption/add/', AppTemporaryExemptionCreateView.as_view(), name='app_temporary_exemption_add'),

    path('app_local_purchase/', AppLocalPurchaseListView.as_view(), name='app_local_purchase_list'),
    path('app_local_purchase/<int:type>/', AppLocalPurchaseListView.as_view(), name='app_local_purchase_list'),
    path('app_local_purchase/<int:pk>/show/', AppLocalPurchaseReadonlyView.as_view(), name='app_local_purchase_show'),    
    path('app_local_purchase/add/', AppLocalPurchaseCreateView.as_view(), name='app_local_purchase_add'),

    path('app_cyanide_certificate/', AppCyanideCertificateListView.as_view(), name='app_cyanide_certificate_list'),
    path('app_cyanide_certificate/<int:type>/', AppCyanideCertificateListView.as_view(), name='app_cyanide_certificate_list'),
    path('app_cyanide_certificate/<int:pk>/show/', AppCyanideCertificateReadonlyView.as_view(), name='app_cyanide_certificate_show'),    
    path('app_cyanide_certificate/add/', AppCyanideCertificateCreateView.as_view(), name='app_cyanide_certificate_add'),

    path('app_explosive_permission/', AppExplosivePermissionListView.as_view(), name='app_explosive_permission_list'),
    path('app_explosive_permission/<int:type>/', AppExplosivePermissionListView.as_view(), name='app_explosive_permission_list'),
    path('app_explosive_permission/<int:pk>/show/', AppExplosivePermissionReadonlyView.as_view(), name='app_explosive_permission_show'),    
    path('app_explosive_permission/add/', AppExplosivePermissionCreateView.as_view(), name='app_explosive_permission_add'),

    path('app_restart_activity/', AppRestartActivityListView.as_view(), name='app_restart_activity_list'),
    path('app_restart_activity/<int:type>/', AppRestartActivityListView.as_view(), name='app_restart_activity_list'),
    path('app_restart_activity/<int:pk>/show/', AppRestartActivityReadonlyView.as_view(), name='app_restart_activity_show'),    
    path('app_restart_activity/add/', AppRestartActivityCreateView.as_view(), name='app_restart_activity_add'),

    path('app_renewal_contract/', AppRenewalContractListView.as_view(), name='app_renewal_contract_list'),
    path('app_renewal_contract/<int:type>/', AppRenewalContractListView.as_view(), name='app_renewal_contract_list'),
    path('app_renewal_contract/<int:pk>/show/', AppRenewalContractReadonlyView.as_view(), name='app_renewal_contract_show'),    
    path('app_renewal_contract/add/', AppRenewalContractCreateView.as_view(), name='app_renewal_contract_add'),

    path('app_import_permission/', AppImportPermissionListView.as_view(), name='app_import_permission_list'),
    path('app_import_permission/<int:type>/', AppImportPermissionListView.as_view(), name='app_import_permission_list'),
    path('app_import_permission/<int:pk>/show/', AppImportPermissionReadonlyView.as_view(), name='app_import_permission_show'),    
    path('app_import_permission/add/', AppImportPermissionCreateView.as_view(), name='app_import_permission_add'),

    path('app_fuel_permission/', AppFuelPermissionListView.as_view(), name='app_fuel_permission_list'),
    path('app_fuel_permission/<int:type>/', AppFuelPermissionListView.as_view(), name='app_fuel_permission_list'),
    path('app_fuel_permission/<int:pk>/show/', AppFuelPermissionReadonlyView.as_view(), name='app_fuel_permission_show'),    
    path('app_fuel_permission/add/', AppFuelPermissionCreateView.as_view(), name='app_fuel_permission_add'),

    path('app_hse_accident/', AppHSEAccidentReportListView.as_view(), name='app_hse_accident_list'),
    path('app_hse_accident/<int:type>/', AppHSEAccidentReportListView.as_view(), name='app_hse_accident_list'),
    path('app_hse_accident/<int:pk>/show/', AppHSEAccidentReportReadonlyView.as_view(), name='app_hse_accident_show'),    
    path('app_hse_accident/add/', AppHSEAccidentReportCreateView.as_view(), name='app_hse_accident_add'),

    path('app_hse_performance/', AppHSEPerformanceReportListView.as_view(), name='app_hse_performance_list'),
    path('app_hse_performance/<int:type>/', AppHSEPerformanceReportListView.as_view(), name='app_hse_performance_list'),
    path('app_hse_performance/<int:pk>/show/', AppHSEPerformanceReportReadonlyView.as_view(), name='app_hse_performance_show'),    
    path('app_hse_performance/add/', AppHSEPerformanceReportCreateView.as_view(), name='app_hse_performance_add'),

    path('app_whom_concern/', AppWhomConcernListView.as_view(), name='app_whom_concern_list'),
    path('app_whom_concern/<int:type>/', AppWhomConcernListView.as_view(), name='app_whom_concern_list'),
    path('app_whom_concern/<int:pk>/show/', AppWhomConcernReadonlyView.as_view(), name='app_whom_concern_show'),    
    path('app_whom_concern/add/', AppWhomConcernCreateView.as_view(), name='app_whom_concern_add'),

    path('app_gold_production/', AppGoldProductionListView.as_view(), name='app_gold_production_list'),
    path('app_gold_production/<int:type>/', AppGoldProductionListView.as_view(), name='app_gold_production_list'),
    path('app_gold_production/<int:pk>/show/', AppGoldProductionReadonlyView.as_view(), name='app_gold_production_show'),    
    path('app_gold_production/add/', AppGoldProductionCreateView.as_view(), name='app_gold_production_add'),

    path('pa_request/', AppRequestListView.as_view(), name='pa_request_list'),
    path('pa_request/<int:type>/', AppRequestListView.as_view(), name='pa_request_list'),
    path('pa_request/<int:pk>/show/', AppRequestReadonlyView.as_view(), name='pa_request_show'),    


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
