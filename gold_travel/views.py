import json
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Count, Sum, F, ExpressionWrapper, DecimalField
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.http import JsonResponse
from gold_travel.models import AppMoveGold, AppPrepareGold, TblStateRepresentative

class UserPermissionMixin(UserPassesTestMixin):
    user_groups = []

    def test_func(self):
        try:
            authority = self.request.user.state_representative.authority
            return (authority==TblStateRepresentative.AUTHORITY_SMRC)
        except:
            return False

        return False

class GoldTravelCert(LoginRequiredMixin,UserPermissionMixin,TemplateView):
    template_name = 'gold_travel/gold_travel.html'

    def _partition(self,lst, size=20):
        l = len(lst)
        if l <= 18:
            yield lst
        else:
            yield lst[0 : 18]
            for i in range(18, l, size):
                yield lst[i : i+size]

    def get(self,*args,**kwargs):
        id = int(self.request.GET['id'])
        obj = get_object_or_404(AppMoveGold,pk=id)

        state_repr = {}
        for r in TblStateRepresentative.objects.filter(state=obj.source_state):
            state_repr[f"{r.authority}"]= r.name

        alloy_chunks = self._partition(obj.appmovegolddetails_set.all())

        self.extra_context = {
            'object': obj,
            'alloy_chunks': alloy_chunks,
            'state_repr': state_repr,
        }
        return render(self.request, self.template_name, self.extra_context)    

class WhomMayConcern(LoginRequiredMixin,UserPermissionMixin,TemplateView):
    template_name = 'gold_travel/whom_may_concern.html'

    def get(self,*args,**kwargs):
        id = int(self.request.GET['id'])
        obj = get_object_or_404(AppPrepareGold,pk=id)
        self.extra_context = {
            'object': obj,
        }
        return render(self.request, self.template_name, self.extra_context)    

def get_exported_gold(request):
    qs = AppMoveGold.objects \
        .filter(form_type=1,state=6) \
        .select_related('appmovegolddetails','source_state') \
        .values('source_state__name','source_state__geom') \
        .annotate(
            total_weight_in_ton = Sum(
                ExpressionWrapper(F('appmovegolddetails__alloy_weight_in_gram') /1000000, output_field=DecimalField())
            ),
            forms_count = Count('appmovegolddetails')
        )
    
    features = []
    for item in qs:
        geom = item['source_state__geom']
        if geom:
            features.append({
                "type": "Feature",
                "geometry": json.loads(geom.geojson),  # Convert GEOSGeometry to dict
                "properties": {
                    "state_name": item['source_state__name'],
                    "total_weight_in_ton": item['total_weight_in_ton'],
                    "forms_count": item['forms_count'],
                }
            })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return JsonResponse(geojson)

    # geojson_data = serialize('geojson', qs, geometry_field='geom', fields=('source_state__name','total_weight_in_ton','forms_count'))
    # return HttpResponse(geojson_data, content_type='application/json')