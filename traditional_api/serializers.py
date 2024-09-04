from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from rest_framework import serializers

class UserRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100)

class UserResponseSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100)
    name = serializers.CharField(required=False,max_length=100)
    state = serializers.CharField(required=False,max_length=100)
    soag = serializers.CharField(required=False,max_length=100)
    status = serializers.IntegerField() #0=ok, 1=invalid data
    statusDescription = serializers.CharField(max_length=100)

class InvoiceRequestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    quantity_in_shoal = serializers.IntegerField()
    amount = serializers.FloatField()

class InvoiceResponseSerializer(serializers.Serializer):
    invoiceId = serializers.IntegerField(required=False)
    status = serializers.IntegerField() #0=ok, 1=invalid data
    statusDescription = serializers.CharField(max_length=100)
