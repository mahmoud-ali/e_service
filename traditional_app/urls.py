from django.urls import path

from traditional_app.views import PayrollT3agood, geojson_soug_view

app_name = "traditional_app"
urlpatterns = [                                                        
    path('payroll_t3agood/', PayrollT3agood.as_view(), name='payroll_t3agood'),
    path('soug_layer/', geojson_soug_view, name='soug_layer'),
]