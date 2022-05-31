from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class BagHorooList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_horoo'
    template_name = "homepage/lavlah/bag_horoo.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        aimag = Aimag.objects.filter(is_active="1")
        objs = Horoo.objects.filter(is_active="1")
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
        select_aimag = rq.get('select_aimag', '')
        select_duureg = rq.get('select_duureg', '')
        para = {}
        if name != '':
            para["name__contains"] = name
        if code != '':
            para["code"] = code
        if select_aimag != '':
            para["duureg__aimag__code"] = select_aimag
        if select_duureg != '':
            para["duureg__code"] = select_duureg
        para["is_active"] = "1"
        objs = Horoo.objects.filter(**para)
        aimag = Aimag.objects.filter(is_active="1")
        duureg = Duureg.objects.filter(is_active="1", aimag__code=select_aimag)

        data = {
            "datas":objs,
            "aimag":aimag,
            "duureg":duureg,
            "search_q":{
                "name":name,
                "code":code,
                "duureg":select_duureg,
                "aimag":select_aimag,
            },
            "menu":self.menu,
        }
        return render(request, self.template_name, data)


class BagHorooAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_bag_horoo.html"
    permission_required = 'data.add_horoo'
    menu = "7"

    def get(self, request, *args, **kwargs):
        aimags = Aimag.objects.filter(is_active=1)
        data = {
            "aimag":aimags,
            "urlz":"/home/lavlagaa/add_baghoroo",
            "menu":self.menu,
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        rq = request.POST
        duureg_code = rq.get('select_duureg', '')
        code = rq.get('code', '')
        name = rq.get('name', '')
        try:
            Horoo.objects.get(code=code, is_active="1")
            messages.warning(request, "Баг/Хорооны дугаар системд бүртгэгдсэн байна. Та өөр дугаар ашиглана уу")
            return redirect('/home/lavlagaa/add_baghoroo')
        except:
            try:
                Horoo.objects.get(duureg__code=duureg_code, name=name, is_active="1")
                messages.warning(request, "Сонгосон дүүрэгт хорооны нэр давхцаж байна. Та өөр нэр ашиглана уу")
                return redirect('/home/lavlagaa/add_baghoroo')
            except Horoo.DoesNotExist:
                duureg_obj = Duureg.objects.get(code=duureg_code)
                horoo = Horoo.objects.create(duureg = duureg_obj)
                horoo.name = name
                horoo.code = code
                horoo.save()
                messages.success(request, "Амжилттай хадгалагдлаа.")
                if "save_and_continue" in rq:
                    return redirect('/home/lavlagaa/add_baghoroo')
                else:
                    return redirect('/home/lavlagaa/bag_horoo')


class BagHorooEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_bag_horoo.html"
    permission_required = 'data.change_horoo'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        horoo = Horoo.objects.get(id=id)
        aimag = Aimag.objects.filter(is_active=1)
        duureg = Duureg.objects.filter(is_active=1, aimag__id=horoo.duureg.aimag.id)
        data = {
            "urlz":"/home/lavlagaa/edit_baghoroo/" + id + "/",
            "aimag" : aimag,
            "horoo":horoo,
            "duureg":duureg,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        duureg_code = rq.get('select_duureg', '')
        code = rq.get('code', '')
        name = rq.get('name', '')
        try:
            horoo = Horoo.objects.get(id=id)
            if horoo.code != code:
                try:
                    Horoo.objects.get(code=code, is_active="1")
                    messages.warning(request, "Баг/Хорооны дугаар системд бүртгэгдсэн байна. Та өөр дугаар ашиглана уу")
                    return redirect("/home/lavlagaa/edit_baghoroo/" + id + "/")
                except Horoo.DoesNotExist:
                    no_error = ""
            if horoo.duureg.code != duureg_code:
                try:
                    Horoo.objects.get(duureg__code=duureg_code, name=name, is_active="1")
                    messages.warning(request, "Сонгосон дүүрэгт хорооны нэр давхцаж байна. Та өөр нэр ашиглана уу")
                    return redirect("/home/lavlagaa/edit_baghoroo/" + id + "/")
                except Horoo.DoesNotExist:
                    duureg_obj = Duureg.objects.get(code=duureg_code)
                    horoo.duureg = duureg_obj
                    no_error = ""
            horoo.name = name
            horoo.code = code
            horoo.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
        except:
            messages.warning(request, "Алдаа гарлаа.")
        return  redirect("/home/lavlagaa/bag_horoo")


class BagHorooDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/bag_horoo.html"
    permission_required = 'data.delete_horoo'

    def get(self, request, id, *args, **kwargs):
        s = Horoo.objects.get(id=id)
        s.is_active = 0
        s.save()
        messages.success(request, "Амжилттай устгагдлаа.")
        return redirect("/home/lavlagaa/bag_horoo")
