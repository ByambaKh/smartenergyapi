from django.contrib import messages
from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin


class CycleList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_cycle'
    template_name = "homepage/lavlah/cycle.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        objs = Cycle.objects.filter(is_active=1)
        data = {
            "cycle":objs,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)
    
    
    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        code = rq.get('code', '')
        cycle_para = {}
        if name != '':
            cycle_para["name__contains"] = name
        if code != '':
            cycle_para["code"] = code
        cycle_para["is_active"] = "1"
        objs = Cycle.objects.filter(**cycle_para)
        data = {
            "cycle":objs,
            "search_q":{
                "name":name,
                "code":code,
            },
            "menu":self.menu,
        }
        return render(request, self.template_name, data)


class CycleAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_cycle.html"
    permission_required = 'data.add_cycle'
    menu = "7"

    def get(self, request, *args, **kwargs):
        data = {
            "menu":self.menu,
            "urlz":"/home/lavlagaa/add_cycle"
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        rq = request.POST
        try:
            Cycle.objects.get(code=rq.get('code', ''), is_active="1")
            data = {
                "name":rq.get('name', ''),
                "code":rq.get('code', ''),
                "tulbur_tuluh":rq.get('tulbur_tuluh', ''),
                "tulbur_garah":rq.get('tulbur_garah', ''),
                "zaalt_avah":rq.get('zaalt_avah', ''),
                "menu":self.menu,
                }
            messages.warning(request, 'Таны бүртгэсэн циклийн дугаар бүртгэлтэй байна.Өөр дугаар оруулна уу!')
            return render(request, self.template_name, data)
        except Cycle.DoesNotExist:
            cycle = Cycle.objects.create()
            cycle.name = rq.get('name', '')
            cycle.code = rq.get('code', '')
            cycle.zaalt_avah = rq.get('zaalt_avah', '')
            cycle.tulbur_garah = rq.get('tulbur_garah', '')
            cycle.tulbur_tuluh = rq.get('tulbur_tuluh', '')
            cycle.angilal = rq.get('angilal', '')
            cycle.save()
            messages.success(request, 'Амжилттай бүртгэгдлээ.')
            if "save" in rq:
                return redirect('/home/lavlagaa/cycle/')
            elif "save_and_continue" in rq:
                return redirect('/home/lavlagaa/add_cycle')
            else:
                return redirect('/home/lavlagaa/cycle/')


class CycleEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_cycle.html"
    permission_required = 'data.change_cycle'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        cycle = Cycle.objects.get(id=id)
        data = {
            "urlz":"/home/lavlagaa/edit_cycle/" + id + "/",
            "cycle":cycle,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        cycleCode = rq.get('code', '')
        try:
            cycle = Cycle.objects.get(id=id)
            if cycle.code != cycleCode:
                try:
                    Cycle.objects.get(code=cycleCode, is_active="1")
                    messages.warning(request, 'Энэ циклийн код бүртгэлтэй байна.')
                    return redirect('/home/lavlagaa/cycle')
                except:
                    no_error = ""
            cycle.name = rq.get('name', '')
            cycle.code = rq.get('code', '')
            cycle.zaalt_avah = rq.get('zaalt_avah', '')
            cycle.tulbur_garah = rq.get('tulbur_garah', '')
            cycle.tulbur_tuluh = rq.get('tulbur_tuluh', '')
            cycle.save()
            messages.success(request, 'Амжилттай хадгалагдлаа.')
            return redirect('/home/lavlagaa/cycle')
        except:
            messages.warning(request, 'Алдаа гарлаа')
            return redirect('/home/lavlagaa/cycle')


class CycleDel(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_cycle'

    def get(self, request, id, *args, **kwargs):
        t = Cycle.objects.get(id=id)
        t.is_active = 0
        t.save()
        messages.success(request, 'Амжилттай устгагдлаа.')
        return redirect("/home/lavlagaa/cycle")