from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.gis.geos import GEOSGeometry

from .models import SmallMining
from .forms import PointCordinateForm

class CheckCordinatesView(LoginRequiredMixin,View):
    form = PointCordinateForm
    detail_formset = None
    menu_name = "check_cordinates:check_view"
    title = ""
    form_title = _("Enter cordinates")
    template_name = "check_cordinates/application_add_master_details.html"
    
    def dispatch(self, *args, **kwargs):    
        self.detail_formset = formset_factory(self.form,extra=0,can_delete=False,min_num=3, validate_min=True)
            
        self.success_url = reverse_lazy(self.menu_name)
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
                            "form_title":self.form_title, 
                            "detail_formset": self.detail_formset,
         }
        return super().dispatch(*args, **kwargs)                    

    def get(self,request):        
        return render(request, self.template_name, self.extra_context)

    def post(self, request, *args, **kwargs):
        formset = self.detail_formset(request.POST)
        
        if formset.is_valid():
            # calculate intersection
            points = []
            for form in formset:
                x,y = (form.cleaned_data['x'],form.cleaned_data['y'])
                points.append(str(x)+' '+str(y))

            points.append(points[0])

            poly_wkt = "POLYGON(("+', '.join(points)+"))"
            poly = GEOSGeometry(poly_wkt)
            data = SmallMining.objects.filter(geom__intersects=poly).values_list("company_name")
            if len(data) > 0:
                tmp = []
                for d in data:
                    if d[0]:
                        tmp.append(d[0])
                messages.add_message(request,messages.ERROR,_("Intersect with other data: ")+ ", ".join(tmp))
            else:
                messages.add_message(request,messages.SUCCESS,_("No intersection!"))
                
        self.extra_context['detail_formset'] = formset

        return render(request, self.template_name, self.extra_context)
