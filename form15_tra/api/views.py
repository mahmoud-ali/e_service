from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import os
from form15_tra.models import Market, CollectionForm, APILog, CollectorAssignment
from form15_tra.api.serializers import (
    MarketSerializer,
    CollectionFormSerializer,
    CancelCollectionSerializer,
    MarkPaidBulkSerializer,
    SetPendingPaymentInvoicesSerializer,
    MarkPaidReceiptsSerializer,
    UpdateEsaliServiceIdSerializer,
    CancelExpiredInvoicesSerializer,
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
        elif self.action == "collector_esali_config":
            permission_classes = [HasAPIKey]
        elif self.action == "update_esali_service_id":
            permission_classes = [HasAPIKey]
        elif self.action == "consume_pending_payment_check_now":
            permission_classes = [HasAPIKey]
        elif self.action == "cancel_expired":
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
        
        instance.transition_status(
            CollectionForm.Status.INVOICE_REQUESTED,
            action="confirm_collection",
            user=request.user,
            ip_address=request.META.get("REMOTE_ADDR"),
            request_data={"id": instance.id},
            response_data=self.get_serializer(instance).data,
            status_code=status.HTTP_200_OK,
            update_fields=["status"],
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

        instance.cancelled_by = request.user
        instance.cancellation_reason = serializer.validated_data["cancellation_reason"]
        instance.transition_status(
            CollectionForm.Status.CANCELLED,
            action="cancel_collection",
            user=request.user,
            ip_address=request.META.get("REMOTE_ADDR"),
            request_data=dict(request.data),
            response_data=CollectionFormSerializer(instance).data,
            status_code=status.HTTP_200_OK,
            update_fields=["cancelled_by", "cancellation_reason", "status"],
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
                updated = 0
                if ids:
                    # Rows are already locked via `eligible`; avoid another select_for_update()
                    # so our skip_locked fallback branch remains testable.
                    forms = list(CollectionForm.objects.filter(id__in=ids))
                    for f in forms:
                        if f.status != CollectionForm.Status.INVOICE_REQUESTED:
                            continue
                        f.status = CollectionForm.Status.INVOICE_QUEUED
                        updated += 1
                    if updated:
                        CollectionForm.objects.bulk_update(forms, ["status", "updated_at"])
                        APILog.objects.bulk_create(
                            [
                                APILog(
                                    action="queue_invoices",
                                    user=None,
                                    request_data={"id": f.id, "from": CollectionForm.Status.INVOICE_REQUESTED, "to": CollectionForm.Status.INVOICE_QUEUED},
                                    response_data=None,
                                    status_code=status.HTTP_200_OK,
                                    ip_address=ip_address,
                                    collection_form=f,
                                )
                                for f in forms
                                if f.status == CollectionForm.Status.INVOICE_QUEUED
                            ],
                            batch_size=500,
                        )

                results = list(
                    CollectionForm.objects.select_related("market")
                    .filter(id__in=ids)
                    .values(
                        "id",
                        "miner_name",
                        "phone",
                        "total_amount",
                        "market__market_name",
                        "collector__username",
                    )
                )
                for row in results:
                    row["market_name"] = row.pop("market__market_name")
                    row["collector_username"] = row.pop("collector__username")

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

    @action(detail=False, methods=["post"], url_path="collector-esali-config")
    def collector_esali_config(self, request: Any) -> Response:
        """
        POST /api/v1/collections/collector-esali-config/
        Fetch Esali credentials (encrypted password) for a given collector username.
        Secured by X-API-KEY (background service).
        """
        ip_address = request.META.get("REMOTE_ADDR")
        collector_username = str((request.data or {}).get("collector_username", "")).strip()
        if not collector_username:
            return Response({"error": "collector_username is required"}, status=status.HTTP_400_BAD_REQUEST)

        assignment = CollectorAssignment.objects.filter(user__username=collector_username, is_collector=True).first()

        if assignment is None:
            return Response(f'{{"error": "collector not found <{collector_username}>"}}', status=status.HTTP_404_NOT_FOUND)

        payload = {
            "collector_username": collector_username,
            "esali_username": assignment.esali_username,
            "esali_password_enc": assignment.esali_password_enc,
            "esali_service_id": assignment.esali_service_id,
        }

        APILog.objects.create(
            action="collector_esali_config",
            user=None,
            request_data={"collector_username": collector_username},
            response_data={"collector_username": collector_username},
            status_code=status.HTTP_200_OK,
            ip_address=ip_address,
            collection_form=None,
        )
        return Response(payload, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["post"],
        url_path="update-esali-service-id",
        serializer_class=UpdateEsaliServiceIdSerializer,
    )
    def update_esali_service_id(self, request: Any) -> Response:
        """
        POST /api/v1/collections/update-esali-service-id/
        Update Esali service_id for a collector (background service).
        Secured by X-API-KEY.
        """
        ip_address = request.META.get("REMOTE_ADDR")
        serializer = UpdateEsaliServiceIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        collector_username = str(serializer.validated_data["collector_username"]).strip()
        esali_service_id = str(serializer.validated_data["esali_service_id"]).strip()

        assignment = (
            CollectorAssignment.objects.select_related("user")
            .filter(user__username=collector_username, is_collector=True)
            .first()
        )
        if assignment is None:
            error_data = {"error": "collector not found"}
            APILog.objects.create(
                action="update_esali_service_id_failed",
                user=None,
                request_data={"collector_username": collector_username},
                response_data=error_data,
                status_code=status.HTTP_400_BAD_REQUEST,
                ip_address=ip_address,
                collection_form=None,
            )
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

        assignment.esali_service_id = esali_service_id
        assignment.save(update_fields=["esali_service_id"])

        payload = {"collector_username": collector_username, "esali_service_id": esali_service_id}
        APILog.objects.create(
            action="update_esali_service_id",
            user=None,
            request_data={"collector_username": collector_username},
            response_data={"collector_username": collector_username},
            status_code=status.HTTP_200_OK,
            ip_address=ip_address,
            collection_form=None,
        )
        return Response(payload, status=status.HTTP_200_OK)

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
                now = timezone.now()
                for form in eligible:
                    form.invoice_id = invoice_map.get(form.id)
                    form.invoice_generated_at = now
                    form.transition_status(
                        CollectionForm.Status.PENDING_PAYMENT,
                        action="set_pending_payment_bulk",
                        user=None,
                        ip_address=ip_address,
                        request_data={"id": form.id},
                        response_data=None,
                        status_code=status.HTTP_200_OK,
                        update_fields=["invoice_id", "invoice_generated_at", "status"],
                    )
                    updated += 1
                    # transition_status already wrote per-record log; keep only summary log below.

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
        receipt_map: dict[int, tuple[str, str]] = {
            item["id"]: (item["receipt_number"], item.get("rrn_number") or "")
            for item in receipts
        }
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
                    receipt_number, rrn_number = receipt_map.get(form.id, ("", ""))
                    form.receipt_number = receipt_number
                    form.rrn_number = rrn_number
                    form.transition_status(
                        CollectionForm.Status.PAID,
                        action="mark_paid_bulk",
                        user=None,
                        ip_address=ip_address,
                        request_data={"id": form.id},
                        response_data=None,
                        status_code=status.HTTP_200_OK,
                        update_fields=["receipt_number", "rrn_number", "status"],
                    )
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

    @action(detail=False, methods=["post"], url_path="consume-pending-payment-check-now")
    def consume_pending_payment_check_now(self, request: Any) -> Response:
        """
        POST /api/v1/collections/consume-pending-payment-check-now/
        Returns collection ids flagged for immediate Esali paid check and clears the flag (atomic).
        Secured by X-API-KEY (sync_e15 worker).
        """
        ip_address = request.META.get("REMOTE_ADDR")
        try:
            with transaction.atomic():
                base_qs = CollectionForm.objects.filter(
                    status=CollectionForm.Status.PENDING_PAYMENT,
                    pending_payment_check_now=True,
                ).order_by("id")
                try:
                    locked = base_qs.select_for_update(skip_locked=True)
                except Exception:
                    locked = base_qs.select_for_update()
                ids = list(locked.values_list("id", flat=True))
                if ids:
                    CollectionForm.objects.filter(id__in=ids).update(pending_payment_check_now=False)

            payload: dict[str, Any] = {"ids": ids}
            APILog.objects.create(
                action="consume_pending_payment_check_now",
                user=None,
                request_data={},
                response_data={"count": len(ids)},
                status_code=status.HTTP_200_OK,
                ip_address=ip_address,
                collection_form=None,
            )
            return Response(payload, status=status.HTTP_200_OK)
        except Exception as exc:
            error_data = {"error": str(exc)}
            APILog.objects.create(
                action="consume_pending_payment_check_now_failed",
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
        url_path="cancel-expired",
        serializer_class=CancelExpiredInvoicesSerializer,
    )
    def cancel_expired(self, request: Any) -> Response:
        """
        POST /api/v1/collections/cancel-expired/
        Bulk transition: * -> Cancelled for eligible, expired invoices (API key).
        Eligibility:
        - invoice_id present (non-empty)
        - invoice_generated_at <= now - N days (configurable; default 3)
        - status not in (Paid, Cancelled)
        """
        ip_address = request.META.get("REMOTE_ADDR")
        serializer = self.get_serializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)

        raw_days = str((os.getenv("INVOICE_CANCEL_AFTER_DAYS", "") or "")).strip()
        try:
            cancel_after_days = int(raw_days) if raw_days else 3
        except ValueError:
            cancel_after_days = 3
        cancel_after_days = max(1, cancel_after_days)

        ids = serializer.validated_data.get("ids") or []
        requested = len(ids)

        now = timezone.now()
        cutoff = now - timedelta(days=cancel_after_days)

        try:
            with transaction.atomic():
                qs = (
                    CollectionForm.objects.select_for_update()
                    .exclude(status__in=[CollectionForm.Status.PAID, CollectionForm.Status.CANCELLED])
                    .filter(invoice_generated_at__isnull=False, invoice_generated_at__lte=cutoff)
                    .filter(invoice_id__isnull=False)
                    .exclude(invoice_id="")
                )
                if ids:
                    qs = qs.filter(id__in=ids)

                forms = list(qs)
                old_by_id = {f.id: str(f.status) for f in forms}
                for f in forms:
                    f.status = CollectionForm.Status.CANCELLED
                    f.cancelled_by = None
                    f.cancellation_reason = f"Auto-cancelled after {cancel_after_days} days"
                if forms:
                    CollectionForm.objects.bulk_update(
                        forms, ["status", "cancelled_by", "cancellation_reason", "updated_at"]
                    )
                    APILog.objects.bulk_create(
                        [
                            APILog(
                                action="cancel_expired_bulk",
                                user=None,
                                request_data={
                                    "id": f.id,
                                    "from": old_by_id.get(f.id),
                                    "to": CollectionForm.Status.CANCELLED,
                                    "cancel_after_days": cancel_after_days,
                                },
                                response_data=None,
                                status_code=status.HTTP_200_OK,
                                ip_address=ip_address,
                                collection_form=f,
                            )
                            for f in forms
                        ],
                        batch_size=500,
                    )
                updated = len(forms)

            payload: dict[str, Any] = {
                "requested": requested,
                "updated": int(updated),
                "skipped": max(0, requested - int(updated)) if requested else None,
                "cancel_after_days": cancel_after_days,
            }

            APILog.objects.create(
                action="cancel_expired_bulk",
                user=None,
                request_data={"requested": requested},
                response_data={"updated": int(updated), "cancel_after_days": cancel_after_days},
                status_code=status.HTTP_200_OK,
                ip_address=ip_address,
                collection_form=None,
            )
            return Response(payload, status=status.HTTP_200_OK)
        except Exception as exc:
            error_data = {"error": str(exc)}
            APILog.objects.create(
                action="cancel_expired_bulk_failed",
                user=None,
                request_data={"requested": requested},
                response_data=error_data,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                ip_address=ip_address,
                collection_form=None,
            )
            return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

