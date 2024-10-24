from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

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

    def _partition(self,lst, size):
        for i in range(0, len(lst), size):
            yield lst[i : i+size]

    def get(self,*args,**kwargs):
        id = int(self.request.GET['id'])
        obj = get_object_or_404(AppMoveGold,pk=id)

        state_repr = {}
        for r in TblStateRepresentative.objects.filter(state=obj.source_state):
            state_repr[f"{r.authority}"]= r.name

        alloy_chunks = self._partition(obj.appmovegolddetails_set.all(),20)

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
