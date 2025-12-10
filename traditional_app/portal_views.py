from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from traditional_app.models import (
    DailyReport, Employee, PayrollMaster, LkpSoag, Vehicle,
    DailyWardHajr, DailyIncome, DailyTahsilForm, DailyKartaMor7ala,
    DailyGrabeel, DailyHofrKabira, DailySmallProcessingUnit, MONTH_CHOICES
)


class PortalUserMixin(UserPassesTestMixin):
    """Mixin to ensure user has traditional_app_user profile"""
    
    def test_func(self):
        try:
            return hasattr(self.request.user, 'traditional_app_user')
        except:
            return False


class DashboardView(LoginRequiredMixin, PortalUserMixin, View):
    """Dashboard view showing statistics and recent reports"""
    
    def get(self, request):
        user_state = request.user.traditional_app_user.state
        
        # Get statistics
        stats = {
            'daily_reports_count': DailyReport.objects.filter(source_state=user_state).count(),
            'employees_count': Employee.objects.filter(state=user_state).count(),
            'sougs_count': LkpSoag.objects.filter(state=user_state).count(),
            'vehicles_count': Vehicle.objects.filter(state=user_state).count(),
        }
        
        # Get recent reports
        recent_reports = DailyReport.objects.filter(
            source_state=user_state
        ).order_by('-date')[:5]
        
        context = {
            'stats': stats,
            'recent_reports': recent_reports,
        }
        
        return render(request, 'traditional_app/portal/dashboard.html', context)


class DailyReportsListView(LoginRequiredMixin, PortalUserMixin, ListView):
    """List view for daily reports with filtering"""
    
    model = DailyReport
    template_name = 'traditional_app/portal/daily_reports.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        user_state = self.request.user.traditional_app_user.state
        queryset = DailyReport.objects.filter(source_state=user_state).order_by('-date')
        
        # Apply filters
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        state = self.request.GET.get('state')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if state:
            queryset = queryset.filter(state=state)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['state_choices'] = DailyReport.STATE_CHOICES.items()
        return context


class DailyReportDetailView(LoginRequiredMixin, PortalUserMixin, DetailView):
    """Detail view for a single daily report"""
    
    model = DailyReport
    template_name = 'traditional_app/portal/daily_report_detail.html'
    context_object_name = 'report'
    
    def get_queryset(self):
        user_state = self.request.user.traditional_app_user.state
        return DailyReport.objects.filter(source_state=user_state)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = self.object
        
        # Get related data
        context['ward_hajr'] = DailyWardHajr.objects.filter(daily_report=report)
        context['daily_income'] = DailyIncome.objects.filter(daily_report=report)
        context['tahsil_forms'] = DailyTahsilForm.objects.filter(daily_report=report)
        context['karta_mor7ala'] = DailyKartaMor7ala.objects.filter(daily_report=report)
        context['grabeel'] = DailyGrabeel.objects.filter(daily_report=report)
        context['hofr_kabira'] = DailyHofrKabira.objects.filter(daily_report=report)
        context['small_processing_units'] = DailySmallProcessingUnit.objects.filter(daily_report=report)
        
        # Get available workflow transitions
        context['next_states'] = report.get_next_states(self.request.user)
        
        return context


class DailyReportTransitionView(LoginRequiredMixin, PortalUserMixin, View):
    """Handle workflow state transitions for daily reports"""
    
    def post(self, request, pk):
        user_state = request.user.traditional_app_user.state
        report = get_object_or_404(DailyReport, pk=pk, source_state=user_state)
        
        next_state_value = request.POST.get('next_state')
        
        if not next_state_value:
            messages.error(request, 'لم يتم تحديد الحالة الجديدة')
            return redirect('traditional_app:portal_daily_report_detail', pk=pk)
        
        try:
            next_state_value = int(next_state_value)
            next_state_label = DailyReport.STATE_CHOICES.get(next_state_value)
            
            if not next_state_label:
                messages.error(request, 'الحالة المحددة غير صحيحة')
                return redirect('traditional_app:portal_daily_report_detail', pk=pk)
            
            next_state = (next_state_value, next_state_label)
            
            # Attempt transition
            report.transition_to_next_state(request.user, next_state)
            messages.success(request, f'تم تحويل التقرير إلى: {next_state_label}')
            
        except Exception as e:
            messages.error(request, f'خطأ في تحويل الحالة: {str(e)}')
        
        return redirect('traditional_app:portal_daily_report_detail', pk=pk)


class EmployeesListView(LoginRequiredMixin, PortalUserMixin, ListView):
    """List view for employees with filtering"""
    
    model = Employee
    template_name = 'traditional_app/portal/employees.html'
    context_object_name = 'employees'
    paginate_by = 20
    
    def get_queryset(self):
        user_state = self.request.user.traditional_app_user.state
        queryset = Employee.objects.filter(state=user_state).select_related('category')
        
        # Apply filters
        name = self.request.GET.get('name')
        no3_elta3god = self.request.GET.get('no3_elta3god')
        
        if name:
            queryset = queryset.filter(name__icontains=name)
        if no3_elta3god:
            queryset = queryset.filter(no3_elta3god=no3_elta3god)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_type_choices'] = Employee.EMPLOYEE_TYPE_CHOICES.items()
        return context


class EmployeeDetailView(LoginRequiredMixin, PortalUserMixin, DetailView):
    """Detail view for a single employee"""
    
    model = Employee
    template_name = 'traditional_app/portal/employee_detail.html'
    context_object_name = 'employee'
    
    def get_queryset(self):
        user_state = self.request.user.traditional_app_user.state
        return Employee.objects.filter(state=user_state).select_related('category').select_related('employeeproject')


class PayrollListView(LoginRequiredMixin, PortalUserMixin, ListView):
    """List view for payroll records"""
    
    model = PayrollMaster
    template_name = 'traditional_app/portal/payroll.html'
    context_object_name = 'payrolls'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = PayrollMaster.objects.all().order_by('-year', '-month')
        
        # Apply filters
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        
        if year:
            queryset = queryset.filter(year=year)
        if month:
            queryset = queryset.filter(month=month)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['month_choices'] = MONTH_CHOICES.items()
        return context


class PayrollDetailView(LoginRequiredMixin, PortalUserMixin, DetailView):
    """Detail view for a single payroll record"""
    
    model = PayrollMaster
    template_name = 'traditional_app/portal/payroll_detail.html'
    context_object_name = 'payroll'


class ProfileView(LoginRequiredMixin, PortalUserMixin, View):
    """User profile view"""
    
    def get(self, request):
        return render(request, 'traditional_app/portal/profile.html')


class SettingsView(LoginRequiredMixin, PortalUserMixin, View):
    """User settings view with password change"""
    
    def get(self, request):
        form = PasswordChangeForm(request.user)
        return render(request, 'traditional_app/portal/settings.html', {'form': form})
    
    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'تم تغيير كلمة المرور بنجاح')
            return redirect('traditional_app:portal_settings')
        else:
            messages.error(request, 'حدث خطأ في تغيير كلمة المرور')
            return render(request, 'traditional_app/portal/settings.html', {'form': form})
