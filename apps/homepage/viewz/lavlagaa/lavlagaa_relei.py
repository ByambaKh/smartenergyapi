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
from apps.data.models import Shugam, Relei, DedStants


class ReleiList(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_relei'
    template_name = 'homepage/lavlah/relei.html'
    menu = '7'
    starter_q = "SELECT rel.id, rel.ner, rel.tip, rel.suuriluulsan_ognoo, rel.hugatsaa_barilttai, rel.hugatsaa_bariltgui," \
                " rel.gazardalt, shug.shugam_ner, ded.name FROM data_relei rel" \
                " JOIN data_shugam shug ON rel.shugam_id=shug.id" \
                " JOIN data_dedstants ded ON rel.ded_stants_id=ded.id" \
                " WHERE rel.is_active = 1"

    def get(self, request, *args, **kwargs):
        q = self.starter_q
        q = q + " ORDER BY rel.created_date DESC"

        try:
            releis = Relei.objects.raw(q)
        except ObjectDoesNotExist as e:
            releis = None
        try:
            ded_stants = DedStants.objects.filter(is_active=1)
        except DedStants.DoesNotExist as e:
            ded_stants = None

        if 'ded_stants' in request.GET:
            ded_stants_id = request.GET['ded_stants']
            result_set = []
            try:
                shugams = Shugam.objects.filter(ded_stants_id=ded_stants_id)
                for shugam in shugams:
                    result_set.append({'id': shugam.id, 'name': shugam.shugam_ner})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"Shugam" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'releis': releis,
            'ded_stants': ded_stants,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        ner = request.POST['ner']
        ded_stants = request.POST['ded_stants']
        shugam = request.POST['shugam']
        tip = request.POST['tip']
        suuriluulsan_ognoo = request.POST['suuriluulsan_ognoo']

        q = self.starter_q

        if ner != '':
            q = q + " AND rel.ner LIKE '%%" + ner + "%%'"
        if shugam != '':
            q = q + " AND shug.id LIKE '%%" + shugam + "%%'"
            shugam = int(shugam)
        if ded_stants != '':
            q = q + " AND ded.id LIKE '%%" + ded_stants + "%%'"
            ded_stants = int(ded_stants)
        if tip != '':
            q = q + " AND rel.tip LIKE '%%" + tip + "%%'"
        if suuriluulsan_ognoo != '':
            q = q + " AND rel.suuriluulsan_ognoo >= '"+ suuriluulsan_ognoo +"'"

        try:
            releis = Relei.objects.raw(q)
        except ObjectDoesNotExist as e:
            releis = None
            logging.error('"Relei" model has no object: %s', e)
        try:
            ded_stants_all = DedStants.objects.filter(is_active=1)
        except DedStants.DoesNotExist as e:
            ded_stants_all = None
        data = {
            'menu': self.menu,
            'releis': releis,
            'ded_stants': ded_stants_all,
            'search_q': {
                'ner': ner,
                'shugam': shugam,
                'ded_stants': ded_stants,
                'tip': tip,
                'suuriluulsan_ognoo': suuriluulsan_ognoo,
            }
        }
        return render(request, self.template_name, data)


class ReleiAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_relei'
    template_name = 'homepage/lavlah/add_relei.html'
    menu = '7'

    def get(self, request, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.filter(is_active=1)
        except DedStants.DoesNotExist as e:
            ded_stants = None
            logging.error('"DedStants" model has no object: %s', e)

        if 'ded_stants' in request.GET:
            ded_stants_id = request.GET['ded_stants']
            result_set = []
            try:
                shugams = Shugam.objects.filter(ded_stants_id=ded_stants_id, is_active=1)
                for shugam in shugams:
                    result_set.append({'id': shugam.id, 'name': shugam.shugam_ner, 'tuluv': shugam.shugam_tuluv})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"Shugam" model has no object: %s', e)

        data = {
            'action': '/home/lavlagaa/add_relei',
            'ded_stants': ded_stants,
            'menu': self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        try:
            shugam = Shugam.objects.get(id=int(request.POST['shugam']))
        except Exception:
            shugam = None


        try:
            ded_stants = DedStants.objects.get(id=int(request.POST['ded_stants']))
        except Exception:
            ded_stants = None

        if shugam is not None:
            try:
                suuriluulsan_ognoo = datetime.strptime(request.POST['suuriluulsan_ognoo'], '%Y-%m-%d')
                relei = Relei(ner=request.POST['ner'], tip=request.POST['tip'], shugam=shugam, ded_stants=ded_stants, suuriluulsan_ognoo=suuriluulsan_ognoo, hugatsaa_barilttai=request.POST['hugatsaa_barilttai'], hugatsaa_bariltgui=request.POST['hugatsaa_bariltgui'], gazardalt=request.POST['gazardalt'], created_user_id=request.user.id)
                relei.save()
                messages.success(request, 'Амжилттай хадгалагдлаа!')
            except Exception as e:
                messages.error(request, 'Хадгалахад алдаа гарлаа!')
                return redirect('/home/lavlagaa/add_relei')

            if "save_and_continue" in request.POST:
                return redirect('/home/lavlagaa/add_relei')
            else:
                return redirect('/home/lavlagaa/relei')
        else:
            try:
                shugams = Shugam.objects.filter(is_active=1)
                ded_stants = DedStants.objects.filter(is_active=1)
            except ObjectDoesNotExist as e:
                shugams = None
                logging.error('"Shugam" model has no object: %s', e)

            data = {
                'action': '/home/lavlagaa/add_relei',
                'ded_stants': ded_stants,
                'shugams': shugams,
                'menu': self.menu,
            }
            return render(request, self.template_name, data)


class ReleiEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_relei'
    template_name = 'homepage/lavlah/add_relei.html'
    menu = '7'

    def get(self, request, id, *args, **kwargs):
        try:
            relei = Relei.objects.get(id=id)
        except ObjectDoesNotExist:
            relei = None
        try:
            ded_stants = DedStants.objects.filter(is_active=1)
        except DedStants.DoesNotExist:
            ded_stants = None
        try:
            shugams = Shugam.objects.filter(ded_stants_id=relei.ded_stants_id)
        except ObjectDoesNotExist:
            shugams = None

        if 'ded_stants' in request.GET:
            ded_stants_id = request.GET['ded_stants']
            result_set = []
            try:
                shugams = Shugam.objects.filter(ded_stants_id=ded_stants_id)
                for shugam in shugams:
                    result_set.append({'id': shugam.id, 'name': shugam.shugam_ner})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"Shugam" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'action': '/home/lavlagaa/edit_relei/'+id+'/',
            'relei': relei,
            'ded_stants': ded_stants,
            'shugams': shugams,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        relei_id = request.POST['relei_id']

        try:
            relei = Relei.objects.get(id=int(relei_id))
            relei.ner = request.POST['ner']
            relei.tip = request.POST['tip']
            relei.hugatsaa_barilttai = request.POST['hugatsaa_barilttai']
            relei.hugatsaa_bariltgui = request.POST['hugatsaa_bariltgui']
            relei.gazardalt = request.POST['gazardalt']
            suuriluulsan_ognoo = datetime.strptime(request.POST['suuriluulsan_ognoo'], '%Y-%m-%d')
            relei.suuriluulsan_ognoo = suuriluulsan_ognoo
            try:
                shugam = Shugam.objects.get(id=int(request.POST['shugam']))
            except ObjectDoesNotExist as e:
                shugam = None
                logging.error('"DedStants" model has no object: %s', e)
            relei.shugam = shugam
            try:
                ded_stants = DedStants.objects.get(id=int(request.POST['ded_stants']))
            except DedStants.DoesNotExist as e:
                ded_stants = None
                logging.error('"DedStants" model has no object: %s', e)
            relei.ded_stants = ded_stants
            relei.save()
            messages.success(request, 'Амжилттай засварлагдлаа!')
        except Exception as e:
            messages.error(request, 'Засварлахад алдаа гарлаа!')
            logging.error('%s', e)

        return redirect('/home/lavlagaa/relei')


class ReleiDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_relei'

    def get(self, request, id, *args, **kwargs):
        try:
            relei = Relei.objects.get(id=id)
            relei.is_active = 0
            relei.save()
            messages.success(request, 'Ажилттай устгагдлаа!')
        except ObjectDoesNotExist as e:
            messages.error(request, 'Устахад алдаа гарлаа!')
            logging.error('"Relei" model has no object: %s', e)

        return redirect('/home/lavlagaa/relei')