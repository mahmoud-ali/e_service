import json
from django.forms import formset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.gis.geos import Polygon,Point

from .models import SmallMining
from .forms import PointCordinateForm

class CheckCordinatesView(LoginRequiredMixin,View):
    form = PointCordinateForm
    detail_formset = None
    menu_name = "check_cordinates:check_view"
    title = _("Check cordinates")
    template_name = "check_cordinates/page.html"
    
    def dispatch(self, *args, **kwargs):    
        self.detail_formset = formset_factory(self.form,extra=0,can_delete=False,min_num=3, validate_min=True)
            
        self.success_url = reverse_lazy(self.menu_name)
        self.extra_context = {
                            "menu_name":self.menu_name,
                            "title":self.title, 
                            "detail_formset": self.detail_formset,
         }
        return super().dispatch(*args, **kwargs)                    

    def get(self,request):        
        return render(request, self.template_name, self.extra_context)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        points = data.get("points",[])

        poly = Polygon(points)
        data = SmallMining.objects.filter(geom__intersects=poly).values_list("company_name")
        if len(data) > 0:
            tmp = []
            for d in data:
                if d[0]:
                    tmp.append(d[0])

            return JsonResponse({
                "code": 1,
                "result": _("Intersect with other data: ")+ ", ".join(tmp)
            })                    
        else:
            return JsonResponse({
                "code": 0,
                "result": _("No intersection!")
            })                    

            