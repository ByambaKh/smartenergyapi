import logging
import simplejson
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from datetime import datetime
from apps.data.models import Shugam, Cable, DedStants
from apps.homepage.forms import CableTrassForm


class CableList(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_cable'
    template_name = 'homepage/lavlah/cable.html'
    menu = '7'
    starter_q = "SELECT cab.id, cab.ner, cab.urt, cab.tip, cab.mulfi_too, cab.trass, gar.shugam_ner, oro.shugam_ner, oro.shugam_tuluv, cab.suuriluulsan_ognoo FROM data_cable cab" \
                " JOIN data_shugam oro ON cab.orolt_id=oro.id" \
                " JOIN data_shugam gar ON cab.garalt_id=gar.id" \
                " WHERE cab.is_active = 1"
    try:
        ded_stants = DedStants.objects.filter(is_active=1).order_by('name')
    except ObjectDoesNotExist:
        ded_stants = None
    try:
        shugams = Shugam.objects.filter(is_active=1).order_by('shugam_ner')
    except ObjectDoesNotExist:
        shugams = None

    def get(self, request, *args, **kwargs):
        if 'start_ded_stants' in request.GET:
            ded_stants_id = request.GET['start_ded_stants']
            result_set = []
            try:
                shugams = Shugam.objects.filter(ded_stants_id=ded_stants_id)
                for shugam in shugams:
                    result_set.append({'id': shugam.id, 'name': shugam.shugam_ner})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"Shugam" model has no object: %s', e)

        if 'end_ded_stants' in request.GET:
            ded_stants_id = request.GET['end_ded_stants']
            result_set = []
            try:
                shugams = Shugam.objects.filter(ded_stants_id=ded_stants_id)
                for shugam in shugams:
                    result_set.append({'id': shugam.id, 'name': shugam.shugam_ner})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"Shugam" model has no object: %s', e)

        try:
            q = self.starter_q
            q = q + " ORDER BY cab.created_date DESC"
            cables = Cable.objects.raw(q)
        except ObjectDoesNotExist as e:
            cables = None
            logging.error('"Cable" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'cables': cables,
            'ded_stants': self.ded_stants,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        ner = request.POST['ner']
        urt = request.POST['urt']
        tip = request.POST['tip']
        mulfi_too = request.POST['mulfi_too']
        orolt = request.POST['orolt']
        garalt = request.POST['garalt']
        start_ded_stants = request.POST['start_ded_stants']
        end_ded_stants = request.POST['end_ded_stants']

        q = self.starter_q

        if ner != '':
            q = q + " AND cab.ner LIKE '%%" + ner + "%%'"
        if urt != '':
            q = q + " AND cab.urt LIKE '%%" + urt + "%%'"
        if tip != '':
            q = q + " AND cab.tip LIKE '%%" + tip + "%%'"
        if mulfi_too != '':
            q = q + " AND cab.mulfi_too LIKE '%%" + mulfi_too + "%%'"
        if start_ded_stants != '':
            q = q + " AND cab.start_ded_stants_id LIKE '%%" + start_ded_stants + "%%'"
            start_ded_stants = int(start_ded_stants)
        if orolt != '':
            q = q + " AND cab.orolt_id LIKE '%%" + orolt + "%%'"
            orolt = int(orolt)
        if end_ded_stants != '':
            q = q + " AND cab.end_ded_stants_id LIKE '%%" + end_ded_stants + "%%'"
            end_ded_stants = int(end_ded_stants)
        if garalt != '':
            q = q + " AND cab.garalt_id LIKE '%%" + garalt + "%%'"
            garalt = int(garalt)

        try:
            cables = Cable.objects.raw(q)
        except ObjectDoesNotExist as e:
            cables = None
            logging.error('"Cable" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'cables': cables,
            'orolts': self.shugams,
            'garalts': self.shugams,
            'ded_stants': self.ded_stants,
            'search_q': {
                'ner': ner,
                'urt': urt,
                'tip': tip,
                'mulfi_too': mulfi_too,
                'start_ded_stants': start_ded_stants,
                'orolt': orolt,
                'end_ded_stants': end_ded_stants,
                'garalt': garalt,
            }
        }
        return render(request, self.template_name, data)


class CableAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_cable'
    template_name = 'homepage/lavlah/add_cable.html'
    menu = '7'

    def get(self, request, *args, **kwargs):
        if 'start_ded_stants' in request.GET:
            ded_stants_id = request.GET['start_ded_stants']
            result_set = []
            try:
                shugams = Shugam.objects.filter(ded_stants_id=ded_stants_id)
                for shugam in shugams:
                    result_set.append({'id': shugam.id, 'name': shugam.shugam_ner})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"Shugam" model has no object: %s', e)

        if 'end_ded_stants' in request.GET:
            ded_stants_id = request.GET['end_ded_stants']
            result_set = []
            try:
                shugams = Shugam.objects.filter(ded_stants_id=ded_stants_id)
                for shugam in shugams:
                    result_set.append({'id': shugam.id, 'name': shugam.shugam_ner})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"Shugam" model has no object: %s', e)

        data = {
            'action': '/home/lavlagaa/add_cable',
            'ded_stants': CableList.ded_stants,
            'menu': self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        trass = None
        if 'trass' in request.FILES:
            form = CableTrassForm(request.POST, request.FILES)
            if form.is_valid():
                trass = request.FILES['trass']

        try:
            suuriluulsan_ognoo = datetime.strptime(request.POST['suuriluulsan_ognoo'], '%Y-%m-%d')
            cable = Cable(created_user_id=request.user.id, ner=request.POST['cable_ner'], urt=request.POST['cable_urt'],
                          tip=request.POST['cable_tip'], mulfi_too=request.POST['mulfi_too'],
                          suuriluulsan_ognoo=suuriluulsan_ognoo,
                          trass=trass, start_ded_stants_id=int(request.POST['start_ded_stants']),
                          orolt_id=int(request.POST['orolt']),
                          end_ded_stants_id=int(request.POST['end_ded_stants']), garalt_id=int(request.POST['garalt']))
            cable.save()
            messages.success(request, 'Амжилттай хадгалагдлаа!')
        except Exception:
            messages.error(request, 'Хадгалахад алдаа гарлаа!')
            return redirect('/home/lavlagaa/add_cable')

        if "save_and_continue" in request.POST:
            return redirect('/home/lavlagaa/add_cable')
        else:
            return redirect('/home/lavlagaa/cable')


class CableEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_cable'
    template_name = 'homepage/lavlah/add_cable.html'
    menu = '7'

    def get(self, request, id, *args, **kwargs):
        try:
            cable = Cable.objects.get(id=id)
        except ObjectDoesNotExist:
            cable = None
        try:
            ded_stants = DedStants.objects.filter(is_active=1).order_by('name')
        except ObjectDoesNotExist:
            ded_stants = None
        try:
            orolts = Shugam.objects.filter(ded_stants_id=cable.start_ded_stants_id).order_by('shugam_ner')
        except ObjectDoesNotExist:
            orolts = None
        try:
            garalts = Shugam.objects.filter(ded_stants_id=cable.end_ded_stants_id).order_by('shugam_ner')
        except ObjectDoesNotExist:
            garalts = None

        data = {
            'menu': self.menu,
            'action': '/home/lavlagaa/edit_cable/'+id+'/',
            'cable': cable,
            'ded_stants': ded_stants,
            'orolts': orolts,
            'garalts': garalts,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        cable_id = request.POST['cable_id']

        try:
            cable = Cable.objects.get(id=int(cable_id))
            cable.ner = request.POST['cable_ner']
            cable.urt = request.POST['cable_urt']
            cable.tip = request.POST['cable_tip']
            cable.mulfi_too = request.POST['mulfi_too']
            suuriluulsan_ognoo = datetime.strptime(request.POST['suuriluulsan_ognoo'], '%Y-%m-%d')
            cable.suuriluulsan_ognoo = suuriluulsan_ognoo
            trass = cable.trass
            if 'trass' in request.FILES:
                form = CableTrassForm(request.POST, request.FILES)
                if form.is_valid():
                    trass = request.FILES['trass']
            cable.trass = trass
            try:
                orolt = Shugam.objects.get(id=int(request.POST['orolt']))
            except ObjectDoesNotExist as e:
                orolt = None
                logging.error('"Shugam" model has no object: %s', e)
            cable.orolt = orolt
            try:
                garalt = Shugam.objects.get(id=int(request.POST['garalt']))
            except ObjectDoesNotExist as e:
                garalt = None
                logging.error('"Shugam" model has no object: %s', e)
            cable.garalt = garalt
            cable.save()
            messages.success(request, 'Амжилттай засварлагдлаа!')
        except Exception as e:
            messages.error(request, 'Засварлахад алдаа гарлаа!')
            logging.error('%s', e)

        return redirect('/home/lavlagaa/cable')


class CableDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_cable'

    def get(self, request, id, *args, **kwargs):
        try:
            cable = Cable.objects.get(id=id)
            cable.is_active = 0
            cable.save()
            messages.success(request, 'Ажилттай устгагдлаа!')
        except ObjectDoesNotExist as e:
            messages.error(request, 'Устахад алдаа гарлаа!')
            logging.error('"Shugam" model has no object: %s', e)

        return redirect('/home/lavlagaa/cable')