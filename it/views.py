from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Q, Count

from hr_bot.models import EmployeeTelegram
from it.forms import HelpRequestForm
from it.models import AccessPoint, EmployeeComputer, Peripheral, HelpRequest, Conversation
from it.utils import AI, queryset_to_markdown


class EmployeeComputerAskAIView(LoginRequiredMixin, DetailView):
    model = EmployeeComputer
    model_details = [Peripheral, AccessPoint]
    template_name = "it/ai_prompt.html"

    def get(self, request, pk):
        obj = self.get_object()

        user_setup = []
        for model in self.model_details:
            qs = model.objects.filter(computer=obj.computer)
            if qs.count() > 0:
                user_setup.append({
                    "title": "## " + qs[0]._meta.verbose_name,
                    "md": format_html(queryset_to_markdown(qs, ["id", "computer"]))
                })

        prompt = AI.get("prompt")
        network_setup = AI.get("network_setup")
        faq = AI.get("faq")

        self.extra_context = {
            "prompt": prompt,
            "faq": faq,
            "network_setup": network_setup,
            "user_setup": user_setup,
        }

        return render(request, self.template_name, self.extra_context)


class HelpdeskTelegramUser(DetailView):
    model = EmployeeComputer

    def get(self, request, user_id):
        employeeComputer = get_object_or_404(EmployeeComputer, uuid=user_id)
        form = HelpRequestForm(request.GET)

        return render(request, "it/help_form.html", {"employee": employeeComputer.employee, "form": form})

    def post(self, request, user_id):
        employeeComputer = get_object_or_404(EmployeeComputer, uuid=user_id)
        form = HelpRequestForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.employee = employeeComputer.employee
            obj.save()

            return render(request, "it/success.html")

        return render(request, "it/help_form.html", {"form": form})


# Manager Portal Views

class ManagerRequiredMixin(UserPassesTestMixin):
    """Mixin to ensure user is in IT Manager group"""

    def test_func(self):
        return self.request.user.groups.filter(name='IT Manager').exists()

    def handle_no_permission(self):
        messages.error(self.request, _('You do not have permission to access this page.'))
        return redirect('admin:index')


class ManagerDashboardView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    """Manager dashboard showing help request statistics and overview"""
    model = HelpRequest
    template_name = 'it/manager/dashboard.html'
    context_object_name = 'help_requests'

    def get_queryset(self):
        return HelpRequest.objects.select_related('employee').order_by('-created_at')[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistics
        context['total_requests'] = HelpRequest.objects.count()
        context['unsolved_requests'] = HelpRequest.objects.filter(
            status=HelpRequest.STATUS_UNSOLVED
        ).count()
        context['solved_requests'] = HelpRequest.objects.filter(
            status=HelpRequest.STATUS_SOLVED
        ).count()

        # Category breakdown
        context['category_stats'] = HelpRequest.objects.values('category').annotate(
            count=Count('id')
        ).order_by('-count')

        return context


class ManagerHelpRequestListView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    """List all help requests with filtering and search"""
    model = HelpRequest
    template_name = 'it/manager/help_request_list.html'
    context_object_name = 'help_requests'
    paginate_by = 20

    def get_queryset(self):
        queryset = HelpRequest.objects.select_related('employee').order_by('-created_at')

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=int(status))

        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search) |
                Q(description__icontains=search) |
                Q(employee__name__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = HelpRequest.STATUS_CHOICES
        context['category_choices'] = HelpRequest.CATEGORY_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_search'] = self.request.GET.get('search', '')
        return context


class ManagerHelpRequestDetailView(LoginRequiredMixin, ManagerRequiredMixin, DetailView):
    """View and manage a single help request"""
    model = HelpRequest
    template_name = 'it/manager/help_request_detail.html'
    context_object_name = 'help_request'
    pk_url_kwarg = 'pk'


class ManagerHelpRequestUpdateView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    """Update help request with investigations, root cause, and solution"""
    model = HelpRequest
    template_name = 'it/manager/help_request_update.html'
    fields = ['investigations', 'root_cause', 'solution', 'status']
    pk_url_kwarg = 'pk'

    def get_success_url(self):
        messages.success(self.request, _('Help request updated successfully.'))
        return reverse_lazy('it:manager_help_request_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, _('Changes saved successfully.'))
        return super().form_valid(form)


class ManagerEmployeeComputerListView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    """List all employee computers"""
    model = EmployeeComputer
    template_name = 'it/manager/employee_computer_list.html'
    context_object_name = 'employee_computers'
    paginate_by = 20

    def get_queryset(self):
        queryset = EmployeeComputer.objects.select_related(
            'employee', 'computer', 'computer__template'
        ).order_by('employee__name')

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(employee__name__icontains=search) |
                Q(employee__code__icontains=search) |
                Q(computer__code__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search', '')
        return context


class ManagerEmployeeComputerDetailView(LoginRequiredMixin, ManagerRequiredMixin, DetailView):
    """View employee computer details and conversation history"""
    model = EmployeeComputer
    template_name = 'it/manager/employee_computer_detail.html'
    context_object_name = 'employee_computer'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conversations'] = Conversation.objects.filter(
            master=self.object
        ).order_by('-created_at')[:50]
        return context
