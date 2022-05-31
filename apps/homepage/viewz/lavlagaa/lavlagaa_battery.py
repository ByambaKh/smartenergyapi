import logging

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from datetime import datetime
from apps.data.models import Battery, DedStants, Amper


class BatteryList(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_battery'
    template_name = 'homepage/lavlah/battery.html'
    menu = '7'
    starter_q = "SELECT bat.id, bat.dugaar, bat.serial, bat.suuriluulsan_ognoo, bat.amper, bat.ajilsan_jil, ded.name FROM data_battery bat JOIN data_dedstants ded ON bat.ded_stants_id=ded.id WHERE bat.is_active = 1"

    try:
        ded_stants = DedStants.objects.filter(is_active=1)
    except ObjectDoesNotExist as e:
        ded_stants = None

    def get(self, request, *args, **kwargs):
        try:
            q = self.starter_q
            q = q + " ORDER BY bat.created_date DESC"
            batteries = Battery.objects.raw(q)
        except ObjectDoesNotExist as e:
            batteries = None
            logging.error('"Battery" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'batteries': batteries,
            'ded_stants': self.ded_stants,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        dugaar = request.POST['dugaar']
        amper = request.POST['amper']
        serial = request.POST['serial']
        ded_stants = request.POST['ded_stants']
        ajilsan_jil = request.POST['ajilsan_jil']

        q = self.starter_q

        if dugaar != '':
            q = q + " AND bat.dugaar LIKE '%%" + dugaar + "%%'"
        if amper != '':
            q = q + " AND bat.amper LIKE '%%" + amper + "%%'"
        if serial != '':
            q = q + " AND bat.serial LIKE '%%" + serial + "%%'"
        if ded_stants != '':
            q = q + " AND ded.id LIKE '%%" + ded_stants + "%%'"
        if ajilsan_jil != '':
            q = q + " AND bat.ajilsan_jil LIKE '%%" + ajilsan_jil + "%%'"

        try:
            batteries = Battery.objects.raw(q)
        except ObjectDoesNotExist as e:
            batteries = None
            logging.error('"Battery" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'batteries': batteries,
            'ded_stants': self.ded_stants,
            'search_q': {
                'dugaar': dugaar,
                'amper': amper,
                'serial': serial,
                'ded_stants': ded_stants,
                'ajilsan_jil': ajilsan_jil,
            }
        }
        return render(request, self.template_name, data)


class BatteryAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_battery'
    template_name = 'homepage/lavlah/add_battery.html'
    menu = '7'

    def get(self, request, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.filter(is_active=1)
        except ObjectDoesNotExist as e:
            ded_stants = None
            logging.error('"DedStants" model has no object: %s', e)

        data = {
            'action': '/home/lavlagaa/add_battery',
            'ded_stants': ded_stants,
            'menu': self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        try:
            battery_nums = Battery.objects.filter(ded_stants_id=int(request.POST['ded_stants']))
            for battery_num in battery_nums:
                if battery_num.dugaar == request.POST['dugaar']:
                    messages.error(request, 'Энэ дэд станц дээрх баттерейны дугаар давхцаж байна!')
                    return redirect('/home/lavlagaa/add_battery')
        except Battery.DoesNotExist:
            battery_num = None

        try:
            ded_stants = DedStants.objects.get(id=int(request.POST['ded_stants']))
        except DedStants.DoesNotExist:
            ded_stants = None

        if ded_stants is not None:
            try:
                suuriluulsan_ognoo = datetime.strptime(request.POST['suuriluulsan_ognoo'], '%Y-%m-%d')
                battery = Battery(dugaar=request.POST['dugaar'], amper=request.POST['amper'], serial=request.POST['serial'], ded_stants=ded_stants, suuriluulsan_ognoo=suuriluulsan_ognoo, ajilsan_jil=request.POST['ajilsan_jil'], created_user_id=request.user.id)
                battery.save()
                messages.success(request, 'Амжилттай хадгалагдлаа!')
            except Exception as e:
                messages.error(request, 'Хадгалахад алдаа гарлаа!')
                return redirect('/home/lavlagaa/add_battery')

            if "save_and_continue" in request.POST:
                return redirect('/home/lavlagaa/add_battery')
            else:
                return redirect('/home/lavlagaa/battery')
        else:
            try:
                ded_stants = DedStants.objects.filter(is_active=1)
            except ObjectDoesNotExist as e:
                ded_stants = None
                logging.error('"DedStants" model has no object: %s', e)

            data = {
                'action': '/home/lavlagaa/add_battery',
                'ded_stants': ded_stants,
                'menu': self.menu,
            }
            return render(request, self.template_name, data)


class BatteryEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_battery'
    template_name = 'homepage/lavlah/add_battery.html'
    menu = '7'

    def get(self, request, id, *args, **kwargs):
        try:
            battery = Battery.objects.get(id=id)
        except ObjectDoesNotExist as e:
            battery = None
            logging.error('"Battery" model has no object: %s', e)

        try:
            ded_stants = DedStants.objects.filter(is_active=1)
        except ObjectDoesNotExist as e:
            ded_stants = None
            logging.error('"DedStants" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'action': '/home/lavlagaa/edit_battery/'+id+'/',
            'battery': battery,
            'ded_stants': ded_stants,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        battery_id = request.POST['battery_id']

        try:
            battery_nums = Battery.objects.filter(ded_stants_id=int(request.POST['ded_stants']))
            for battery_num in battery_nums:
                if battery_num.dugaar == request.POST['dugaar'] and int(battery_id) != battery_num.id:
                    messages.error(request, 'Энэ дэд станц дээрх баттерейны дугаар давхцаж байна!')
                    return redirect('/home/lavlagaa/battery')
        except Battery.DoesNotExist:
            battery_num = None

        try:
            battery = Battery.objects.get(id=int(battery_id))
            battery.dugaar = request.POST['dugaar']
            battery.serial = request.POST['serial']
            battery.ajilsan_jil = request.POST['ajilsan_jil']
            battery.amper = request.POST['amper']
            suuriluulsan_ognoo = datetime.strptime(request.POST['suuriluulsan_ognoo'], '%Y-%m-%d')
            battery.suuriluulsan_ognoo = suuriluulsan_ognoo
            try:
                ded_stants = DedStants.objects.get(id=int(request.POST['ded_stants']))
            except ObjectDoesNotExist as e:
                ded_stants = None
                logging.error('"DedStants" model has no object: %s', e)
            battery.ded_stants = ded_stants
            battery.save()
            messages.success(request, 'Амжилттай засварлагдлаа!')
        except Exception as e:
            messages.error(request, 'Засварлахад алдаа гарлаа!')
            #logging.error('%s', e)
            print(e)

        return redirect('/home/lavlagaa/battery')


class BatteryDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_battery'

    def get(self, request, id, *args, **kwargs):
        try:
            battery = Battery.objects.get(id=id)
            battery.is_active = 0
            battery.save()
            messages.success(request, 'Ажилттай устгагдлаа!')
        except ObjectDoesNotExist as e:
            messages.error(request, 'Устахад алдаа гарлаа!')
            logging.error('"Battery" model has no object: %s', e)

        return redirect('/home/lavlagaa/battery')