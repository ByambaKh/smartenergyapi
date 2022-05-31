from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class LavlagaaBair(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_bair'
    template_name = "homepage/lavlah/bair.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        objs = Bair.objects.filter(is_active="1")
        data = {
            "datas": objs,
            "menu": self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        para = {}
        if name != '':
            para["name__contains"] = name
        para["is_active"] = "1"
        objs = Bair.objects.filter(**para)
        data = {
            "datas": objs,
            "search_q": {
                "name": name,
            },
            "menu": self.menu,
        }
        return render(request, self.template_name, data)


class LavlagaaBairAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_bair.html"
    permission_required = 'data.add_bair'
    menu = "7"

    def get(self, request, *args, **kwargs):
        data = {
            "urlz": "/home/lavlagaa/add_bair",
            "menu": self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        try:
            Bair.objects.get(name=name, is_active="1")
            messages.warning(request, "Байрны нэр системд бүртгэгдсэн байна. Та өөр нэр ашиглана уу")
            return redirect('/home/lavlagaa/add_bair')
        except:
            bair = Bair.objects.create()
            bair.name = name
            bair.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
            if "save_and_continue" in rq:
                return redirect('/home/lavlagaa/add_bair')
            else:
                return redirect('/home/lavlagaa/bair')


class LavlagaaBairEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_bair.html"
    permission_required = 'data.change_bair'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        bair = Bair.objects.get(id=id)
        data = {
            "urlz": "/home/lavlagaa/edit_bair/" + id + "/",
            "data": bair,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        try:
            bair = Bair.objects.get(id=id)
            if bair.name != name:
                try:
                    Bair.objects.get(name=name, is_active="1")
                    messages.warning(request, "Байрны нэр системд бүртгэгдсэн байна. Та өөр нэр ашиглана уу")
                    return redirect("/home/lavlagaa/edit_baghoroo/" + id + "/")
                except Bair.DoesNotExist:
                    no_error = ""
            bair.name = name
            bair.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
        except:
            messages.warning(request, "Алдаа гарлаа.")
        return redirect("/home/lavlagaa/bair")


class LavlagaaBairDelete(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_bair'

    def get(self, request, id, *args, **kwargs):
        s = Bair.objects.get(id=id)
        s.is_active = 0
        s.save()
        messages.success(request, "Амжилттай устгагдлаа.")
        return redirect("/home/lavlagaa/bair")
