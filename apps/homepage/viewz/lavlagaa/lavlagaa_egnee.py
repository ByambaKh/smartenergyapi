import datetime
from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class EgneeList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_block'
    template_name = "homepage/lavlah/egnee.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        aimag = Aimag.objects.filter(is_active=1)
        objs = Block.objects.filter(is_active=1)
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
        selected_aimag = rq.get('select_aimag', '')
        selected_duureg = rq.get('select_duureg', '')
        selected_horoo = rq.get('select_horoo', '')
        selected_hothon = rq.get('select_hothon', '')

        para = {}
        hothon = None
        horoo = None
        duureg = None
        if name != '':
            para["name__contains"] = name
        if code != '':
            para["code"] = code
        if selected_hothon != '':
            para["hothon__code"] = selected_hothon
        if selected_horoo != '':
            para["hothon__horoo__code"] = selected_horoo
            hothon = Hothon.objects.filter(is_active="1", horoo__code=selected_horoo)
        if selected_duureg != '':
            para["hothon__horoo__duureg__code"] = selected_duureg
            horoo = Horoo.objects.filter(is_active="1", duureg__code=selected_duureg)
        if selected_aimag != '':
            para["hothon__horoo__duureg__aimag__code"] = selected_aimag
            duureg = Duureg.objects.filter(is_active="1", aimag__code = selected_aimag)
        para["is_active"] = "1"
        aimag = Aimag.objects.filter(is_active=1)
        objs = Block.objects.filter(**para)
        data = {
            "datas":objs,
            "aimag":aimag,
            "duureg":duureg,
            "horoo":horoo,
            "hothon":hothon,
            "search_q":{
                "name":name,
                "code":code,
                "horoo":selected_horoo,
                "hothon":selected_hothon,
                "duureg":selected_duureg,
                "aimag":selected_aimag,
                "menu":self.menu,
            }
        }
        return render(request, self.template_name, data)


class EgneeAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_egnee.html"
    permission_required = 'data.add_block'
    menu = "7"
    def get(self, request, *args, **kwargs):
        aimags = Aimag.objects.filter(is_active=1)
        data = {
            "aimag":aimags,
            "urlz":"/home/lavlagaa/add_egnee",
            "menu":self.menu,
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        rq = request.POST
        hothon_code = rq.get('select_hothon', '')
        name = rq.get('name', '')
        code = rq.get('code', '')
        try:
            Block.objects.get(code=code, is_active="1")
            messages.warning(request, "Эгнээний дугаар системд бүртгэгдсэн байна. Та өөр дугаар ашиглана уу")
            return redirect('/home/lavlagaa/add_hothon')
        except Block.DoesNotExist:
            try:
                Block.objects.get(hothon__id=hothon_code, name=name, is_active=1)
                messages.warning(request, "Сонгосон хотхонд эгнээний нэр бүртгэгдсэн байна. Та өөр нэр ашиглана уу.")
                return redirect('/home/lavlagaa/add_egnee')
            except Block.DoesNotExist:
                hothon_obj = Hothon.objects.get(id=hothon_code)
                egnee = Block.objects.create(hothon = hothon_obj)
                egnee.name = rq.get('name', '')
                egnee.code = rq.get('code', '')
                egnee.save()
                messages.success(request, "Амжилттай хадгалагдлаа.")
                if "save_and_continue" in rq:
                    return redirect('/home/lavlagaa/add_egnee')
                else:
                    return redirect('/home/lavlagaa/egnee')


class EgneeEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_egnee.html"
    permission_required = 'data.change_block'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        egnee = Block.objects.get(id=id)
        aimag = Aimag.objects.filter(is_active=1)
        duureg = Duureg.objects.filter(is_active=1, aimag__id=egnee.hothon.horoo.duureg.aimag.id)
        horoo = Horoo.objects.filter(is_active=1, duureg__id=egnee.hothon.horoo.duureg.id)
        hothon = Hothon.objects.filter(is_active=1, horoo__id=egnee.hothon.horoo.id)
        data = {
            "urlz":"/home/lavlagaa/edit_egnee/" + id + "/",
            "aimag" : aimag,
            "egnee":egnee,
            "duureg":duureg,
            "horoo":horoo,
            "hothon":hothon,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        hothon_code = rq.get('select_hothon', '')
        name = rq.get('name', '')
        code = rq.get('code', '')
        print(id)
        try:
            egnee = Block.objects.get(id=id)
            if egnee.code != code:
                try:
                    Block.objects.get(code=code, is_active="1")
                    messages.warning(request, "Эгнээний дугаар системд бүртгэгдсэн байна. Та өөр дугаар ашиглана уу")
                    return redirect("/home/lavlagaa/edit_egnee/" + id + "/")
                except Block.DoesNotExist:
                    no_error = ""
            if egnee.hothon.code != hothon_code:
                try:
                    Block.objects.get(hothon__code=hothon_code, name=name)
                    messages.warning(request, "Сонгосон хотхонд эгнээний нэр бүртгэгдсэн байна. Та өөр нэр ашиглана уу.")
                    return redirect("/home/lavlagaa/edit_egnee/" + id + "/")
                except Block.DoesNotExist:
                    hothon_obj = Hothon.objects.get(code=hothon_code)
                    egnee.hothon = hothon_obj
                    no_error = ""
            egnee.name = name
            egnee.code = code
            egnee.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
        except Exception as e:
            print(e)
            messages.warning(request, "Алдаа гарлаа.")
        return  redirect("/home/lavlagaa/egnee")


class EgneeDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/egnee.html"
    permission_required = 'data.delete_block'

    def get(self, request, id, *args, **kwargs):
        s = Block.objects.get(id=id)
        s.is_active = 0
        s.save()
        messages.success(request, "Амжилттай устгагдлаа.")
        return redirect("/home/lavlagaa/egnee")
