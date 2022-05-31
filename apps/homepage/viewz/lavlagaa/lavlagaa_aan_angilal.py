__author__ = 'L'
from django.contrib import messages
from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin


class AANListView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = 'data.view_aanangilal'
    template_name = "homepage/lavlah/aan_angilal.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        aan_angilal_info = AanAngilal.objects.filter(is_active="1")
        data = {
            "datas": aan_angilal_info,
            "menu":self.menu
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')

        para = {}
        if name != '':
            para["name__contains"] = name
        para["is_active"] = "1"
        objs = AanAngilal.objects.filter(**para)
        data = {
            "datas": objs,
            "search_q":{
                "name":name,
            },
            "menu": self.menu
        }
        return render(request, self.template_name, data)


class AANAddView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = 'data.add_aanangilal'
    template_name = "homepage/lavlah/aan_angilal_add.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        data = {
            "urlz": "/home/lavlagaa/aan_add",
            "menu":self.menu
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        try:
            AanAngilal.objects.get(name=name, is_active="1")
            messages.warning(request, "Ахуйн хэрэглэгчийн нэр бүртгэгдсэн байна.")
            return redirect("/home/lavlagaa/aan_add")
        except AanAngilal.DoesNotExist:
            aan_obj = AanAngilal.objects.create()
            aan_obj.name = name
            aan_obj.save()
            messages.success(request, "Амжилттай бүртгэгдлээ.")
            if "save" in rq:
                return redirect('/home/lavlagaa/aan_angilal')
            else:
                return redirect('/home/lavlagaa/aan_add')


class AANEditView(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = 'data.change_aanangilal'
    template_name = "homepage/lavlah/aan_angilal_add.html"
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        aan_obj = AanAngilal.objects.get(id=id)
        data = {
            "edit_data": aan_obj,
            "urlz": "/home/lavlagaa/aan_edit/" + id + "/",
            "menu":self.menu
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        try:
            aan_obj = AanAngilal.objects.get(id=id)
            if aan_obj.name != name:
                try:
                    AanAngilal.objects.get(name=name, is_active="1")
                    messages.warning(request, "Аж ахуйн ангилалийн нэр бүртгэгдсэн байна.")
                    return redirect("/home/lavlagaa/aan_add/"+str(id)+"/")
                except AanAngilal.DoesNotExist:
                    no_error = ""
            aan_obj.name = name
            aan_obj.save()
            messages.success(request, 'Амжилттай хадгалагдлаа.')
        except AanAngilal.DoesNotExist:
            messages.warning(request, 'Алдаа гарлаа')
        return redirect('/home/lavlagaa/aan_angilal')


class AANDeleteiew(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = 'data.delete_aanangilal'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        aan_obj = AanAngilal.objects.get(id=id)
        aan_obj.is_active = 0
        aan_obj.save()
        messages.success(request, 'Амжилттай устгагдлаа.')
        return redirect('/home/lavlagaa/aan_angilal')
