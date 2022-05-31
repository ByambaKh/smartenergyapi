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
from apps.data.models import AshiglaltZaavarchilgaa, ZaavarchilgaaCategory, Zaavarchilgaa, ZaavarchilgaaUsers


class AshiglaltZaavarchilgaaList(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_ashiglaltzaavarchilgaa'
    template_name = "homepage/ashiglalt/zaavarchilgaa_list.html"
    menu = '4'
    sub = '7'

    try:
        ugsuns = User.objects.filter(Q(groups__name='АА-ны менежер') | Q(groups__name='Ахлах диспетчер инженер') |
                                     Q(groups__name='Диспетчер инженер') | Q(groups__name='Инженер') |
                                     Q(groups__name='Угсралтын инженер'))
    except ObjectDoesNotExist:
        ugsuns = None
    try:
        avsans = User.objects.filter(Q(groups__name='АА-ны менежер') | Q(groups__name='Ахлах диспетчер инженер') |
                                     Q(groups__name='Баримт бичгийн ажилтан') | Q(groups__name='Диспетчер инженер') |
                                     Q(groups__name='Инженер') | Q(groups__name='Монтёр') | Q(groups__name='Угсралтын инженер'))
    except ObjectDoesNotExist:
        avsans = None

    def get(self, request, *args, **kwargs):
        try:
            zaavarchilgaas = AshiglaltZaavarchilgaa.objects.filter(is_active=1).order_by('-ognoo')
        except ObjectDoesNotExist:
            zaavarchilgaas = None

        data = {
            'zaavarchilgaas': zaavarchilgaas,
            'ugsuns': self.ugsuns,
            'menu': self.menu,
            'sub': self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        zaavar_ugsun = request.POST['zaavar_ugsun']
        start_ognoo = request.POST['start_ognoo']
        end_ognoo = request.POST['end_ognoo']

        if zaavar_ugsun != '':
            try:
                zaavarchilgaas = AshiglaltZaavarchilgaa.objects.filter(is_active=1).filter(zaavar_ugsun_id=zaavar_ugsun)
            except ObjectDoesNotExist:
                zaavarchilgaas = None
        elif start_ognoo != '':
            try:
                zaavarchilgaas = AshiglaltZaavarchilgaa.objects.filter(is_active=1).filter(ognoo__date=start_ognoo)
            except ObjectDoesNotExist:
                zaavarchilgaas = None
        elif start_ognoo != '' and end_ognoo != '':
            try:
                zaavarchilgaas = AshiglaltZaavarchilgaa.objects.filter(is_active=1).filter(ognoo__range=[start_ognoo, end_ognoo])
            except ObjectDoesNotExist:
                zaavarchilgaas = None
        elif zaavar_ugsun != '' and start_ognoo != '' and end_ognoo != '':
            try:
                zaavarchilgaas = AshiglaltZaavarchilgaa.objects.filter(is_active=1).filter(ognoo__range=[start_ognoo, end_ognoo]).filter(zaavar_ugsun_id=zaavar_ugsun)
            except ObjectDoesNotExist:
                zaavarchilgaas = None
        else:
            try:
                zaavarchilgaas = AshiglaltZaavarchilgaa.objects.filter(is_active=1).order_by('-ognoo')
            except ObjectDoesNotExist:
                zaavarchilgaas = None

        data = {
            'zaavarchilgaas': zaavarchilgaas,
            'ugsuns': self.ugsuns,
            'menu': self.menu,
            'sub': self.sub,
            'qry': {
                'zaavar_ugsun': int(zaavar_ugsun) if zaavar_ugsun != '' else zaavar_ugsun,
                'start_ognoo': start_ognoo,
                'end_ognoo': end_ognoo,
            }
        }
        return render(request, self.template_name, data)


class AshiglaltZaavarchilgaaAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_ashiglaltzaavarchilgaa'
    template_name = "homepage/ashiglalt/zaavarchilgaa_add.html"
    menu = '4'
    sub = '7'

    try:
        categories = ZaavarchilgaaCategory.objects.filter(is_active=1).order_by('name')
    except ObjectDoesNotExist:
        categories = None

    def get(self, request, *args, **kwargs):
        if 'category' in request.GET:
            category_id = request.GET['category']
            result_set = []
            try:
                zaavarchilgaas = Zaavarchilgaa.objects.filter(category_id=category_id,is_active=1)
                for zaavarchilgaa in zaavarchilgaas:
                    result_set.append({'id': zaavarchilgaa.id, 'title': zaavarchilgaa.title})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"Zaavarchilgaa" model has no object: %s', e)

        data = {
            'action': '/home/ashiglalt/zaavarchilgaa_add',
            'ugsuns': AshiglaltZaavarchilgaaList.ugsuns,
            'avsans': AshiglaltZaavarchilgaaList.avsans,
            'categories': self.categories,
            'menu': self.menu,
            'sub': self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        zaavar_ids = request.POST.getlist('zaavar_ids', '')
        zaavar_ids = zaavar_ids[0].split(',')
        zaavar_ugsun = request.POST['zaavar_ugsun']
        zaavar_avsans = request.POST.getlist('zaavar_avsan', '')

        try:
            last_id = max(AshiglaltZaavarchilgaa.objects.values_list('id', flat=True)) + 1
            ognoo = datetime.strptime(request.POST['ognoo'], '%m/%d/%Y %H:%M %p')
            zaavarchilgaa = AshiglaltZaavarchilgaa.objects.create(zaavar_ugsun_id=zaavar_ugsun, ognoo=ognoo)
            zaavarchilgaa.created_user_id = request.user.id
            for zaavar_avsan in zaavar_avsans:
                user = User.objects.get(id=zaavar_avsan)
                zaavarchilgaa.zaavar_avsan.add(user)
                zaavarchilgaa_users = ZaavarchilgaaUsers.objects.create(ashiglalt_zaavar_id=last_id, user_id=user.id)
                zaavarchilgaa_users.created_user_id = request.user.id
                zaavarchilgaa_users.save()
            for zaavar_id in zaavar_ids:
                zaavar = Zaavarchilgaa.objects.get(id=zaavar_id)
                zaavarchilgaa.zaavarchilgaa.add(zaavar)
            zaavarchilgaa.save()
            messages.success(request, 'Амжилттай хадгалагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Хадгалахад алдаа гарлаа!')
            return redirect('/home/ashiglalt/zaavarchilgaa_add')

        return redirect('/home/ashiglalt/zaavarchilgaa_list')


class AshiglaltZaavarchilgaaEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_ashiglaltzaavarchilgaa'
    template_name = 'homepage/ashiglalt/zaavarchilgaa_add.html'
    menu = '4'
    sub = '7'

    def get(self, request, id, *args, **kwargs):
        if 'zaavar_id' in request.GET:
            zaavar_id = request.GET['zaavar_id']
            result_set = []
            try:
                zaavarchilgaas = AshiglaltZaavarchilgaa.objects.get(id=zaavar_id)
                for zaavarchilgaa in zaavarchilgaas.zaavarchilgaa_list:
                    result_set.append({'id': zaavarchilgaa.id, 'title': zaavarchilgaa.title})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"AshiglaltZaavarchilgaa" model has no object: %s', e)

        if 'category' in request.GET:
            category_id = request.GET['category']
            result_set = []
            try:
                zaavarchilgaas = Zaavarchilgaa.objects.filter(category_id=category_id).filter(is_active='1').order_by('id')
                for zaavarchilgaa in zaavarchilgaas:
                    result_set.append({'id': zaavarchilgaa.id, 'title': zaavarchilgaa.title})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"Zaavarchilgaa" model has no object: %s', e)

        zaavar_avsan_ids = []
        try:
            zaavarchilgaa = AshiglaltZaavarchilgaa.objects.get(id=id)
            for zaavarchilgaa_id in zaavarchilgaa.zaavar_avsan_list:
                zaavar_avsan_ids.append(zaavarchilgaa_id.id)
        except ObjectDoesNotExist:
            zaavarchilgaa = None
        try:
            ugsuns = User.objects.filter(Q(groups__name='АА-ны менежер') | Q(groups__name='Ахлах диспетчер инженер') |
                                         Q(groups__name='Диспетчер инженер') | Q(groups__name='Инженер') |
                                         Q(groups__name='Угсралтын инженер'))
        except ObjectDoesNotExist:
            ugsuns = None
        try:
            avsans_out = User.objects.filter(Q(groups__name='АА-ны менежер') | Q(groups__name='Ахлах диспетчер инженер') |
                                         Q(groups__name='Баримт бичгийн ажилтан') | Q(groups__name='Диспетчер инженер') |
                                         Q(groups__name='Инженер') | Q(groups__name='Монтёр') |
                                         Q(groups__name='Угсралтын инженер')).filter(~Q(id__in=zaavar_avsan_ids))
        except ObjectDoesNotExist:
            avsans_out = None
        try:
            avsans_in = User.objects.filter(Q(groups__name='АА-ны менежер') | Q(groups__name='Ахлах диспетчер инженер') |
                                         Q(groups__name='Баримт бичгийн ажилтан') | Q(groups__name='Диспетчер инженер') |
                                         Q(groups__name='Инженер') | Q(groups__name='Монтёр') |
                                         Q(groups__name='Угсралтын инженер')).filter(Q(id__in=zaavar_avsan_ids))
        except ObjectDoesNotExist:
            avsans_in = None

        data = {
            'action': '/home/ashiglalt/zaavarchilgaa_edit/'+id+'/',
            'zaavarchilgaa': zaavarchilgaa,
            'ugsuns': ugsuns,
            'avsans_out': avsans_out,
            'avsans_in': avsans_in,
            'categories': AshiglaltZaavarchilgaaAdd.categories,
            'menu': self.menu,
            'sub': self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        zaavar_ids = request.POST.getlist('zaavar_ids', '')
        zaavar_ids = zaavar_ids[0].split(',')
        zaavar_avsans = request.POST.getlist('zaavar_avsan', '')
        ognoo = datetime.strptime(request.POST['ognoo'], '%m/%d/%Y %H:%M %p')

        try:
            zaavar_ugsun = User.objects.get(id=request.POST['zaavar_ugsun'])
        except ObjectDoesNotExist:
            zaavar_ugsun = None

        try:
            zaavarchilgaa = AshiglaltZaavarchilgaa.objects.get(id=id)
            zaavarchilgaa.zaavar_ugsun = zaavar_ugsun
            for zaavar in zaavarchilgaa.zaavarchilgaa_list:
                zaavarchilgaa.zaavarchilgaa.remove(zaavar)
            zaavarchilgaa_users = ZaavarchilgaaUsers.objects.filter(ashiglalt_zaavar_id=id)
            for zaavarchilgaa_user in zaavarchilgaa_users:
                zaavar_user = ZaavarchilgaaUsers.objects.get(id=zaavarchilgaa_user.id)
                zaavar_user.delete()
            if len(zaavar_avsans) > 0:
                for zaavar_avsan in zaavar_avsans:
                    user = User.objects.get(id=zaavar_avsan)
                    zaavarchilgaa.zaavar_avsan.add(user)
                    zaavarchilgaa_users = ZaavarchilgaaUsers.objects.create(ashiglalt_zaavar_id=id, user_id=user.id)
                    zaavarchilgaa_users.created_user_id = request.user.id
                    zaavarchilgaa_users.save()
            if len(zaavar_ids) > 0:
                for zaavar_id in zaavar_ids:
                    zaavar = Zaavarchilgaa.objects.get(id=zaavar_id)
                    zaavarchilgaa.zaavarchilgaa.add(zaavar)
            zaavarchilgaa.ognoo = ognoo
            zaavarchilgaa.save()
            messages.success(request, 'Амжилттай засварлагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Засварлахад алдаа гарлаа!')
            return redirect('/home/ashiglalt/zaavarchilgaa_add')

        return redirect('/home/ashiglalt/zaavarchilgaa_list')


class AshiglaltZaavarchilgaaDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_ashiglaltzaavarchilgaa'

    def get(self, request, id, *args, **kwargs):
        try:
            zaavarchilgaa = AshiglaltZaavarchilgaa.objects.get(id=id)
            zaavarchilgaa.is_active = 0
            zaavarchilgaa.save()
            messages.success(request, 'Амжилттай устгагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Устахад алдаа гарлаа!')

        return redirect('/home/ashiglalt/zaavarchilgaa_list')


class AshiglaltZaavarTaniltsah(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        ashiglalt_zaavar_ids = request.POST.getlist('zaavarchilgaa_id', '')

        try:
            for ashiglalt_zaavar_id in ashiglalt_zaavar_ids:
                zaavar_user = ZaavarchilgaaUsers.objects.get(ashiglalt_zaavar_id=ashiglalt_zaavar_id, user_id=request.user.id)
                zaavar_user.taniltssan_eseh = 1
                zaavar_user.save()
                messages.success(request, 'Амжилттай хадгалагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Хадгалахад алдаа гарлаа!')

        return redirect('/home/ashiglalt/zaavarchilgaa_list')