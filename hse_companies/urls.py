from django.urls import path
from django.conf.urls.static import static

# from django.conf import settings

from hse_companies.views.incident import IncidentInfoCreateView, IncidentInfoListView, IncidentInfoReadonlyView


app_name = "hse_companies"
urlpatterns = [
    # path('', PaDailyView.as_view(), name='home'),

    path('incident/', IncidentInfoListView.as_view(), name='incident_list'),
    path('incident/<int:type>/', IncidentInfoListView.as_view(), name='incident_list'),
    # path('incident/<int:pk>/edit/', AppWorkPlanUpdateView.as_view(), name='incident_edit'),    
    path('incident/<int:pk>/show/', IncidentInfoReadonlyView.as_view(), name='incident_show'),    
    # path('incident/<int:pk>/delete/', AppWorkPlanDeleteView.as_view(), name='incident_delete'),    
    path('incident/add/', IncidentInfoCreateView.as_view(), name='incident_add'),


] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
