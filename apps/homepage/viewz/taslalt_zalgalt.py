import datetime

import xlwt
from django.http import HttpResponse
from django.views import View
from apps.homepage.forms import *
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class TaslaltZalgaltList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_salgalt'
    template_name = "homepage/borluulalt/taslalt.html"
    qry = """SELECT tas.id, cus.code, cus.first_name, cus.last_name, addr.address_name, tas.status, tas.salgasan_date, tas.zalgasan_date
        FROM data_salgalt tas JOIN data_customer cus ON tas.customer_id = cus.id JOIN data_address addr ON cus.id = addr.customer_id
        WHERE tas.is_active = '1' AND cus.is_active = '1' AND addr.is_active = '1'"""
    menu = "3"
    sub = "7"

    def get(self, request, *args, **kwargs):
        q = self.qry + " ORDER BY tas.created_date DESC"
        cus = list(Customer.objects.raw(q))

        data = {
            "datas": cus,
            "menu": self.menu,
            "sub": self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST

        customer_code = rq.get('customer_code', '')
        customer_name = rq.get('customer_name', '')
        address = rq.get('tooluur_number', '')
        phone = rq.get('tooluur_mark', '')
        select_status = rq.get('select_status', '')

        srchQry = self.qry

        if customer_code != '':
            srchQry = srchQry + " AND cus.code LIKE '%%" + customer_code + "%%'"
        if customer_name != '':
            srchQry = srchQry + " AND (cus.first_name LIKE '%%" + customer_name + "%%' OR cus.last_name LIKE '%%" + customer_name + "%%')"
        if address != '':
            srchQry = srchQry + " AND addr.address_name LIKE '%%" + address + "%%'"
        if phone != '':
            srchQry = srchQry + " AND cus.phone LIKE '%%" + phone + "%%'"
        if select_status != '':
            srchQry = srchQry + " AND tas.status = " + select_status

        srchQry = srchQry + " ORDER BY tas.created_date DESC"
        cuss = list(Customer.objects.raw(srchQry))

        if 'export_xls' in rq:
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="taslalt_zalgalt.xls"'

            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Users')

            # Sheet header, first row
            row_num = 0

            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            columns = ['Хэрэглэгчийн код', 'Овог нэр', 'Хаяг', 'Төлөв', 'Тасалсан огноо', 'Залгасан огноо', ]

            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)

            # Sheet body, remaining rows
            font_style = xlwt.XFStyle()

            if cuss is not None:
                for row in cuss:
                    row_num += 1
                    col_num = 0
                    ws.write(row_num, col_num, row.code, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.last_name + row.first_name, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.address_name, font_style)
                    col_num += 1
                    status = ''
                    if row.status == '0':
                        status = 'Таслалт хийх'
                    elif row.status == '1':
                        status = 'Тасласан'
                    elif row.status == '2':
                        status = 'Залгасан'
                    ws.write(row_num, col_num, status , font_style)
                    col_num += 1
                    ws.write(row_num, col_num, str(row.salgasan_date) if row.salgasan_date is not None else '', font_style)
                    col_num += 1
                    ws.write(row_num, col_num, str(row.zalgasan_date) if row.zalgasan_date is not None else '', font_style)

            wb.save(response)
            return response


        search = {'customer_code': customer_code, 'customer_name': customer_name, 'address': address,
                  'phone': phone, 'select_status': select_status}

        data = {
            "datas": cuss,
            "search": search,
            "menu": self.menu,
            "sub": self.sub
        }

        return render(request, self.template_name, data)


class TaslaltHiih(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_salgalt'

    def get(self, request, id, *args, **kwargs):
        s = Salgalt.objects.get(id=id)
        s.salgasan_date = datetime.datetime.today()
        s.status = 1
        s.save()
        return redirect("/home/borluulalt/taslalt")


class ZalgaltHiih(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_salgalt'

    def get(self, request, id, *args, **kwargs):
        s = Salgalt.objects.get(id=id)
        s.zalgasan_date = datetime.datetime.today()
        s.status = 2
        s.save()
        return redirect("/home/borluulalt/taslalt")