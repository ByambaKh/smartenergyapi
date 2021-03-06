from apps.homepage.forms import *
from django.views import View
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages


class HuchdeliinTrans(LoginRequiredMixin, PermissionRequiredMixin, View):
    menu = "7"
    login_url = '/home/index'
    permission_required = 'data.view_transformator'
    template_name = "homepage/lavlah/huchdeliin_trans.html"

    starter_q = "SELECT t.id, ds.name ds_name, tm.name mark_name, t.number, t.name trans_name, t.coefficient, t.multiply_coef " \
                "FROM data_transformator t JOIN data_dedstants ds ON ds.id = t.dedstants_id " \
                "JOIN data_transformatormark tm ON tm.id = t.mark_id " \
                "WHERE t.type = 1 AND t.is_active = 1"

    def get(self, request, *args, **kwargs):

        q = self.starter_q
        q = q + " ORDER BY t.created_date DESC"

        objs = Transformator.objects.raw(q)
        data = {
            "datas":objs,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST

        name = rq.get('name', '')
        tip = rq.get('tip', '')
        number = rq.get('number', '')
        trans_name = rq.get('trans_name', '')
        coefficient = rq.get('coefficient', '')

        q = self.starter_q

        if name != '':
            q = q + " AND ds.name LIKE '%%" + name + "%%'"
        if tip != '':
            q = q + " AND tm.name LIKE '%%" + tip + "%%'"
        if number != '':
            q = q + " AND t.number LIKE '%%" + number + "%%'"
        if trans_name != '':
            q = q + " AND t.name LIKE '%%" + trans_name + "%%'"
        if coefficient != '':
            q = q + " AND t.coefficient = " + coefficient

        objs = Transformator.objects.raw(q)

        data = {
            "datas": objs,
            "search_q": {
                "name": name,
                "tip": tip,
                "number": number,
                "trans_name": trans_name,
                "coefficient": coefficient,
                "menu": self.menu,
            }
        }
        return render(request, self.template_name, data)


class HuchdeliinTransAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    menu = "7"
    login_url = '/home/index'
    permission_required = 'data.add_transformator'
    template_name = "homepage/lavlah/add_huchdeliin_trans.html"

    def get(self, request, *args, **kwargs):
        dedstants_list = DedStants.objects.filter(is_active='1').order_by('name')
        mark_list = TransformatorMark.objects.filter(is_active='1', type=1).order_by('name')

        data = {
            "urlz":"/home/lavlagaa/add_huchdeliin_trans",
            "dedstants_list": dedstants_list,
            "mark_list": mark_list,
            "menu": self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST

        dedstants_id = rq.get('select_dedstants', '')
        a_coeff = rq.get('coefficient', '')
        a_mult_koef = rq.get('multiply_coef', '')
        mark_id = rq.get('select_mark', '')
        a_number = rq.get('number', '')
        trans_name = rq.get('trans_name', '')

        try:
            Transformator.objects.get(number=a_number, is_active="1")
            messages.warning(request, "???????? ???????????????? ???????????? ?????????????????????? ??????????. ???? ?????? ???????????? ?????????????? ????.")
            return redirect('/home/lavlagaa/add_huchdeliin_trans')
        except Transformator.DoesNotExist:
            trans = Transformator.objects.create()
            dedstants = DedStants.objects.get(id=dedstants_id)
            mark = TransformatorMark.objects.get(id=mark_id)

            trans.type = "1"
            trans.mark = mark
            trans.dedstants = dedstants
            trans.number = a_number
            trans.name = trans_name
            trans.multiply_coef = Decimal(a_mult_koef)
            trans.created_date = timezone.now()
            trans.created_user_id = request.user.id
            trans.coefficient = a_coeff

            trans.save()

            messages.success(request, "?????????????????? ????????????????????????.")
            if "save_and_continue" in rq:
                return redirect('/home/lavlagaa/add_huchdeliin_trans')
            else:
                return redirect('/home/lavlagaa/huchdeliin_trans')


class HuchdeliinTransEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    menu = "7"
    login_url = '/home/index'
    permission_required = 'data.change_transformator'
    template_name = "homepage/lavlah/add_huchdeliin_trans.html"

    def get(self, request, id, *args, **kwargs):

        trans = Transformator.objects.get(id=id)
        dedstants_list = DedStants.objects.filter(is_active='1').order_by('name')
        mark_list = TransformatorMark.objects.filter(is_active='1', type=1).order_by('name')
        try:
            huvaagch = float(trans.coefficient)/float(trans.multiply_coef)
            huvaagch = str(huvaagch)
        except ZeroDivisionError:
            huvaagch = "0.0"
        print(huvaagch, trans.coefficient, trans.multiply_coef)

        data = {
            "urlz": "/home/lavlagaa/huchdel_edit/" + id + "/",
            "dedstants_list": dedstants_list,
            "mark_list": mark_list,
            "huvaagch": huvaagch,
            "transformator": trans,
            "menu": self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST

        dedstants_id = rq.get('select_dedstants', '')
        a_coeff = rq.get('coefficient', '')
        a_mult_koef = rq.get('multiply_coef', '')
        mark_id = rq.get('select_mark', '')
        a_number = rq.get('number', '')
        trans_name = rq.get('trans_name', '')

        try:
            trans = Transformator.objects.get(id=id)
            if trans.number != a_number:
                try:
                    Transformator.objects.get(number=a_number, is_active="1")
                    messages.warning(request, "???????????????????????????? ???????????? ?????????????????? ??????????.")
                    return  redirect("/home/lavlagaa/huchdel_edit/" + id + "/")
                except Transformator.DoesNotExist:
                    no_error = ""
            dedstants = DedStants.objects.get(id=dedstants_id)
            mark = TransformatorMark.objects.get(id=mark_id)

            trans.mark = mark
            trans.dedstants = dedstants
            trans.number = a_number
            trans.name = trans_name
            trans.multiply_coef = Decimal(a_mult_koef)
            trans.coefficient = a_coeff

            trans.save()

            messages.success(request, "?????????????????? ????????????????????????.")
        except:
            messages.warning(request, "?????????? ????????????.")
        return redirect('/home/lavlagaa/huchdeliin_trans')


class HuchdelDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_transformator'
    template_name = "homepage/lavlah/huchdeliin_trans.html"

    def get(self, request, id, *args, **kwargs):
        trans = Transformator.objects.get(id=id)

        trans.is_active = 0
        trans.save()

        messages.success(request, "?????????????????? ????????????????????.")
        return redirect("/home/lavlagaa/huchdeliin_trans")