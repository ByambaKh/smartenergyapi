from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class DuuregList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_duureg'
    template_name = "homepage/lavlah/sum_duureg.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        aimag = Aimag.objects.filter(is_active=1)
        objs = Duureg.objects.filter(is_active=1)
        data = {
            "datas":objs,
            "aimag":aimag,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        code = rq.get('code', '')
        aimag_id = rq.get('select_aimag', '')

        para = {}
        if name != '':
            para["name__contains"] = name
        if code != '':
            para["code__contains"] = code
        if aimag_id != '':
            para["aimag_id"] = aimag_id
            aimag_id = int(aimag_id)

        para["is_active"] = "1"
        objs = Duureg.objects.filter(**para)
        aimag = Aimag.objects.filter(is_active=1)
        data = {
            "datas":objs,
            "aimag":aimag,
            "search_q":{
                "name":name,
                "code":code,
                "aimag_id":aimag_id,
                "menu":self.menu,
            }
        }
        return render(request, self.template_name, data)


class SumDuuregAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_sum_duureg.html"
    permission_required = 'data.add_duureg'
    menu = "7"

    def get(self, request, *args, **kwargs):
        aimags = Aimag.objects.filter(is_active=1)
        data = {
            "aimag":aimags,
            "menu":self.menu,
            "urlz":"/home/lavlagaa/add_sum_duureg"
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        code = rq.get('code', '')
        aimag_id = rq.get('as', '')
        try:
            Duureg.objects.get(code=code, is_active="1")
            messages.warning(request, "Сум/дүүргийн дугаар системд бүртгэгдсэн байна. Та өөр дугаар ашиглана уу")
            return redirect("/home/lavlagaa/add_sum_duureg")
        except Duureg.DoesNotExist:
            try:
                Duureg.objects.get(aimag_id=aimag_id, name=name, is_active="1")
                messages.warning(request, "Сонгосон аймагт дүүргийн нэр бүртгэгдсэн байна. Та өөр нэр ашиглана уу.")
                return redirect('/home/lavlagaa/add_sum_duureg')
            except Duureg.DoesNotExist:
                d = Duureg.objects.create(aimag_id =aimag_id)
                d.name = name
                d.code = code
                d.save()
                messages.success(request, "Амжилттай хадгалагдлаа.")
                if "save_and_continue" in rq:
                    return redirect('/home/lavlagaa/add_sum_duureg')
                else:
                    return redirect('/home/lavlagaa/sum_duureg')


class SumDuuregEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/indedx'
    template_name = "homepage/lavlah/add_sum_duureg.html"
    permission_required = 'data.change_duureg'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        duureg = Duureg.objects.get(id=id)
        aimag = Aimag.objects.filter(is_active=1)
        data = {
            "urlz":"/home/lavlagaa/edit_sum_duureg/" + id + "/",
            "aimag" : aimag,
            "duureg":duureg,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        code = rq.get('code', '')
        aimag_id = rq.get('as', '')
        try:
            duureg = Duureg.objects.get(id=id)
            if duureg.code != code:
                try:
                    Duureg.objects.get(code=code, is_active="1")
                    messages.warning(request, "Сум/дүүргийн дугаар системд бүртгэгдсэн байна. Та өөр дугаар ашиглана уу")
                    return redirect("/home/lavlagaa/edit_sum_duureg/" + id + "/")
                except:
                    no_error = ""
            if duureg.aimag.id != aimag_id:
                try:
                    Duureg.objects.get(aimag__id=aimag_id, name=name, is_active="1")
                    messages.warning(request, "Сум/дүүргийн дугаар системд бүртгэгдсэн байна. Та өөр дугаар ашиглана уу")
                    return redirect("/home/lavlagaa/edit_sum_duureg/" + id + "/")
                except Duureg.DoesNotExist:
                    aimag_obj = Aimag.objects.get(id=aimag_id)
                    duureg.aimag = aimag_obj
                    no_error = ""
            duureg.name = name
            duureg.code = code
            duureg.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
            return redirect('/home/lavlagaa/sum_duureg')
        except:
            messages.warning(request, "Алдаа гарлаа.")
        return redirect("/home/lavlagaa/sum_duureg")


class SumDuuregDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/sum_duureg.html"
    permission_required = 'data.delete_duureg'

    def get(self, request, id, *args, **kwargs):
        s = Duureg.objects.get(id=id)
        s.is_active = 0
        s.save()
        messages.success(request, "Амжилттай устгагдлаа.")
        return redirect("/home/lavlagaa/sum_duureg")