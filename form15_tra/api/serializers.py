from rest_framework import serializers
from form15_tra.models import Market, CollectionForm, CollectorAssignment
from typing import Any


class MarketSerializer(serializers.ModelSerializer):
    """
    Serializer for Market model.
    """
    class Meta:
        model = Market
        fields = ['id', 'market_name', 'location']


class CollectionFormSerializer(serializers.ModelSerializer):
    """
    Serializer for CollectionForm model.
    Handles creation and basic updates.
    """
    collector = serializers.SerializerMethodField()
    status = serializers.ReadOnlyField()
    receipt_number = serializers.ReadOnlyField()
    market = serializers.ReadOnlyField(source='market.market_name')

    class Meta:
        model = CollectionForm
        fields = [
            'id', 'receipt_number', 'miner_name', 'phone', 'arrival_source', 'vehicle_plate', 'sacks_count',
            'total_amount', 'status', 'collector', 'market',
            'created_at', 'updated_at'
        ]

    def get_collector(self, obj: CollectionForm) -> str | None:
        if obj.collector_id is None:
            return None
        return getattr(obj.collector, "username", None)

    def create(self, validated_data: dict[str, Any]) -> CollectionForm:
        """
        Assign the current user as the collector and their market upon creation.
        """
        user = self.context['request'].user
        try:
            assignment = CollectorAssignment.objects.get(user=user)
            validated_data['market'] = assignment.market
        except CollectorAssignment.DoesNotExist:
            raise serializers.ValidationError({"error": "You are not assigned to any market."})

        validated_data['status'] = CollectionForm.Status.DRAFT
        validated_data["created_by"] = user
        validated_data["updated_by"] = user
        return super().create(validated_data)


class CancelCollectionSerializer(serializers.Serializer):
    """
    Serializer for the cancellation action.
    """
    cancellation_reason = serializers.CharField(required=True, min_length=5)


class MarkPaidBulkSerializer(serializers.Serializer):
    """
    Request payload serializer for bulk mark-paid action.
    """
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        required=True,
    )


class InvoiceRefSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    invoice_id = serializers.CharField(min_length=1, max_length=64)


class SetPendingPaymentInvoicesSerializer(serializers.Serializer):
    invoices = serializers.ListField(
        child=InvoiceRefSerializer(),
        allow_empty=False,
        required=True,
    )


class ReceiptRefSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    receipt_number = serializers.CharField(min_length=1, max_length=64)
    rrn_number = serializers.CharField(min_length=1, max_length=64, required=False, allow_blank=True)


class MarkPaidReceiptsSerializer(serializers.Serializer):
    receipts = serializers.ListField(
        child=ReceiptRefSerializer(),
        allow_empty=False,
        required=True,
    )


class UpdateEsaliServiceIdSerializer(serializers.Serializer):
    collector_username = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)
    esali_service_id = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)


class CancelExpiredInvoicesSerializer(serializers.Serializer):
    """
    Optional list of collection ids for bulk cancel-expired.
    If omitted or empty, server may cancel all expired eligible rows.
    """
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
    )
