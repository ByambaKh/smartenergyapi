from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class HothonList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_hothon'
    template_name = "homepage/lavlah/hothon.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        aimag = Aimag.objects.filter(is_active=1)
        objs = Hothon.objects.filter(is_active=1)
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
        selected_horoo = rq.get('select_horoo', '')
        selected_duureg = rq.get('select_duureg', '')
        selected_aimag = rq.get('select_aimag', '')

        para = {}
        horoo = None
        duureg = None
        if name != '':
            para["name__contains"] = name
        if code != '':
            para["code"] = code
        if selected_horoo != '':
            para["horoo__code"] = selected_horoo
        if selected_duureg != '':
            para["horoo__duureg__code"] = selected_duureg
            horoo = Horoo.objects.filter(is_active="1", duureg__code=selected_duureg)
        if selected_aimag != '':
            para["horoo__duureg__aimag__code"] = selected_aimag
            duureg = Duureg.objects.filter(is_active="1", aimag__code = selected_aimag)
        para["is_active"] = "1"

        objs = Hothon.objects.filter(**para)
        aimag = Aimag.objects.filter(is_active=1)
        data = {
            "datas":objs,
            "aimag":aimag,
            "duureg":duureg,
            "horoo":horoo,
            "search_q":{
                "name":name,
                "code":code,
                "duureg":selected_duureg,
                "aimag":selected_aimag,
                "horoo":selected_horoo,
            },
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    
class HothonAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_hothon.html"
    permission_required = 'data.add_hothon'
    menu = "7"

    def get(self, request, *args, **kwargs):
        aimags = Aimag.objects.filter(is_active=1)
        data = {
            "aimag":aimags,
            "urlz":"/home/lavlagaa/add_hothon",
            "menu":self.menu,
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        rq = request.POST
        horoo_code = rq.get('select_horoo', '')
        name = rq.get('name', '')
        code = rq.get('code', '')
        try:
            Hothon.objects.get(code=code, is_active="1")
            messages.warning(request, "Хотхоны дугаар системд бүртгэгдсэн байна. Та өөр дугаар ашиглана уу.")
            return redirect('/home/lavlagaa/add_hothon')
        except Hothon.DoesNotExist:
            try:
                Hothon.objects.get(horoo__code=horoo_code, name=name, is_active="1")
                messages.warning(request, "Сонгосон хороонд хотхоны нэр бүртгэгдсэн байна. Та өөр нэр ашиглана уу.")
                return redirect('/home/lavlagaa/add_hothon')
            except Hothon.DoesNotExist:
                horoo_obj = Horoo.objects.get(code=horoo_code)
                hothon = Hothon.objects.create(horoo = horoo_obj)
                hothon.name = name
                hothon.code = code
                hothon.save()
                messages.success(request, "Амжилттай хадгалагдлаа.")
                if "save_and_continue" in rq:
                    return redirect('/home/lavlagaa/add_hothon')
                else:
                    return redirect('/home/lavlagaa/hothon')


class HothonEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_hothon.html"
    permission_required = 'data.change_hothon'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        hothon = Hothon.objects.get(id=id)
        aimag = Aimag.objects.filter(is_active=1)
        duureg = Duureg.objects.filter(is_active=1, aimag__id=hothon.horoo.duureg.aimag.id)
        horoo = Horoo.objects.filter(is_active=1, duureg__id=hothon.horoo.duureg.id)
        data = {
            "urlz":"/home/lavlagaa/edit_hothon/" + id + "/",
            "aimag" : aimag,
            "duureg": duureg,
            "horoo":horoo,
            "hothon":hothon,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        horoo_code = rq.get('select_horoo', '')
        name = rq.get('name', '')
        code = rq.get('code', '')

        try:
            hothon = Hothon.objects.get(id=id)
            if hothon.code != code:
                try:
                    Hothon.objects.get(code=code, is_active="1")
                    messages.warning(request, "Хотхоны дугаар системд бүртгэгдсэн байна. Та өөр дугаар ашиглана уу.")
                    return redirect("/home/lavlagaa/edit_hothon/" + id + "/")
                except Hothon.DoesNotExist:
                    no_error = ""
            if hothon.horoo.code != horoo_code:
                try:
                    Horoo.objects.get(code=horoo_code, name=name, is_active="1")
                    messages.warning(request, "Сонгосон хороонд хотхоны нэр бүртгэгдсэн байна. Та өөр нэр ашиглана уу.")
                    return redirect("/home/lavlagaa/edit_hothon/" + id + "/")
                except Horoo.DoesNotExist:
                    horoo_obj = Horoo.objects.get(code=horoo_code)
                    hothon.horoo = horoo_obj
                    no_error = ""
            hothon.name = name
            hothon.code = code
            hothon.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
        except Exception as e:
            print(e)
            messages.warning(request, "Алдаа гарлаа.")
        return  redirect("/home/lavlagaa/hothon")


class HothonDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/hothon.html"
    permission_required = 'data.delete_hothon'

    def get(self, request, id, *args, **kwargs):
        s = Hothon.objects.get(id=id)
        s.is_active = 0
        s.save()
        messages.success(request, "Амжилттай устгагдлаа.")
        return redirect("/home/lavlagaa/hothon")