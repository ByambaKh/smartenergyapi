from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from datetime import datetime
from apps.data.models import DedStants, UzlegShalgalt


class UzlegShalgaltList(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_uzlegshalgalt'
    template_name = "homepage/ashiglalt/uzleg_shalgalt_list.html"
    menu = '4'
    sub = '3'

    qry = "SELECT uzl.id, uzl.ognoo, uzl.aguulga, ded.name as ded_stants_name FROM data_uzlegshalgalt uzl" \
          " JOIN data_dedstants ded ON uzl.ded_stants_id=ded.id" \
          " JOIN auth_user aut ON uzl.ajiltan_id=aut.id" \
          " WHERE uzl.is_active=1"

    try:
        ded_stants = DedStants.objects.filter(is_active=1).order_by('name')
    except ObjectDoesNotExist:
        ded_stants = None
    try:
        ajiltans = User.objects.filter(Q(groups__name='Ахлах диспетчер инженер') | Q(groups__name='Диспетчер инженер') | Q(groups__name='Монтер'))
    except ObjectDoesNotExist:
        ajiltans = None

    def get(self, request, *args, **kwargs):
        q = self.qry
        q = q + " ORDER BY uzl.created_date DESC"

        try:
            uzleg_list = UzlegShalgalt.objects.raw(q)
        except ObjectDoesNotExist:
            uzleg_list = None

        data = {
            'uzleg_list': uzleg_list,
            'ded_stants': self.ded_stants,
            'ajiltans': self.ajiltans,
            'menu': self.menu,
            'sub': self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        ded_stants = request.POST['ded_stants']
        ajiltan = request.POST['ajiltan']
        ognoo = request.POST['ognoo']

        q = self.qry

        if ded_stants != '':
            q = q + " AND uzl.ded_stants_id LIKE '%%" + ded_stants + "%%'"
        if ajiltan != '':
            q = q + " AND uzl.ajiltan_id LIKE '%%" + ajiltan + "%%'"
        if ognoo != '':
            q = q + " AND uzl.ognoo >= '" + ognoo + "'"

        try:
            uzleg_list = UzlegShalgalt.objects.raw(q)
        except ObjectDoesNotExist:
            uzleg_list = None

        data = {
            'uzleg_list': uzleg_list,
            'ded_stants': self.ded_stants,
            'ajiltans': self.ajiltans,
            'menu': self.menu,
            'sub': self.sub,
            'qry': {
                'ded_stants': int(ded_stants) if ded_stants != '' else ded_stants,
                'ajiltan': int(ajiltan) if ajiltan != '' else ajiltan,
                'ognoo': ognoo,
            }
        }
        return render(request, self.template_name, data)


class UzlegShalgaltAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_uzlegshalgalt'
    template_name = "homepage/ashiglalt/uzleg_shalgalt_add.html"
    menu = '4'
    sub = '3'

    def get(self, request, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.filter(is_active=1).order_by('name')
        except ObjectDoesNotExist:
            ded_stants = None
        try:
            ajiltans = User.objects.filter(Q(groups__name='Ахлах диспетчер инженер') | Q(groups__name='Диспетчер инженер') | Q(groups__name='Монтер'))
        except ObjectDoesNotExist:
            ajiltans = None

        data = {
            'action': '/home/ashiglalt/uzleg_shalgalt_add',
            'ded_stants': ded_stants,
            'ajiltans': ajiltans,
            'menu': self.menu,
            'sub': self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.get(id=request.POST['ded_stants'])
        except ObjectDoesNotExist:
            ded_stants = None
        try:
            ajiltan = User.objects.get(id=request.POST['ajiltan'])
        except ObjectDoesNotExist:
            ajiltan = None

        if ded_stants is not None and ajiltan is not None:
            ognoo = datetime.strptime(request.POST['ognoo'], '%Y-%m-%d %H:%M')

            try:
                uzleg = UzlegShalgalt.objects.create(ajiltan=ajiltan, ded_stants=ded_stants, ognoo=ognoo)
                uzleg.created_user_id = request.user.id
                uzleg.aguulga = request.POST['aguulga']
                uzleg.save()
                messages.success(request, 'Амжилттай хадгалагдлаа!')
            except ObjectDoesNotExist:
                messages.error(request, 'Хадгалахад алдаа гарлаа!')
                return redirect('/home/ashiglalt/uzleg_shalgalt_add')

            return redirect('/home/ashiglalt/uzleg_shalgalt_list')


class UzlegShalgaltEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_uzlegshalgalt'
    template_name = 'homepage/ashiglalt/uzleg_shalgalt_add.html'
    menu = '4'
    sub = '3'

    def get(self, request, id, *args, **kwargs):
        try:
            uzleg = UzlegShalgalt.objects.get(id=id)
        except ObjectDoesNotExist:
            uzleg = None
        try:
            ded_stants = DedStants.objects.filter(is_active=1)
        except ObjectDoesNotExist:
            ded_stants = None
        try:
            ajiltans = User.objects.filter(Q(groups__name='Ахлах диспетчер инженер') | Q(groups__name='Диспетчер инженер') | Q(groups__name='Монтер'))
        except ObjectDoesNotExist:
            ajiltans = None

        data = {
            'action': '/home/ashiglalt/uzleg_shalgalt_edit/'+id+'/',
            'uzleg': uzleg,
            'ded_stants': ded_stants,
            'ajiltans': ajiltans,
            'menu': self.menu,
            'sub': self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.get(id=request.POST['ded_stants'])
        except ObjectDoesNotExist:
            ded_stants = None
        try:
            ajiltan = User.objects.get(id=request.POST['ajiltan'])
        except ObjectDoesNotExist:
            ajiltan = None

        ognoo = datetime.strptime(request.POST['ognoo'], '%Y-%m-%d %H:%M')

        try:
            uzleg = UzlegShalgalt.objects.get(id=id)
            uzleg.ded_stants = ded_stants
            uzleg.ajiltan = ajiltan
            uzleg.ognoo = ognoo
            uzleg.aguulga = request.POST['aguulga']
            uzleg.save()
            messages.success(request, 'Амжилттай засварлагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Засварлахад алдаа гарлаа!')
            return redirect('/home/ashiglalt/uzleg_shalgalt_add')

        return redirect('/home/ashiglalt/uzleg_shalgalt_list')


class UzlegShalgaltDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_uzlegshalgalt'

    def get(self, request, id, *args, **kwargs):
        try:
            uzleg = UzlegShalgalt.objects.get(id=id)
            uzleg.is_active = 0
            uzleg.save()
            messages.success(request, 'Амжилттай устгагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Устахад алдаа гарлаа!')

        return redirect('/home/ashiglalt/uzleg_shalgalt_list')