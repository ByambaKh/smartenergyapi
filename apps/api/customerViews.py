from rest_framework import viewsets
from apps.api.serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from rest_framework import status
from mcsi.utils import *
from apps.extra import *
from rest_framework.views import APIView
from apps.homepage.viewz.customer_manager import *
from django.shortcuts import render, HttpResponse, redirect
# from basicauth.decorators import basic_auth_required

import simplejson
import json

@api_view(['POST'])
# @basic_auth_required(
#     target_test=lambda request: not request.user.is_authenticated
# )
def getCustomerBankAdd(request):
    try:  
        message='Мэдээлэл олдсонгүй.'
        status=0
        error=''
        serializer = CustomerBankSerializer(data=request.data)   
        if serializer.is_valid():   
            user_code =serializer.data['customerCode']
            bank_id =serializer.data['bankCode']
            bank_code =serializer.data['bankCode']
            status=0
            if user_code != '' and bank_id != '' and bank_code != '':            
                customerManager=CustomerManager()        
                newBank=customerManager.create_customer_bank(bank_id,bank_code,user_code) 
                if newBank['code']==200:
                    message=newBank['message']
                    status=1
                else:
                    message=newBank['message']  
            else:
                message='Дутуу мэдээлэл илгээсэн байна.'
        else:
            message = serializer.errors
    except Exception as ex:
        error=str(ex)
        message='Алдаа: '+ error
        status=0
    finally:
        data_last={
            'status': status,
            'message': message
        }
        log = ServiceLog.objects.create(invoice_no='',request=request.data, response=data_last, type='getCustomerBankAdd', request_date=datetime.datetime.now(), response_date=datetime.datetime.now(),status=status,bank_type='',error=error)
        log.save()
        return HttpResponse(simplejson.dumps(data_last), content_type='application/json')

@api_view(['POST'])
# @basic_auth_required(
#     target_test=lambda request: not request.user.is_authenticated
# )
def getCustomerBankRemove(request):
    try:  
        message='Мэдээлэл олдсонгүй.'
        status=0
        error=''
        serializer = CustomerBankSerializer(data=request.data)   
        if serializer.is_valid():   
            user_code =serializer.data['customerCode']
            bank_id =serializer.data['bankCode']
            bank_code =serializer.data['bankCode']
            status=0
            if user_code != '' and bank_id != '' and bank_code != '':            
                customerManager=CustomerManager()        
                newBank=customerManager.remove_customer_bank(bank_id,bank_code,user_code) 
                if newBank['code']==200:
                    message=newBank['message']
                    status=1
                else:
                    message=newBank['message']  
            else:
                message='Дутуу мэдээлэл илгээсэн байна.'
        else:
            message = serializer.errors
    except Exception as ex:
        error=str(ex)
        message='Алдаа: '+ error
        status=0
    finally:
        data_last={
            'status': status,
            'message': message
        }
        log = ServiceLog.objects.create(invoice_no='',request=request.data, response=data_last, type='getCustomerBankRemove', request_date=datetime.datetime.now(), response_date=datetime.datetime.now(),status=status,bank_type='',error=error)
        log.save()
        return HttpResponse(simplejson.dumps(data_last), content_type='application/json')

   