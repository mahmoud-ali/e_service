from rest_framework import serializers
from gold_travel.models import AppMoveGold, AppMoveGoldDetails


class OwnerNameField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name

class GoldTravelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppMoveGold

        fields = ['id', ]

class GoldTravelDetailSerializer(serializers.ModelSerializer):
    alloy_shape = serializers.CharField(source='get_alloy_shape_display', read_only=True)

    class Meta:
        model = AppMoveGoldDetails

        fields = ['alloy_id','alloy_weight_in_gram','alloy_shape'] #'alloy_note',

class GoldTravelMasterSerializer(serializers.ModelSerializer):
    # alloy_list = GoldTravelDetailSerializer(many=True, read_only=True)
    repr_identity_type = serializers.CharField(source='get_repr_identity_type_display', read_only=True)
    destination = serializers.CharField(source='get_destination_display', read_only=True)
    company_name = OwnerNameField(source='owner_name_lst', read_only=True)
    company_address = serializers.CharField(source='owner_address', read_only=True)

    
    alloy_list = serializers.JSONField()

    class Meta:
        model = AppMoveGold

        fields = ['id','code','date','destination','company_name','company_address','repr_name','repr_address','repr_phone','repr_identity_type','repr_identity','repr_identity_issue_date','alloy_list']
    