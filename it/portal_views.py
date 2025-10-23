from django.shortcuts import reverse_lazy
from django.views.generic import TemplateView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _

from .models import HelpRequest, EmployeeComputer
from .forms import HelpRequestForm


class PortalDashboard(LoginRequiredMixin, TemplateView):
    template_name = 'it/portal/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch employee's computers and recent help requests
        employee = self.request.user.employee  # Assumes User has an 'employee' attribute linking to EmployeeBasic
        context['employee_computers'] = EmployeeComputer.objects.filter(employee=employee)
        context['help_requests'] = HelpRequest.objects.filter(employee=employee).order_by('-created_at')[:5]
        return context


class HelpRequestCreateView(LoginRequiredMixin, CreateView):
    model = HelpRequest
    form_class = HelpRequestForm
    template_name = 'it/portal/help_request_form.html'
    success_url = reverse_lazy('it:portal_dashboard')

    def form_valid(self, form):
        form.instance.employee = self.request.user.employee  # Assumes User has an 'employee' attribute
        return super().form_valid(form)


class ComputerDetailView(LoginRequiredMixin, DetailView):
    model = EmployeeComputer
    template_name = 'it/portal/computer_detail.html'

    def get_queryset(self):
        # Ensure users can only view their own computers
        return super().get_queryset().filter(employee=self.request.user.employee)
