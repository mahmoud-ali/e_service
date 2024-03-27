from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from django.contrib import messages

from ..models import TblCompanyCommitment
from ..forms import TblCompanyCommitmentForm

from ..tables import TblCompanyCommitmentTable,CommitmentFilter

from .application import ApplicationListView, ApplicationCreateView, ApplicationReadonlyView

class TblCompanyCommitmentListView(ApplicationListView):
    model = TblCompanyCommitment
    table_class = TblCompanyCommitmentTable
    filterset_class = CommitmentFilter
    menu_name = "pa:commitment_list"
    title = _("List of commitments")
    
    # def dispatch(self, *args, **kwargs):         
    #     # if not hasattr(self.request.user,"pro_company"):
    #     #     return HttpResponseRedirect(reverse_lazy("pa:home"))    
            
    #     return super().dispatch(*args, **kwargs)        
            
    # def get_queryset(self):

    #     query = super().get_queryset()        
    #     return query


class TblCompanyCommitmentCreateView(ApplicationCreateView):
    model = TblCompanyCommitment
    form_class = TblCompanyCommitmentForm
    menu_name = "pa:commitment_list"
    title = _("Add new commitment")

    def dispatch(self, *args, **kwargs):         
        # if not hasattr(self.request.user,"pro_company"):
        #     return HttpResponseRedirect(reverse_lazy("pa:home"))    
            
        return super().dispatch(*args, **kwargs)        
            

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        self.object.created_by = self.object.updated_by = self.request.user

        self.object.save()
        
        messages.add_message(self.request,messages.SUCCESS,_("Record saved successfully."))
        
        # info = (self.object._meta.app_label, self.object._meta.model_name)
        # resp_user = get_sumitted_responsible('pro_company')
        # url = 'https://'+Site.objects.get_current().domain+reverse_lazy('admin:%s_%s_change' % info, args=(self.object.id,))
        # send_transition_email(self.object.state,resp_user.email,url,resp_user.lang.lower())
        
        return HttpResponseRedirect(self.get_success_url())
        
class TblCompanyCommitmentReadonlyView(ApplicationReadonlyView):
    model = TblCompanyCommitment
    form_class = TblCompanyCommitmentForm
    menu_name = "pa:commitment_list"
    title = _("Show added commitment")

    def dispatch(self, *args, **kwargs):         
        # if not hasattr(self.request.user,"pro_company"):
        #     return HttpResponseRedirect(reverse_lazy("pa:home"))               
        return super().dispatch(*args, **kwargs)        

    def get_queryset(self):
        query = super().get_queryset()        
        return query

