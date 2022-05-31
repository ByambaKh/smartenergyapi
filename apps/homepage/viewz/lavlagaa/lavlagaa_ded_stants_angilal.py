from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class DedStantsAngilalList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_dedstantsangilal'
    template_name = 'homepage/lavlah/ded_stants_angilal.html'
    menu = '7'

    def get(self, request, *args, **kwargs):
        try:
            ded_stants_angilals = DedStantsAngilal.objects.filter(is_active='1').order_by('name')
        except ObjectDoesNotExist:
            ded_stants_angilals = None

        data = {
            'ded_stants_angilals': ded_stants_angilals,
            'menu': self.menu,
        }
        return render(request, self.template_name, data)


class DedStantsAngilalAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_dedstantsangilal'
    template_name = 'homepage/lavlah/add_ded_stants_angilal.html'
    menu = '7'

    def get(self, request, *args, **kwargs):
        data = {
            'action': '/home/lavlagaa/add_ded_stants_angilal',
            'menu': self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        name = request.POST['name']

        try:
            DedStantsAngilal.objects.get(name=name, is_active='1')
            messages.error(request, "Таны оруулсан дэд станц ангилал бүртгэгдсэн байна.")
            return redirect('/home/lavlagaa/add_ded_stants_angilal')
        except ObjectDoesNotExist:
            ded_stants_angilal = DedStantsAngilal.objects.create()
            ded_stants_angilal.created_user_id = request.user.id
            ded_stants_angilal.name = name
            ded_stants_angilal.description = request.POST['description']
            ded_stants_angilal.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
            if "save_and_continue" in request.POST:
                return redirect('/home/lavlagaa/add_ded_stants_angilal')
            else:
                return redirect('/home/lavlagaa/list_ded_stants_angilal')


class DedStantsAngilalEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_dedstantsangilal'
    template_name = 'homepage/lavlah/add_ded_stants_angilal.html'
    menu = '7'

    def get(self, request, id, *args, **kwargs):
        try:
            ded_stants_angilal = DedStantsAngilal.objects.get(id=id)
        except ObjectDoesNotExist:
            ded_stants_angilal = None

        data = {
            'ded_stants_angilal': ded_stants_angilal,
            'action': '/home/lavlagaa/edit_ded_stants_angilal/'+id+'/',
            'menu': self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        name = request.POST['name']
        try:
            ded_stants_angilal = DedStantsAngilal.objects.get(id=id)
            ded_stants_angilal.name = name
            ded_stants_angilal.description = request.POST['description']
            ded_stants_angilal.save()
            messages.success(request, 'Амжилттай хадгалагдлаа!')
            return redirect('/home/lavlagaa/list_ded_stants_angilal')
        except ObjectDoesNotExist:
            messages.error(request, 'Алдаа гарлаа!')
            return redirect('/home/lavlagaa/edit_ded_stants_angilal/'+id+'/')


class DedStantsAngilalDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_dedstantsangilal'

    def get(self, request, id, *args, **kwargs):
        try:
            ded_stants_angilal = DedStantsAngilal.objects.get(id=id)
            ded_stants_angilal.is_active = '0'
            ded_stants_angilal.save()
            messages.success(request, 'Амжилттай устгагдлаа.')
            return redirect("/home/lavlagaa/list_ded_stants_angilal")
        except ObjectDoesNotExist:
            messages.error(request, 'Алдаа гарлаа!')
            return redirect("/home/lavlagaa/list_ded_stants_angilal")