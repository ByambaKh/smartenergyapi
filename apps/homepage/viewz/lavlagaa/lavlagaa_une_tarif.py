from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class UneTarif(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_pricetariff'
    template_name = "homepage/lavlah/une_tarif.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        objs = PriceTariff.objects.filter(is_active="1")
        data = {
            "datas":objs,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)
    
    def post(self, request, *args, **kwargs):
        rq = request.POST
        une_type = rq.get('select_une_type', '')
        bus_type = rq.get('select_bus_type', '')
        para = {}
        if une_type != '':
            para["une_type"] = une_type
        if bus_type != '':
            para["bus_type"] = bus_type
        para["is_active"] = "1"
        objs = PriceTariff.objects.filter(**para)
        data = {
            "datas":objs,
            "search_q":{
                "une_type":une_type,
                "bus_type":bus_type,
            },
            "menu":self.menu,
        }
        return render(request, self.template_name, data)


class UneTarifAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_une_tarif.html"
    permission_required = 'data.add_pricetariff'
    menu = "7"

    def get(self, request, *args, **kwargs):
        data = {
            "urlz":"/home/lavlagaa/add_unetarif",
            "menu":self.menu,
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        rq = request.POST
        select_unetype = rq.get('select_unetype', '')
        select_bustype = rq.get('select_bustype', '')
        select_tariff_type = rq.get('select_tariff_type', '')
        # start_date = rq.get('start_date', '')
        # end_date = rq.get('end_date', '')
        try:
            PriceTariff.objects.get(bus_type=select_bustype, une_type=select_unetype, tariff_type=select_tariff_type, is_active="1")
            messages.warning(request, "Өмнөх оруулсан тарифийн мэдээлэлтэй давхцаж байна. Та шалгаад дахин оруулна уу.")
            return redirect("/home/lavlagaa/add_unetarif")
        except PriceTariff.DoesNotExist:
            une = PriceTariff.objects.create()
            une.odor_une = rq.get('odor_une', '0')
            une.shono_une = rq.get('shono_une', '0')
            une.orgil_une = rq.get('orgil_une', '0')
            une.serg_une = rq.get('serg_une', '0')
            une.chadal_une = rq.get('chadal_une', '0')
            une.limit = rq.get('limit', '0')
            une.high_limit_price = rq.get('high_limit', '0')
            une.low_limit_price = rq.get('low_limit', '0')
            une.suuri_une = rq.get('suuri_une', '0')
            une.barimt_une = rq.get('barimt_une', '0')
            une.nuat_huvi = rq.get('nuat_huvi', '0')
            une.ald_huvi = rq.get('ald_huvi', '0')
            une.tv_une = rq.get('tv_une', '0')
            une.une_type = select_unetype
            une.bus_type = select_bustype
            une.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
            if "save_and_continue" in rq:
                return redirect('/home/lavlagaa/add_unetarif')
            else:
                return redirect('/home/lavlagaa/une_tarif')


class UneTarifEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/edit_une_tarif.html"
    permission_required = 'data.change_pricetariff'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        une = PriceTariff.objects.get(id=id)
        data = {
            "urlz":"/home/lavlagaa/edit_unetarif/" + id + "/",
            "une":une,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        select_unetype = rq.get('select_unetype', '')
        select_bustype = rq.get('select_bustype', '')
        start_date = rq.get('start_date', '')
        end_date = rq.get('end_date', '')
        une = PriceTariff.objects.filter(id=id, is_active='1').first()
        if une is not None:
            une.odor_une = rq.get('odor_une', '0')
            une.shono_une = rq.get('shono_une', '0')
            une.orgil_une = rq.get('orgil_une', '0')
            une.serg_une = rq.get('serg_une', '0')
            une.chadal_une = rq.get('chadal_une', '0')
            une.limit = rq.get('limit', '0')
            une.high_limit_price = rq.get('high_limit', '0')
            une.low_limit_price = rq.get('low_limit', '0')
            une.suuri_une = rq.get('suuri_une', '0')
            une.barimt_une = rq.get('barimt_une', '0')
            une.nuat_huvi = rq.get('nuat_huvi', '0')
            une.ald_huvi = rq.get('ald_huvi', '0')
            une.tv_une = rq.get('tv_une', '0')
            une.une_type = select_unetype
            une.bus_type = select_bustype
            une.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
        else:
            messages.error(request, "Амжилтгүй боллоо!")
        return redirect('/home/lavlagaa/une_tarif')


class UneDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/une_tarif.html"
    permission_required = 'data.delete_pricetariff'

    def get(self, request, id, *args, **kwargs):
        une = PriceTariff.objects.get(id=id)
        une.is_active = 0
        une.save()
        messages.success(request, "Амжилттай устгагдлаа.")
        return redirect("/home/lavlagaa/une_tarif")