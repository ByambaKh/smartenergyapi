from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, HttpResponse
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import simplejson
import datetime
import calendar
import xlwt
from django.contrib.auth.mixins import PermissionRequiredMixin
from apps.homepage.viewz.bichilt_manager import BichiltManager
from mcsi.utils import getPayDate


class UilchilgeeList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/borluulalt/vilchilgee.html"
    permission_required = 'data.view_customeruilchilgeetulbur'
    objtoxls = None
    menu = "3"
    sub = "5"

    def get(self, request, *args, **kwargs):
        now = datetime.datetime.now()
        start_date = str(now.year) + '-' + str(now.month) + '-01'
        end_date = str(now.year) + '-' + str(now.month) + '-' + str(now.day)

        objs = CustomerUilchilgeeTulbur.objects.filter(is_active='1', created_date__range=(start_date, end_date))
        servicelist = TulburtUilchilgee.objects.filter(is_active='1')

        counter = 0
        for obj in objs:
            counter += 1
            print("obj " + str(counter) + " : " + str(obj.uilchilgee.name) + " , pay : " + str(obj.payment))

        data = {
            "datas": objs,
            "servicelist": servicelist,
            "search_q": {
                "start_d": start_date,
                "end_d": end_date,
            },
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        service = rq.get('services', '')
        start_d = rq.get('start_d', '')
        end_d = rq.get('end_d', '')
        user_code = rq.get('user_code', '')

        para = {'is_active': '1'}
        if service != "":
            para.update({'uilchilgee_id': service})
        if user_code != "":
            para.update({'customer__code': user_code})
        if start_d != "" and end_d != "":
            start_date = datetime.datetime.strptime(start_d, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_d, '%Y-%m-%d').date()
            para.update({'created_date__range': (start_date, end_date)})

        objs = CustomerUilchilgeeTulbur.objects.filter(**para)
        servicelist = TulburtUilchilgee.objects.filter(is_active='1')

        if 'export_xls' in rq:
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="uilchilgee.xls"'

            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Users')

            # Sheet header, first row
            row_num = 0

            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            columns = ['Хэрэглэгчийн код', 'Овог нэр', 'Хаяг', 'Үйлчилгээний нэр', 'Төлбөр', 'Огноо', ]

            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)

            # Sheet body, remaining rows
            font_style = xlwt.XFStyle()

            if objs is not None:
                for row in objs:
                    row_num += 1
                    col_num = 0
                    ws.write(row_num, col_num, row.customer.code, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.customer.last_name + row.customer.first_name, font_style)
                    col_num += 1
                    addr = ''
                    address = Address.objects.filter(is_active='1', customer=row.customer).first()
                    if address is not None:
                        addr = address.address_name
                    ws.write(row_num, col_num, addr, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.uilchilgee.name, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.uilchilgee.payment, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, str(row.uil_date), font_style)

            wb.save(response)
            return response

        data = {
            "datas": objs,
            "servicelist": servicelist,
            "search_q": {
                "service": int(service) if service != '' else 0,
                "start_d": start_d,
                "end_d": end_d,
                "user_code": user_code,
            },
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)


class Uilchilgee_add(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/borluulalt/add_vilchilgee.html"
    permission_required = 'data.add_customeruilchilgeetulbur'
    objtoxls = None
    menu = "3"
    sub = "5"

    def get(self, request, *args, **kwargs):
        monters = User.objects.filter(groups__name__in=['Монтер', 'Борлуулалт тооцооны ажилтан', 'Борлуулалт тооцооны инженер', 'ХТ менежер', 'Тоолуурын инженер'], is_active='1')
        data = {
            "monters": monters,
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        services = rq.getlist('services', '')
        user_code = rq.get('user_code', '')
        tooluur_select = rq.get('tooluur_select', '')
        select_monter = rq.get('select_monter', '')
        uil_date = rq.get('uil_date', '')

        now_date = datetime.datetime.now()
        now_month = str(now_date.month)
        if now_month[0] == '0':
            now_month = now_month[1]
        tooluur = TooluurHistory.objects.filter(number = tooluur_select, year = str(now_date.year), month = now_month).first()
        if tooluur is None:
            if len(services) > 0:
                if uil_date != '':
                    uil_date = datetime.datetime.strptime(rq.get('uil_date', ''), '%Y-%m-%d')
                else:
                    uil_date = now_date

                for service in services:
                    tulbur_uil = TulburtUilchilgee.objects.filter(id=service, is_active='1').first()
                    u = CustomerUilchilgeeTulbur.objects.create(created_user_id=request.user.id,
                                                                created_date=now_date,
                                                                tooluur_id=Tooluur.objects.filter(number=tooluur_select).first().id,
                                                                customer_id=Customer.objects.filter(code=user_code).first().id,
                                                                uilchilgee=tulbur_uil,
                                                                uil_date=uil_date)
                    u.payment = u.uilchilgee.payment
                    u.year = str(now_date.year)
                    u.month = now_month
                    if select_monter != '':
                        monter = User.objects.get(id=select_monter)
                        u.monter_id = monter.id
                    u.save()
        else:
            messages.warning(request, 'Та ирэх сарын эхний заалт авахаас өмнө төлбөрт үйлчилгээгээ оруулна уу!')
        return redirect("/home/vilchilgee")


class UilchilgeeDelete(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/borluulalt/vilchilgee.html"
    permission_required = 'data.delete_customeruilchilgeetulbur'
    menu = "3"
    sub = "5"

    def get(self, request, id, *args, **kwargs):
        cuil = CustomerUilchilgeeTulbur.objects.filter(id=id).first()
        if cuil.avlaga is not None:
            messages.warning(request, 'Энэ төлбөрт үйлчилгээ дээр авлага үүссэн тул устгах боломжгүй!')
            return redirect("/home/vilchilgee")
        else:
            cuil.avlaga = None
            cuil.is_active = '0'
            cuil.save()
            messages.success(request, 'Амжилттай устгагдлаа!')
            return redirect("/home/vilchilgee")

    def post(self, request, *args, **kwargs):
        return redirect("/home/vilchilgee")


def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)


def get_tooluur_byuser(request):
    code = request.GET['user_code']
    result = []
    list = TooluurCustomer.objects.filter(customer_code=code)
    if len(list) > 0:
        for obj in list:
            result.append({'name': obj.tooluur.number, 'code': obj.tooluur.number})
            len(result)
        return HttpResponse(simplejson.dumps(result), content_type='application/json')
    else:
        print("not tooluur")


def get_username_addr(request):
    code = request.GET['user_code']

    result = []
    cus = Customer.objects.filter(code=code, is_active='1').first()
    addresses = Address.objects.filter(customer=cus, is_active='1').first()
    address = ''
    if addresses is not None:
        address = addresses.address_name

    if cus is not None:
        result.append({'user_name': cus.first_name + " " + cus.last_name,
                       'address_name': address,
                       'angilal': cus.customer_angilal })

        return HttpResponse(simplejson.dumps(result), content_type='application/json')


def get_uilchilgee_bytype(request):
    ang = request.GET['angilal']

    result = []
    uils = TulburtUilchilgee.objects.filter(is_active=1, angilal=ang)

    if uils is not None:
        print()
        if len(uils) > 0:
            for obj in uils:
                result.append({'name': obj.name, 'payment': obj.payment, 'id': obj.id})
            return HttpResponse(simplejson.dumps(result), content_type='application/json')
        else:
            print("not tooluur")