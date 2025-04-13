from django.urls import path
from django.conf.urls.static import static

# from django.conf import settings

from company_profile_exploration.views.workplan import AppWorkPlanCreateView, AppWorkPlanDeleteView, AppWorkPlanListView, AppWorkPlanReadonlyView, AppWorkPlanUpdateView


app_name = "exploration"
urlpatterns = [
    # path('', PaDailyView.as_view(), name='home'),

    path('work_plan/', AppWorkPlanListView.as_view(), name='workplan_list'),
    path('work_plan/<int:type>/', AppWorkPlanListView.as_view(), name='workplan_list'),
    path('work_plan/<int:pk>/edit/', AppWorkPlanUpdateView.as_view(), name='workplan_edit'),    
    path('work_plan/<int:pk>/show/', AppWorkPlanReadonlyView.as_view(), name='workplan_show'),    
    path('work_plan/<int:pk>/delete/', AppWorkPlanDeleteView.as_view(), name='workplan_delete'),    
    path('work_plan/add/', AppWorkPlanCreateView.as_view(), name='workplan_add'),


] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
