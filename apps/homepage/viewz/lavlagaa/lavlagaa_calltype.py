from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class CallTypeList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_calltype'
    template_name = "homepage/lavlah/call_type.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        objs = CallType.objects.filter(is_active="1")
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
        objs = CallType.objects.filter(**para)
        data = {
            "datas":objs,
            "search_q":{
                "name":name,
            },
            "menu":self.menu,
        }
        return render(request, self.template_name, data)


class CallTypeAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_calltype.html"
    permission_required = 'data.add_calltype'
    menu = "7"

    def get(self, request, *args, **kwargs):
        data = {
            "menu":self.menu,
            "urlz":"/home/lavlagaa/add_calltype"
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        try:
            CallType.objects.get(name=name, is_active="1")
            messages.warning(request, 'Таны оруулсан дуудлагын нэр бүртгэлтэй байна. Өөр нэр оруулна уу.')
            return render("/home/lavlagaa/add_calltype")
        except CallType.DoesNotExist:
            calltype = CallType.objects.create()
            calltype.name = rq.get('name', '')
            calltype.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
            if "save_and_continue" in rq:
                return redirect('/home/lavlagaa/add_calltype')
            else:
                return redirect('/home/lavlagaa/call_type')


class CallTypeEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_calltype'
    template_name = "homepage/lavlah/add_calltype.html"
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        calltype = CallType.objects.get(id=id)
        data = {
            "urlz":"/home/lavlagaa/edit_calltype/" + id + "/",
            "calltype":calltype,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        name = rq.get('name','')
        try:
            calltype = CallType.objects.get(id=id)
            if name != calltype.name:
                try:
                    CallType.objects.get(name=name, is_active="1")
                    messages.warning(request, 'Таны оруулсан дуудлагын нэр бүртгэлтэй байна. Өөр нэр оруулна уу.')
                    return redirect("/home/lavlagaa/edit_calltype/" + id + "/")
                except:
                    no_error = ""
            calltype.name = rq.get('name', '')
            calltype.save()
            messages.success(request, 'Амжилттай хадгалагдлаа.')
        except:
            messages.warning(request, 'Алдаа гарлаа.')
        return redirect('/home/lavlagaa/call_type')


class CallTypeDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_calltype'
    template_name = "homepage/lavlah/call_type.html"

    def get(self, request, id, *args, **kwargs):
        t = CallType.objects.get(id=id)
        t.is_active = 0
        t.save()
        messages.success(request, 'Амжилттай устгагдлаа.')
        return redirect("/home/lavlagaa/call_type")