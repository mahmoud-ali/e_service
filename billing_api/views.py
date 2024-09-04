from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, viewsets

from  .serializers import GroupSerializer, InquiryResponseSerializer, PaymentRequestSerializer, PaymentResponseSerializer, UserSerializer,InquiryRequestSerializer


# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     User = get_user_model()
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class InqueryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        client_id = request.POST.get('uniqueId',None)
        transaction_id = request.POST.get('transactionId',None)
        inquery_req = InquiryRequestSerializer(data={
            'uniqueId':client_id,
            'transactionId':transaction_id,
        })

        inquery_res = InquiryResponseSerializer(data={
            'uniqueId':client_id,
            'transactionId':transaction_id,
        })
        

        if inquery_req.is_valid():
            inquery_res.initial_data['amount'] = 500
            #Check if client exists
            inquery_res.initial_data['status'] = 0
            inquery_res.initial_data['statusDescription'] = 'Successful inquiry'
            #if client not exists
            # inquery_res.initial_data['status'] = 11
            # inquery_res.initial_data['statusDescription'] = 'Invalid client'           
        else:
            inquery_res.initial_data['status'] = 22
            inquery_res.initial_data['statusDescription'] = 'System error'

        inquery_res.is_valid()
        return Response(inquery_res.data)
    
class PaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        rrn = request.POST.get('rrn',None)
        transaction_id = request.POST.get('transactionId',None)
        amount = request.POST.get('amount',0)
        payment_req = PaymentRequestSerializer(data={
            'rrn':rrn,
            'transactionId':transaction_id,
            'amount':amount,
        })

        payment_res = PaymentResponseSerializer(data={
            'transactionId':transaction_id,
        })
        

        if payment_req.is_valid():
            payment_res.initial_data['amount'] = amount
            #Check if transaction not duplicated
            payment_res.initial_data['status'] = 0
            payment_res.initial_data['statusDescription'] = 'Successful payment'
            #if transaction duplicated
            # payment_res.initial_data['status'] = 12
            # payment_res.initial_data['statusDescription'] = 'Duplicated payment'           
        else:
            payment_res.initial_data['status'] = 13
            payment_res.initial_data['statusDescription'] = 'System error'

        payment_res.is_valid()
        return Response(payment_res.data)