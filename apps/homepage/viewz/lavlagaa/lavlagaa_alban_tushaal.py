from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class AlbanTushaalList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = 'data.view_albantushaal'
    template_name = "homepage/lavlah/alban_tushaal.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        objs = AlbanTushaal.objects.filter(is_active="1")
        data = {
            "datas":objs,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)
    
    
    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        code = rq.get('code', '')
        para = {}
        if name != '':
            para["name__contains"] = name
        if code != '':
            para["code__contains"] = code
        para["is_active"] = "1"
        objs = AlbanTushaal.objects.filter(**para)
        data = {
            "datas":objs,
            "search_q":{
                "name":name,
                "code":code,
            },
            "menu":self.menu,
        }
        return render(request, self.template_name, data)


class TushaalAdd(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/add_alban_tushaal.html"
    permission_required = 'data.add_albantushaal'
    menu = "7"

    def get(self, request, *args, **kwargs):
        data = {
            "urlz":"/home/lavlagaa/add_alban_tushaal",
            "menu":self.menu,
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        rq = request.POST
        code = rq.get('code', '')
        name = rq.get('name', '')
        try:
            AlbanTushaal.objects.get(code=code, is_active="1")
            data = {
                "name":name,
                "code":code,
                "menu":self.menu,
            }
            messages.add_message(request, messages.WARNING, 'Таны оруулсан код бүртгэлтэй байна. Өөр код оруулна уу.')
            return render(request, self.template_name, data)
        except AlbanTushaal.DoesNotExist:
            ser = AlbanTushaal.objects.create()
            ser.name = name
            ser.code = code
            ser.save()
            messages.success(request, 'Амжилттай бүртгэгдлээ.')
            if "save" in rq:
                return redirect('/home/lavlagaa/alban_tushaal')
            elif "save_and_continue" in rq:
                return redirect('/home/lavlagaa/add_alban_tushaal')

    
class TushaalEdit(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/add_alban_tushaal.html"
    permission_required = 'data.change_albantushaal'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        ser = AlbanTushaal.objects.get(id=id)
        data = {
            "urlz":"/home/lavlagaa/edit_alban_tushaal/" + id + "/",
            "tushaal":ser,
            "name":ser.name,
            "code":ser.code,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        code = rq.get('code', '')
        name = rq.get('name', '')
        try:
            ser = AlbanTushaal.objects.get(id=id, is_active="1")
            if ser.code != code:
                try:
                    AlbanTushaal.objects.get(code=code)
                    messages.warning(request, 'Таны оруулсан код бүртгэлтэй байна. Өөр код оруулна уу.')
                    return redirect("/home/lavlagaa/add_alban_tushaal/" + id + "/")
                except AlbanTushaal.DoesNotExist:
                    no_error =""
                ser.name = name
                ser.code = code
                ser.save()
                messages.success(request, "Амжилттай хадгалагдлаа.")
                return redirect('/home/lavlagaa/alban_tushaal')
            return redirect('/home/lavlagaa/alban_tushaal')

        except:
            messages.warning(request, 'Алдаа гарлаа.')
            return redirect("/home/lavlagaa/alban_tushaal")


class TushaalDel(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = 'data.delete_albantushaal'

    def get(self, request, id, *args, **kwargs):
        s = AlbanTushaal.objects.get(id=id)
        s.is_active = 0
        s.save()
        messages.success(request, 'Амжилттай устгагдлаа.')
        return redirect("/home/lavlagaa/alban_tushaal")