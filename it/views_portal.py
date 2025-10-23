from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.views.generic import ListView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import HelpRequest

class ManagerRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure user is in 'Manager' group."""
    def test_func(self):
        return self.request.user.groups.filter(name='Manager').exists()

    def handle_no_permission(self):
        messages.error(self.request, _("You do not have permission to access this page."))
        return super().handle_no_permission()

class HelpRequestListView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = HelpRequest
    template_name = 'it/portal/help_request_list.html'
    context_object_name = 'help_requests'
    paginate_by = 10  # For large lists
    ordering = '-created_at'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Add filtering if needed, e.g., by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = HelpRequest.STATUS_CHOICES
        context['category_choices'] = HelpRequest.CATEGORY_CHOICES
        return context
