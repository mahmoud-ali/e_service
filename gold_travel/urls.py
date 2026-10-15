from django.urls import path

from django.conf import settings

from .views import AppGoldStorageCompaniesCert, GoldTravelCert, LkpAlloySelectView, WhomMayConcern, get_exported_gold


app_name = "gold_travel"
urlpatterns = [                                                        
    path('certificate/gold_travel', GoldTravelCert.as_view(), name='gold_travel_cert'),
    path('certificate/whom_may_concern', WhomMayConcern.as_view(), name='whom_may_concern'),
    path('certificate/gold_storage_companies', AppGoldStorageCompaniesCert.as_view(), name='gold_storage_companies_cert'),
    path('lkp_alloy/<int:master_id>/<int:dependent_id>/', LkpAlloySelectView.as_view(), name='lkp_alloy_select'),
    path('geojson/exported_gold', get_exported_gold, name='get_exported_gold'),

]