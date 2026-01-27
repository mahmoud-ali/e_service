from datetime import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound

from auditlog.signals import accessed

from gold_travel.models import AppMoveGold, AppMoveGoldDetails
from production_control.models import GoldProductionForm, GoldShippingForm

from  .serializers import GoldProductionListSerializer, GoldProductionMasterSerializer,GoldProductionDetailSerializer, GoldShippingListSerializer, GoldShippingMasterSerializer,GoldShippingDetailSerializer, GoldTravelListSerializer, GoldTravelMasterSerializer, GoldTravelDetailSerializer

class IsInGroup(permissions.BasePermission):
    """
    Allows access only to users in a specific group.
    """

    def has_permission(self, request, view):
        required_groups = getattr(view, 'required_groups', [])
        return request.user and request.user.is_authenticated and (
            request.user.groups.filter(name__in=required_groups).exists()
        )
    
########### Gold travel(ترحيل بغرض الصادر) ##############
class GoldTravelListView(generics.ListAPIView):
    queryset = AppMoveGold.objects.filter(form_type=AppMoveGold.FORM_TYPE_GOLD_EXPORT)
    serializer_class = GoldTravelListSerializer
    permission_classes = [permissions.IsAuthenticated, IsInGroup,]

    required_groups = ['baldna_gold_travel']

    def list(self, request,date):
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponse("Invalid date format. Use YYYY-MM-DD.")

        queryset = self.get_queryset().filter(date=date_obj,state__in=[AppMoveGold.STATE_SMRC,AppMoveGold.STATE_SSMO])
        serializer = self.serializer_class(queryset, many=True)

        result = [item['id'] for item in serializer.data]

        return Response({
            'app_list': result
        })

class GoldTravelDetailView(generics.RetrieveAPIView):
    queryset = AppMoveGold.objects.filter(form_type=AppMoveGold.FORM_TYPE_GOLD_EXPORT)
    serializer_class = GoldTravelMasterSerializer
    permission_classes = [permissions.IsAuthenticated, IsInGroup,]

    required_groups = ['baldna_gold_travel']

    def retrieve(self, request,pk):
        queryset = self.get_queryset() 

        try:
            obj = get_object_or_404(queryset, pk=pk)
        except Http404:
            raise NotFound(detail=f"No request found with request_number: {pk}.")

        obj.alloy_list = GoldTravelDetailSerializer(instance=obj.appmovegolddetails_set, many=True).data

        serializer = self.serializer_class(instance=obj)

        result = serializer.data

        # Log access
        accessed.send(obj.__class__, instance=obj)

        return Response(result)

########### Gold production(انتاج الشركات) ##############
class GoldProductionListView(generics.ListAPIView):
    queryset = GoldProductionForm.objects.filter(state=GoldProductionForm.STATE_APPROVED)
    serializer_class = GoldProductionListSerializer
    permission_classes = [permissions.IsAuthenticated, IsInGroup,]

    required_groups = ['baldna_gold_travel']

    def list(self, request,date):
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponse("Invalid date format. Use YYYY-MM-DD.")
        
        queryset = self.get_queryset().filter(date=date_obj)

        serializer = self.serializer_class(queryset, many=True)

        result = [item['id'] for item in serializer.data]

        return Response({
            "app_list": result
        })

class GoldProductionDetailView(generics.RetrieveAPIView):
    queryset = GoldProductionForm.objects.filter(state=GoldProductionForm.STATE_APPROVED)
    serializer_class = GoldProductionMasterSerializer
    permission_classes = [permissions.IsAuthenticated, IsInGroup,]

    required_groups = ['baldna_gold_travel']

    def retrieve(self, request,pk):
        queryset = self.get_queryset() 

        try:
            obj = get_object_or_404(queryset, pk=pk)
        except Http404:
            raise NotFound(detail=f"No request found with request_number: {pk}.")

        serializer = self.serializer_class(instance=obj)

        result = serializer.data

        # Log access
        accessed.send(obj.__class__, instance=obj)

        return Response(result)

########### Gold shipping(ترحيل ذهب الشركات) ##############
class GoldShippingListView(generics.ListAPIView):
    queryset = GoldShippingForm.objects.filter(state=GoldShippingForm.STATE_APPROVED)
    serializer_class = GoldShippingListSerializer
    permission_classes = [permissions.IsAuthenticated, IsInGroup,]

    required_groups = ['baldna_gold_travel']

    def list(self, request,date):
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponse("Invalid date format. Use YYYY-MM-DD.")
        
        queryset = self.get_queryset().filter(date=date_obj)

        serializer = self.serializer_class(queryset, many=True)

        result = [item['id'] for item in serializer.data]

        return Response({
            "app_list": result
        })

class GoldShippingDetailView(generics.RetrieveAPIView):
    queryset = GoldShippingForm.objects.filter(state=GoldShippingForm.STATE_APPROVED)
    serializer_class = GoldShippingMasterSerializer
    permission_classes = [permissions.IsAuthenticated, IsInGroup,]

    required_groups = ['baldna_gold_travel']

    def retrieve(self, request,pk):
        queryset = self.get_queryset() 

        try:
            obj = get_object_or_404(queryset, pk=pk)
        except Http404:
            raise NotFound(detail=f"No request found with request_number: {pk}.")
        
        serializer = self.serializer_class(instance=obj)

        result = serializer.data

        # Log access
        accessed.send(obj.__class__, instance=obj)

        return Response(result)
