import logging

import simplejson
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from datetime import datetime
from apps.data.models import DedStants, NaryadMedeelel, Shugam


class NaryadMedeelelList(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_naryadmedeelel'
    template_name = "homepage/ashiglalt/naryad_medeelel_list.html"
    menu = '4'
    sub = '4'

    qry = "SELECT naryad.id, naryad.naryad_dugaar, naryad.ajil_name, naryad.ajil_start_date, naryad.ajil_end_date, ded.name AS ded_stants_name," \
          " narolg.first_name AS narolg_first_name, narolg.last_name AS narolg_last_name, udird.first_name AS udird_first_name," \
          " udird.last_name AS udird_last_name, guitsed.first_name AS guitsed_first_name, guitsed.last_name AS guitsed_last_name," \
          " ajig.first_name AS ajig_first_name, ajig.last_name AS ajig_last_name, zuvolg.first_name AS zuvolg_first_name," \
          " zuvolg.last_name AS zuvolg_last_name, oruul.first_name AS oruul_first_name, oruul.last_name AS oruul_last_name" \
          " FROM data_naryadmedeelel naryad" \
          " JOIN data_dedstants ded ON naryad.ded_stants_id=ded.id" \
          " JOIN auth_user narolg ON naryad.naryad_olgogch_id=narolg.id" \
          " JOIN auth_user udird ON naryad.udirdagch_id=udird.id" \
          " JOIN auth_user guitsed ON naryad.guitsedgegch_id=guitsed.id" \
          " LEFT JOIN auth_user ajig ON naryad.ajiglagch_id=ajig.id" \
          " JOIN auth_user zuvolg ON naryad.zuv_olgogch_id=zuvolg.id" \
          " JOIN auth_user oruul ON naryad.ajil_oruulagch_id=oruul.id" \
          " WHERE naryad.is_active=1"
    try:
        ded_stants = DedStants.objects.filter(is_active=1).order_by('name')
    except ObjectDoesNotExist:
        ded_stants = None
    try:
        naryad_members = User.objects.filter(Q(groups__name='АА-ны менежер') | Q(groups__name='Ахлах диспетчер инженер') |
                                             Q(groups__name='Баримт бичгийн ажилтан') | Q(groups__name='Диспетчер инженер') |
                                             Q(groups__name='Инженер') | Q(groups__name='Монтёр') | Q(groups__name='Угсралтын инженер') |
                                             Q(groups__name='Борлуулалт тооцооны ахлах инженер'))
    except ObjectDoesNotExist:
        naryad_members = None

    def get(self, request, *args, **kwargs):
        q = self.qry
        q = q + " ORDER BY naryad.created_date DESC"

        try:
            naryad_list = NaryadMedeelel.objects.raw(q)
        except ObjectDoesNotExist:
            naryad_list = None

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
            'naryad_list': naryad_list,
            'ded_stants': self.ded_stants,
            'naryad_members': self.naryad_members,
            'menu': self.menu,
            'sub': self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        ded_stants = request.POST['ded_stants']
        ajil_name = request.POST['ajil_name']
        ajil_start_date = request.POST['ajil_start_date']
        ajil_end_date = request.POST['ajil_end_date']
        zuv_olgogch = request.POST['zuv_olgogch']
        udirdagch = request.POST['udirdagch']
        guitsedgegch = request.POST['guitsedgegch']
        naryad_olgogch = request.POST['naryad_olgogch']
        ajil_oruulagch = request.POST['ajil_oruulagch']

        q = self.qry

        if ded_stants != '':
            q = q + " AND naryad.ded_stants_id LIKE '%%" + ded_stants + "%%'"
        if ajil_name != '':
            q = q + " AND naryad.ajil_name LIKE '%%" + ajil_name + "%%'"
        if ajil_start_date != '':
            q = q + " AND naryad.ajil_start_date >= '" + ajil_start_date + "'"
        if ajil_end_date != '':
            q = q + " AND naryad.ajil_end_date <= '" + ajil_end_date + "'"
        if zuv_olgogch != '':
            q = q + " AND naryad.zuv_olgogch_id LIKE '%%" + zuv_olgogch + "%%'"
        if udirdagch != '':
            q = q + " AND naryad.udirdagch_id LIKE '%%" + udirdagch + "%%'"
        if guitsedgegch != '':
            q = q + " AND naryad.guitsedgegch_id LIKE '%%" + guitsedgegch + "%%'"
        if naryad_olgogch != '':
            q = q + " AND naryad.naryad_olgogch_id LIKE '%%" + naryad_olgogch + "%%'"
        if ajil_oruulagch != '':
            q = q + " AND naryad.ajil_oruulagch_id LIKE '%%" + ajil_oruulagch + "%%'"


        try:
            naryad_list = NaryadMedeelel.objects.raw(q)
        except ObjectDoesNotExist:
            naryad_list = None

        data = {
            'naryad_list': naryad_list,
            'ded_stants': self.ded_stants,
            'naryad_members': self.naryad_members,
            'menu': self.menu,
            'sub': self.sub,
            'qry': {
                'ded_stants': int(ded_stants) if ded_stants != '' else ded_stants,
                'ajil_name': ajil_name,
                'ajil_start_date': ajil_start_date,
                'ajil_end_date': ajil_end_date,
                'zuv_olgogch': int(zuv_olgogch) if zuv_olgogch != '' else zuv_olgogch,
                'udirdagch': int(udirdagch) if udirdagch != '' else udirdagch,
                'guitsedgegch': int(guitsedgegch) if guitsedgegch != '' else guitsedgegch,
                'naryad_olgogch': int(naryad_olgogch) if naryad_olgogch != '' else naryad_olgogch,
                'ajil_oruulagch': int(ajil_oruulagch) if ajil_oruulagch != '' else ajil_oruulagch,
            }
        }
        return render(request, self.template_name, data)


class NaryadMedeelelAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_naryadmedeelel'
    template_name = "homepage/ashiglalt/naryad_medeelel_add.html"
    menu = '4'
    sub = '4'

    def get(self, request, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.filter(is_active=1).order_by('name')
        except ObjectDoesNotExist:
            ded_stants = None
        try:
            naryad_members = User.objects.filter(Q(groups__name='АА-ны менежер') | Q(groups__name='Ахлах диспетчер инженер') |
                                                 Q(groups__name='Баримт бичгийн ажилтан') | Q(groups__name='Диспетчер инженер') |
                                                 Q(groups__name='Инженер') | Q(groups__name='Монтёр') | Q(groups__name='Угсралтын инженер') |
                                                 Q(groups__name='Борлуулалт тооцооны ахлах инженер'))
        except ObjectDoesNotExist:
            naryad_members = None

        data = {
            'action': '/home/ashiglalt/naryad_medeelel_add',
            'ded_stants': ded_stants,
            'naryad_members': naryad_members,
            'menu': self.menu,
            'sub': self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        brigad_members = request.POST.getlist('brigad_members', '')
        ajil_start_date = datetime.strptime(request.POST['ajil_start_date'], '%Y-%m-%d %H:%M')
        ajil_end_date = datetime.strptime(request.POST['ajil_end_date'], '%Y-%m-%d %H:%M')
        om_full_names = request.POST.getlist('om_full_name', '')
        try:
            naryad = NaryadMedeelel.objects.create(ded_stants_id=request.POST['ded_stants'], ajil_start_date=ajil_start_date,
                                                  ajil_end_date=ajil_end_date, naryad_olgogch_id=request.POST['naryad_olgogch'],
                                                  ajil_name=request.POST['ajil_name'], udirdagch_id=request.POST['udirdagch'],
                                                  guitsedgegch_id=request.POST['guitsedgegch'], zuv_olgogch_id=request.POST['zuv_olgogch'],
                                                  ajil_oruulagch_id=request.POST['ajil_oruulagch'], naryad_dugaar=request.POST['naryad_dugaar'],
                                                  ajiglagch_id=request.POST['ajiglagch'])
            naryad.ayulgui_baidal = request.POST['ayulgui_baidal']
            om_names = ''
            for om_full_name in om_full_names:
                om_names += om_full_name + ';'
            naryad.other_members = om_names
            naryad.created_user_id = request.user.id
            for brigad_member in brigad_members:
                user = User.objects.get(id=brigad_member)
                naryad.brigad_members.add(user)
            naryad.save()
            messages.success(request, 'Амжилттай хадгалагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Хадгалахад алдаа гарлаа!')
            return redirect('/home/ashiglalt/naryad_medeelel_add')

        return redirect('/home/ashiglalt/naryad_medeelel_list')


class NaryadMedeelelEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_naryadmedeelel'
    template_name = 'homepage/ashiglalt/naryad_medeelel_add.html'
    menu = '4'
    sub = '4'

    def get(self, request, id, *args, **kwargs):
        om_full_names = []
        try:
            naryad = NaryadMedeelel.objects.get(id=id)
            if naryad.other_members:
                other_members = naryad.other_members.split(';')
                other_members.pop(len(other_members)-1)
                for other_member in other_members:
                    om_full_names.append(other_member)
        except ObjectDoesNotExist:
            naryad = None
        try:
            ded_stants = DedStants.objects.filter(is_active=1).order_by('name')
        except ObjectDoesNotExist:
            ded_stants = None
        brigad_member_ids = []
        try:
            for brigad_member in naryad.brigad_members_list:
                brigad_member_ids.append(brigad_member.id)
        except Exception as e:
            logging.error('%s', e)
        try:
            naryad_members = User.objects.filter(Q(groups__name='АА-ны менежер') | Q(groups__name='Ахлах диспетчер инженер') |
                                                 Q(groups__name='Баримт бичгийн ажилтан') | Q(groups__name='Диспетчер инженер') |
                                                 Q(groups__name='Инженер') | Q(groups__name='Монтёр') | Q(groups__name='Угсралтын инженер') |
                                                 Q(groups__name='Борлуулалт тооцооны ахлах инженер'))
        except ObjectDoesNotExist:
            naryad_members = None
        try:
            naryad_members_in = User.objects.filter(Q(groups__name='АА-ны менежер') | Q(groups__name='Ахлах диспетчер инженер') |
                                                 Q(groups__name='Баримт бичгийн ажилтан') | Q(groups__name='Диспетчер инженер') |
                                                 Q(groups__name='Инженер') | Q(groups__name='Монтёр') | Q(groups__name='Угсралтын инженер') |
                                                 Q(groups__name='Борлуулалт тооцооны ахлах инженер')).filter(Q(id__in=brigad_member_ids))
        except ObjectDoesNotExist:
            naryad_members_in = None
        try:
            naryad_members_out = User.objects.filter(Q(groups__name='АА-ны менежер') | Q(groups__name='Ахлах диспетчер инженер') |
                                                     Q(groups__name='Баримт бичгийн ажилтан') | Q(groups__name='Диспетчер инженер') |
                                                     Q(groups__name='Инженер') | Q(groups__name='Монтёр') | Q(groups__name='Угсралтын инженер') |
                                                     Q(groups__name='Борлуулалт тооцооны ахлах инженер')).filter(~Q(id__in=brigad_member_ids))
        except ObjectDoesNotExist:
            naryad_members_out = None

        data = {
            'action': '/home/ashiglalt/naryad_medeelel_edit/'+id+'/',
            'naryad': naryad,
            'ded_stants': ded_stants,
            'naryad_members_in': naryad_members_in,
            'naryad_members': naryad_members,
            'om_full_names': om_full_names,
            'naryad_members_out': naryad_members_out,
            'menu': self.menu,
            'sub': self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        brigad_members = request.POST.getlist('brigad_members', '')
        om_full_names = request.POST.getlist('om_full_name', '')
        ajil_start_date = datetime.strptime(request.POST['ajil_start_date'], '%Y-%m-%d %H:%M')
        ajil_end_date = datetime.strptime(request.POST['ajil_end_date'], '%Y-%m-%d %H:%M')
        try:
            naryad = NaryadMedeelel.objects.get(id=id)
            naryad.ded_stants_id = request.POST['ded_stants']
            naryad.naryad_olgogch_id = request.POST['naryad_olgogch']
            naryad.zuv_olgogch_id = request.POST['zuv_olgogch']
            naryad.udirdagch_id = request.POST['udirdagch']
            naryad.guitsedgegch_id = request.POST['guitsedgegch']
            naryad.naryad_dugaar = request.POST['naryad_dugaar']
            naryad.ajil_name = request.POST['ajil_name']
            naryad.ajil_start_date = ajil_start_date
            naryad.ajil_end_date = ajil_end_date
            naryad.ayulgui_baidal = request.POST['ayulgui_baidal']
            naryad.ajiglagch_id = request.POST['ajiglagch']
            naryad.ajil_oruulagch_id = request.POST['ajil_oruulagch']
            for member in naryad.brigad_members_list:
                naryad.brigad_members.remove(member)
            if len(brigad_members) > 0:
                for brigad_member in brigad_members:
                    user = User.objects.get(id=brigad_member)
                    naryad.brigad_members.add(user)
            om_names = ''
            for om_full_name in om_full_names:
                om_names += om_full_name + ';'
            naryad.other_members = om_names
            naryad.save()
            messages.success(request, 'Амжилттай засварлагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Засварлахад алдаа гарлаа!')
            return redirect('/home/ashiglalt/naryad_medeelel_add')

        return redirect('/home/ashiglalt/naryad_medeelel_list')


class NaryadMedeelelDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_naryadmedeelel'

    def get(self, request, id, *args, **kwargs):
        try:
            naryad = NaryadMedeelel.objects.get(id=id)
            naryad.is_active = 0
            naryad.save()
            messages.success(request, 'Амжилттай устгагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Устахад алдаа гарлаа!')

        return redirect('/home/ashiglalt/naryad_medeelel_list')