from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

from traditional_api.models import LkpSoag, TblCollector, TblInvoice

from  .serializers import InvoiceRequestSerializer, InvoiceResponseSerializer, UserRequestSerializer, UserResponseSerializer

class LkpSelectView(LoginRequiredMixin,TemplateView):
    template_name = 'select.html'
    kwargs = None

    def get_queryset(self):
        return None #not implemented

    def dispatch(self, *args, **kwargs):
        self.kwargs = kwargs
        self.extra_context = {
                            "options":self.get_queryset(), 
                            "old_value":self.kwargs['dependent_id']
         }
        return super().dispatch(*args, **kwargs)                    

    def get(self, request, *args, **kwargs):                   
        return render(request, self.template_name, self.extra_context)    

class LkpSoagSelectView(LkpSelectView):
    def get_queryset(self):
        qs = LkpSoag.objects.filter(state__id = self.kwargs['master_id'])
        return qs

class AuthView(APIView):
    permission_classes = []

    def post(self, request, format=None):
        username = request.POST.get('username','')
        password = request.POST.get('password','')

        auth_req = UserRequestSerializer(data={
            'username':username,
            'password':password,
        })

        auth_res = UserResponseSerializer(data={
            'status':1,
            'statusDescription':'invalid data',
        })
        
        if auth_req.is_valid():
            try:
                user = authenticate(email=username, password=password)
                if user is not None:
                    token = Token.objects.get(user=user).key
                    collector = TblCollector.objects.get(user=user)

                    auth_res.initial_data['token'] = token
                    auth_res.initial_data['name'] = collector.name
                    auth_res.initial_data['state'] = collector.state.name
                    auth_res.initial_data['soag'] = collector.soag.name
                    auth_res.initial_data['status'] = 0
                    auth_res.initial_data['statusDescription'] = _('Authenticated sucessfully.')
            except:
                pass

        auth_res.is_valid()
        return Response(auth_res.data)

class InvoiceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        name = request.POST.get('name','')
        quantity_in_shoal = int(request.POST.get('quantity_in_shoal',0))
        amount = float(request.POST.get('amount',0))

        invoice_req = InvoiceRequestSerializer(data={
            'name':name,
            'quantity_in_shoal':quantity_in_shoal,
            'amount':amount,
        })

        invoice_res = InvoiceResponseSerializer(data={
            'status':1,
            'statusDescription':'invalid data',
        })
        
        if invoice_req.is_valid():
            try:
                collector = TblCollector.objects.get(user=request.user)
                invoice = TblInvoice.objects.create(
                    collector=collector,
                    mo3adin_name=name,
                    quantity_in_shoal=quantity_in_shoal,
                    amount=amount,
                    created_by=request.user,
                    updated_by = request.user

                )
                                
                invoice_res.initial_data['invoiceId'] = invoice.id
                invoice_res.initial_data['status'] = 0
                invoice_res.initial_data['statusDescription'] = _('Record added sucessfully.')
            except Exception as e:
                pass
                # print(e)

        invoice_res.is_valid()
        return Response(invoice_res.data)
    
