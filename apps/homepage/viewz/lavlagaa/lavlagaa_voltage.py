from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class VoltageList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_voltage'
    template_name = "homepage/lavlah/voltage.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        objs = Voltage.objects.filter(is_active=1)
        data = {
            "datas":objs,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)


class VoltageAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_voltage.html"
    permission_required = 'data.add_voltage'
    menu = "7"

    def get(self, request, *args, **kwargs):
        data = {
            "urlz":"/home/lavlagaa/add_voltage",
            "menu":self.menu,
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        rq = request.POST
        value = rq.get('value', '')
        try:
            Voltage.objects.get(value=value, is_active="1")
            messages.warning(request, "Таны оруулсан хүчдэл бүртгэгдсэн байна.")
            return  redirect('/home/lavlagaa/add_voltage')
        except Voltage.DoesNotExist:
            voltage = Voltage.objects.create()
            voltage.value = rq.get('value', '')
            voltage.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
            if "save_and_continue" in rq:
                return redirect('/home/lavlagaa/add_voltage')
            else:
                return redirect('/home/lavlagaa/voltage')

    
class VoltageEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_voltage.html"
    permission_required = 'data.change_voltage'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        voltage = Voltage.objects.get(id=id)
        data = {
            "urlz":"/home/lavlagaa/edit_voltage/" + id + "/",
            "voltage":voltage,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        value = rq.get('value', '')
        try:
            voltage = Voltage.objects.get(id=id)
            if voltage.value != value:
                try:
                    Voltage.objects.get(value=value, is_active="1")
                    messages.warning(request, "Таны оруулсан хүчдэл бүртгэгдсэн байна.")
                    return  redirect("/home/lavlagaa/edit_voltage/" + id + "/")
                except Voltage.DoesNotExist:
                    no_error = ""
            voltage.value = value
            voltage.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
        except:
            messages.warning(request, 'Алдаа гарлаа.')
        return redirect('/home/lavlagaa/voltage')


class VoltageDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/voltage.html"
    permission_required = 'data.delete_voltage'

    def get(self, request, id, *args, **kwargs):
        a = Voltage.objects.get(id=id)
        a.is_active = 0
        a.save()
        messages.success(request, "Амжилттай устгагдлаа.")
        return redirect("/home/lavlagaa/voltage")