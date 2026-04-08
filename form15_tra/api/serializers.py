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
    collector = serializers.ReadOnlyField(source='collector.username')
    status = serializers.ReadOnlyField()
    receipt_number = serializers.ReadOnlyField()
    market = serializers.ReadOnlyField(source='market.market_name')

    class Meta:
        model = CollectionForm
        fields = [
            'id', 'receipt_number', 'miner_name', 'sacks_count', 
            'total_amount', 'status', 'collector', 'market',
            'created_at', 'updated_at'
        ]

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

        validated_data['collector'] = user
        validated_data['status'] = CollectionForm.Status.DRAFT
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


class MarkPaidReceiptsSerializer(serializers.Serializer):
    receipts = serializers.ListField(
        child=ReceiptRefSerializer(),
        allow_empty=False,
        required=True,
    )
