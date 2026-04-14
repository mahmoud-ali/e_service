from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils import dateformat
from django.http import JsonResponse
from typing import Any

from django.db.models import Q, QuerySet
from form15_tra.models import CollectionForm, CollectorAssignment
from form15_tra.forms import CollectionFormModelForm


def collections_visible_to_user(user: Any) -> QuerySet[CollectionForm]:
    """
    Same row visibility as the mining dashboard (market + role rules).
    """
    if not hasattr(user, "assignment"):
        return CollectionForm.objects.none()

    qs = CollectionForm.objects.filter(market=user.assignment.market)

    if user.assignment.is_senior_collector:
        qs = qs.exclude(status=CollectionForm.Status.DRAFT)
    elif user.assignment.is_collector:
        # Collectors can see all non-draft rows in their market.
        qs = qs.exclude(status=CollectionForm.Status.DRAFT)
    else:
        # Observers (and any non-collector role): can see only records created by them (any status).
        qs = qs.filter(created_by=user)
    return qs


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
        qs = collections_visible_to_user(self.request.user)

        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(
                Q(receipt_number__startswith=query)
                | Q(invoice_id__startswith=query)
                | Q(phone__startswith=query)
            )

        return qs.order_by("-created_at")


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

        form.instance.status = CollectionForm.Status.DRAFT
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
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
            obj.created_by == self.request.user and
            obj.status == CollectionForm.Status.DRAFT
        )

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "تم تحديث المسودة بنجاح.")
        return super().form_valid(form)

class CollectionDetailView(LoginRequiredMixin, DetailView):
    """
    View details of a collection.
    """
    model = CollectionForm
    template_name = 'mining/collection_detail.html'

    def get_queryset(self) -> QuerySet[CollectionForm]:
        return collections_visible_to_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context["object"]
        if obj.status == CollectionForm.Status.PENDING_PAYMENT:
            CollectionForm.objects.filter(
                pk=obj.pk,
                status=CollectionForm.Status.PENDING_PAYMENT,
            ).update(pending_payment_check_now=True)
        return context


class CollectionStatusPollView(LoginRequiredMixin, View):
    """
    Minimal JSON for collection-detail auto-refresh (status + updated_at only).
    """

    def get(self, request: Any, pk: int) -> JsonResponse:
        row = get_object_or_404(
            collections_visible_to_user(request.user).values("status", "updated_at"),
            pk=pk,
        )
        updated = row["updated_at"]
        if updated is not None:
            updated_iso = dateformat.format(timezone.localtime(updated), "c")
        else:
            updated_iso = ""
        resp = JsonResponse({"status": row["status"], "updated_at": updated_iso})
        resp["Cache-Control"] = "private, max-age=0"
        return resp


class InvoicePrintView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    View for professional invoice printing.
    Only allows 'Pending Payment' invoices to be printed.
    """
    model = CollectionForm
    template_name = 'mining/invoice_print.html'

    def test_func(self) -> bool:
        obj = self.get_object()
        has_assignment = hasattr(self.request.user, 'assignment')
        can_print = has_assignment and (
            self.request.user.assignment.is_collector or
            self.request.user.assignment.is_senior_collector
        )
        return can_print and obj.status == CollectionForm.Status.PENDING_PAYMENT

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "ليس لديك صلاحية للطباعة")
        return redirect("collection-list")
    

class ReceiptPrintView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    View for receipt printing.
    Only allows 'Paid' receipts to be printed.
    """
    model = CollectionForm
    template_name = 'mining/receipt_print.html'

    def test_func(self) -> bool:
        obj = self.get_object()
        has_assignment = hasattr(self.request.user, 'assignment')
        can_print = has_assignment and (
            self.request.user.assignment.is_collector or
            self.request.user.assignment.is_senior_collector
        )
        return can_print and obj.status == CollectionForm.Status.PAID

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "ليس لديك صلاحية للطباعة")
        return redirect("collection-list")


class CollectionActionView(LoginRequiredMixin, View):
    """
    Handle actions (Confirm/Cancel).
    """

    def post(self, request, pk, action):
        collection = get_object_or_404(CollectionForm, pk=pk)
        
        if action == 'confirm':
            if not (hasattr(request.user, 'assignment') and (request.user.assignment.is_collector or request.user.assignment.is_observer)):
                messages.error(request, "ليس لديك صلاحية لتأكيد الإيصالات.")
                return redirect("collection-list")
                
            if collection.status != CollectionForm.Status.DRAFT:
                messages.error(request, "لا يمكن تأكيد هذا الإيصال.")
            else:
                if request.user.assignment.is_observer:
                    collection.transition_status(
                        CollectionForm.Status.COLLECTOR_CONFIRMATION,
                        action="html_confirm_collection_observer",
                        user=request.user,
                        ip_address=request.META.get("REMOTE_ADDR"),
                        request_data={"id": collection.id},
                        response_data=None,
                        status_code=200,
                        update_fields=["status"],
                    )
                    messages.success(request, "تم تأكيد الإيصال وإرساله لتأكيد المتحصل.")
                else:
                    collection.updated_by = request.user
                    update_fields = ["updated_by", "status"]
                    if collection.collector_id is None:
                        collection.collector = request.user
                        update_fields = ["collector", *update_fields]
                    collection.transition_status(
                        CollectionForm.Status.INVOICE_REQUESTED,
                        action="html_confirm_collection",
                        user=request.user,
                        ip_address=request.META.get("REMOTE_ADDR"),
                        request_data={"id": collection.id},
                        response_data=None,
                        status_code=200,
                        update_fields=update_fields,
                    )
                    messages.success(request, "تم تأكيد الإيصال وتم طلب الفاتورة.")
        
        elif action == 'approve':
             if not (hasattr(request.user, 'assignment') and request.user.assignment.is_collector):
                messages.error(request, "ليس لديك صلاحية للموافقة على الإيصالات.")
                return redirect("collection-list")

             if collection.status != CollectionForm.Status.COLLECTOR_CONFIRMATION:
                 messages.error(request, "لا يمكن تأكيد هذا الإيصال في هذه المرحلة.")
             else:
                 collection.updated_by = request.user
                 update_fields = ["updated_by", "status"]
                 if collection.collector_id is None:
                     collection.collector = request.user
                     update_fields = ["collector", *update_fields]
                 collection.transition_status(
                     CollectionForm.Status.INVOICE_REQUESTED,
                     action="html_approve_collection",
                     user=request.user,
                     ip_address=request.META.get("REMOTE_ADDR"),
                     request_data={"id": collection.id},
                     response_data=None,
                     status_code=200,
                     update_fields=update_fields,
                 )
                 messages.success(request, "تم تأكيد الإيصال وتم طلب الفاتورة.")

        elif action == 'cancel':
            if not (hasattr(request.user, 'assignment') and request.user.assignment.is_senior_collector):
                messages.error(request, "ليس لديك صلاحية لإلغاء الإيصالات.")
                return redirect("collection-list")

            if collection.status != CollectionForm.Status.PENDING_PAYMENT:
                messages.error(request, "لا يمكن إلغاء هذا الإيصال.")
            else:
                reason = request.POST.get('cancellation_reason')
                if not reason:
                    messages.error(request, "يجب ذكر سبب الإلغاء.")
                    return redirect('collection-detail', pk=pk)
                
                collection.cancelled_by = request.user
                collection.cancellation_reason = reason
                collection.updated_by = request.user
                collection.transition_status(
                    CollectionForm.Status.CANCELLED,
                    action="html_cancel_collection",
                    user=request.user,
                    ip_address=request.META.get("REMOTE_ADDR"),
                    request_data={"id": collection.id, "cancellation_reason": reason},
                    response_data=None,
                    status_code=200,
                    update_fields=["cancelled_by", "cancellation_reason", "updated_by", "status"],
                )
                messages.success(request, "تم إلغاء الإيصال.")
        
        return redirect('collection-list') 
