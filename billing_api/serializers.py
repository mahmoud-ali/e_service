from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()

        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class InquiryRequestSerializer(serializers.Serializer):
    uniqueId = serializers.CharField(max_length=100)
    transactionId = serializers.CharField(max_length=100)

class InquiryResponseSerializer(serializers.Serializer):
    uniqueId = serializers.CharField(max_length=100)
    transactionId = serializers.CharField(max_length=100)
    amount = serializers.FloatField(required=False)
    minAmount = serializers.FloatField(required=False)
    maxAmount = serializers.FloatField(required=False)
    status = serializers.IntegerField()
    statusDescription = serializers.CharField(max_length=100)
    
class PaymentRequestSerializer(serializers.Serializer):
    rrn = serializers.CharField(max_length=100)
    transactionId = serializers.CharField(max_length=100)
    amount = serializers.FloatField()

class PaymentResponseSerializer(serializers.Serializer):
    transactionId = serializers.CharField(max_length=100)
    amount = serializers.FloatField(required=False)
    status = serializers.IntegerField()
    statusDescription = serializers.CharField(max_length=100)
    