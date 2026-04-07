from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from typing import Any

from django.db.models import Q
from form15_tra.models import CollectionForm, CollectorAssignment
from form15_tra.forms import CollectionFormModelForm


class DashboardView(LoginRequiredMixin, ListView):
    """
    Lists collections.
    """
    model = CollectionForm
    template_name = 'mining/dashboard.html'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
             
        return context

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.filter(market=self.request.user.assignment.market)

        if self.request.user.assignment.is_senior_collector:
            qs = qs.exclude(status=CollectionForm.Status.DRAFT)
        elif self.request.user.assignment.is_collector:
            # Collectors see their own drafts + receipts awaiting their confirmation
            qs = qs.filter(
                Q(collector=self.request.user) | 
                Q(status=CollectionForm.Status.COLLECTOR_CONFIRMATION)
            )
        else:
            # Observers (and others) see only their own
            qs = qs.filter(collector=self.request.user)
        
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(
                Q(receipt_number=query) |
                Q(miner_name__icontains=query)
            )

        return qs


class CollectionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Create a new draft collection.
    """
    model = CollectionForm
    form_class = CollectionFormModelForm
    template_name = 'mining/collection_form.html'

    def get_success_url(self):
        return reverse('collection-detail', kwargs={'pk': self.object.pk})

    def test_func(self) -> bool:
        return hasattr(self.request.user, 'assignment') and (
            self.request.user.assignment.is_collector or 
            self.request.user.assignment.is_observer
        )

    def form_valid(self, form):
        try:
            assignment = CollectorAssignment.objects.get(user=self.request.user)
            form.instance.market = assignment.market
        except CollectorAssignment.DoesNotExist:
            form.add_error(None, "عفواً، أنت غير مسجل في أي سوق. الرجاء مراجعة الإدارة.")
            return self.form_invalid(form)

        form.instance.collector = self.request.user
        form.instance.status = CollectionForm.Status.DRAFT
        messages.success(self.request, "تم إنشاء المسودة بنجاح.")
        return super().form_valid(form)

class CollectionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Edit an existing draft collection.
    """
    model = CollectionForm
    form_class = CollectionFormModelForm
    template_name = 'mining/collection_form.html'

    def get_success_url(self):
        return reverse('collection-detail', kwargs={'pk': self.object.pk})

    def test_func(self) -> bool:
        obj = self.get_object()
        has_assignment = hasattr(self.request.user, 'assignment')
        is_authorized = has_assignment and (
            self.request.user.assignment.is_collector or 
            self.request.user.assignment.is_observer
        )
        return (
            is_authorized and
            obj.collector == self.request.user and 
            obj.status == CollectionForm.Status.DRAFT
        )

    def form_valid(self, form):
        messages.success(self.request, "تم تحديث المسودة بنجاح.")
        return super().form_valid(form)

class CollectionDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a collection.
    """
    model = CollectionForm
    template_name = 'mining/collection_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
                
        return context

class InvoicePrintView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    View for professional invoice printing.
    Only allows 'Paid' invoices to be printed.
    """
    model = CollectionForm
    template_name = 'mining/invoice_print.html'

    def test_func(self) -> bool:
        obj = self.get_object()
        return obj.status == CollectionForm.Status.PAID

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "يمكن طباعة الإيصالات المدفوعة فقط")
        return redirect('collection-detail', pk=self.get_object().pk)
    

class CollectionActionView(LoginRequiredMixin, View):
    """
    Handle actions (Confirm/Cancel).
    """

    def post(self, request, pk, action):
        collection = get_object_or_404(CollectionForm, pk=pk)
        
        if action == 'confirm':
            if not (hasattr(request.user, 'assignment') and (request.user.assignment.is_collector or request.user.assignment.is_observer)):
                messages.error(request, "ليس لديك صلاحية لتأكيد الإيصالات.")
                return redirect('collection-detail', pk=pk)
                
            if collection.status != CollectionForm.Status.DRAFT:
                messages.error(request, "لا يمكن تأكيد هذا الإيصال.")
            else:
                if request.user.assignment.is_observer:
                    collection.status = CollectionForm.Status.COLLECTOR_CONFIRMATION
                    messages.success(request, "تم تأكيد الإيصال وإرساله لتأكيد المتحصل.")
                else:
                    collection.status = CollectionForm.Status.INVOICE_REQUESTED
                    messages.success(request, "تم تأكيد الإيصال وتم طلب الفاتورة.")
                collection.save()
        
        elif action == 'approve':
             if not (hasattr(request.user, 'assignment') and request.user.assignment.is_collector):
                messages.error(request, "ليس لديك صلاحية للموافقة على الإيصالات.")
                return redirect('collection-detail', pk=pk)

             if collection.status != CollectionForm.Status.COLLECTOR_CONFIRMATION:
                 messages.error(request, "لا يمكن تأكيد هذا الإيصال في هذه المرحلة.")
             else:
                 collection.status = CollectionForm.Status.INVOICE_REQUESTED
                 collection.save()
                 messages.success(request, "تم تأكيد الإيصال وتم طلب الفاتورة.")

        elif action == 'cancel':
            if not (hasattr(request.user, 'assignment') and request.user.assignment.is_senior_collector):
                messages.error(request, "ليس لديك صلاحية لإلغاء الإيصالات.")
                return redirect('collection-detail', pk=pk)

            if collection.status != CollectionForm.Status.PENDING_PAYMENT:
                messages.error(request, "لا يمكن إلغاء هذا الإيصال.")
            else:
                reason = request.POST.get('cancellation_reason')
                if not reason:
                    messages.error(request, "يجب ذكر سبب الإلغاء.")
                    return redirect('collection-detail', pk=pk)
                
                collection.status = CollectionForm.Status.CANCELLED
                collection.cancelled_by = request.user
                collection.cancellation_reason = reason
                collection.save()
                messages.success(request, "تم إلغاء الإيصال.")
        
        return redirect('collection-list') 
