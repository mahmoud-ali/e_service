from django.forms import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404,render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django.contrib import messages

from company_profile.models import TblCompanyProduction
from ..forms import ApplicationExectiveProcessingShowEditForm
from ..tables import ApplicationExectiveProcessingTable,ApplicationExectiveProcessingFilter

from ..models import  STATE_TYPE_DRAFT,STATE_TYPE_CONFIRM, ApplicationExectiveProcessing

from .application import ApplicationListView, ApplicationMasterDetailUpdateView, ApplicationReadonlyView

model_master = ApplicationExectiveProcessing
details = []

class ApplicationExectiveProcessingListView(ApplicationListView):
    model = model_master
    table_class = ApplicationExectiveProcessingTable
    filterset_class = ApplicationExectiveProcessingFilter
    user_groups = ['doc_executive','doc_department']
    menu_name = "doc_workflow:executive_processing_list"
    title = _("List of application in executive processing")
    template_name = "doc_workflow/views/application_list_without_add.html"
    
class ApplicationExectiveProcessingUpdateView(ApplicationMasterDetailUpdateView):
    model = model_master
    form_class = ApplicationExectiveProcessingShowEditForm
    details = details
    user_groups = ['doc_department']
    menu_name = "doc_workflow:executive_processing_list"
    menu_show_name = "doc_workflow:executive_processing_show"
    title = _("Edit application in executive processing")

    def get_queryset(self):
        query = ApplicationExectiveProcessing.objects.all()     
        return query.filter(action_state=STATE_TYPE_DRAFT)
    
    def post(self, request,pk, *args, **kwargs):
        form = self.form_class(request.POST,request.FILES,instance=self.model.objects.get(id=pk))
        self.extra_context["form"] = form
        form.id = pk
        if form.is_valid():
            self.object = form.save(commit=False)
            
            if not self.object.id:
                self.object.created_by = self.object.updated_by = request.user
                self.object.created_at = self.object.updated_at = timezone.now()
            else:
                self.object.updated_by = request.user
                self.object.updated_at = timezone.now()
            
            if self.request.POST.get('_save_confirm') and self.test_group('doc_department'):
                self.object.action_state = STATE_TYPE_CONFIRM
            
            # self.object.clean()
            try:
                self.object.save()
                messages.add_message(request,messages.SUCCESS,_("Application sent successfully."))
                return HttpResponseRedirect(self.success_url)
            except ValidationError as e:
                form.add_error(None,e)

        self.extra_context["form"] = form

        return render(request, self.template_name, self.extra_context)

class ApplicationExectiveProcessingReadonlyView(ApplicationReadonlyView):
    model = model_master
    form_class = ApplicationExectiveProcessingShowEditForm
    details = details
    user_groups = ['doc_executive','doc_department']
    menu_name = "doc_workflow:executive_processing_list"
    menu_edit_name = "doc_workflow:executive_processing_edit"
    menu_delete_name = None
    title = _("Show application in executive processing")
    template_name = "doc_workflow/views/application_readonly.html"
