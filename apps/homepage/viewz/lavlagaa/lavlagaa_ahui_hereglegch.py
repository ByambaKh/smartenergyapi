from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin

class AhuiListView(LoginRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/ahui_hereglegch.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        ahui_hereglegch_array = AhuinHereglegch.objects.filter(is_active="1")
        data = {
            "datas": ahui_hereglegch_array,
            "menu":self.menu
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        search_t = rq.get('searchText', '')
        ahui_hereglegch_array = AhuinHereglegch.objects.filter(is_active="1", name__contains=search_t)
        data = {
            "datas": ahui_hereglegch_array,
            "searchText":search_t,
            "menu":self.menu
        }
        return render(request, self.template_name, data)

class AhuiAddView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/ahui_add.html"
    permission_required = 'data.add_ahuinhereglegch'
    menu = "7"

    def get(self, request, *args, **kwargs):
        data = {
            "urlz": "/home/lavlagaa/ahui_add",
            "menu":self.menu
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        try:
            AhuinHereglegch.objects.get(name=name, is_active="1")
            messages.warning(request, "Аж ахуйн ангилалийн нэр бүртгэгдсэн байна.")
            return redirect("/home/lavlagaa/ahui_add")
        except AhuinHereglegch.DoesNotExist:
            obj = AhuinHereglegch.objects.create()
            obj.name = name
            obj.save()
            messages.success(request, "Амжилттай бүртгэгдлээ.")
            if "save" in rq:
                return redirect('/home/lavlagaa/ahui_hereglegch')
            else:
                return redirect('/home/lavlagaa/ahui_add')

class AhuiEditView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = 'data.change_ahuinhereglegch'
    template_name = "homepage/lavlah/ahui_add.html"
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        obj = AhuinHereglegch.objects.get(id=id)
        data = {
            "edit_data": obj,
            "urlz": "/home/lavlagaa/ahui_edit/" + id + "/",
            "menu":self.menu
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        try:
            obj = AhuinHereglegch.objects.get(id=id)
            if obj.name != name:
                try:
                    AhuinHereglegch.objects.get(name=name, is_active="1")
                    messages.warning(request, "Аж ахуйн ангилалийн нэр бүртгэгдсэн байна.")
                    return redirect("/home/lavlagaa/ahui_add/"+str(id)+"/")
                except AhuinHereglegch.DoesNotExist:
                    no_error = ""
            obj.name = name
            obj.save()
            messages.success(request, 'Амжилттай хадгалагдлаа.')
        except AhuinHereglegch.DoesNotExist:
            messages.warning(request, 'Алдаа гарлаа')
        return redirect('/home/lavlagaa/ahui_hereglegch')

class AhuiDeleteView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = 'data.delete_ahuinhereglegch'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        obj = AhuinHereglegch.objects.get(id=id)
        obj.is_active = 0
        obj.save()
        messages.success(request, 'Амжилттай устгагдлаа.')
        return redirect('/home/lavlagaa/ahui_hereglegch')