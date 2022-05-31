from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class AmperList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_amper'
    template_name = "homepage/lavlah/amper.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        objs = Amper.objects.filter(is_active="1")
        data = {
            "datas":objs,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)


class AmperAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_amper.html"
    permission_required = 'data.add_amper'
    menu = "7"   
    def get(self, request, *args, **kwargs):
        data = {
            "urlz":"/home/lavlagaa/add_amper",
            "menu":self.menu,
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        rq = request.POST
        value = rq.get('value', '')
        try:
            Amper.objects.get(value=value, is_active="1")
            messages.warning(request, "Таны оруулсан гүйдэл бүртгэгдсэн байна.")
            return  redirect('/home/lavlagaa/add_amper')
        except Amper.DoesNotExist:
            amper = Amper.objects.create()
            amper.value = rq.get('value', '')
            amper.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
            if "save_and_continue" in rq:
                return redirect('/home/lavlagaa/add_amper')
            else:
                return redirect('/home/lavlagaa/amper')


class AmperEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_amper.html"
    permission_required = 'data.change_amper'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        amper = Amper.objects.get(id=id)
        data = {
            "urlz":"/home/lavlagaa/edit_amper/" + id + "/",
            "amper":amper,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        value = rq.get('value', '')
        try:
            amper = Amper.objects.get(id=id)
            if amper.value != value:
                try:
                    Amper.objects.get(value=value, is_active="1")
                    messages.warning(request, "Гүйдэл бүртгэгдсэн байна.")
                    return  redirect('/home/lavlagaa/add_amper')
                except Amper.DoesNotExist:
                    no_error = ""
            amper.value = rq.get('value', '')
            amper.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
        except:
            messages.warning(request, 'Алдаа гарлаа.')
        return redirect('/home/lavlagaa/amper')


class AmperDel(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/amper.html"
    permission_required = 'data.delete_amper'

    def get(self, request, id, *args, **kwargs):
        a = Amper.objects.get(id=id)
        a.is_active = 0
        a.save()
        messages.success(request, "Амжилттай устгагдлаа.")
        return redirect("/home/lavlagaa/amper")