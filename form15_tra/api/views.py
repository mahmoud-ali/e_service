from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from form15_tra.models import Market, CollectionForm, APILog
from form15_tra.api.serializers import (
    MarketSerializer,
    CollectionFormSerializer,
    CancelCollectionSerializer,
    MarkPaidBulkSerializer,
    SetPendingPaymentInvoicesSerializer,
    MarkPaidReceiptsSerializer,
)
from form15_tra.api.permissions import IsCollector, IsSeniorCollector, HasAPIKey
from typing import Any


class MarketViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing markets.
    """
    queryset = Market.objects.all()
    serializer_class = MarketSerializer
    permission_classes = [permissions.IsAuthenticated]


class CollectionFormViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Collection Forms.
    """
    queryset = CollectionForm.objects.all()
    serializer_class = CollectionFormSerializer

    def get_permissions(self) -> list[Any]:
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'confirm']:
            permission_classes = [IsCollector]
        elif self.action == 'cancel':
            permission_classes = [IsSeniorCollector]
        elif self.action == 'queue_invoices':
            permission_classes = [HasAPIKey]
        elif self.action == 'mark_paid':
            permission_classes = [HasAPIKey]
        elif self.action == 'set_pending_payment':
            permission_classes = [HasAPIKey]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['put'])
    def confirm(self, request: Any, pk: Any = None) -> Response:
        """
        PUT /api/v1/collections/{id}/confirm/
        Transition: Draft -> Invoice Requested.
        """
        instance = self.get_object()
        if instance.status != CollectionForm.Status.DRAFT:
            error_data = {"error": f"Cannot confirm from status {instance.status}. Only Drafts can be confirmed."}
            APILog.objects.create(
                action="confirm_collection_failed",
                user=request.user,
                request_data={"id": instance.id},
                response_data=error_data,
                status_code=status.HTTP_400_BAD_REQUEST,
                ip_address=request.META.get('REMOTE_ADDR'),
                collection_form=instance
            )
            return Response(
                error_data,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance.status = CollectionForm.Status.INVOICE_REQUESTED
        instance.save()
        
        # Log action
        APILog.objects.create(
            action="confirm_collection",
            user=request.user,
            request_data={"id": instance.id},
            response_data=self.get_serializer(instance).data,
            status_code=status.HTTP_200_OK,
            ip_address=request.META.get('REMOTE_ADDR'),
            collection_form=instance
        )
        
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=['post'], serializer_class=CancelCollectionSerializer)
    def cancel(self, request: Any, pk: Any = None) -> Response:
        """
        POST /api/v1/collections/{id}/cancel/
        Transition: Pending Payment -> Cancelled.
        Requires cancellation_reason.
        """
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if instance.status != CollectionForm.Status.PENDING_PAYMENT:
            error_data = {"error": f"Cannot cancel from status {instance.status}. Only Pending Payments can be cancelled."}
            APILog.objects.create(
                action="cancel_collection_failed",
                user=request.user,
                request_data=request.data,
                response_data=error_data,
                status_code=status.HTTP_400_BAD_REQUEST,
                ip_address=request.META.get('REMOTE_ADDR'),
                collection_form=instance
            )
            return Response(
                error_data,
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.status = CollectionForm.Status.CANCELLED
        instance.cancelled_by = request.user
        instance.cancellation_reason = serializer.validated_data['cancellation_reason']
        instance.save()

        # Log action
        APILog.objects.create(
            action="cancel_collection",
            user=request.user,
            request_data=request.data,
            response_data=CollectionFormSerializer(instance).data,
            status_code=status.HTTP_200_OK,
            ip_address=request.META.get('REMOTE_ADDR'),
            collection_form=instance
        )

        return Response(CollectionFormSerializer(instance).data)

    @action(detail=False, methods=["post"], url_path="queue-invoices")
    def queue_invoices(self, request: Any) -> Response:
        """
        POST /api/v1/collections/queue-invoices/
        Batched transition: Invoice Requested -> Invoice Queued.
        Secured by X-API-KEY (background service).
        """
        ip_address = request.META.get("REMOTE_ADDR")
        default_limit = 50
        max_limit = 500
        raw_limit = request.query_params.get("limit", None)
        try:
            limit = int(raw_limit) if raw_limit is not None else default_limit
        except (TypeError, ValueError):
            limit = default_limit
        limit = max(1, min(max_limit, limit))

        try:
            with transaction.atomic():
                base_qs = (
                    CollectionForm.objects.filter(status=CollectionForm.Status.INVOICE_REQUESTED)
                    .order_by("created_at", "id")
                )

                # Prefer skip_locked to avoid multiple workers picking same rows.
                try:
                    eligible = base_qs.select_for_update(skip_locked=True)
                except Exception:
                    eligible = base_qs.select_for_update()

                ids = list(eligible.values_list("id", flat=True)[:limit])

                if ids:
                    updated = CollectionForm.objects.filter(id__in=ids).update(
                        status=CollectionForm.Status.INVOICE_QUEUED
                    )
                else:
                    updated = 0

                results = list(
                    CollectionForm.objects.select_related("market")
                    .filter(id__in=ids)
                    .values("id", "miner_name", "total_amount", "market__market_name")
                )
                for row in results:
                    row["market_name"] = row.pop("market__market_name")

            payload = {
                "updated": updated,
                "limit": limit,
                "returned": len(results),
                "results": results,
            }

            APILog.objects.create(
                action="queue_invoices",
                user=None,
                request_data={},
                response_data={
                    "updated": updated,
                    "limit": limit,
                    "returned": len(results),
                },
                status_code=status.HTTP_200_OK,
                ip_address=ip_address,
                collection_form=None,
            )

            return Response(payload, status=status.HTTP_200_OK)
        except Exception as exc:
            error_data = {"error": str(exc)}
            APILog.objects.create(
                action="queue_invoices_failed",
                user=None,
                request_data={},
                response_data=error_data,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                ip_address=ip_address,
                collection_form=None,
            )
            return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(
        detail=False,
        methods=["post"],
        url_path="set-pending-payment",
        serializer_class=SetPendingPaymentInvoicesSerializer,
    )
    def set_pending_payment(self, request: Any) -> Response:
        """
        POST /api/v1/collections/set-pending-payment/
        Bulk transition: Invoice Queued -> Pending Payment for provided invoices.
        Secured by X-API-KEY (background service).
        """
        ip_address = request.META.get("REMOTE_ADDR")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invoices: list[dict[str, Any]] = serializer.validated_data["invoices"]
        invoice_map: dict[int, str] = {item["id"]: item["invoice_id"] for item in invoices}
        ids = list(invoice_map.keys())
        requested = len(ids)

        try:
            with transaction.atomic():
                eligible = (
                    CollectionForm.objects.select_for_update()
                    .filter(
                    id__in=ids,
                    status=CollectionForm.Status.INVOICE_QUEUED,
                )
                )
                updated = 0
                for form in eligible:
                    form.invoice_id = invoice_map.get(form.id)
                    form.status = CollectionForm.Status.PENDING_PAYMENT
                    form.save(update_fields=["invoice_id", "status"])
                    updated += 1

            payload = {"requested": requested, "updated": updated, "skipped": requested - updated}

            APILog.objects.create(
                action="set_pending_payment_bulk",
                user=None,
                request_data={"invoices_count": requested},
                response_data=payload,
                status_code=status.HTTP_200_OK,
                ip_address=ip_address,
                collection_form=None,
            )

            return Response(payload, status=status.HTTP_200_OK)
        except Exception as exc:
            error_data = {"error": str(exc)}
            APILog.objects.create(
                action="set_pending_payment_bulk_failed",
                user=None,
                request_data={"invoices_count": requested},
                response_data=error_data,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                ip_address=ip_address,
                collection_form=None,
            )
            return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(
        detail=False,
        methods=["post"],
        url_path="mark-paid",
        serializer_class=MarkPaidReceiptsSerializer,
    )
    def mark_paid(self, request: Any) -> Response:
        """
        POST /api/v1/collections/mark-paid/
        Bulk transition: Pending Payment -> Paid for provided receipts.
        Secured by X-API-KEY (background service).
        """
        ip_address = request.META.get("REMOTE_ADDR")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receipts: list[dict[str, Any]] = serializer.validated_data["receipts"]
        receipt_map: dict[int, str] = {item["id"]: item["receipt_number"] for item in receipts}
        ids = list(receipt_map.keys())
        requested = len(ids)

        try:
            with transaction.atomic():
                eligible = (
                    CollectionForm.objects.select_for_update()
                    .filter(
                    id__in=ids,
                    status=CollectionForm.Status.PENDING_PAYMENT,
                )
                )
                updated = 0
                for form in eligible:
                    form.receipt_number = receipt_map.get(form.id, "")
                    form.status = CollectionForm.Status.PAID
                    form.save(update_fields=["receipt_number", "status"])
                    updated += 1

            payload = {"requested": requested, "updated": updated, "skipped": requested - updated}

            APILog.objects.create(
                action="mark_paid_bulk",
                user=None,
                request_data={"receipts_count": requested},
                response_data=payload,
                status_code=status.HTTP_200_OK,
                ip_address=ip_address,
                collection_form=None,
            )

            return Response(payload, status=status.HTTP_200_OK)
        except Exception as exc:
            error_data = {"error": str(exc)}
            APILog.objects.create(
                action="mark_paid_bulk_failed",
                user=None,
                request_data={"receipts_count": requested},
                response_data=error_data,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                ip_address=ip_address,
                collection_form=None,
            )
            return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


