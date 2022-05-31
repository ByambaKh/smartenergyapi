from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class AimagList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_aimag'
    template_name = "homepage/lavlah/aimag_niislel.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        objs = Aimag.objects.filter(is_active="1")
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
            para['code'] = code
        para["is_active"] = "1"
        objs = Aimag.objects.filter(**para)
        data = {
            "datas":objs,
            "search_q":{
                "name":name,
                "code":code,
            },
            "menu":self.menu,
        }
        return render(request, self.template_name, data)


class AimagAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_aimag.html"
    permission_required = 'data.add_aimag'
    menu = "7"

    def get(self, request, *args, **kwargs):
        data = {
            "urlz":"/home/lavlagaa/add_niislel",
            "menu":self.menu,
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        code = rq.get('code', '')
        try:
            Aimag.objects.get(code=code, is_active="1")
            messages.warning(request, "Аймаг/нийслэлийн дугаар системд бүртгэгдсэн байна. Та өөр дугаар ашиглана уу")
            return redirect("/home/lavlagaa/add_niislel")
        except Aimag.DoesNotExist:
            aimag = Aimag.objects.create()
            aimag.name = name
            aimag.code = code
            aimag.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
            if "save_and_continue" in rq:
                return redirect('/home/lavlagaa/add_niislel')
            else:
                return redirect('/home/lavlagaa/aimag_niislel')


class AimagNiislelEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_aimag.html"
    permission_required = 'data.change_aimag'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        aimag = Aimag.objects.get(id=id)
        data = {
            "urlz":"/home/lavlagaa/edit_niislel/" + id + "/",
            "aimag":aimag,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        code = rq.get('code', '')
        try:
            aimag = Aimag.objects.get(id=id)
            if aimag.code != code:
                try:
                    Aimag.objects.get(code=code, is_active="1")
                    messages.warning(request, "Аймаг/нийслэлийн дугаар системд бүртгэгдсэн байна. Та өөр дугаар ашиглана уу")
                    return redirect("/home/lavlagaa/add_niislel")
                except Aimag.DoesNotExist:
                    no_error = ""
            aimag.name = name
            aimag.code = code
            aimag.save()
        except:
            messages.warning(request, "Алдаа гарлаа.")
        return redirect('/home/lavlagaa/aimag_niislel')


class AimagDel(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/aimag_niislel.html"
    permission_required = 'data.delete_aimag'

    def get(self, request, id, *args, **kwargs):
        t = Aimag.objects.get(id=id)
        t.is_active = 0
        t.save()
        messages.success(request, 'Амжилттай устгагдлаа.')
        return redirect("/home/lavlagaa/aimag_niislel")