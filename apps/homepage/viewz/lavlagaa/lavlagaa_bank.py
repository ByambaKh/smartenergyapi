from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class BankList(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = 'data.add_bank'
    template_name = "homepage/lavlah/bank.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        objs = Bank.objects.filter(is_active="1")
        data = {
            "datas":objs,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)
    
    
    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        para = {}
        if name != '':
            para["name__contains"] = name
        para["is_active"] = "1"
        objs = Bank.objects.filter(**para)
        data = {
            "datas":objs,
            "search_q":{
                "name":name,
            },
            "menu":self.menu,
        }
        return render(request, self.template_name, data)
    
class BankAdd(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/add_bank.html"
    permission_required = ('data.add_bank', 'data.change_bank')
    menu = "7"

    def get(self, request, *args, **kwargs):
        data = {
            "menu":self.menu,
            "urlz":"/home/lavlagaa/add_bank"
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        rq = request.POST
        dans = rq.get('dans', '')
        name = rq.get('name', '')
        try:
            Bank.objects.get(dans=dans, is_active="1")
            data = {
                "name":name,
                "dans":dans,
                "menu":self.menu,
            }
            messages.warning(request, 'Таны оруулсан дансны дугаар бүртгэлтэй байна. Өөр дансны дугаар оруулна уу.')
            return render(request, self.template_name, data)
        except Bank.DoesNotExist:
            bank = Bank.objects.create()
            bank.name = name
            bank.dans = dans
            bank.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
            if "save_and_continue" in rq:
                return redirect('/home/lavlagaa/add_bank')
            else:
                return redirect('/home/lavlagaa/bank')

class BankEdit(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/add_bank.html"
    permission_required = ('data.add_bank', 'data.change_bank')
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        bank = Bank.objects.get(id=id)
        data = {
            "urlz":"/home/lavlagaa/edit_bank/" + id + "/",
            "name":bank.name,
            "dans":bank.dans,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        dans = rq.get('dans', '')
        name = rq.get('name', '')
        try:
            bank = Bank.objects.get(id=id)
            if dans != bank.dans:
                try:
                    Bank.objects.get(dans=dans, is_active="1")
                    data = {
                        "name":name,
                        "dans":dans,
                        "menu":self.menu,
                        }
                    messages.warning(request, 'Таны оруулсан дансны дугаар бүртгэлтэй байна. Өөр дугаар оруулна уу.')
                    return render(request, self.template_name, data)
                except Bank.DoesNotExist:
                    no_error = ""
            bank.name = name
            bank.dans = dans
            bank.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
            return redirect('/home/lavlagaa/bank')
        except:
            messages.warning(request, "Алдаа гарлаа.")
            return redirect("/home/lavlagaa/bank")

class BankDel(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = ('data.add_bank', 'data.delete_bank')

    def get(self, request, id, *args, **kwargs):
        print("id",id)
        t = Bank.objects.get(id=id)
        t.is_active = 0
        t.save()
        messages.success(request, 'Амжилттай устгагдлаа.')
        return redirect("/home/lavlagaa/bank")