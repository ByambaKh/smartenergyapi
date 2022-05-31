from rest_framework import viewsets
from apps.api.serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from rest_framework import status
from mcsi.utils import *
from apps.extra import *
from rest_framework.views import APIView
from apps.homepage.viewz.bichilt_manager import *
from django.shortcuts import render, HttpResponse, redirect
# from basicauth.decorators import basic_auth_required
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer


import simplejson
import json

# @parse_request(['json', 'xml'], ['POST', 'GET', 'PATCH'])

@api_view(['GET'])
def checkInfo(Request):
    data = {"success":1, "message":"Хэвийн ажиллаж байна"}
    return Response(data)

