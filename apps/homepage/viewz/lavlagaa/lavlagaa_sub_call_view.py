from django.shortcuts import render, redirect
from apps.data.models import *
from apps.homepage.forms import *
from django.views import View
import code
from pprint import pprint
from django.contrib.auth.mixins import LoginRequiredMixin

class SubTypeList(LoginRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/sub_calltype_add.html"
    starter_q = "SELECT id,name FROM data_callgeneraltype where is_active=1"

    def get(self, request, *args, **kwargs):
        q = self.starter_q
        objs = CallGeneralType.objects.raw(q)
        data = {
            "datas":objs,
        }
        return render(request, self.template_name, data)
    
    def post(self, request, *args, **kwargs):
        NewForm = SubCallType(request.POST)
        if NewForm.is_valid():
            aan_obj = CallSubType.objects.create()
            aan_obj.name = NewForm.cleaned_data['name']
            aan_obj.is_active = NewForm.cleaned_data['is_active']
            aan_obj.general_type = NewForm.cleaned_data['general_type']
            aan_obj.save()
        return redirect('/home/lavlagaa/sub_calltype_add')