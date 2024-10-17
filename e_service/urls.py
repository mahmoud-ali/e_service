"""
URL configuration for e_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path,include
from django.views.generic import TemplateView

from django.contrib import admin
from django.contrib.flatpages import views as flatpages_views
from django.conf import settings


urlpatterns = [
    path("__debug__/", include("debug_toolbar.urls")),
    path('api/', include('billing_api.urls')), 
    path('api-traditional/', include('traditional_api.urls')), 

    path('managers/', admin.site.urls),
    path('accounts/', include('accounts.urls')), 
    path('check/', include('check_cordinates.urls')), 
    path("about/", flatpages_views.flatpage, {"url": "/about/"}, name="about"),
    path('pa/', include('pa.urls')), 
    path('help/', include('help_request.urls')), 
    path('gold_travel/', include('gold_travel.urls')), 

    path('', include('company_profile.urls')),
    # path('', include('pwa.urls')),  # You MUST use an empty string as the URL prefix    
]

if settings.DEBUG:
    urlpatterns = [path('app/', include(urlpatterns))]

    from django.urls import reverse
    from django.shortcuts import redirect
    def redirect_to_home(request):
        return redirect(reverse('profile:home'))
    
    urlpatterns.append(
        path('', redirect_to_home)
    )
