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
from django.urls import path,include,reverse
from django.views.generic import TemplateView

from django.contrib import admin
from django.contrib.flatpages import views as flatpages_views
from django.conf import settings
# from django.conf.urls.static import static

# from django.shortcuts import redirect

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# def redirect_to_home(request):
#     return redirect(reverse('admin:index'))

@login_required
def dashboard(request):
    return render(request, 'acceptance/dashboard.html')

urlpatterns = [
    path('managers/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    # path('accounts/', include('accounts.urls')), 
    # path('check/', include('check_cordinates.urls')), 
    # path("about/", flatpages_views.flatpage, {"url": "/about/"}, name="about"),
    # path('pa/', include('pa.urls')), 
    path('hr/', include('hr.urls')), 
    path('it/', include('it.urls')), 
    path('fleet/', include('fleet.urls')), 
    path('sandog/', include('sandog.urls')), 
    path('needs/', include('needs_request.urls')),
    
    # path('help/', include('help_request.urls')), 
    path('', include('hr_bot.urls')), 
    path('', dashboard, name='acceptance_home'),
    # path("__debug__/", include("debug_toolbar.urls")),


] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# if settings.DEBUG:
#     urlpatterns = [path('app/', include(urlpatterns))]

#     from django.urls import reverse
#     from django.shortcuts import redirect
#     def redirect_to_home(request):
#         return redirect(reverse('profile:home'))
    
#     urlpatterns.append(
#         path('', redirect_to_home)
#     )
