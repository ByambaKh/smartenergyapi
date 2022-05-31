# coding=utf-8
from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import simplejson
from mcsi.utils import *
from django.contrib import messages
from apps.homepage.viewz.bichilt_manager import *


class BichiltBairAdd(LoginRequiredMixin, View):
    template_name = 'homepage/borluulalt/bichilt_bair_add.html'
    q_bichil_list = "to"
    login_url = '/login'
    NUAT = 0.1
    POWER_TIME_BY_USER = 12
    POWER_TIME_BY_ORG = 5
    menu = "3"
    sub = "2"

    def get(self, request, *args, **kwargs):
        data = {}
        bairs = Bair.objects.filter(is_active="1").exclude(name='')
        data["bairs"] = bairs
        data["urlz"] = "/home/borluulalt/bichilt_bair_add"
        data["menu"] = self.menu
        data["sub"] = self.sub
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        bichilt_date = rq.get('bichilt_date', '')
        bair_id = rq.get('station_code_select', '')
        tooluur_number = rq.get('tooluur_select', '')
        day = rq.get('day_zaalt', '')
        night = rq.get('night_zaalt', '')
        if night == '' or night == None:
            night = "0"
        rush = rq.get('rush_zaalt', '')
        if rush == '' or rush == None:
            rush = "0"

        b_date = datetime.datetime.strptime(bichilt_date, '%Y-%m-%d')
        # print ("bichilt date= " + bichilt_date + " dedstants_code= " + dedstants_code + " tooluur= " + tooluur_number + " day= " + day)
        response = BichiltManager().create_bichilt(2, tooluur_number, bair_id, b_date, "0", day, night, rush, "",
                                                   request.user.id, "0")
        if response["code"] == 400:
            return self.error_builder_with_return(request, response["code"], response["description"], bichilt_date)
        else:
            return self.success_builder_with_return(request, bichilt_date)

    def error_builder_with_return(self, request, code, description, date):
        bairs = Bair.objects.filter(is_active="1")
        messages.warning(request, description)

        data = {
            "add_q": {
                "bichilt_date": date,
            },
            "error": {
                "code": code,
                "description": description
            },
            "menu": self.menu,
            "sub": self.sub
        }
        data["bairs"] = bairs
        data["urlz"] = "/home/borluulalt/bichilt_add"
        return render(request, self.template_name, data)

    def success_builder_with_return(self, request, date):
        messages.success(request, "Амжилттай хадгалагдлаа.")
        data = {
            "add_q": {
                "bichilt_date": date,
            },
            "success": "True",
            "menu": self.menu,
            "sub": self.sub
        }
        bairs = Bair.objects.filter(is_active="1")
        data["bairs"] = bairs
        data["urlz"] = "/home/borluulalt/bichilt_bair_add"
        return render(request, self.template_name, data)


class BichiltBairEdit(LoginRequiredMixin, View):
    template_name = 'homepage/borluulalt/bichilt_bair_add.html'
    login_url = '/login'
    menu = "3"
    sub = "2"

    def get(self, request, id, *args, **kwargs):
        try:
            selected_bichilt = Bichilt.objects.get(id=id)
        except Bichilt.DoesNotExist:
            redirect("/home/borluulalt/bichilt_list")

        prev_bichilt = {}
        if selected_bichilt.prev_bichilt_id != "0" and selected_bichilt.prev_bichilt_id != None:
            prev = Bichilt.objects.get(id=selected_bichilt.prev_bichilt_id)
            prev_bichilt['day'] = prev.day_balance
            prev_bichilt['night'] = prev.night_balance
            prev_bichilt['rush'] = prev.rush_balance
            prev_bichilt['created_date'] = prev.bichilt_date.strftime("%Y-%m-%d")
        else:
            prev_bichilt['day'] = selected_bichilt.tooluur.tooluur.balance_value
            prev_bichilt['night'] = selected_bichilt.tooluur.tooluur.balance_value_night
            prev_bichilt['rush'] = selected_bichilt.tooluur.tooluur.balance_value_rush
            prev_bichilt['created_date'] = selected_bichilt.tooluur.tooluur.installed_date.strftime("%Y-%m-%d")

        data = {
            "urlz": "/home/borluulalt/bichilt_bair_edit/" + id + "/",
            "edit_data": selected_bichilt,
            "prev_data": prev_bichilt,
            "add_q": {
                "bichilt_date": selected_bichilt.bichilt_date.strftime("%Y-%m-%d"),
            },
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        bichilt_date = rq.get('bichilt_date', '')
        day = rq.get('day_zaalt', '')
        night = rq.get('night_zaalt', '')
        if night == '':
            night = "0"
        rush = rq.get('rush_zaalt', '')
        if rush == '':
            rush = "0"

        try:
            selected_bichilt = Bichilt.objects.get(id=id)
            is_problem = rq.get('is_problem', '')
        except Bichilt.DoesNotExist:
            redirect("/home/borluulalt/bichilt_list")
        b_date = datetime.datetime.strptime(bichilt_date, '%Y-%m-%d')
        response = BichiltManager().edit_bichilt(2, selected_bichilt, b_date, "0", day, night, rush, "",
                                                 request.user.id, is_problem)
        if response["code"] == 400:
            return self.error_builder_with_return(request, response["code"], response["description"], bichilt_date)
        return redirect("/home/borluulalt/bichilt_list/4")


class BichiltBairView(LoginRequiredMixin, View):
    template_name = 'homepage/borluulalt/bichilt_bair_add.html'
    login_url = '/login'

    def get(self, request, id, *args, **kwargs):
        try:
            selected_bichilt = Bichilt.objects.get(id=id)
        except Bichilt.DoesNotExist:
            redirect("/home/borluulalt/bichilt_list")
        prev_bichilt = {}
        if selected_bichilt.prev_bichilt_id != "0" and selected_bichilt.prev_bichilt_id != None:
            prev = Bichilt.objects.get(id=selected_bichilt.prev_bichilt_id)
            prev_bichilt['day'] = prev.day_balance
            prev_bichilt['night'] = prev.night_balance
            prev_bichilt['rush'] = prev.rush_balance
            prev_bichilt['created_date'] = prev.bichilt_date.strftime("%Y-%m-%d")
        else:
            prev_bichilt['day'] = selected_bichilt.tooluur.tooluur.balance_value
            prev_bichilt['night'] = selected_bichilt.tooluur.tooluur.balance_value_night
            prev_bichilt['rush'] = selected_bichilt.tooluur.tooluur.balance_value_rush
            prev_bichilt['created_date'] = selected_bichilt.tooluur.tooluur.installed_date.strftime("%Y-%m-%d")
        data = {
            "urlz": "/home/borluulalt/bichilt_bair_edit/" + id + "/",
            "edit_data": selected_bichilt,
            "prev_data": prev_bichilt,
            "type": "1",
            "add_q": {
                "bichilt_date": selected_bichilt.bichilt_date.strftime("%Y-%m-%d"),
            },
        }
        return render(request, self.template_name, data)


def get_bair_tooluur(request):
    data = {}
    tooluur = []
    station_id = request.GET['bair_id']
    tooluur_customers = TooluurCustomer.objects.filter(bair_id=station_id, is_active="1")
    if len(tooluur_customers) > 0:
        for item in tooluur_customers:
            tooluur.append(
                {'tooluur_code': item.tooluur.number, 'tooluur_name': item.tooluur.name, 'tooluur_id': item.tooluur.id,
                 'tooluur_type': item.tooluur.tariff})
    data['tooluurs'] = tooluur
    return HttpResponse(simplejson.dumps(data), content_type='application/json')
