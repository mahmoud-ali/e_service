from django.urls import path
from django.conf.urls.static import static

# from django.conf import settings

from hse_companies.views.incident import IncidentInfoCreateView, IncidentInfoListView, IncidentInfoReadonlyView
from hse_companies.views import evaluation
from hse_companies.views.corrective_action import CorrectiveActionReportPDFView


app_name = "hse_companies"
urlpatterns = [
    # path('', PaDailyView.as_view(), name='home'),

    path('incident/', IncidentInfoListView.as_view(), name='incident_list'),
    path('incident/<int:type>/', IncidentInfoListView.as_view(), name='incident_list'),
    # path('incident/<int:pk>/edit/', AppWorkPlanUpdateView.as_view(), name='incident_edit'),    
    path('incident/<int:pk>/show/', IncidentInfoReadonlyView.as_view(), name='incident_show'),    
    # path('incident/<int:pk>/delete/', AppWorkPlanDeleteView.as_view(), name='incident_delete'),    
    path('incident/add/', IncidentInfoCreateView.as_view(), name='incident_add'),

    # Corrective Action PDF Reports
    path('corrective-action/pdf/', CorrectiveActionReportPDFView.as_view(), name='corrective_action_pdf'),
    path('corrective-action/action/<int:action_id>/pdf/', CorrectiveActionReportPDFView.as_view(), name='corrective_action_single_pdf'),
    path('corrective-action/report/<int:report_id>/pdf/', CorrectiveActionReportPDFView.as_view(), name='corrective_action_report_pdf'),
    path('corrective-action/incident/<int:incident_id>/pdf/', CorrectiveActionReportPDFView.as_view(), name='corrective_action_incident_pdf'),
    path('corrective-action/company/<int:company_id>/pdf/', CorrectiveActionReportPDFView.as_view(), name='corrective_action_company_pdf'),
]

