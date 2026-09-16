from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count, Avg, Sum
from django.http import JsonResponse
from django.utils import timezone

from maintenance.models import (
    MaintenanceRequest, MaintenanceUnit, FaultCategory,
    CompletionReport, ServiceRating, SparePart, StockMovement,
    LowStockAlert, Notification, SafetyPermit, Floor, Apartment, TechnicalTechnician
)
from maintenance.forms import (
    EmployeeRequestForm, CompletionReportForm, ServiceRatingForm,
    SparePartForm, StockMovementForm, RequestFilterForm, SparePartUsageForm,
    SafetyPermitForm, SafetyPermitApprovalForm, TechnicalTechnicianForm
)


class GroupRequiredMixin(UserPassesTestMixin):
    allowed_groups = []

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if self.request.user.is_superuser:
            return True
        return self.request.user.groups.filter(name__in=self.allowed_groups).exists()

    def handle_no_permission(self):
        messages.error(self.request, _('ليس لديك صلاحية للوصول لهذه الصفحة.'))
        return redirect('maintenance:dashboard')


ADMIN_GROUPS  = ['maintenance_admin']
STORE_GROUPS  = ['maintenance_store', 'maintenance_admin']
SAFETY_GROUPS = ['maintenance_safety', 'maintenance_admin']
TECH_GROUPS   = ['maintenance_elec', 'maintenance_air_cond', 'maintenance_mech',
                 'maintenance_const', 'maintenance_admin']
ALL_GROUPS    = TECH_GROUPS + ['maintenance_employee', 'maintenance_store', 'maintenance_safety']


def get_user_role(user):
    if user.is_superuser:
        return 'admin'
    groups = list(user.groups.values_list('name', flat=True))
    if 'maintenance_admin' in groups:
        return 'admin'
    if 'maintenance_safety' in groups:
        return 'safety'
    if 'maintenance_store' in groups:
        return 'store'
    if any(g in groups for g in TECH_GROUPS):
        return 'technician'
    return 'employee'


def get_user_unit(user):
    unit_map = {
        'maintenance_elec':     'ELEC',
        'maintenance_air_cond': 'AIR_COND',
        'maintenance_mech':     'MECH',
        'maintenance_const':    'CONST',
        'maintenance_safety':   'SAFETY',
    }
    for group_name, unit_code in unit_map.items():
        if user.groups.filter(name=group_name).exists():
            try:
                return MaintenanceUnit.objects.get(code=unit_code)
            except MaintenanceUnit.DoesNotExist:
                return None
    return None


@login_required
def dashboard(request):
    role = get_user_role(request.user)
    if role == 'admin':
        return redirect('maintenance:admin_dashboard')
    elif role == 'store':
        return redirect('maintenance:store_dashboard')
    elif role == 'technician':
        return redirect('maintenance:technician_request_list')
    else:
        return redirect('maintenance:my_requests')
class NewRequestView(LoginRequiredMixin, View):
    """إنشاء طلب صيانة جديد"""
    template_name = 'maintenance/employee/request_form.html'

    def _get_units(self, user):
        is_admin = user.is_superuser or user.groups.filter(name='maintenance_admin').exists()
        units = MaintenanceUnit.objects.prefetch_related('fault_categories').all()
        if not is_admin:
            units = units.filter(requires_safety_permit=False).exclude(code=MaintenanceUnit.CODE_SAFETY)
        return units

    def get(self, request):
        form  = EmployeeRequestForm(user=request.user)
        units = self._get_units(request.user)
        return render(request, self.template_name, {
            'form':  form,
            'units': units,
        })

    def post(self, request):
        form = EmployeeRequestForm(request.POST, user=request.user)
        if form.is_valid():
            req = form.save()
            messages.success(request, _(f'تم تقديم طلبك بنجاح. رقم الطلب: {req.request_number}'))
            return redirect('maintenance:request_detail', pk=req.pk)

        units = self._get_units(request.user)
        return render(request, self.template_name, {
            'form':  form,
            'units': units,
        })


class MyRequestsView(LoginRequiredMixin, ListView):
    model               = MaintenanceRequest
    template_name       = 'maintenance/employee/my_requests.html'
    context_object_name = 'requests'
    paginate_by         = 15

    def get_queryset(self):
        qs = MaintenanceRequest.objects.filter(
            requester=self.request.user
        ).select_related('fault_category', 'fault_category__unit', 'assigned_technician')

        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(
                Q(request_number__icontains=search) |
                Q(employee_name__icontains=search) |
                Q(department__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = MaintenanceRequest.STATUS_CHOICES
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['unread_count']   = Notification.objects.filter(
            recipient=self.request.user, is_read=False).count()
        return ctx


class RequestDetailView(LoginRequiredMixin, DetailView):
    model               = MaintenanceRequest
    template_name       = 'maintenance/employee/request_detail.html'
    context_object_name = 'req'

    def get_queryset(self):
        role = get_user_role(self.request.user)
        qs   = MaintenanceRequest.objects.select_related(
            'fault_category', 'fault_category__unit',
            'assigned_unit', 'assigned_technician', 'requester'
        )
        if role == 'admin':
            return qs
        elif role == 'technician':
            unit = get_user_unit(self.request.user)
            return qs.filter(assigned_unit=unit) if unit else qs.none()
        elif role == 'store':
            return qs
        else:
            return qs.filter(requester=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        req = self.object
        ctx['can_rate']      = (
            req.status == 'completed' and
            req.requester == self.request.user and
            not hasattr(req, 'rating')
        )
        ctx['spare_parts']   = req.spare_parts_used.select_related('spare_part').all()
        ctx['notifications'] = Notification.objects.filter(
            recipient=self.request.user, related_request=req)
        return ctx


class RateServiceView(LoginRequiredMixin, View):
    template_name = 'maintenance/employee/rating_form.html'

    def get(self, request, pk):
        req = get_object_or_404(MaintenanceRequest, pk=pk, requester=request.user,
                                status='completed')
        if hasattr(req, 'rating'):
            messages.info(request, _('لقد قيّمت هذا الطلب مسبقاً.'))
            return redirect('maintenance:request_detail', pk=pk)
        return render(request, self.template_name, {
            'req':  req,
            'form': ServiceRatingForm(),
        })

    def post(self, request, pk):
        req = get_object_or_404(MaintenanceRequest, pk=pk, requester=request.user,
                                status='completed')
        form = ServiceRatingForm(request.POST)
        if form.is_valid():
            rating          = form.save(commit=False)
            rating.request  = req
            rating.save()
            messages.success(request, _('شكراً على تقييمك!'))
            return redirect('maintenance:request_detail', pk=pk)
        return render(request, self.template_name, {'req': req, 'form': form})

class TechnicianRequestListView(LoginRequiredMixin, ListView):
    model               = MaintenanceRequest
    template_name       = 'maintenance/technician/request_list.html'
    context_object_name = 'requests'
    paginate_by         = 15

    def get_queryset(self):
        user = self.request.user
        role = get_user_role(user)

        qs = MaintenanceRequest.objects.select_related(
            'fault_category', 'fault_category__unit', 'assigned_technician', 'requester'
        )

        if role == 'admin':
            pass  
        else:
            unit = get_user_unit(user)
            if unit:
                qs = qs.filter(assigned_unit=unit)
            else:
                return qs.none()

        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)

        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(
                Q(request_number__icontains=search) |
                Q(employee_name__icontains=search) |
                Q(department__icontains=search)
            )

        return qs.order_by('status', '-created_at')

    def get_context_data(self, **kwargs):
        ctx  = super().get_context_data(**kwargs)
        user = self.request.user
        unit = get_user_unit(user)
        ctx['unit']           = unit
        ctx['status_choices'] = MaintenanceRequest.STATUS_CHOICES
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['unread_count']   = Notification.objects.filter(
            recipient=user, is_read=False).count()
        return ctx


class TechnicianRequestDetailView(LoginRequiredMixin, View):
    template_name = 'maintenance/technician/request_detail.html'

    def _get_request(self, request, pk):
        role = get_user_role(request.user)
        qs   = MaintenanceRequest.objects.select_related(
            'fault_category__unit', 'assigned_unit', 'assigned_technician', 'requester'
        )
        if role in ['admin', 'safety']:
            return get_object_or_404(qs, pk=pk)
        unit = get_user_unit(request.user)
        return get_object_or_404(qs, pk=pk, assigned_unit=unit)

    def get(self, request, pk):
        req           = self._get_request(request, pk)
        report_form   = CompletionReportForm()
        part_form     = SparePartUsageForm()
        spare_parts   = req.spare_parts_used.select_related('spare_part').all()
        units         = MaintenanceUnit.objects.all()
        tech_list     = TechnicalTechnician.objects.filter(is_active=True).order_by('name')
        return render(request, self.template_name, {
            'req':                        req,
            'report_form':                report_form,
            'part_form':                  part_form,
            'spare_parts':                spare_parts,
            'units':                      units,
            'all_technical_technicians': tech_list,
        })

    def post(self, request, pk):
        req    = self._get_request(request, pk)
        action = request.POST.get('action')

        if action == 'receive':
            req.status = 'received'
            if not req.assigned_technician:
                req.assigned_technician = request.user
            req.save()
            messages.success(request, _('تمت استلام الطلب وتغيير حالته إلى (تم الاستلام).'))

        elif action == 'start':
            role = get_user_role(request.user)
            if role == 'safety' and not (request.user.is_superuser or request.user.groups.filter(name='maintenance_admin').exists()):
                messages.error(request, _('عذراً، موظف السلامة يملك صلاحية اعتماد وإغلاق التصريح فقط، وليس من صلاحياته بدء العمل الفني على الطلب.'))
                return redirect('maintenance:technician_request_detail', pk=pk)

            if req.requires_safety_permit:
                permit = getattr(req, 'safety_permit', None)
                if not permit or permit.status != 'approved':
                    messages.error(request, _('عذراً، يتطلب هذا البلاغ تصريح سلامة مهنية معتمد من قسم السلامة الداخلية قبل بدء العمل.'))
                    return redirect('maintenance:technician_request_detail', pk=pk)

            # Handle assigned technical technicians if passed in execution modal
            tech_ids = request.POST.getlist('technical_technicians')
            if tech_ids:
                req.assigned_technical_technicians.set(tech_ids)

            req.status              = 'in_progress'
            if not req.assigned_technician:
                req.assigned_technician = request.user
            req.save()
            messages.success(request, _('تم بدء العمل وتغيير حالة الطلب إلى (قيد التنفيذ).'))

        elif action == 'assign_technical_technicians':
            tech_ids = request.POST.getlist('technical_technicians')
            req.assigned_technical_technicians.set(tech_ids)
            req.save()
            messages.success(request, _('تم تحديث قائمة الفنيين التقنيين المشاركين بنجاح.'))

        elif action == 'update_delay':
            delay_reason = request.POST.get('delay_reason', '').strip()
            req.delay_reason = delay_reason
            req.save()
            messages.success(request, _('تم حفظ سبب التأخير للطلب.'))

        elif action == 'update_priority':
            new_priority = request.POST.get('priority', '')
            if new_priority in dict(MaintenanceRequest.PRIORITY_CHOICES):
                req.priority = new_priority
                req.save()
                messages.success(request, _('تم تحديث أولوية الطلب بنجاح.'))

        elif action == 'add_part':
            role = get_user_role(request.user)
            if role == 'safety' and not (request.user.is_superuser or request.user.groups.filter(name='maintenance_admin').exists()):
                messages.error(request, _('عذراً، خصم وإضافة قطع الغيار هي مسؤولية الفني المختص وليس موظف السلامة.'))
                return redirect('maintenance:technician_request_detail', pk=pk)

            part_form = SparePartUsageForm(request.POST)
            if part_form.is_valid():
                part = part_form.cleaned_data.get('spare_part')
                qty  = part_form.cleaned_data.get('quantity', 1)
                if part and qty:
                    if part.quantity_in_stock < qty:
                        messages.error(request, _('الكمية المطلوبة أكبر من الرصيد المتاح.'))
                    else:
                        StockMovement.objects.create(
                            spare_part=part,
                            movement_type='out',
                            quantity=qty,
                            maintenance_request=req,
                            performed_by=request.user,
                            notes=f'استهلاك في طلب {req.request_number}'
                        )
                        messages.success(request, _(f'تم خصم {qty} × {part.name} من المخزون.'))
            return redirect('maintenance:technician_request_detail', pk=pk)

        elif action == 'complete':
            role = get_user_role(request.user)
            if role == 'safety' and not (request.user.is_superuser or request.user.groups.filter(name='maintenance_admin').exists()):
                messages.error(request, _('عذراً، رفع تقرير الإنجاز هو مسؤولية الفني المختص فقط. دور موظف السلامة ينحصر في إغلاق الطلب والتصريح بعد رفع التقرير.'))
                return redirect('maintenance:technician_request_detail', pk=pk)

            report_form = CompletionReportForm(request.POST)
            if report_form.is_valid():
                if not hasattr(req, 'completion_report'):
                    report              = report_form.save(commit=False)
                    report.request      = req
                    report.technician   = request.user
                    report.save()

                if req.requires_safety_permit:
                    messages.success(request, _('تم رفع تقرير الإنجاز بنجاح. البلاغ الآن بانتظار إغلاق الطلب من قبل قسم السلامة الداخلية.'))
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    safety_users = User.objects.filter(groups__name='maintenance_safety')
                    for u in safety_users:
                        Notification.objects.create(
                            recipient=u,
                            notification_type=Notification.TYPE_REQUEST_COMPLETED,
                            title=_('تم رفع تقرير الإنجاز — بانتظار إغلاق السلامة النهائي'),
                            message=f'قام الفني برفع تقرير الإنجاز للطلب {req.request_number}. يرجى المعاينة والضغط على زر إغلاق الطلب.',
                            related_request=req
                        )
                else:
                    req.status       = 'completed'
                    req.completed_at = timezone.now()
                    req.save()
                    messages.success(request, _('تم إغلاق الطلب ورفع تقرير الإنجاز.'))
            else:
                messages.error(request, _('يرجى ملء تقرير الإنجاز بشكل صحيح.'))
                return redirect('technician_request_detail', pk=pk)

        elif action == 'switch_unit':
            role = get_user_role(request.user)
            if role != 'admin' and not request.user.groups.filter(name='maintenance_admin').exists():
                messages.error(request, _('عذراً، تبديل الوحدة هي صلاحية خاصة بـ مدير إدارة الصيانة فقط.'))
                return redirect('maintenance:technician_request_detail', pk=pk)

            new_unit_id = request.POST.get('new_unit_id')
            if not new_unit_id:
                messages.error(request, _('يرجى اختيار الوحدة الجديدة.'))
                return redirect('maintenance:technician_request_detail', pk=pk)

            new_unit = get_object_or_404(MaintenanceUnit, pk=new_unit_id)
            if req.assigned_unit_id == new_unit.id:
                messages.warning(request, _('الطلب موجه بالفعل إلى هذه الوحدة.'))
                return redirect('maintenance:technician_request_detail', pk=pk)

            old_unit_name = req.assigned_unit.name if req.assigned_unit else _('غير محدد')
            req.assigned_unit = new_unit
            req.assigned_technician = None
            req.status = 'pending'
            req.save()

            messages.success(request, _(f'تم تبديل الوحدة من ({old_unit_name}) إلى ({new_unit.name}) بنجاح.'))
            return redirect('maintenance:technician_request_detail', pk=pk)

        return redirect('maintenance:technician_request_detail', pk=pk)


class StoreDashboardView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = STORE_GROUPS
    template_name  = 'maintenance/store/dashboard.html'

    def get(self, request):
        low_stock_parts = SparePart.objects.filter(
            is_active=True,
            quantity_in_stock__lte=models_reorder()
        ).select_related('unit')[:20]

        recent_movements = StockMovement.objects.select_related(
            'spare_part', 'performed_by', 'maintenance_request'
        ).order_by('-created_at')[:20]

        unresolved_alerts = LowStockAlert.objects.filter(is_resolved=False).select_related('spare_part')

        return render(request, self.template_name, {
            'low_stock_parts':   SparePart.objects.filter(is_active=True).filter(
                                     quantity_in_stock__lte=_reorder_subquery()
                                 ).select_related('unit'),
            'recent_movements':  recent_movements,
            'unresolved_alerts': unresolved_alerts,
            'total_parts':       SparePart.objects.filter(is_active=True).count(),
            'low_stock_count':   SparePart.objects.filter(
                                     is_active=True,
                                     quantity_in_stock__lte=0
                                 ).count(),
            'unread_count':      Notification.objects.filter(
                                     recipient=request.user, is_read=False).count(),
        })


def models_reorder():
    return 0


def _reorder_subquery():
    from django.db.models import F
    return F('reorder_point')


class SparePartListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    allowed_groups      = STORE_GROUPS
    model               = SparePart
    template_name       = 'maintenance/store/spare_part_list.html'
    context_object_name = 'parts'
    paginate_by         = 20

    def get_queryset(self):
        qs = SparePart.objects.select_related('unit').filter(is_active=True)
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(Q(sku__icontains=search) | Q(name__icontains=search))
        unit = self.request.GET.get('unit')
        if unit:
            qs = qs.filter(unit__code=unit)
        low_only = self.request.GET.get('low_only')
        if low_only:
            from django.db.models import F
            qs = qs.filter(quantity_in_stock__lte=F('reorder_point'))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['units']    = MaintenanceUnit.objects.all()
        ctx['unit_filter'] = self.request.GET.get('unit', '')
        ctx['search']   = self.request.GET.get('search', '')
        ctx['low_only'] = self.request.GET.get('low_only', '')
        return ctx


class SparePartCreateView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    allowed_groups = STORE_GROUPS
    model          = SparePart
    form_class     = SparePartForm
    template_name  = 'maintenance/store/spare_part_form.html'
    success_url    = reverse_lazy('maintenance:spare_part_list')

    def form_valid(self, form):
        messages.success(self.request, _('تمت إضافة القطعة بنجاح.'))
        return super().form_valid(form)


class SparePartUpdateView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    allowed_groups = STORE_GROUPS
    model          = SparePart
    form_class     = SparePartForm
    template_name  = 'maintenance/store/spare_part_form.html'
    success_url    = reverse_lazy('maintenance:spare_part_list')

    def form_valid(self, form):
        messages.success(self.request, _('تم تحديث بيانات القطعة.'))
        return super().form_valid(form)


class StockMovementCreateView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = STORE_GROUPS
    template_name  = 'maintenance/store/stock_movement_form.html'

    def get(self, request):
        return render(request, self.template_name, {'form': StockMovementForm()})

    def post(self, request):
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.performed_by = request.user
            movement.save()
            messages.success(request, _('تم تسجيل حركة المخزون بنجاح.'))
            return redirect('maintenance:store_dashboard')
        return render(request, self.template_name, {'form': form})


class StockMovementListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    allowed_groups      = STORE_GROUPS
    model               = StockMovement
    template_name       = 'maintenance/store/stock_movement_list.html'
    context_object_name = 'movements'
    paginate_by         = 25

    def get_queryset(self):
        qs = StockMovement.objects.select_related(
            'spare_part', 'performed_by', 'maintenance_request'
        ).order_by('-created_at')
        movement_type = self.request.GET.get('type', '')
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(spare_part__name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['movement_type'] = self.request.GET.get('type', '')
        ctx['search_query']  = self.request.GET.get('search', '')
        return ctx



class LowStockAlertListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    allowed_groups      = STORE_GROUPS
    model               = LowStockAlert
    template_name       = 'maintenance/store/low_stock_alerts.html'
    context_object_name = 'alerts'

    def get_queryset(self):
        return LowStockAlert.objects.filter(is_resolved=False).select_related('spare_part__unit')

    def post(self, request):
        alert_id = request.POST.get('alert_id')
        if alert_id:
            alert = get_object_or_404(LowStockAlert, pk=alert_id)
            alert.is_resolved = True
            alert.resolved_at = timezone.now()
            alert.save()
            messages.success(request, _('تم وضع علامة "تمت المعالجة" على التنبيه.'))
        return redirect('maintenance:low_stock_alerts')


class AdminDashboardView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = ADMIN_GROUPS
    template_name  = 'maintenance/admin_panel/dashboard.html'

    def get(self, request):
        total       = MaintenanceRequest.objects.count()
        pending     = MaintenanceRequest.objects.filter(status='pending').count()
        in_progress = MaintenanceRequest.objects.filter(status='in_progress').count()
        completed   = MaintenanceRequest.objects.filter(status='completed').count()
        cancelled   = MaintenanceRequest.objects.filter(status='cancelled').count()

        stats = {
            'total_requests':       total,
            'pending_requests':     pending,
            'in_progress_requests': in_progress,
            'completed_requests':   completed,
            'cancelled_requests':   cancelled,
        }

        unit_stats_qs = MaintenanceUnit.objects.annotate(
            req_count=Count('assigned_requests')
        ).order_by('-req_count')

        unit_stats = [
            {
                'name': u.name,
                'request_count': u.req_count
            }
            for u in unit_stats_qs
        ]

        avg_rating = ServiceRating.objects.aggregate(avg=Avg('rating'))['avg'] or 0

        completed_reqs = MaintenanceRequest.objects.filter(
            status='completed', completed_at__isnull=False
        )
        total_hours = 0
        comp_count = 0
        for r in completed_reqs:
            if r.completed_at and r.created_at:
                diff = (r.completed_at - r.created_at).total_seconds() / 3600.0
                total_hours += max(0, diff)
                comp_count += 1
        avg_hours = round(total_hours / comp_count, 1) if comp_count > 0 else 0.0

        total_parts_used = StockMovement.objects.filter(
            movement_type='out'
        ).aggregate(sum_qty=Sum('quantity'))['sum_qty'] or 0
        recent_requests = MaintenanceRequest.objects.select_related(
            'fault_category__unit', 'assigned_unit', 'assigned_technician', 'requester'
        ).order_by('-created_at')[:10]
        low_alerts  = LowStockAlert.objects.filter(is_resolved=False).count()
        unread      = Notification.objects.filter(
            recipient=request.user, is_read=False).count()

        return render(request, self.template_name, {
            'stats':            stats,
            'total':            total,
            'pending':          pending,
            'in_progress':      in_progress,
            'completed':        completed,
            'cancelled':        cancelled,
            'unit_stats':       unit_stats,
            'avg_rating':       round(avg_rating, 1),
            'avg_hours':        avg_hours,
            'total_parts_used': total_parts_used,
            'recent_requests':  recent_requests,
            'recent_reqs':      recent_requests,
            'low_alerts':       low_alerts,
            'unread_count':     unread,
        })


class AdminAllRequestsView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    allowed_groups      = ADMIN_GROUPS
    model               = MaintenanceRequest
    template_name       = 'maintenance/admin_panel/all_requests.html'
    context_object_name = 'requests'
    paginate_by         = 20

    def get_queryset(self):
        qs = MaintenanceRequest.objects.select_related(
            'fault_category__unit', 'assigned_unit',
            'assigned_technician', 'requester'
        )
        filter_form = RequestFilterForm(self.request.GET)
        if filter_form.is_valid():
            status = filter_form.cleaned_data.get('status')
            search = filter_form.cleaned_data.get('search')
            unit   = filter_form.cleaned_data.get('unit')
            priority = filter_form.cleaned_data.get('priority')
            if status:
                qs = qs.filter(status=status)
            if search:
                qs = qs.filter(
                    Q(request_number__icontains=search) |
                    Q(employee_name__icontains=search) |
                    Q(department__icontains=search) |
                    Q(general_dept__icontains=search)
                )
            if unit:
                qs = qs.filter(assigned_unit__code=unit)
            if priority:
                qs = qs.filter(priority=priority)
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter_form'] = RequestFilterForm(self.request.GET)
        ctx['units']       = MaintenanceUnit.objects.all()
        return ctx


class AdminPrintReportView(LoginRequiredMixin, GroupRequiredMixin, View):
    """عرض تقرير قابل للطباعة كـ PDF — صفحة مستقلة بترويسة وجدول منسق"""
    allowed_groups = ADMIN_GROUPS

    def get(self, request):
        qs = MaintenanceRequest.objects.select_related(
            'fault_category__unit', 'assigned_unit',
            'assigned_technician', 'requester'
        )
        # Apply same filters as AdminAllRequestsView
        status   = request.GET.get('status', '')
        search   = request.GET.get('q', '') or request.GET.get('search', '')
        unit     = request.GET.get('unit', '')
        priority = request.GET.get('priority', '')

        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(
                Q(request_number__icontains=search) |
                Q(employee_name__icontains=search) |
                Q(department__icontains=search) |
                Q(general_dept__icontains=search)
            )
        if unit:
            qs = qs.filter(assigned_unit__id=unit)
        if priority:
            qs = qs.filter(priority=priority)

        requests_qs = qs.order_by('-created_at')

        # Summary counts for the report header
        total       = requests_qs.count()
        pending     = requests_qs.filter(status='pending').count()
        in_progress = requests_qs.filter(status='in_progress').count()
        completed   = requests_qs.filter(status='completed').count()
        cancelled   = requests_qs.filter(status='cancelled').count()

        ctx = {
            'requests':    requests_qs,
            'total':       total,
            'pending':     pending,
            'in_progress': in_progress,
            'completed':   completed,
            'cancelled':   cancelled,
            'print_date':  timezone.now(),
            'printed_by':  request.user,
            # Active filters description
            'filter_status':   status,
            'filter_search':   search,
            'filter_priority': priority,
        }
        return render(request, 'maintenance/admin_panel/print_report.html', ctx)


class AdminAssignTechnicianView(LoginRequiredMixin, GroupRequiredMixin, View):
    allowed_groups = ADMIN_GROUPS

    def post(self, request, pk):
        req          = get_object_or_404(MaintenanceRequest, pk=pk)
        technician_id = request.POST.get('technician_id')
        if technician_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                tech = User.objects.get(pk=technician_id)
                req.assigned_technician = tech
                req.status = 'in_progress'
                req.save()
                messages.success(request, _(f'تم تعيين {tech} للطلب.'))
            except User.DoesNotExist:
                messages.error(request, _('الفني المحدد غير موجود.'))
        return redirect('maintenance:admin_request_detail', pk=pk)


class AdminRequestDetailView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    """تفاصيل طلب للمدير"""
    allowed_groups      = ADMIN_GROUPS
    model               = MaintenanceRequest
    template_name       = 'maintenance/admin_panel/request_detail.html'
    context_object_name = 'req'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        req = self.object
        ctx['spare_parts'] = req.spare_parts_used.select_related('spare_part').all()
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if req.assigned_unit:
            ctx['technicians'] = User.objects.filter(
                groups__name=req.assigned_unit.group_name
            ).order_by('first_name', 'last_name')
        else:
            ctx['technicians'] = User.objects.none()
        ctx['all_technical_technicians'] = TechnicalTechnician.objects.filter(is_active=True).order_by('name')
        ctx['admin_notes_form'] = AdminNotesForm(instance=req)
        return ctx

    def post(self, request, pk):
        req    = get_object_or_404(MaintenanceRequest, pk=pk)
        action = request.POST.get('action')

        if action == 'reject':
            rejection_reason = request.POST.get('rejection_reason', '').strip()
            req.status = 'rejected'
            req.rejection_reason = rejection_reason
            req.save()
            Notification.objects.create(
                recipient=req.requester,
                notification_type=Notification.TYPE_REQUEST_UPDATED,
                title=_('الاعتذار عن طلب الصيانة'),
                message=f'اعتذر مدير الصيانة عن تنفيذ الطلب {req.request_number}. السبب: {rejection_reason or "غير محدد"}',
                related_request=req
            )
            messages.warning(request, _(f'تم رفض/الاعتذار عن الطلب {req.request_number}.'))
            return redirect('maintenance:admin_request_detail', pk=pk)

        elif action == 'receive':
            req.status = 'received'
            req.save()
            messages.success(request, _('تمت تحديث حالة الطلب إلى (تم الاستلام).'))
            return redirect('maintenance:admin_request_detail', pk=pk)

        elif action == 'start':
            req.status = 'in_progress'
            tech_ids = request.POST.getlist('technical_technicians')
            if tech_ids:
                req.assigned_technical_technicians.set(tech_ids)
            req.save()
            messages.success(request, _('تمت تحديث حالة الطلب إلى (قيد التنفيذ).'))
            return redirect('maintenance:admin_request_detail', pk=pk)

        elif action == 'complete':
            req.status = 'completed'
            req.completed_at = timezone.now()
            req.save()
            messages.success(request, _('تم إغلاق الطلب وتحديد حالته كـ مكتمل.'))
            return redirect('maintenance:admin_request_detail', pk=pk)

        elif action == 'assign_technical_technicians':
            tech_ids = request.POST.getlist('technical_technicians')
            req.assigned_technical_technicians.set(tech_ids)
            req.save()
            messages.success(request, _('تم تحديث الفنيين التقنيين المكلفين.'))
            return redirect('maintenance:admin_request_detail', pk=pk)

        elif action == 'update_delay':
            delay_reason = request.POST.get('delay_reason', '').strip()
            req.delay_reason = delay_reason
            req.save()
            messages.success(request, _('تم حفظ سبب التأخير.'))
            return redirect('maintenance:admin_request_detail', pk=pk)

        elif action == 'cancel':
            if req.status not in ['completed', 'cancelled', 'rejected']:
                req.status = 'cancelled'
                req.save()
                messages.warning(request, _(f'تم إلغاء الطلب {req.request_number}.'))
            return redirect('maintenance:admin_request_detail', pk=pk)

        elif action == 'reopen':
            if req.status in ['cancelled', 'rejected']:
                req.status = 'pending'
                req.save()
                messages.success(request, _(f'تم إعادة فتح الطلب {req.request_number}.'))
            return redirect('maintenance:admin_request_detail', pk=pk)

        # Default: save admin notes form
        form = AdminNotesForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم حفظ ملاحظات المدير.'))
        return redirect('maintenance:admin_request_detail', pk=pk)


from django import forms as dj_forms
class AdminNotesForm(dj_forms.ModelForm):
    class Meta:
        model  = MaintenanceRequest
        fields = ['admin_notes', 'priority']
        widgets = {
            'admin_notes': dj_forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full', 'rows': 3
            }),
            'priority': dj_forms.Select(attrs={'class': 'select select-bordered w-full'}),
        }

@login_required
def get_fault_categories(request):
    unit_code  = request.GET.get('unit_code', '')
    categories = []
    if unit_code:
        is_admin = request.user.is_superuser or request.user.groups.filter(name='maintenance_admin').exists()
        unit = MaintenanceUnit.objects.filter(code=unit_code).first()
        if unit:
            if (unit.requires_safety_permit or unit.code == MaintenanceUnit.CODE_SAFETY) and not is_admin:
                return JsonResponse({'categories': []})

            qs = FaultCategory.objects.filter(
                unit=unit, is_active=True
            )
            if not is_admin:
                qs = qs.filter(requires_safety_permit=False)
            qs = qs.order_by('sub_category', 'order', 'name')
            categories = [
                {
                    'id':           c.id,
                    'name':         c.name,
                    'sub_category': c.sub_category,
                }
                for c in qs
            ]
    return JsonResponse({'categories': categories})


@login_required
def get_apartments(request):
    floor_id = request.GET.get('floor_id', '')
    apartments = []
    if floor_id:
        qs = Apartment.objects.filter(floor_id=floor_id).order_by('name')
        apartments = [{'id': a.id, 'name': a.name} for a in qs]
    return JsonResponse({'apartments': apartments})


class TechnicalTechnicianListView(LoginRequiredMixin, ListView):
    model               = TechnicalTechnician
    template_name       = 'maintenance/technical_technicians/list.html'
    context_object_name = 'techs'
    paginate_by         = 20

    def get_queryset(self):
        qs = TechnicalTechnician.objects.select_related('unit').all()
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(phone__icontains=search) | Q(specialty__icontains=search))
        unit_code = self.request.GET.get('unit', '')
        if unit_code:
            qs = qs.filter(unit__code=unit_code)
        return qs.order_by('-is_active', 'unit', 'name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['units'] = MaintenanceUnit.objects.all()
        ctx['unit_filter'] = self.request.GET.get('unit', '')
        return ctx

    def post(self, request):
        role = get_user_role(request.user)
        if role not in ['admin', 'technician'] and not request.user.is_superuser:
            messages.error(request, _('غير مصرح لك بإضافة أو تعديل الفنيين التقنيين.'))
            return redirect('maintenance:technical_technician_list')

        tech_id   = request.POST.get('tech_id')
        name      = request.POST.get('name', '').strip()
        phone     = request.POST.get('phone', '').strip()
        unit_id   = request.POST.get('unit_id')
        specialty = request.POST.get('specialty', '').strip()
        is_active = request.POST.get('is_active') == 'on' or request.POST.get('is_active') == 'true'

        if not name or not phone:
            messages.error(request, _('يرجى كتابة اسم الفني ورقم الهاتف بشكل صحيح.'))
            return redirect('maintenance:technical_technician_list')

        unit_obj = MaintenanceUnit.objects.filter(pk=unit_id).first() if unit_id else None

        if tech_id:
            tech = get_object_or_404(TechnicalTechnician, pk=tech_id)
            tech.name      = name
            tech.phone     = phone
            tech.unit      = unit_obj
            tech.specialty = specialty
            tech.is_active = is_active
            tech.save()
            messages.success(request, _(f'تم تحديث بيانات الفني التقني: {tech.name}'))
        else:
            tech = TechnicalTechnician.objects.create(
                name=name, phone=phone, unit=unit_obj, specialty=specialty, is_active=is_active
            )
            messages.success(request, _(f'تمت إضافة الفني التقني: {tech.name} بنجاح.'))

        return redirect('maintenance:technical_technician_list')


@login_required
def ajax_add_technical_technician(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        unit_id = request.POST.get('unit_id')
        specialty = request.POST.get('specialty', '').strip()

        unit_obj = MaintenanceUnit.objects.filter(pk=unit_id).first() if unit_id else None

        if name and phone:
            tech = TechnicalTechnician.objects.create(
                name=name, phone=phone, unit=unit_obj, specialty=specialty, is_active=True
            )
            unit_name = tech.unit.name if tech.unit else ''
            return JsonResponse({'status': 'ok', 'id': tech.id, 'name': tech.name, 'phone': tech.phone, 'unit': unit_name})
        return JsonResponse({'status': 'error', 'message': _('الاسم ورقم الهاتف مطلوبان')}, status=400)
    return JsonResponse({'status': 'error'}, status=405)


@login_required
def mark_notification_read(request, pk):
    if request.method == 'POST':
        notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)


@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('related_request').order_by('-created_at')[:30]
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'ok'})

    return render(request, 'maintenance/notifications.html', {
        'notifications': notifications
    })


# ─────────────────────────────────────────────
# فصول ووجهات تصاريح السلامة المهنية (Safety Permit)
# ─────────────────────────────────────────────
class SafetyPermitCreateUpdateView(LoginRequiredMixin, View):
    """تعبئة/تحديث استمارة تصريح السلامة والصحة المهنية (الفني / المسؤول)"""
    template_name = 'maintenance/safety/permit_form.html'

    def get(self, request, request_pk):
        req = get_object_or_404(MaintenanceRequest, pk=request_pk)
        permit = getattr(req, 'safety_permit', None)
        
        from maintenance.templatetags.maintenance_tags import user_display_name
        initial_data = {}
        if not permit:
            # اسم محرر الطلب (الموظف الذي أنشأ الطلب) وليس الفني الحالي
            requester_name = req.employee_name or (user_display_name(req.requester) if req.requester else '')
            initial_data = {
                'work_description': req.fault_description,
                'start_time': timezone.now().strftime('%Y-%m-%dT%H:%M'),
                'end_time': (timezone.now() + timezone.timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M'),
                'responsible_person_name': requester_name,
                'responsible_person_job': _('فني صيانة'),
            }
        form = SafetyPermitForm(instance=permit, initial=initial_data, unit=req.assigned_unit)
        return render(request, self.template_name, {
            'req': req,
            'permit': permit,
            'form': form,
        })

    def post(self, request, request_pk):
        req = get_object_or_404(MaintenanceRequest, pk=request_pk)
        permit = getattr(req, 'safety_permit', None)
        form = SafetyPermitForm(request.POST, instance=permit, unit=req.assigned_unit)

        if form.is_valid():
            permit_obj = form.save(commit=False)
            permit_obj.request = req
            permit_obj.responsible_person = request.user
            permit_obj.hazardous_activities = form.cleaned_data.get('hazardous_activities', [])
            permit_obj.site_preparations = form.cleaned_data.get('site_preparations', [])
            permit_obj.ppe_equipment = form.cleaned_data.get('ppe_equipment', [])
            permit_obj.status = 'pending_safety'
            permit_obj.save()
            form.save_m2m()

            req.status = 'pending_safety'
            req.save()

            from django.contrib.auth import get_user_model
            User = get_user_model()
            safety_users = User.objects.filter(groups__name='maintenance_safety')
            for u in safety_users:
                Notification.objects.create(
                    recipient=u,
                    notification_type=Notification.TYPE_REQUEST_UPDATED,
                    title=_('استمارة تصريح سلامة جديدة بانتظار الاعتماد'),
                    message=f'تم تعبئة استمارة تصريح السلامة للطلب {req.request_number}. يرجى المراجعة وتحديد مدة التصريح والاعتماد.',
                    related_request=req
                )

            messages.success(request, _('تم حفظ وتمرير فورمة تصريح السلامة إلى قسم السلامة الداخلية بنجاح.'))
            return redirect('maintenance:technician_request_detail', pk=req.pk)

        return render(request, self.template_name, {'req': req, 'permit': permit, 'form': form})



class SafetyPermitApproveView(LoginRequiredMixin, GroupRequiredMixin, View):
    """اعتماد وموافقة تصريح السلامة من قبل قسم السلامة الداخلية"""
    allowed_groups = ['maintenance_safety', 'maintenance_admin']
    template_name = 'maintenance/safety/permit_approve.html'

    def get(self, request, request_pk):
        req = get_object_or_404(MaintenanceRequest, pk=request_pk)
        permit = get_object_or_404(SafetyPermit, request=req)
        form = SafetyPermitApprovalForm(initial={
            'permit_duration': permit.permit_duration or '4 ساعات',
            'safety_notes': permit.safety_notes,
        })
        return render(request, self.template_name, {
            'req': req,
            'permit': permit,
            'form': form,
        })

    def post(self, request, request_pk):
        req = get_object_or_404(MaintenanceRequest, pk=request_pk)
        permit = get_object_or_404(SafetyPermit, request=req)
        form = SafetyPermitApprovalForm(request.POST)

        if form.is_valid():
            duration = form.cleaned_data['permit_duration']
            notes = form.cleaned_data['safety_notes']
            decision = form.cleaned_data['decision']

            permit.permit_duration = duration
            permit.safety_notes = notes
            permit.safety_officer = request.user

            if decision == 'approve':
                permit.status = 'approved'
                permit.approved_at = timezone.now()
                permit.save()

                messages.success(request, _(f'تمت الموافقة على تصريح السلامة للطلب {req.request_number} بنجاح.'))
                
                if req.assigned_technician:
                    Notification.objects.create(
                        recipient=req.assigned_technician,
                        notification_type=Notification.TYPE_REQUEST_UPDATED,
                        title=_('تم اعتماد تصريح السلامة — يمكن البدء بالعمل'),
                        message=f'وافق قسم السلامة على تصريح العمل للطلب {req.request_number} بمدة تصريح ({duration}). يمكنك الآن بدء العمل.',
                        related_request=req
                    )
            else:
                permit.status = 'rejected'
                permit.save()
                messages.warning(request, _(f'تم رفض تصريح السلامة للطلب {req.request_number}.'))

            return redirect('maintenance:safety_dashboard')

        return render(request, self.template_name, {'req': req, 'permit': permit, 'form': form})


class SafetyPermitCloseView(LoginRequiredMixin, GroupRequiredMixin, View):
    """إغلاق الطلب وتصريح السلامة نهائياً من قبل قسم السلامة الداخلية"""
    allowed_groups = ['maintenance_safety', 'maintenance_admin']

    def post(self, request, request_pk):
        req = get_object_or_404(MaintenanceRequest, pk=request_pk)
        permit = get_object_or_404(SafetyPermit, request=req)

        permit.status = 'closed'
        permit.closed_at = timezone.now()
        permit.save()

        req.status = 'completed'
        req.completed_at = timezone.now()
        req.save()

        messages.success(request, _(f'تم إغلاق تصريح السلامة والطلب {req.request_number} نهائياً.'))
        return redirect('maintenance:safety_dashboard')


class SafetyDashboardView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    """لوحة تحكم قسم السلامة الداخلية"""
    allowed_groups = ['maintenance_safety', 'maintenance_admin']
    template_name = 'maintenance/safety/dashboard.html'
    context_object_name = 'permits'
    paginate_by = 15

    def get_queryset(self):
        return SafetyPermit.objects.select_related(
            'request', 'request__assigned_technician', 'request__fault_category', 'responsible_person'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['pending_count'] = SafetyPermit.objects.filter(status='pending_safety').count()
        ctx['approved_count'] = SafetyPermit.objects.filter(status='approved').count()
        ctx['closed_count'] = SafetyPermit.objects.filter(status='closed').count()
        return ctx
