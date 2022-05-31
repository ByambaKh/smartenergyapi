from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages

class AldangiList(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = 'data.add_aldangi'
    template_name = "homepage/lavlah/aldangi.html"
    menu = "7"

    def get(self, request, *args, **kwargs):
        objs = Aldangi.objects.filter(is_active="1")
        data = {
            "datas":objs,
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
            cycle_para["code__contains"] = code
        cycle_para["is_active"] = "1"
        objs = Aldangi.objects.filter(**cycle_para)
        data = {
            "datas":objs,
            "search_q":{
                "name":name,
                "code":code,
                "menu":self.menu,
            }
        }
        return render(request, self.template_name, data)

class AldangiAdd(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/add_aldangi.html"
    permission_required = ('data.add_aldangi', 'data.change_aldangi')
    menu = "7"

    def get(self, request, *args, **kwargs):
        data = {
            "urlz":"/home/lavlagaa/add_aldangi",
            "menu":self.menu,
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        rq = request.POST
        code = rq.get('code', '')
        name = rq.get('name', '')
        huvi = rq.get('huvi', '')
        start_date = rq.get('start_date', '')
        end_date = rq.get('end_date', '')

        try:
            Aldangi.objects.get(code=code, is_active="1")
            data = {
                "name":rq.get('name', ''),
                "huvi":rq.get('huvi', ''),
                "start_date":rq.get('start_date', ''),
                "end_date":rq.get('end_date', ''),
                "menu":self.menu,
            }
            messages.warning(request, 'Таны оруулсан код бүртгэлтэй байна. Өөр код оруулна уу!')
            return render(request, self.template_name, data)
        except Aldangi.DoesNotExist:
            ser = Aldangi.objects.create(start_date=start_date, end_date=end_date)
            ser.name = name
            ser.code = code
            ser.huvi = huvi
            ser.save()
            messages.success(request, 'Амжилттай бүртгэгдлээ.')
            if "save_and_continue" in rq:
                return redirect('/home/lavlagaa/add_aldangi')
            else:
                return redirect('/home/lavlagaa/aldangi')
        
    
class AldangiEdit(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/add_aldangi.html"
    permission_required = ('data.add_aldangi', 'data.change_aldangi')
    menu = "7"
    def get(self, request, id, *args, **kwargs):
        ser = Aldangi.objects.get(id=id)
        start_date = ser.start_date.strftime("%Y-%m-%d")
        end_date = ser.end_date.strftime("%Y-%m-%d")
        data = {
            "urlz":"/home/lavlagaa/edit_aldangi/" + id + "/",
            "aldangi":ser,
            "name":ser.name,
            "code":ser.code,
            "huvi":ser.huvi,
            "start_date":start_date,
            "end_date":end_date,
            "menu":self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        code = rq.get('code', '')
        name = rq.get('name', '')
        huvi = rq.get('huvi', '')
        start_date = rq.get('start_date', '')
        end_date = rq.get('end_date', '')
        try:
            ser = Aldangi.objects.get(id=id)
            if ser.code != code:
                try:
                    Aldangi.objects.get(code=code, is_active="1")
                    messages.warning(request, "Таны оруулсан код бүртгэлтэй байна. Өөр код оруулна уу!")
                    return  redirect("/home/lavlagaa/edit_aldangi/" + id + "/")
                except Aldangi.DoesNotExist:
                    no_error = ""
            ser.end_date = end_date
            ser.start_date = start_date
            ser.name = name
            ser.code = code
            ser.huvi = huvi
            ser.save()
            messages.success(request, 'Амжилттай хадгалагдлаа.')
        except:
            messages.warning(request, "Алдаа гарлаа.")
        return redirect('/home/lavlagaa/aldangi')

class AldangiDel(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = ('data.delete_aldangi')

    def get(self, request, id, *args, **kwargs):
        try:
            s = Aldangi.objects.get(id=id)
            s.is_active = 0
            s.save()
        except Exception as e:
            print(e)
        messages.success(request, 'Амжилттай устгагдлаа.')
        return redirect("/home/lavlagaa/aldangi")

    