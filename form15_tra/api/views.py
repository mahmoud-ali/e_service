from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from form15_tra.models import Market, CollectionForm, APILog
from form15_tra.api.serializers import (
    MarketSerializer, CollectionFormSerializer, CancelCollectionSerializer
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
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['put'])
    def confirm(self, request: Any, pk: Any = None) -> Response:
        """
        PUT /api/v1/collections/{id}/confirm/
        Transition: Draft -> Pending Payment.
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
        
        instance.status = CollectionForm.Status.PENDING_PAYMENT
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


class BankCallbackWebhook(APIView):
    """
    POST /api/v1/webhooks/bank-callback/
    Unauthenticated (uses API Key/IP validation).
    Updates status to Paid upon bank confirmation.
    """
    permission_classes = [HasAPIKey]

    def get(self, request: Any, format: Any = None) -> Response:
        """
        GET /api/v1/webhooks/bank-callback/?receipt_number=XXXXXXXXXX
        Retrieves the total_amount for a given receipt_number.
        """
        receipt_number = request.query_params.get('receipt_number')
        if not receipt_number:
            return Response({"error": "receipt_number query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        form = get_object_or_404(CollectionForm, receipt_number=receipt_number)
        return Response({"name": form.miner_name, "total_amount": form.total_amount, "receipt_number": form.receipt_number}, status=status.HTTP_200_OK)

    def post(self, request: Any, format: Any = None) -> Response:
        receipt_number = request.data.get('receipt_number','').strip()
        payment_status = request.data.get('payment_status','').strip().upper()
        ref_number = request.data.get('ref_number','').strip()

        if payment_status != 'SUCCESS':
            error_data = {"error": f"Payment status is not SUCCESS"}
            APILog.objects.create(
                action="bank_callback_failed",
                user=None,
                request_data=request.data,
                response_data=error_data,
                status_code=status.HTTP_400_BAD_REQUEST,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return Response(
                error_data,
                status=status.HTTP_400_BAD_REQUEST
            )

        if not receipt_number:
            error_data = {"error": "Invalid notification"}
            APILog.objects.create(
                action="bank_callback_failed",
                user=None,
                request_data=request.data,
                response_data=error_data,
                status_code=status.HTTP_400_BAD_REQUEST,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

        if not ref_number:
            error_data = {"error": "Invalid referance number"}
            APILog.objects.create(
                action="bank_callback_failed",
                user=None,
                request_data=request.data,
                response_data=error_data,
                status_code=status.HTTP_400_BAD_REQUEST,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

        form = get_object_or_404(CollectionForm, receipt_number=receipt_number)
        
        if form.status != CollectionForm.Status.PENDING_PAYMENT:
            error_data = {"error": f"Form is in {form.status} status, cannot mark as Paid."}
            APILog.objects.create(
                action="bank_callback_failed",
                user=None,
                request_data=request.data,
                response_data=error_data,
                status_code=status.HTTP_400_BAD_REQUEST,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return Response(
                error_data,
                status=status.HTTP_400_BAD_REQUEST
            )

        form.status = CollectionForm.Status.PAID
        form.save()

        # Log action
        APILog.objects.create(
            action="bank_callback_success",
            user=None,  # Webhook is typically unauthenticated or uses API Key
            request_data=request.data,
            response_data={"status": "Payment recorded successfully"},
            status_code=status.HTTP_200_OK,
            ip_address=request.META.get('REMOTE_ADDR'),
            collection_form=form
        )

        return Response({"status": "Payment recorded successfully"}, status=status.HTTP_200_OK)
