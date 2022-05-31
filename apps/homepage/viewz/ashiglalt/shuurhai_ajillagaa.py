from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from datetime import datetime
from apps.data.models import ShuurhaiAjillagaa


class ShuurhaiAjillagaaList(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_shuurhaiajillagaa'
    template_name = "homepage/ashiglalt/shuurhai_ajillagaa_list.html"
    menu = '4'
    sub = '6'

    qry = "SELECT sha.id, sha.ognoo, sha.temdeglel, sha.taniltssan_eseh, dis.first_name AS dis_first_name," \
          " dis.last_name AS dis_last_name, tan.first_name AS tan_first_name, tan.last_name AS tan_last_name" \
          " FROM data_shuurhaiajillagaa sha" \
          " JOIN auth_user dis ON sha.dispetcher_id=dis.id" \
          " LEFT JOIN auth_user tan ON sha.taniltssan_id=tan.id" \
          " WHERE sha.is_active=1"
    try:
        dispetchers = User.objects.filter(Q(groups__name='Ахлах диспетчер инженер') | Q(groups__name='Диспетчер инженер'))
    except ObjectDoesNotExist:
        dispetchers = None
    try:
        taniltssans = User.objects.filter(groups__name='АА-ны менежер')
    except ObjectDoesNotExist:
        taniltssans = None

    def get(self, request, *args, **kwargs):
        q = self.qry
        q = q + " ORDER BY sha.created_date DESC"

        try:
            ajillagaas = ShuurhaiAjillagaa.objects.raw(q)
        except ObjectDoesNotExist:
            ajillagaas = None

        data = {
            'ajillagaas': ajillagaas,
            'dispetchers': self.dispetchers,
            'taniltssans': self.taniltssans,
            'menu': self.menu,
            'sub': self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        action = request.POST['action']
        if action == 'taniltsah':
            taniltssan_esehs = request.POST.getlist('taniltssan_eseh', '')
            try:
                for taniltssan_eseh in taniltssan_esehs:
                    ajillagaa = ShuurhaiAjillagaa.objects.get(id=taniltssan_eseh)
                    ajillagaa.taniltssan_eseh = 1
                    ajillagaa.taniltssan_id = request.user.id
                    ajillagaa.save()
                messages.success(request, 'Амжилттай хадгалагдлаа!')
            except ObjectDoesNotExist:
                messages.error(request, 'Хадгалахад алдаа гарлаа!')
            return redirect('/home/ashiglalt/shuurhai_ajillagaa_list')
        elif action == 'search':
            taniltssan_eseh = request.POST['taniltssan_eseh']
            dispetcher = request.POST['dispetcher']
            ognoo = request.POST['ognoo']

            q = self.qry

            if taniltssan_eseh != '':
                q = q + " AND sha.taniltssan_eseh LIKE '%%" + taniltssan_eseh + "%%'"
            if dispetcher != '':
                q = q + " AND sha.dispetcher_id LIKE '%%" + dispetcher + "%%'"
            if ognoo != '':
                q = q + " AND sha.ognoo >= '" + ognoo + "'"

            try:
                ajillagaas = ShuurhaiAjillagaa.objects.raw(q)
            except ObjectDoesNotExist:
                ajillagaas = None

            data = {
                'ajillagaas': ajillagaas,
                'dispetchers': self.dispetchers,
                'taniltssans': self.taniltssans,
                'menu': self.menu,
                'sub': self.sub,
                'qry': {
                    'taniltssan_eseh': taniltssan_eseh,
                    'dispetcher': int(dispetcher) if dispetcher != '' else dispetcher,
                    'ognoo': ognoo,
                }
            }
            return render(request, self.template_name, data)
        else:
            return redirect('/home/ashiglalt/shuurhai_ajillagaa_list')


class ShuurhaiAjillagaaAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_shuurhaiajillagaa'
    template_name = "homepage/ashiglalt/shuurhai_ajillagaa_add.html"
    menu = '4'
    sub = '6'

    def get(self, request, *args, **kwargs):
        data = {
            'action': '/home/ashiglalt/shuurhai_ajillagaa_add',
            'menu': self.menu,
            'sub': self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        ognoo = datetime.strptime(request.POST['ognoo'], '%Y-%m-%d %H:%M')
        try:
            ajillagaa = ShuurhaiAjillagaa.objects.create(dispetcher_id=request.user.id, ognoo=ognoo, temdeglel=request.POST['temdeglel'])
            ajillagaa.created_user_id = request.user.id
            ajillagaa.save()
            messages.success(request, 'Амжилттай хадгалагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Хадгалахад алдаа гарлаа!')
            return redirect('/home/ashiglalt/shuurhai_ajillagaa_add')

        return redirect('/home/ashiglalt/shuurhai_ajillagaa_list')


class ShuurhaiAjillagaaEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_shuurhaiajillagaa'
    template_name = 'homepage/ashiglalt/shuurhai_ajillagaa_add.html'
    menu = '4'
    sub = '6'

    def get(self, request, id, *args, **kwargs):
        try:
            ajillagaa = ShuurhaiAjillagaa.objects.get(id=id)
        except ObjectDoesNotExist:
            ajillagaa = None

        data = {
            'action': '/home/ashiglalt/shuurhai_ajillagaa_edit/'+id+'/',
            'ajillagaa': ajillagaa,
            'menu': self.menu,
            'sub': self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        ognoo = datetime.strptime(request.POST['ognoo'], '%m/%d/%Y %H:%M')
        try:
            ajillagaa = ShuurhaiAjillagaa.objects.get(id=id)
            ajillagaa.dispetcher_id = request.POST['dispetcher']
            ajillagaa.taniltssan_id = request.POST['taniltssan']
            ajillagaa.taniltssan_eseh = request.POST['taniltssan_eseh']
            ajillagaa.temdeglel = request.POST['temdeglel']
            ajillagaa.ognoo = ognoo
            ajillagaa.save()
            messages.success(request, 'Амжилттай засварлагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Засварлахад алдаа гарлаа!')
            return redirect('/home/ashiglalt/shuurhai_ajillagaa_add')

        return redirect('/home/ashiglalt/shuurhai_ajillagaa_list')


class ShuurhaiAjillagaaDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_shuurhaiajillagaa'

    def get(self, request, id, *args, **kwargs):
        try:
            ajillagaa = ShuurhaiAjillagaa.objects.get(id=id)
            ajillagaa.is_active = 0
            ajillagaa.save()
            messages.success(request, 'Амжилттай устгагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Устахад алдаа гарлаа!')

        return redirect('/home/ashiglalt/shuurhai_ajillagaa_list')