import datetime
import xlwt
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.views import View
from apps.homepage.forms import *
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin


class TuluvluguuList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/borluulalt/tuluwluguu.html"
    permission_required = 'data.view_tuluvluguu'
    menu = "3"
    sub = "1"

    qhereg_bus1 = """SElECT bich.id, SUM(bich.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) AS total_diff FROM data_bichilt bich
        JOIN data_tooluurcustomer tocu ON bich.tooluur_id = tocu.id LEFT JOIN data_transformator guid ON tocu.guidliin_trans_id = guid.id
        LEFT JOIN data_transformator huch ON tocu.huchdeliin_trans_id = huch.id WHERE bich.is_active = '1' AND tocu.is_active = '1'"""

    qhereg_bus2 = """SELECT bich.id, SUM(bich.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) AS total_diff FROM data_bichilt bich
        JOIN data_tooluurcustomer tocu ON bich.tooluur_id = tocu.id LEFT JOIN data_transformator guid ON tocu.guidliin_trans_id = guid.id
        LEFT JOIN data_transformator huch ON tocu.huchdeliin_trans_id = huch.id LEFT JOIN data_address addr ON tocu.customer_id = addr.customer_id
        WHERE bich.is_active = '1' AND tocu.is_active = '1' AND addr.is_active = '1'"""

    def get(self, request, *args, **kwargs):
        now = datetime.datetime.now()
        minus_month = now + relativedelta(months=-1)
        year = str(minus_month.year)
        if minus_month.day < 25:
            month = str(minus_month.month)
        else:
            month = str(now.month)
        list = []

        try:
            objs = Tuluvluguu.objects.filter(year=year, month=month)
            for o in objs:
                datas = {}
                if o.bus_type == '0':
                    qhereg_bus1 = self.qhereg_bus1 + " AND tocu.customer_code = '" + str(
                        o.code) + "' AND bich.year = '" + str(year) + "' and bich.month = '" + str(month) + "'"
                    try:
                        val = Bichilt.objects.raw(qhereg_bus1)[0].total_diff
                    except ObjectDoesNotExist:
                        val = 0
                elif o.bus_type == '1':
                    qhereg_bus2 = self.qhereg_bus2 + " AND addr.hothon_code = '" + str(
                        o.code) + "' AND bich.year = '" + str(year) + "' AND bich.month = '" + str(month) + "'"
                    try:
                        val = Bichilt.objects.raw(qhereg_bus2)[0].total_diff
                    except ObjectDoesNotExist:
                        val = 0
                else:
                    val = 0

                datas["id"] = o.id
                datas["code"] = o.code
                datas["name"] = o.name
                datas["tuluvluguu"] = o.tuluvluguu
                datas["hereg"] = val
                datas["zuruu"] = float(0 if o.tuluvluguu is None else o.tuluvluguu) - float(0 if val is None else val)
                datas["zuruu_huvi"] = float(0 if val is None else val) / float(0 if o.tuluvluguu is None else o.tuluvluguu) * 100
                datas["year"] = o.year
                datas["month"] = o.month
                list.append(datas)
        except ObjectDoesNotExist:
            return redirect('/home/tuluvluguu')

        data = {
            "datas": list,
            "year": year,
            "month": month,
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        year = rq.get('year', '')
        month = rq.get('month', '')

        if year != '' and month != '':
            try:
                objs = Tuluvluguu.objects.filter(year=year, month=month)
                list = []
                if objs is not None:
                    for o in objs:
                        datas = {}
                        if o.bus_type == '0':
                            qhereg_bus1 = self.qhereg_bus1 + " AND tocu.customer_code = '" + str(o.code) + "' AND bich.year = '" + str(year) + "' and bich.month = '" + str(month) + "'"
                            try:
                                val = Bichilt.objects.raw(qhereg_bus1)[0].total_diff
                            except ObjectDoesNotExist:
                                val = 0
                        elif o.bus_type == '1':
                            qhereg_bus2 = self.qhereg_bus2 + " AND addr.hothon_code = '" + str(o.code) + "' AND bich.year = '" + str(year) + "' AND bich.month = '" + str(month) + "'"
                            try:
                                val = Bichilt.objects.raw(qhereg_bus2)[0].total_diff
                            except ObjectDoesNotExist:
                                val = 0
                        else:
                            val = 0

                        datas["id"] = o.id
                        datas["code"] = o.code
                        datas["name"] = o.name
                        datas["tuluvluguu"] = o.tuluvluguu
                        datas["hereg"] = val
                        datas["zuruu"] = float(0 if o.tuluvluguu is None else o.tuluvluguu) - float(0 if val is None else val)
                        datas["zuruu_huvi"] = float(0 if val is None else val) / float(0 if o.tuluvluguu is None else o.tuluvluguu) * 100
                        datas["year"] = o.year
                        datas["month"] = o.month
                        list.append(datas)

                    if 'export_xls' in rq:
                        response = HttpResponse(content_type='application/ms-excel')
                        response['Content-Disposition'] = 'attachment; filename="tuluvluguu.xls"'

                        wb = xlwt.Workbook(encoding='utf-8')
                        ws = wb.add_sheet('Users')

                        # Sheet header, first row
                        row_num = 0

                        font_style = xlwt.XFStyle()
                        font_style.font.bold = True

                        columns = ['Хэрэглэгч | Хотхон', 'ХАЦЭХ-ний санал', 'ХАЦЭХ-ний гүйцэтгэл', 'Зөрүү кВтц', 'Зөрүү %', 'Жил', 'Сар']

                        for col_num in range(len(columns)):
                            ws.write(row_num, col_num, columns[col_num], font_style)

                        # Sheet body, remaining rows
                        font_style = xlwt.XFStyle()

                        for row in list:
                            row_num += 1
                            col_num = 0
                            ws.write(row_num, col_num, str(row['code']) + '' if row['name'] == '' else ' - ' + str(row['name']), font_style)
                            col_num += 1
                            ws.write(row_num, col_num, row['tuluvluguu'], font_style)
                            col_num += 1
                            ws.write(row_num, col_num, row['hereg'], font_style)
                            col_num += 1
                            ws.write(row_num, col_num, row['zuruu'], font_style)
                            col_num += 1
                            ws.write(row_num, col_num, row['zuruu_huvi'], font_style)
                            col_num += 1
                            ws.write(row_num, col_num, row['year'], font_style)
                            col_num += 1
                            ws.write(row_num, col_num, row['month'], font_style)

                        wb.save(response)
                        return response

                data = {
                    "datas": list,
                    "year": year,
                    "month": month,
                    "menu": self.menu,
                    "sub": self.sub
                }
                return render(request, self.template_name, data)
            except ObjectDoesNotExist:
                return redirect('/home/tuluvluguu')
        else:
            return redirect('/home/tuluvluguu')


class TuluvluguuAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_tuluvluguu'
    template_name = "homepage/borluulalt/add_tuluv.html"
    starter_q = "select * from (select id,code,last_name as name, customer_angilal as bus_type from data_customer where customer_angilal=0 union select id,code, h.name as name, 1 as bus_type from data_hothon h) as t"
    q = "select * from (select id,code,last_name as name, customer_angilal as bus_type from data_customer where customer_angilal=0 and is_active=1 union select id,code, h.name as name, 1 as bus_type from data_hothon h) as t"
    menu = "3"
    sub = "1"

    def get(self, request, *args, **kwargs):
        q = self.starter_q
        objs = Tuluvluguu.objects.raw(q)

        data = {
            "datas": objs,
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        q = self.starter_q
        rq = request.POST
        year = rq.get('year', '')
        month = rq.get('month', '')
        org_tuluv = rq.get('org_tuluv', '')
        value = rq.get('value', '')
        if (year != None and month != None):
            q += " where t.code not in (select code from data_tuluvluguu where year =" + year + " and month=" + month + ")"
        objs = Tuluvluguu.objects.raw(q)
        qe = self.q
        if (org_tuluv != None):
            qe += " where t.code=" + org_tuluv
            print(org_tuluv)
        e = Tuluvluguu.objects.raw(qe)[0]
        print(e.name)
        if (e != None):
            try:
                preT = Tuluvluguu.objects.get(code=e.code, year=year, month=month)
                t = preT
            except Tuluvluguu.DoesNotExist:
                t = Tuluvluguu.objects.create(created_user_id=request.user.id)
            t.name = e.name
            t.code = e.code
            t.bus_type = e.bus_type
            t.year = year
            t.month = month
            t.tuluvluguu = value
            t.created_user_id = request.user.id
            t.save()
        data = {
            "datas": objs,
            "year": year,
            "month": month,
            "menu": self.menu,
            "sub": self.sub
        }
        return redirect('/home/tuluvluguu')


class TuluvluguuDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_tuluvluguu'
    template_name = "homepage/borluulalt/tuluwluguu.html"
    menu = "3"
    sub = "1"

    def get(self, request, id, *args, **kwargs):
        t = Tuluvluguu.objects.get(id=id)
        t.delete()
        data = {
            "menu": self.menu,
            "sub": self.sub
        }
        return redirect('/home/tuluvluguu')