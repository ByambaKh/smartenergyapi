from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages

class LavlahUilchilgeeList(LoginRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/lavlah_uilchilgee.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        objs = TulburtUilchilgee.objects.filter(is_active="1")
        data = {
            "datas":objs,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)
    
    
    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        code = rq.get('code', '')
        payment = rq.get('payment','')

        para = {}
        if name != '':
            para["name__icontains"] = name
        if code != '':
            para["code"] = code
        if payment != '':
            para["payment__gte"] = payment
        para["is_active"] = "1"
        objs = TulburtUilchilgee.objects.filter(**para)
        data = {
            "datas":objs,
            "search_q":{
                "name":name,
                "code":code,
                "payment":payment,
            },
            "menu":self.menu,
        }
        return render(request, self.template_name, data)
    
class LavlahUilchilgeeAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/add_lavlah_uilchilgee.html"
    permission_required = 'data.add_tulburtuilchilgee'
    menu = "7"

    def get(self, request, *args, **kwargs):
        data = {
            "urlz":"/home/lavlagaa/add_service",
            "menu":self.menu,
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        code = rq.get('code', '')
        payment = rq.get('payment', '')
        angilal = rq.get('select_angilal', '')

        try:
            TulburtUilchilgee.objects.get(code=code, is_active="1")
            messages.warning(request, 'Таны бүртгэсэн дугаар бүртгэлтэй байна.Өөр дугаар оруулна уу.')
            return redirect("/home/lavlagaa/add_service")
        except TulburtUilchilgee.DoesNotExist:
            ser = TulburtUilchilgee.objects.create()
            ser.name = name
            ser.code = code
            ser.angilal = angilal
            ser.payment = payment
            ser.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
            if "save_and_continue" in rq:
                return redirect('/home/lavlagaa/add_service')
            else:
                return redirect('/home/lavlagaa/uilchilgee')
    
class LavlahUilchilgeeEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/add_lavlah_uilchilgee.html"
    permission_required = 'data.change_tulburtuilchilgee'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        service = TulburtUilchilgee.objects.get(id=id)
        print(service.payment)
        data = {
            "urlz":"/home/lavlagaa/edit_service/" + id + "/",
            "service":service,
            "payment":str(service.payment),
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        code = rq.get('code', '')
        payment = rq.get('payment', '')
        angilal = rq.get('select_angilal', '')
        try:
            ser = TulburtUilchilgee.objects.get(id=id)
            if ser.code != code:
                try:
                    TulburtUilchilgee.objects.get(code=code, is_active="1")
                    messages.add_message(request, messages.WARNING, 'Таны оруулсан дугаар бүртгэлтэй байна. Өөр дугаар оруулна уу.')
                    return redirect("/home/lavlagaa/edit_service/" + id + "/")
                except TulburtUilchilgee.DoesNotExist:
                    no_error = ""
            ser.name = name
            ser.code = code
            ser.payment = payment
            ser.angilal = angilal
            ser.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
        except:
            messages.warning(request, "Алдаа гарлаа.")
        return redirect('/home/lavlagaa/uilchilgee')

class LavlahUilchilgeeDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/lavlah_uilchilgee.html"
    permission_required = 'data.delete_tulburtuilchilgee'

    def get(self, request, id, *args, **kwargs):
        s = TulburtUilchilgee.objects.get(id=id)
        s.is_active = 0
        s.save()
        messages.success(request, "Амжилттай устгагдлаа.")
        return redirect("/home/lavlagaa/uilchilgee")