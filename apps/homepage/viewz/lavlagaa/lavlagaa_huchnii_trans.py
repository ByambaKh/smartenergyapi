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
from apps.data.models import DedStants, Shugam, PowerTransformator


class HuchniiTransList(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_powertransformator'
    template_name = 'homepage/lavlah/huchnii_trans.html'
    menu = '7'
    starter_q = "SELECT power.id, power.ner, power.chadal, power.tip, power.ajillasan_tsag," \
                " power.uildverlesen_ognoo, power.antsaf, power.suuriluulsan_ognoo, ded.name, shug.shugam_ner" \
                " FROM data_powertransformator power" \
                " JOIN data_dedstants ded ON power.ded_stants_id=ded.id" \
                " JOIN data_shugam shug ON power.shugam_id=shug.id" \
                " WHERE power.is_active = 1"
    try:
        ded_stants = DedStants.objects.filter(is_active=1).order_by('name')
    except ObjectDoesNotExist:
        ded_stants = None
    try:
        shugams = Shugam.objects.filter(is_active=1).order_by('shugam_ner')
    except ObjectDoesNotExist:
        shugams = None

    def get(self, request, *args, **kwargs):
        if 'ded_stants' in request.GET:
            ded_stants_id = request.GET['ded_stants']
            result_set = []
            try:
                shugams = Shugam.objects.filter(ded_stants_id=ded_stants_id)
                for shugam in shugams:
                    result_set.append({'id': shugam.id, 'name': shugam.shugam_ner, 'tuluv': shugam.shugam_tuluv})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"Shugam" model has no object: %s', e)

        try:
            q = self.starter_q
            q = q + " GROUP BY power.ded_stants_id ORDER BY power.created_date DESC"
            trans = PowerTransformator.objects.raw(q)
            total_chadal = self.total_chadal(trans)
        except ObjectDoesNotExist as e:
            trans = None
            total_chadal = None
            logging.error('"PowerTransformator" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'trans': trans,
            'ded_stants': self.ded_stants,
            'shugams': self.shugams,
            'total_chadal': total_chadal,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        ner = request.POST['ner']
        chadal = request.POST['chadal']
        tip = request.POST['tip']
        ded_stants = request.POST['ded_stants']
        shugam = request.POST['shugam']

        q = self.starter_q

        if ner != '':
            q = q + " AND power.ner LIKE '%%" + ner + "%%'"
        if tip != '':
            q = q + " AND power.tip LIKE '%%" + tip + "%%'"
        if ded_stants != '':
            q = q + " AND ded.id LIKE '%%" + ded_stants + "%%'"
        if chadal != '':
            q = q + " AND power.chadal LIKE '%%" + chadal + "%%'"
        if shugam != '':
            q = q + " AND shug.id LIKE '%%" + shugam + "%%'"

        try:
            trans = PowerTransformator.objects.raw(q)
        except ObjectDoesNotExist as e:
            trans = None
            logging.error('"PowerTransformator" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'trans': trans,
            'ded_stants': self.ded_stants,
            'shugams': self.shugams,
            'search_q': {
                'ner': ner,
                'tip': tip,
                'ded_stants': ded_stants,
                'chadal': chadal,
                'shugam': shugam,
            }
        }
        return render(request, self.template_name, data)

    def total_chadal(self, datas):
        total = 0
        try:
            for item in datas:
                total = total + float(item.chadal)
        except Exception:
            print("error")
        return total


class HuchniiTransAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_powertransformator'
    template_name = 'homepage/lavlah/add_huchnii_trans.html'
    menu = '7'

    def get(self, request, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.filter(is_active=1)
        except ObjectDoesNotExist as e:
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
            'action': '/home/lavlagaa/add_huchnii_trans',
            'ded_stants': ded_stants,
            'menu': self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.get(id=request.POST['ded_stants'])
        except ObjectDoesNotExist as e:
            ded_stants = None

        try:
            shugam = Shugam.objects.get(id=request.POST['shugam'])
        except ObjectDoesNotExist as e:
            shugam = None

        if shugam is not None and ded_stants is not None:
            try:
                suuriluulsan_ognoo = datetime.strptime(request.POST['suuriluulsan_ognoo'], '%Y-%m-%d %H:%M')
                uildverlesen_ognoo = datetime.strptime(request.POST['uildverlesen_ognoo'], '%Y-%m-%d')
                transformator = PowerTransformator(ner=request.POST['ner'], chadal=request.POST['chadal'], tip=request.POST['tip'], ajillasan_tsag=request.POST['ajillasan_tsag'], ded_stants=ded_stants, shugam=shugam, suuriluulsan_ognoo=suuriluulsan_ognoo, uildverlesen_ognoo=uildverlesen_ognoo, antsaf=request.POST['antsaf'], created_user_id=request.user.id)
                transformator.save()
                messages.success(request, 'Амжилттай хадгалагдлаа!')
            except Exception as e:
                messages.error(request, 'Хадгалахад алдаа гарлаа!')
                logging.error('%s', e)
            return redirect('/home/lavlagaa/huchnii_trans')
        else:
            try:
                ded_stants = DedStants.objects.filter(is_active=1)
            except ObjectDoesNotExist as e:
                ded_stants = None
                logging.error('"DedStants" model has no object: %s', e)

            try:
                shugams = Shugam.objects.filter(is_active=1)
            except ObjectDoesNotExist as e:
                shugams = None
                logging.error('"Shugam" model has no object: %s', e)

            data = {
                'action': '/home/lavlagaa/add_huchnii_trans',
                'ded_stants': ded_stants,
                'shugams': shugams,
                'menu': self.menu,
            }
            return render(request, self.template_name, data)


class HuchniiTransEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_powertransformator'
    template_name = 'homepage/lavlah/add_huchnii_trans.html'
    menu = '7'

    def get(self, request, id, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.filter(is_active=1)
        except ObjectDoesNotExist as e:
            ded_stants = None
            logging.error('"DedStants" model has no object: %s', e)

        try:
            shugams = Shugam.objects.filter(is_active=1)
        except ObjectDoesNotExist as e:
            shugams = None
            logging.error('"Shugam" model has no object: %s', e)

        try:
            transformator = PowerTransformator.objects.get(id=id)
        except ObjectDoesNotExist as e:
            transformator = None
            logging.error('"Transformator" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'action': '/home/lavlagaa/edit_huchnii_trans/'+id+'/',
            'transformator': transformator,
            'shugams': shugams,
            'ded_stants': ded_stants,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        transformator_id = request.POST['transformator_id']

        try:
            ded_stant = DedStants.objects.get(id=int(request.POST['ded_stants']))
        except ObjectDoesNotExist as e:
            ded_stant = None
            logging.error('"DedStants" model has no object: %s', e)

        try:
            shugam = Shugam.objects.get(id=int(request.POST['shugam']))
        except ObjectDoesNotExist as e:
            shugam = None
            logging.error('"Shugam" model has no object: %s', e)

        try:
            transformator = PowerTransformator.objects.get(id=int(transformator_id))
            suuriluulsan_ognoo = datetime.strptime(request.POST['suuriluulsan_ognoo'], '%m/%d/%Y %H:%M %p')
            uildverlesen_ognoo = datetime.strptime(request.POST['uildverlesen_ognoo'], '%Y-%m-%d')
            transformator.suuriluulsan_ognoo = suuriluulsan_ognoo
            transformator.ner = request.POST['ner']
            transformator.chadal = request.POST['chadal']
            transformator.tip = request.POST['tip']
            transformator.ajillasan_tsag = request.POST['ajillasan_tsag']
            transformator.shugam = shugam
            transformator.ded_stants = ded_stant
            transformator.antsaf = request.POST['antsaf']
            transformator.uildverlesen_ognoo = uildverlesen_ognoo
            transformator.save()
            messages.success(request, 'Амжилттай засварлагдлаа!')
        except Exception as e:
            messages.error(request, 'Засварлахад алдаа гарлаа!')
            logging.error('%s', e)

        if "save_and_continue" in request:
            return redirect('/home/lavlagaa/add_huchnii_trans')
        else:
            return redirect('/home/lavlagaa/huchnii_trans')


class HuchniiTransDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_powertransformator'

    def get(self, request, id, *args, **kwargs):
        try:
            transformator = PowerTransformator.objects.get(id=id)
            transformator.is_active = 0
            transformator.save()
            messages.success(request, 'Ажилттай устгагдлаа!')
        except ObjectDoesNotExist as e:
            messages.error(request, 'Устахад алдаа гарлаа!')
            logging.error('"Transformator" model has no object: %s', e)

        return redirect('/home/lavlagaa/huchnii_trans')