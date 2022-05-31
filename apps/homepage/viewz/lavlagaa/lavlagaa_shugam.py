import logging
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from datetime import datetime
from apps.data.models import DedStants, Tooluur, Shugam


class ShugamList(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_shugam'
    template_name = 'homepage/lavlah/shugam.html'
    menu = '7'
    starter_q = "SELECT shug.id, shug.shugam_ner, shug.shugam_tip, shug.shugam_tuluv, shug.suuriluulsan_ognoo, ded.name," \
                " tool.number FROM data_shugam shug" \
                " JOIN data_dedstants ded ON shug.ded_stants_id=ded.id" \
                " LEFT JOIN data_tooluur tool ON shug.tooluur_id=tool.id" \
                " WHERE shug.is_active = 1"
    try:
        ded_stants = DedStants.objects.filter(is_active=1).order_by('name')
    except ObjectDoesNotExist:
        ded_stants = None

    def get(self, request, *args, **kwargs):
        try:
            q = self.starter_q
            q = q + " ORDER BY shug.created_date DESC"
            shugams = Shugam.objects.raw(q)
        except ObjectDoesNotExist as e:
            shugams = None
            logging.error('"Shugam" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'shugams': shugams,
            'ded_stants': self.ded_stants,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        ner = request.POST['ner']
        tuluv = request.POST['tuluv']
        tip = request.POST['tip']
        ded_stants = request.POST['ded_stants']
        tooluur = request.POST['tooluur']
        suuriluulsan_ognoo = request.POST['suuriluulsan_ognoo']

        q = self.starter_q

        if ner != '':
            q = q + " AND shug.shugam_ner LIKE '%%" + ner + "%%'"
        if tip != '':
            q = q + " AND shug.shugam_tip LIKE '%%" + tip + "%%'"
        if ded_stants != '':
            q = q + " AND ded.id = " + ded_stants
        if tuluv != '':
            q = q + " AND shug.shugam_tuluv LIKE '%%" + tuluv + "%%'"
        if tooluur != '':
            q = q + " AND tool.name LIKE '%%" + tooluur + "%%'"
        if suuriluulsan_ognoo != '':
            q = q + " AND shug.suuriluulsan_ognoo >= '" + suuriluulsan_ognoo + "'"

        try:
            shugams = Shugam.objects.raw(q)
        except ObjectDoesNotExist as e:
            shugams = None
            logging.error('"Shugam" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'shugams': shugams,
            'ded_stants': self.ded_stants,
            'search_q': {
                'ner': ner,
                'tip': tip,
                'ded_stants': ded_stants,
                'tuluv': tuluv,
                'tooluur': tooluur,
                'suuriluulsan_ognoo': suuriluulsan_ognoo,
            }
        }
        return render(request, self.template_name, data)


class ShugamAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_shugam'
    template_name = 'homepage/lavlah/add_shugam.html'
    menu = '7'

    def get(self, request, *args, **kwargs):
        try:
            ded_stants_list = DedStants.objects.filter(is_active=1).order_by('name')
        except ObjectDoesNotExist as e:
            ded_stants_list = None
        try:
            shugam_tooluur_ids = Shugam.objects.filter(is_active=1).filter(Q(tooluur_id__isnull=False)).values_list('tooluur_id', flat=True)
        except ObjectDoesNotExist:
            shugam_tooluur_ids = None
        try:
            tooluur_list = Tooluur.objects.filter(~Q(id__in=shugam_tooluur_ids)).order_by('name')
            print(len(tooluur_list))
        except ObjectDoesNotExist:
            tooluur_list = None

        data = {
            'action': '/home/lavlagaa/add_shugam',
            'ded_stants_list': ded_stants_list,
            'tooluur_list': tooluur_list,
            'menu': self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.get(id=int(request.POST['ded_stants']))
        except DedStants.DoesNotExist:
            ded_stants = None

        if request.POST['tooluur'] != '':
            try:
                tooluur = Tooluur.objects.get(id=int(request.POST['tooluur']))
            except Tooluur.DoesNotExist:
                tooluur = None
        else:
            tooluur = None

        if ded_stants is not None:
            try:
                suuriluulsan_ognoo = datetime.strptime(request.POST['suuriluulsan_ognoo'], '%Y-%m-%d')
                shugam = Shugam(shugam_ner=request.POST['shugam_ner'], shugam_tip=request.POST['shugam_tip'], shugam_tuluv=request.POST['shugam_tuluv'], suuriluulsan_ognoo=suuriluulsan_ognoo, ded_stants=ded_stants, tooluur=tooluur, created_user_id=request.user.id)
                shugam.save()
                messages.success(request, 'Амжилттай хадгалагдлаа!')
            except Exception as e:
                messages.error(request, 'Хадгалахад алдаа гарлаа!')
                return redirect('/home/lavlagaa/add_shugam')

            if "save_and_continue" in request.POST:
                return redirect('/home/lavlagaa/add_shugam')
            else:
                return redirect('/home/lavlagaa/shugam')
        else:
            try:
                ded_stants_list = DedStants.objects.filter(is_active=1).order_by('name')
            except ObjectDoesNotExist as e:
                ded_stants_list = None
            try:
                shugam_tooluur_ids = Shugam.objects.filter(is_active=1).filter(Q(tooluur_id__isnull=False)).values_list('tooluur_id', flat=True)
            except ObjectDoesNotExist:
                shugam_tooluur_ids = None
            try:
                tooluur_list = Tooluur.objects.filter(~Q(id__in=shugam_tooluur_ids)).order_by('name')
                print(len(tooluur_list))
            except ObjectDoesNotExist:
                tooluur_list = None

            data = {
                'action': '/home/lavlagaa/add_shugam',
                'ded_stants_list': ded_stants_list,
                'tooluur_list': tooluur_list,
                'menu': self.menu,
            }
            return render(request, self.template_name, data)


class ShugamEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_shugam'
    template_name = 'homepage/lavlah/add_shugam.html'
    menu = '7'

    def get(self, request, id, *args, **kwargs):
        try:
            ded_stants_list = DedStants.objects.filter(is_active=1)
        except ObjectDoesNotExist as e:
            ded_stants_list = None
            logging.error('"DedStants" model has no object: %s', e)

        try:
            tooluur_list = Tooluur.objects.filter(is_active=1)
        except ObjectDoesNotExist as e:
            tooluur_list = None
            logging.error('"Tooluur" model has no object: %s', e)

        try:
            shugam = Shugam.objects.get(id=id)
        except ObjectDoesNotExist as e:
            shugam = None
            logging.error('"Shugam" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'action': '/home/lavlagaa/edit_shugam/'+id+'/',
            'shugam': shugam,
            'ded_stants_list': ded_stants_list,
            'tooluur_list': tooluur_list,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        shugam_id = request.POST['shugam_id']

        try:
            shugam = Shugam.objects.get(id=int(shugam_id))
            shugam.shugam_ner = request.POST['shugam_ner']
            shugam.shugam_tip = request.POST['shugam_tip']
            shugam.shugam_tuluv = request.POST['shugam_tuluv']
            suuriluulsan_ognoo = datetime.strptime(request.POST['suuriluulsan_ognoo'], '%Y-%m-%d')
            shugam.suuriluulsan_ognoo = suuriluulsan_ognoo
            try:
                ded_stants = DedStants.objects.get(id=int(request.POST['ded_stants']))
            except ObjectDoesNotExist as e:
                ded_stants = None
                logging.error('"DedStants" model has no object: %s', e)
            shugam.ded_stants = ded_stants
            try:
                tooluur = Tooluur.objects.get(id=int(request.POST['tooluur']))
            except ObjectDoesNotExist as e:
                tooluur = None
                logging.error('"Tooluur" model has no object: %s', e)
            shugam.tooluur = tooluur
            shugam.save()
            messages.success(request, 'Амжилттай засварлагдлаа!')
        except Exception as e:
            messages.error(request, 'Засварлахад алдаа гарлаа!')
            logging.error('%s', e)

        if "save_and_continue" in request:
            return redirect('/home/lavlagaa/add_shugam')
        else:
            return redirect('/home/lavlagaa/shugam')


class ShugamDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_shugam'

    def get(self, request, id, *args, **kwargs):
        try:
            shugam = Shugam.objects.get(id=id)
            shugam.is_active = 0
            shugam.save()
            messages.success(request, 'Ажилттай устгагдлаа!')
        except ObjectDoesNotExist as e:
            messages.error(request, 'Устахад алдаа гарлаа!')
            logging.error('"Shugam" model has no object: %s', e)

        return redirect('/home/lavlagaa/shugam')