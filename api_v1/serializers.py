from rest_framework import serializers
from gold_travel.models import AppMoveGold, AppMoveGoldDetails
from production_control.models import GoldProductionForm, GoldProductionFormAlloy, GoldShippingForm, GoldShippingFormAlloy

########### Gold travel(ترحيل بغرض الصادر) ##############
class OwnerNameField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name
    
class CompanyNameField(serializers.RelatedField):
    def to_representation(self, value):
        return value.name_ar

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
    
########### Gold production(انتاج الشركات) ##############
class GoldProductionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldProductionForm

        fields = ['id', ]

class GoldProductionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldProductionFormAlloy

        fields = ['alloy_serial_no','alloy_weight','alloy_added_gold'] #'alloy_note',

class GoldProductionMasterSerializer(serializers.ModelSerializer):
    company = CompanyNameField(read_only=True)
    
    # alloy_list = serializers.JSONField()
    alloy_list = GoldProductionDetailSerializer(source='goldproductionformalloy_set', many=True)
    class Meta:
        model = GoldProductionForm

        fields = ['id','form_no','date','company','alloy_jaf','alloy_khabath','alloy_remaind','alloy_weight_expected','alloy_list']
    
########### Gold shipping(ترحيل ذهب شركات) ##############
class GoldShippingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldShippingForm

        fields = ['id', ]

class GoldShippingDetailSerializer(serializers.ModelSerializer):
    alloy_serial_no = serializers.CharField(source='alloy_serial_no.alloy_serial_no', read_only=True)
    alloy_weight = serializers.CharField(source='alloy_serial_no.alloy_weight', read_only=True)
    alloy_added_gold = serializers.CharField(source='alloy_serial_no.alloy_added_gold', read_only=True)
    class Meta:
        model = GoldShippingFormAlloy

        fields = ['alloy_serial_no','alloy_weight','alloy_added_gold'] 

class GoldShippingMasterSerializer(serializers.ModelSerializer):
    company = CompanyNameField(read_only=True)
    
    # alloy_list = serializers.JSONField()
    alloy_list = GoldShippingDetailSerializer(source='goldshippingformalloy_set', many=True)
    class Meta:
        model = GoldShippingForm

        fields = ['id','form_no','date','company','alloy_list']
