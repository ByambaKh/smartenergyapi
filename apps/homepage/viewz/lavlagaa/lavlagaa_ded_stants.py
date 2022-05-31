from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class DedStantsList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_dedstants'
    template_name = "homepage/lavlah/ded_stants.html"
    starter_q = "SELECT d.id, d.code, d.guidliin_trans, d.huchdeliin_trans,d.chadal,d.s_aimag, d.s_duureg,d.s_horoo, d.s_address, d.etseg_ded_stants, d1.name AS dname FROM data_dedstants d LEFT JOIN data_dedstants AS d1 on d1.id=d.etseg_ded_stants WHERE d.is_active=1 "
    menu = "7"
    
    def get(self, request, *args, **kwargs):
        q = self.starter_q
        q = q + "ORDER BY d.created_date DESC"
        ded_stants = DedStants.objects.filter(is_active='1')
        objs = list(DedStants.objects.raw(q))
        total_chadal = self.total_chadal(objs)
        data = {
            "datas":objs,
            "total_chadal": total_chadal,
            "ded_stants":ded_stants,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)
    
    
    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        parent_station = rq.get('select_stants', '')
        s_address = rq.get('s_address', '')
        chadal = rq.get('chadal', '')
        q = self.starter_q
        
        if name != '':
            q = q + " AND d.name like '%%" +name +"%%'"
        if parent_station != '':
            q = q + " AND d.etseg_ded_stants = '" + parent_station + "'"
            parent_station = int(parent_station)
        if s_address != '':
            q = q + " AND d.s_address like '%%" + s_address +"%%'"
        if chadal != '':
            q = q + " AND d.chadal like '%%" + chadal + "%%'"
        q = q + " ORDER BY d.created_date desc"

        objs = DedStants.objects.raw(q)
        ded_stants = DedStants.objects.filter(is_active='1')
        total_chadal = self.total_chadal(objs)
        data = {
            "datas":objs,
            "total_chadal":total_chadal,
            "ded_stants":ded_stants,
            "search_q":{
                "name":name,
                "parent_station":parent_station,
                "s_address":s_address,
                "s_chadal":chadal,
                "menu":self.menu,
            }
        }
        return render(request, self.template_name, data)

    def total_chadal(self, datas):
        total = 0
        for item in datas:
            total = total + float(item.chadal)
        return total


class DedStantsDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_dedstants'
    template_name = "homepage/lavlah/ded_stants.html"
    permission_required = ('data.add_dedstants', 'data.delete_dedstants')

    def get(self, request, id, *args, **kwargs):
        ded = DedStants.objects.get(id=id)
        ded.is_active = 0
        ded.save()
        return redirect("/home/lavlagaa/ded_stants")


class DedStantsAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_dedstants'
    template_name = "homepage/lavlah/add_ded_stants.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        return self.build_add_request(request)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        angilal = rq.get('angilal', '')
        name = rq.get('name', '')
        chadal = rq.get('chadal', '')
        code = rq.get('code', '')
        etseg_ded_stants = rq.get('ds', '')
        s_aimag = rq.get('select_aimag', '')
        s_duureg = rq.get('select_duureg', '')
        s_horoo = rq.get('select_horoo', '')
        s_address = rq.get('s_address', '')
        try:
            DedStants.objects.get(name=name, is_active="1")
            messages.warning(request, "Дэд станцын нэр системд бүртгэгдсэн байна. Та өөр нэр ашиглана уу.")
            return self.build_add_request(request)
        except DedStants.DoesNotExist:
            stants = DedStants.objects.create()
            stants.angilal_id = angilal
            stants.name = name
            stants.chadal = chadal
            stants.etseg_ded_stants = etseg_ded_stants
            stants.s_aimag = s_aimag
            stants.s_duureg = s_duureg
            stants.code = code
            stants.s_horoo = s_horoo
            stants.s_address = s_address
            stants.save()
            messages.success(request, "Амжилттай бүртгэгдлээ.")
            if "save" in rq:
                return redirect('/home/lavlagaa/ded_stants')
            else:
                return redirect('/home/lavlagaa/add_ded_stants')

    def build_add_request(self, request):
        ded_stants_angilals = DedStantsAngilal.objects.filter(is_active=1).order_by('name')
        dedstants = DedStants.objects.filter(is_active=1)
        aimags = Aimag.objects.filter(is_active=1)
        data = {
            "ded_stants_angilals":ded_stants_angilals,
            "dedstants":dedstants,
            "aimags": aimags,
            "urlz":"/home/lavlagaa/add_ded_stants",
            "menu":self.menu,
        }
        return render(request, self.template_name, data)


class DedStantsEdit(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_dedstants'
    template_name = "homepage/lavlah/add_ded_stants.html"
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        ded_stants_angilals = DedStantsAngilal.objects.filter(is_active=1).order_by('name')
        selected_station = DedStants.objects.get(id=id)
        dedstants = DedStants.objects.filter(is_active=1)
        aimags = Aimag.objects.filter(is_active=1)
        duureg = Duureg.objects.filter(aimag__code=selected_station.s_aimag)
        horoo = Horoo.objects.filter(duureg__code=selected_station.s_duureg)
        data = {
            "urlz":"/home/lavlagaa/add_ded_stants/" + id + "/",
            "selected_station":selected_station,
            "ded_stants_angilals":ded_stants_angilals,
            "aimags": aimags,
            "duuregs": duureg,
            "horoos": horoo,
            "dedstants" : dedstants,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        angilal = rq.get('angilal', '')
        name = rq.get('name', '')
        chadal = rq.get('chadal', '')
        etseg_ded_stants = rq.get('ds', '')
        code = rq.get('code', '')
        s_aimag = rq.get('select_aimag', '')
        s_duureg = rq.get('select_duureg', '')
        s_horoo = rq.get('select_horoo', '')
        s_address = rq.get('s_address', '')

        try:
            stants = DedStants.objects.get(id=id)
            if stants.name != name:
                try:
                    DedStants.objects.get(name=name, is_active="1")
                    messages.warning(request, 'Энэ дэд станцын нэрээр бүртгэгдсэн байна.')
                    return redirect('/home/lavlagaa/tooluur/')
                except:
                    no_error = ""
            stants.angilal_id = angilal
            stants.name = name
            stants.code = code
            stants.chadal = chadal
            stants.s_aimag = s_aimag
            stants.s_duureg = s_duureg
            stants.s_horoo = s_horoo
            stants.s_address =  s_address
            stants.etseg_ded_stants = etseg_ded_stants
            stants.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
        except:
            messages.warning(request, 'Алдаа гарлаа')
        return redirect('/home/lavlagaa/ded_stants')