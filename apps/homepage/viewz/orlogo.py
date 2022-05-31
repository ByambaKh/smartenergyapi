# coding=utf-8
import xlwt
import xlrd
import simplejson
from xlrd import open_workbook
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, HttpResponse, redirect
from django.views import View
from apps.homepage.forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.extra import *
from decimal import Decimal
from django.contrib.auth.mixins import PermissionRequiredMixin
from apps.homepage.viewz.services.posapi import PosapiMTA
from datetime import datetime
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import os
from django.conf import settings
import json
class OrlogoList(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = 'homepage/borluulalt/orlogo.html'
    permission_required = 'data.view_paymenthistory'
    login_url = '/home/index'
    menu = "3"
    sub = "4"
    olist = []

    def get(self, request, *args, **kwargs):
        now = datetime.now()
        minus_month = now + relativedelta(months=-1)

        start_date = str(now.year) + '-' + str(now.month) + '-' + '01'
        if now.day < 10:
            now_day = '0' + str(now.day)
        else:
            now_day = str(now.day)
        end_date = str(now.year) + '-' + str(now.month) + '-' + now_day

        qry_pahi = """SELECT pahi.id, cust.code, cust.last_name, cust.first_name, cust.customer_angilal,
            IF(IFNULL((fiba.balance + IFNULL((SELECT (avla.heregleenii_tulbur + avla.uilchilgeenii_tulbur + avla.barimt_une)
            FROM data_avlaga avla WHERE avla.customer_id = cust.id AND avla.is_active = '1' AND avla.year = '"""+str(now.year)+"""' AND avla.month = '"""+str(now.month)+"""'), 0.00)), 0.00) > pahi.pay_total, pahi.pay_total,
            IFNULL((fiba.balance + IFNULL((SELECT (avla.heregleenii_tulbur + avla.uilchilgeenii_tulbur + avla.tv_huraamj + IFNULL(avla.light, 0.00) + IFNULL(avla.ten, 0.00) + avla.barimt_une)
            FROM data_avlaga avla WHERE avla.customer_id = cust.id AND avla.is_active = '1' AND avla.year = '"""+str(now.year)+"""' AND avla.month = '"""+str(now.month)+"""'), 0.00)), 0.00)) AS cur_pay,
            IF(IFNULL((fiba.balance + IFNULL((SELECT (avla.heregleenii_tulbur + avla.uilchilgeenii_tulbur + avla.tv_huraamj + IFNULL(avla.light, 0.00) + IFNULL(avla.ten, 0.00) + avla.barimt_une)
            FROM data_avlaga avla WHERE avla.customer_id = cust.id AND avla.is_active = '1' AND avla.year = '"""+str(now.year)+"""' AND avla.month = '"""+str(now.month)+"""'), 0.00)
            - pahi.pay_total), 0) < 0, ((fiba.balance + IFNULL((SELECT (avla.heregleenii_tulbur + avla.uilchilgeenii_tulbur + avla.tv_huraamj + IFNULL(avla.light, 0.00) + IFNULL(avla.ten, 0.00) + avla.barimt_une)
            FROM data_avlaga avla WHERE avla.customer_id = cust.id AND avla.is_active = '1' AND avla.year = '"""+str(now.year)+"""' AND avla.month = '"""+str(now.month)+"""'), 0.00)
            - pahi.pay_total) * -1), 0) AS iluu, pahi.pay_total, bank.name AS bank_name, pahi.pay_date, addr.address_name FROM data_paymenthistory pahi
            JOIN data_customer cust ON pahi.customer_id = cust.id JOIN data_final_balance fiba ON pahi.customer_id = fiba.customer_id
            LEFT JOIN data_bank bank ON pahi.bank_id = bank.id LEFT JOIN data_address addr ON pahi.customer_id = addr.customer_id
            WHERE cust.is_active = '1' AND pahi.is_active = '1' AND fiba.year = '"""+str(minus_month.year)+"""' AND fiba.month = '"""+str(minus_month.month)+"""' AND pahi.pay_date
            BETWEEN '"""+start_date+""" 00:00:00.000000' AND '"""+end_date+""" 23:59:59.999999' ORDER BY pahi.pay_date DESC, pahi.created_date DESC;"""
        try:
            pahis = PaymentHistory.objects.raw(qry_pahi)
        except Exception as e:
            pahis = None

        datalist = []
        total_payment = 0
        total_iluu = 0
        total_cur_pay = 0
        if pahis is not None:
            for d in pahis:
                l = {}
                l['id'] = d.id
                l['cur_pay'] = d.cur_pay
                total_cur_pay += d.cur_pay
                l['iluu'] = d.iluu
                total_iluu += d.iluu
                l['payment'] = d.pay_total
                total_payment += d.pay_total
                l['date_max'] = d.pay_date
                l['code'] = d.code
                l['bank_name'] = d.bank_name
                l['name'] = d.last_name + " " + d.first_name
                l['address'] = d.address_name
                datalist.append(l)

        banks = Bank.objects.filter(is_active='1')

        if (len(datalist) == 0):
            OrlogoList.olist = None
        else:
            OrlogoList.olist = datalist

        data = {
            "search_q": {
                "start_date": start_date,
                "end_date": end_date
            },
            "data_orlogo": datalist,
            "banks": banks,
            "menu": self.menu,
            "sub": self.sub,
            "total_pay": total_payment,
            "total_iluu": total_iluu,
            "total_cur_pay": total_cur_pay,
        }

        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST

        start_date = rq.get('start_date', '')
        end_date = rq.get('end_date', '')
        customer_code = rq.get('customer_code', '')
        user_name = rq.get('user_name', '').strip()
        select_bank = rq.get('select_bank', '')
        select_angilal = rq.get('select_angilal', '')

        search_start = datetime.strptime(start_date, '%Y-%m-%d')
        minus_month = search_start + relativedelta(months=-1)

        qry_pahi = """SELECT pahi.id, cust.code, cust.last_name, cust.first_name, cust.customer_angilal,
            IF(IFNULL((fiba.balance + IFNULL((SELECT (avla.heregleenii_tulbur + avla.uilchilgeenii_tulbur + avla.barimt_une)
            FROM data_avlaga avla WHERE avla.customer_id = cust.id AND avla.is_active = '1' AND avla.year = '"""+str(search_start.year)+"""' AND avla.month = '"""+str(search_start.month)+"""'), 0.00)), 0.00) > pahi.pay_total, pahi.pay_total,
            IFNULL((fiba.balance + IFNULL((SELECT (avla.heregleenii_tulbur + avla.uilchilgeenii_tulbur + avla.tv_huraamj + IFNULL(avla.light, 0.00) + IFNULL(avla.ten, 0.00) + avla.barimt_une)
            FROM data_avlaga avla WHERE avla.customer_id = cust.id AND avla.is_active = '1' AND avla.year = '"""+str(search_start.year)+"""' AND avla.month = '"""+str(search_start.month)+"""'), 0.00)), 0.00)) AS cur_pay,
            IF(IFNULL((fiba.balance + IFNULL((SELECT (avla.heregleenii_tulbur + avla.uilchilgeenii_tulbur + avla.tv_huraamj + IFNULL(avla.light, 0.00) + IFNULL(avla.ten, 0.00) + avla.barimt_une)
            FROM data_avlaga avla WHERE avla.customer_id = cust.id AND avla.is_active = '1' AND avla.year = '"""+str(search_start.year)+"""' AND avla.month = '"""+str(search_start.month)+"""'), 0.00)
            - pahi.pay_total), 0) < 0, ((fiba.balance + IFNULL((SELECT (avla.heregleenii_tulbur + avla.uilchilgeenii_tulbur + avla.tv_huraamj + IFNULL(avla.light, 0.00) + IFNULL(avla.ten, 0.00) + avla.barimt_une)
            FROM data_avlaga avla WHERE avla.customer_id = cust.id AND avla.is_active = '1' AND avla.year = '"""+str(search_start.year)+"""' AND avla.month = '"""+str(search_start.month)+"""'), 0.00)
            - pahi.pay_total) * -1), 0) AS iluu, pahi.pay_total, bank.name AS bank_name, pahi.pay_date, addr.address_name FROM data_paymenthistory pahi
            JOIN data_customer cust ON pahi.customer_id = cust.id JOIN data_final_balance fiba ON pahi.customer_id = fiba.customer_id
            LEFT JOIN data_bank bank ON pahi.bank_id = bank.id LEFT JOIN data_address addr ON pahi.customer_id = addr.customer_id
            WHERE cust.is_active = '1' AND pahi.is_active = '1' AND fiba.year = '"""+str(minus_month.year)+"""' AND fiba.month = '"""+str(minus_month.month)+"""' AND pahi.pay_date
            BETWEEN '"""+start_date+""" 00:00:00.000000' AND '"""+end_date+""" 23:59:59.999999'"""

        if customer_code != "":
            qry_pahi = qry_pahi + " AND cust.code = '" + customer_code + "'"
        if user_name != "":
            qry_pahi = qry_pahi + " AND cust.first_name LIKE '%%" + user_name + "%%' OR cust.last_name LIKE '%%" + user_name + "%%'"
        if select_bank != "":
            qry_pahi = qry_pahi + " AND bank.id = " + select_bank
        if select_angilal != "":
            qry_pahi = qry_pahi + " AND cust.customer_angilal = '" + select_angilal + "'"

        try:
            qry_pahi += " ORDER BY pahi.pay_date DESC;"
            pahis = PaymentHistory.objects.raw(qry_pahi)
        except Exception:
            pahis = None

        banks = Bank.objects.filter(is_active='1')

        datalist = []
        total_payment = 0
        total_iluu = 0
        total_cur_pay = 0

        if pahis is not None:
            for d in pahis:
                l = {}
                l['id'] = d.id
                l['cur_pay'] = d.cur_pay
                total_cur_pay += d.cur_pay
                l['iluu'] = d.iluu
                total_iluu += d.iluu
                l['payment'] = d.pay_total
                total_payment += d.pay_total
                l['date_max'] = d.pay_date
                l['code'] = d.code
                l['bank_name'] = d.bank_name
                l['name'] = d.last_name + " " + d.first_name
                l['address'] = d.address_name
                l['customer_angilal'] = d.customer_angilal
                datalist.append(l)

        if 'export_xls' in request.POST:
            bank_name = 'Бүх банк'

            if select_bank != '':
                bank = Bank.objects.filter(is_active='1', code=select_bank).first()
                if bank is not None:
                    bank_name = bank.name

            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="Orlogo_'+start_date+'_'+end_date+'.xls"'

            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Users')

            now = datetime.now()
            row_num = 3

            borders = xlwt.Borders()
            borders.left = xlwt.Borders.THIN
            borders.right = xlwt.Borders.THIN
            borders.top = xlwt.Borders.THIN
            borders.bottom = xlwt.Borders.THIN
            header_style = xlwt.XFStyle()
            header_style.font.bold = True
            header_style.alignment.wrap = True
            header_style.alignment.vert = header_style.alignment.VERT_CENTER
            header_style.borders = borders
            title_style = xlwt.XFStyle()
            title_style.font.bold = True
            row_style = xlwt.XFStyle()
            row_style.borders = borders
            font_style = xlwt.XFStyle()

            ws.write(0, 2, '"' + bank_name + '"-ны ' + start_date + ' -- ' + end_date + '-ний орлогын дэлгэрэнгүй тайлан', title_style)
            ws.write(2, 5, 'Хэвлэсэн: ' + now.strftime('%Y-%m-%d'), font_style)

            columns = ['№','Код', 'Хэрэглэгчийн нэр', 'Огноо', 'Тухайн сард орсон', 'Урьдчилж төлсөн', 'Нийт Дүн']
            col_width = [int(5 * 260), int(10 * 260), int(30 * 260), int(10 * 260), int(14 * 260), int(14 * 260), int(14 * 260)]
            for col_num in range(len(columns)):
                ws.col(col_num).width = col_width[col_num]
                ws.write(row_num, col_num, columns[col_num], header_style)

            row_num += 1
            ws.write_merge(row_num, row_num, 0, 6, 'Ахуйн хэрэглэгч', header_style)
            ahui_counter = 0
            ahui_cur_pay = 0
            ahui_iluu = 0
            ahui_payment = 0
            for data in datalist:
                if data['customer_angilal'] == '1':
                    row_num += 1
                    col_num = 0
                    ahui_counter += 1
                    ws.write(row_num, col_num, str(ahui_counter), row_style)
                    col_num += 1
                    ws.write(row_num, col_num, data['code'], row_style)
                    col_num += 1
                    ws.write(row_num, col_num, data['name'], row_style)
                    col_num += 1
                    ws.write(row_num, col_num, str(data['date_max']), row_style)
                    col_num += 1
                    ws.write(row_num, col_num, data['cur_pay'], row_style)
                    ahui_cur_pay = round(ahui_cur_pay + float(data['cur_pay']), 2)
                    col_num += 1
                    ws.write(row_num, col_num, data['iluu'], row_style)
                    ahui_iluu = round(ahui_iluu + float(data['iluu']), 2)
                    col_num += 1
                    ws.write(row_num, col_num, data['payment'], row_style)
                    ahui_payment = round(ahui_payment + float(data['payment']), 2)
            row_num += 1
            ws.write_merge(row_num, row_num, 0, 2, 'Хэрэглэгчийн тоо: ' + str(ahui_counter), header_style)
            ws.write(row_num, 3, '', header_style)
            ws.write(row_num, 4, str(ahui_cur_pay), header_style)
            ws.write(row_num, 5, str(ahui_iluu), header_style)
            ws.write(row_num, 6, str(ahui_payment), header_style)

            row_num += 1
            ws.write_merge(row_num, row_num, 0, 6, 'Байгууллага, ААН', header_style)
            aan_counter = 0
            aan_cur_pay = 0
            aan_iluu = 0
            aan_payment = 0
            for data in datalist:
                if data['customer_angilal'] == '0':
                    row_num += 1
                    col_num = 0
                    aan_counter += 1
                    ws.write(row_num, col_num, str(aan_counter), row_style)
                    col_num += 1
                    ws.write(row_num, col_num, data['code'], row_style)
                    col_num += 1
                    ws.write(row_num, col_num, data['name'], row_style)
                    col_num += 1
                    ws.write(row_num, col_num, str(data['date_max']), row_style)
                    col_num += 1
                    ws.write(row_num, col_num, data['cur_pay'], row_style)
                    aan_cur_pay = round(aan_cur_pay + float(data['cur_pay']), 2)
                    col_num += 1
                    ws.write(row_num, col_num, data['iluu'], row_style)
                    aan_iluu = round(aan_iluu + float(data['iluu']), 2)
                    col_num += 1
                    ws.write(row_num, col_num, data['payment'], row_style)
                    aan_payment = round(aan_payment + float(data['payment']), 2)
            row_num += 1
            ws.write_merge(row_num, row_num, 0, 2, 'Хэрэглэгчийн тоо: ' + str(aan_counter), header_style)
            ws.write(row_num, 3, '', header_style)
            ws.write(row_num, 4, str(aan_cur_pay), header_style)
            ws.write(row_num, 5, str(aan_iluu), header_style)
            ws.write(row_num, 6, str(aan_payment), header_style)

            row_num += 1
            ws.write_merge(row_num, row_num, 0, 2, 'Нийт хэрэглэгчийн тоо: ' + str(aan_counter + ahui_counter), header_style)
            ws.write(row_num, 3, '', header_style)
            ws.write(row_num, 4, str(round(aan_cur_pay + ahui_cur_pay, 2)), header_style)
            ws.write(row_num, 5, str(round(aan_iluu + ahui_iluu, 2)), header_style)
            ws.write(row_num, 6, str(round(aan_payment + ahui_payment, 2)), header_style)

            wb.save(response)
            return response

        data = {
            "search_q": {
                "start_date": start_date,
                "end_date": end_date,
                "customer_code": customer_code,
                "user_name": user_name,
                "bank": 0 if select_bank == '' else int(select_bank),
                "customer_angilal": select_angilal,
            },
            "data_orlogo": datalist,
            "banks": banks,
            "total_pay": total_payment,
            "total_iluu": total_iluu,
            "total_cur_pay": total_cur_pay,
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)

    def export_xls(request):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="orlogo.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Users')

        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        # columns = ['Код', 'Нэр', 'Хаяг', 'Эцсийн үлдэгдэл', 'Орлого', 'Огноо']
        columns = ['Код', 'Нэр', 'Хаяг', 'Банк', 'Орлого', 'Огноо']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()

        rows = OrlogoList.olist

        for row in rows:
            row_num += 1
            col_num = 0
            ws.write(row_num, col_num, row['code'], font_style)
            col_num += 1
            ws.write(row_num, col_num, row['name'], font_style)
            col_num += 1
            ws.write(row_num, col_num, row['address'], font_style)
            # col_num += 1
            # ws.write(row_num, col_num, row['uldegdel'], font_style)
            col_num += 1
            ws.write(row_num, col_num, row['bank_name'], font_style)
            col_num += 1
            ws.write(row_num, col_num, row['payment'], font_style)
            col_num += 1
            ws.write(row_num, col_num, str(row['date_max']), font_style)

        wb.save(response)
        return response


class OrlogoAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = 'homepage/borluulalt/orlogo_add.html'
    permission_required = 'data.add_paymenthistory'
    login_url = '/home/index'
    lpre = []
    avlagaLast = []
    payLast = None
    pay_uldegdel = None
    o_date = None
    o_bank = None
    menu = "3"
    sub = "4"

    def get(self, request, *args, **kwargs):
        bank = Bank.objects.filter(is_active=1)
        p = OrlogoAdd.lpre
        last = OrlogoAdd.avlagaLast
        pLast = OrlogoAdd.payLast
        pUl = OrlogoAdd.pay_uldegdel

        data = {
            "bank_id": OrlogoAdd.o_bank,
            "bank": bank,
            "save_orlogo_date": OrlogoAdd.o_date,
            "preList": p,
            "avlagalast": last,
            "paylast": pLast,
            "pUl": pUl,
            "menu":self.menu,
            "sub":self.sub,
            "qr_data":None
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        code = request.POST['user_code']
        orlogo_date = request.POST['orlogo_date']
        select_bank = request.POST['select_bank']
        total = Decimal(request.POST['orlogo_total'])
        bichilt = Decimal(request.POST['bichilt'])
        ehnii = Decimal(request.POST['ehnii'])
        pay_total = Decimal(request.POST['pay_total'])
        balance = Decimal(request.POST['balance'])
        orlogo = total

        OrlogoAdd.o_date = orlogo_date
        OrlogoAdd.o_bank = int(select_bank)

        customer = Customer.objects.filter(code=code).first()

        if customer is not None:
            today = datetime.now()
            minus1_month = today + relativedelta(months=-1)
            last_date = str(today)[:10]

            today_year = last_date[:4]
            today_month = last_date[5:7]
            orlogo_year = orlogo_date[:4]
            orlogo_month = orlogo_date[5:7]

            if (today_year + today_month) != (orlogo_year + orlogo_month):
                if '0' == today_month[0]:
                    today_month = today_month[1]
                if '0' == orlogo_month[0]:
                    orlogo_month = orlogo_month[1]
                if int(orlogo_year) == int(today_year):
                    if int(today_year + today_month) - 1 == int(orlogo_year + orlogo_month):
                        fiba = Final_Balance.objects.filter(year=orlogo_year, month=orlogo_month, customer_id=customer.id).first()
                        if fiba is not None:
                            fiba.balance = Decimal(round(fiba.balance - total, 2))
                            fiba.save()
                    else:
                        messages.error(request, 'Та зөвхөн өмнөх сарын орлого л нөхөж оруулах боломжтой. Тэрнээс өмнөх сарын орлого оруулах боломжгүй!')
                        return redirect('/home/borluulalt/orlogo_add')
                elif int(orlogo_month) == 12:
                    fiba = Final_Balance.objects.filter(year=orlogo_year, month=orlogo_month, customer_id=customer.id).first()
                    if fiba is not None:
                        fiba.balance = Decimal(round(fiba.balance - total, 2))
                        fiba.save()
                else:
                    messages.error(request, 'Та зөвхөн өмнөх сарын орлого л нөхөж оруулах боломжтой. Тэрнээс өмнөх сарын орлого оруулах боломжгүй!')
                    return redirect('/home/borluulalt/orlogo_add')

            pay_date = datetime.strptime(orlogo_date + ' 00:00', '%Y-%m-%d %H:%M')

            his = PaymentHistory.objects.create(pay_date=pay_date, pay_total=total, customer=customer)

            # avlaga_list = Avlaga.objects.filter(customer=customer, pay_type='0').order_by('created_date')
            # if avlaga_list is not None:
            #     for avlaga in avlaga_list:
            #         ald_hemjee = Decimal(0)
            #         # days = (datetime.now() - avlaga.tulbur_date).days
            #         # if days > 1:
            #         #     ald_hemjee = Decimal(avlaga.pay_uld / Decimal(avlaga.ald_huvi) / Decimal(days))
            #
            #         if total >= (avlaga.pay_uld + ald_hemjee):
            #             total = total - Decimal(avlaga.pay_uld + ald_hemjee)
            #             avlaga.ald_hemjee = ald_hemjee
            #             avlaga.pay_type = '1'  # tulsun tuluv
            #             avlaga.paid_date = pay_date
            #             avlaga.pay_uld = 0.00
            #         else:
            #             if total > 0:
            #                 avlaga.ald_hemjee = ald_hemjee
            #                 total = total - ald_hemjee
            #                 avlaga.pay_uld = avlaga.pay_uld - total
            #                 total = 0.00
            #         avlaga.payment_history = his
            #         avlaga.save()
            # if total > 0:
            #     payment = Payment.objects.filter(customer=customer).first()
            #     if payment is not None:
            #         payment.uldegdel = payment.uldegdel + total
            #         payment.save()
            #     else:
            #         payment = Payment.objects.create(customer=customer, uldegdel=Decimal(total))
            #         payment.save()
            #     his.payment = payment

            bank = Bank.objects.filter(code=select_bank).first()

            his.bank = bank
            his.created_user_id = request.user.id
            his.save()

            orlogo = str('{:.{prec}f}'.format(orlogo, prec=2))
            ehnii_orlogo = str('{:.{prec}f}'.format(pay_total, prec=2))
            ehnii = str('{:.{prec}f}'.format(ehnii, prec=2))
            bichilt = str('{:.{prec}f}'.format(bichilt, prec=2))
            balance = str('{:.{prec}f}'.format(balance, prec=2))

            if(select_bank == '6' or select_bank == '5'):

                cur_month_avlaga = Avlaga.objects.filter(customer_id=customer.id, is_active='1').order_by('-created_date').first()
                #cur_month_avlaga = Avlaga.objects.filter(customer=customer, is_active='1', month=today_month, year=today_year).first()
                if cur_month_avlaga is not None:
                    year = str(cur_month_avlaga.year)
                    month = str(cur_month_avlaga.month)
                    if len(month) == 1:
                        month = '0' + month
                    start_date = year + '-' + month + '-01'
                    if customer.customer_angilal == '1':
                        return redirect('/home/borluulalt/new_invoice_ahui/1/' + code + '/' + start_date + '/' + last_date + '/' + str(ehnii) + '/' + str(ehnii_orlogo) + '/' + str(orlogo) + '/' + str(bichilt) + '/')
                    else:
                        return redirect('/home/borluulalt/new_invoice_aan/1/' + code + '/' + start_date + '/' + last_date + '/' + str(ehnii) + '/' + str(ehnii_orlogo) + '/' + str(orlogo) + '/' + str(bichilt) + '/')

            else:
                return redirect('/home/borluulalt/orlogo_list')

        #return redirect('/home/borluulalt/orlogo_list')

class OrlogoImport(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = 'homepage/borluulalt/orlogo_import.html'
    permission_required = 'data.add_paymenthistory'
    login_url = '/home/index'
    lpre = []
    avlagaLast = []
    payLast = None
    pay_uldegdel = None
    o_date = None
    o_bank = None
    menu = "3"
    sub = "4"

    def get(self, request, *args, **kwargs):
        bank = Bank.objects.filter(is_active=1)
        p = OrlogoImport.lpre
        last = OrlogoImport.avlagaLast
        pLast = OrlogoImport.payLast
        pUl = OrlogoImport.pay_uldegdel

        data = {
            "bank_id": OrlogoAdd.o_bank,
            "bank": bank,
            "save_orlogo_date": OrlogoAdd.o_date,
            "preList": p,
            "avlagalast": last,
            "paylast": pLast,
            "pUl": pUl,
            "menu":self.menu,
            "sub":self.sub,
            "qr_data":None
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        bank = Bank.objects.filter(is_active=1)
        p = OrlogoImport.lpre
        last = OrlogoImport.avlagaLast
        pLast = OrlogoImport.payLast
        pUl = OrlogoImport.pay_uldegdel
        upload_file = None
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, 'tmp/data.xls'))
        except Exception:
            test = True
        if 'file' in request.FILES:
            upload_file = request.FILES['file']
            path = default_storage.save('tmp/data.xls', ContentFile(upload_file.read()))
            #print(upload_file.name)

            wb = open_workbook(os.path.join(settings.MEDIA_ROOT, 'tmp/data.xls'), encoding_override="cp1252")
            strtest = ""
            for sheet in wb.sheets():
                number_of_rows = sheet.nrows
                number_of_columns = sheet.ncols

                orlogo = []



                for row in range(1, number_of_rows):
                    try:
                        item = {}

                        item["code"] = str(int(round(float(sheet.cell(row, 1).value))))
                        print(int(sheet.cell(row, 1).value))
                        customer = Customer.objects.filter(is_active=1, code = str(item["code"])).first()
                        if(customer is not None):

                            item["name"] = customer.last_name + " " + customer.first_name
                            dval = sheet.cell(row, 0).value
                            #dt = datetime.fromordinal(dval)
                            date_value =datetime(*xlrd.xldate_as_tuple(dval, wb.datemode))
                            month = str(date_value.month)
                            if(len(month) == 1):
                                month = "0" + month
                            day = str(date_value.day)
                            if (len(day) == 1):
                                day = "0" + day
                            item["date"] = str(date_value.year) + '-' + month + '-' + day
                            item["amount"] = sheet.cell(row, 2).value
                            item["bank_id"] = round(float(sheet.cell(row, 3).value), 0)
                            item["cus_id"] = customer.id
                            bank = Bank.objects.filter(is_active=1, code=int(item["bank_id"])).first()
                            if (bank is not None):
                                #print(bank.code)
                                item["bank"] = bank.name
                                item["bank_id"] = bank.id
                                orlogo.append(item)
                                #print(str(item))

                        else:
                            print("customer not found" )
                    except Exception as err:
                        print(err)


            os.remove(os.path.join(settings.MEDIA_ROOT, 'tmp/data.xls'))
            json_string = json.dumps(orlogo)
            data = {
                "menu": self.menu,
                "sub": self.sub,
                "orlogo": orlogo,
                "json_string": json_string
            }
        else:
            if 'save' in request.POST:
                values = request.POST["values"]

                orlogos = json.loads(values)

                for idata in orlogos:
                    customer = Customer.objects.filter(code=idata["code"]).first()

                    today = datetime.now()
                    minus1_month = today + relativedelta(months=-1)
                    last_date = str(today)[:10]

                    today_year = last_date[:4]
                    today_month = last_date[5:7]
                    orlogo_year = idata["date"][:4]
                    orlogo_month = idata["date"][5:7]

                    if (today_year + today_month) != (orlogo_year + orlogo_month):
                        if '0' == today_month[0]:
                            today_month = today_month[1]
                        if '0' == orlogo_month[0]:
                            orlogo_month = orlogo_month[1]
                        if int(orlogo_year) == int(today_year):
                            if int(today_year + today_month) - 1 == int(orlogo_year + orlogo_month):
                                fiba = Final_Balance.objects.filter(year=orlogo_year, month=orlogo_month,
                                                                    customer_id=idata["cus_id"]).first()
                                if fiba is not None:
                                    total = Decimal(idata["amount"])
                                    fiba.balance = Decimal(round(fiba.balance - total, 2))
                                    fiba.save()
                            else:
                                messages.error(request,
                                               'Та зөвхөн өмнөх сарын орлого л нөхөж оруулах боломжтой. Тэрнээс өмнөх сарын орлого оруулах боломжгүй!')
                                #return redirect('/home/borluulalt/orlogo_add')
                        elif int(orlogo_month) == 12:
                            fiba = Final_Balance.objects.filter(year=orlogo_year, month=orlogo_month,
                                                                customer_id=idata["id"]).first()
                            if fiba is not None:
                                fiba.balance = Decimal(round(fiba.balance - idata["amount"], 2))
                                fiba.save()
                        else:
                            messages.error(request,
                                           'Та зөвхөн өмнөх сарын орлого л нөхөж оруулах боломжтой. Тэрнээс өмнөх сарын орлого оруулах боломжгүй!')
                            #return redirect('/home/borluulalt/orlogo_add')

                    pay_date = datetime.strptime(idata["date"] + ' 00:00', '%Y-%m-%d %H:%M')

                    his = PaymentHistory.objects.create(pay_date=pay_date, pay_total=idata["amount"], customer=customer)

                    bank = Bank.objects.filter(code=idata["bank_id"]).first()

                    his.bank = bank
                    his.created_user_id = request.user.id
                    his.save()
            data = {
                "menu": self.menu,
                "sub": self.sub,
            }

        return render(request, self.template_name, data)
        # code = request.POST['user_code']
        # orlogo_date = request.POST['orlogo_date']
        # select_bank = request.POST['select_bank']
        # total = Decimal(request.POST['orlogo_total'])
        # bichilt = Decimal(request.POST['bichilt'])
        # ehnii = Decimal(request.POST['ehnii'])
        # pay_total = Decimal(request.POST['pay_total'])
        # balance = Decimal(request.POST['balance'])
        # orlogo = total
        #
        # OrlogoAdd.o_date = orlogo_date
        # OrlogoAdd.o_bank = int(select_bank)
        #
        # customer = Customer.objects.filter(code=code).first()
        #
        # if customer is not None:
        #     today = datetime.now()
        #     minus1_month = today + relativedelta(months=-1)
        #     last_date = str(today)[:10]
        #
        #     today_year = last_date[:4]
        #     today_month = last_date[5:7]
        #     orlogo_year = orlogo_date[:4]
        #     orlogo_month = orlogo_date[5:7]
        #
        #     if (today_year + today_month) != (orlogo_year + orlogo_month):
        #         if '0' == today_month[0]:
        #             today_month = today_month[1]
        #         if '0' == orlogo_month[0]:
        #             orlogo_month = orlogo_month[1]
        #         if int(orlogo_year) == int(today_year):
        #             if int(today_year + today_month) - 1 == int(orlogo_year + orlogo_month):
        #                 fiba = Final_Balance.objects.filter(year=orlogo_year, month=orlogo_month, customer_id=customer.id).first()
        #                 if fiba is not None:
        #                     fiba.balance = Decimal(round(fiba.balance - total, 2))
        #                     fiba.save()
        #             else:
        #                 messages.error(request, 'Та зөвхөн өмнөх сарын орлого л нөхөж оруулах боломжтой. Тэрнээс өмнөх сарын орлого оруулах боломжгүй!')
        #                 return redirect('/home/borluulalt/orlogo_add')
        #         elif int(orlogo_month) == 12:
        #             fiba = Final_Balance.objects.filter(year=orlogo_year, month=orlogo_month, customer_id=customer.id).first()
        #             if fiba is not None:
        #                 fiba.balance = Decimal(round(fiba.balance - total, 2))
        #                 fiba.save()
        #         else:
        #             messages.error(request, 'Та зөвхөн өмнөх сарын орлого л нөхөж оруулах боломжтой. Тэрнээс өмнөх сарын орлого оруулах боломжгүй!')
        #             return redirect('/home/borluulalt/orlogo_add')
        #
        #     pay_date = datetime.strptime(orlogo_date + ' 00:00', '%Y-%m-%d %H:%M')
        #
        #     his = PaymentHistory.objects.create(pay_date=pay_date, pay_total=total, customer=customer)
        #
        #     # avlaga_list = Avlaga.objects.filter(customer=customer, pay_type='0').order_by('created_date')
        #     # if avlaga_list is not None:
        #     #     for avlaga in avlaga_list:
        #     #         ald_hemjee = Decimal(0)
        #     #         # days = (datetime.now() - avlaga.tulbur_date).days
        #     #         # if days > 1:
        #     #         #     ald_hemjee = Decimal(avlaga.pay_uld / Decimal(avlaga.ald_huvi) / Decimal(days))
        #     #
        #     #         if total >= (avlaga.pay_uld + ald_hemjee):
        #     #             total = total - Decimal(avlaga.pay_uld + ald_hemjee)
        #     #             avlaga.ald_hemjee = ald_hemjee
        #     #             avlaga.pay_type = '1'  # tulsun tuluv
        #     #             avlaga.paid_date = pay_date
        #     #             avlaga.pay_uld = 0.00
        #     #         else:
        #     #             if total > 0:
        #     #                 avlaga.ald_hemjee = ald_hemjee
        #     #                 total = total - ald_hemjee
        #     #                 avlaga.pay_uld = avlaga.pay_uld - total
        #     #                 total = 0.00
        #     #         avlaga.payment_history = his
        #     #         avlaga.save()
        #     # if total > 0:
        #     #     payment = Payment.objects.filter(customer=customer).first()
        #     #     if payment is not None:
        #     #         payment.uldegdel = payment.uldegdel + total
        #     #         payment.save()
        #     #     else:
        #     #         payment = Payment.objects.create(customer=customer, uldegdel=Decimal(total))
        #     #         payment.save()
        #     #     his.payment = payment
        #
        #     bank = Bank.objects.filter(code=select_bank).first()
        #
        #     his.bank = bank
        #     his.created_user_id = request.user.id
        #     his.save()
        #
        #     orlogo = str('{:.{prec}f}'.format(orlogo, prec=2))
        #     ehnii_orlogo = str('{:.{prec}f}'.format(pay_total, prec=2))
        #     ehnii = str('{:.{prec}f}'.format(ehnii, prec=2))
        #     bichilt = str('{:.{prec}f}'.format(bichilt, prec=2))
        #     balance = str('{:.{prec}f}'.format(balance, prec=2))
        #
        #     if(select_bank == '6' or select_bank == '5'):
        #
        #         cur_month_avlaga = Avlaga.objects.filter(customer_id=customer.id, is_active='1').order_by('-created_date').first()
        #         #cur_month_avlaga = Avlaga.objects.filter(customer=customer, is_active='1', month=today_month, year=today_year).first()
        #         if cur_month_avlaga is not None:
        #             year = str(cur_month_avlaga.year)
        #             month = str(cur_month_avlaga.month)
        #             if len(month) == 1:
        #                 month = '0' + month
        #             start_date = year + '-' + month + '-01'
        #             if customer.customer_angilal == '1':
        #                 return redirect('/home/borluulalt/new_invoice_ahui/1/' + code + '/' + start_date + '/' + last_date + '/' + str(ehnii) + '/' + str(ehnii_orlogo) + '/' + str(orlogo) + '/' + str(bichilt) + '/')
        #             else:
        #                 return redirect('/home/borluulalt/new_invoice_aan/1/' + code + '/' + start_date + '/' + last_date + '/' + str(ehnii) + '/' + str(ehnii_orlogo) + '/' + str(orlogo) + '/' + str(bichilt) + '/')
        #
        #     else:
        #         return redirect('/home/borluulalt/orlogo_list')

        #return redirect('/home/borluulalt/orlogo_list')

class OrlogoDelete(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'data.delete_paymenthistory'
    login_url = '/home/index'

    def get(self, request, id, code, orlogo, *args, **kwargs):
        today = datetime.now()
        today_year = str(today)[:4]
        today_month = str(today)[5:7]
        is_success = False
        message = ''

        payment_histoty = PaymentHistory.objects.filter(id=id).first()
        if payment_histoty is not None:
            orlogo_date = str(payment_histoty.pay_date)[:10]
            orlogo_year = orlogo_date[:4]
            orlogo_month = orlogo_date[5:7]
            is_success2 = False

            if (today_year + today_month) != (orlogo_year + orlogo_month):
                if '0' == today_month[0]:
                    today_month = today_month[1]
                if '0' == orlogo_month[0]:
                    orlogo_month = orlogo_month[1]
                if int(today_year) == int(orlogo_year):
                    if int(today_year + today_month) - 1 == int(orlogo_year + orlogo_month):
                        customer = Customer.objects.filter(code=code).first()
                        if customer is not None:
                            fiba = Final_Balance.objects.filter(year=orlogo_year, month=orlogo_month, customer_id=customer.id).first()
                            if fiba is not None:
                                posapi = PosAPI.objects.filter(customer__code=code, pay_his_id=id).first()
                                if posapi is not None:
                                    if posapi.is_send == True:
                                        messages.error(request, "Татварлуу илгээгдсэн тул устгах боломжгүй!")
                                        return redirect('/home/borluulalt/orlogo_list')

                                if posapi is not None:
                                    result_rb = PosapiMTA().return_bill(posapi.billId, posapi.date)
                                    if result_rb['success']:
                                        posapi.is_active = '0'
                                        posapi.pay_his = None
                                        posapi.save()

                                        avlagas = Avlaga.objects.filter(customer__code=code, payment_history_id=id)
                                        if avlagas is not None:
                                            for avlaga in avlagas:
                                                avlaga.payment_history_id = None
                                                avlaga.save()

                                            fiba.balance = Decimal(round(fiba.balance + Decimal(orlogo), 2))
                                            fiba.save()

                                            payment_histoty.is_active = '0'
                                            payment_histoty.save()

                                            is_success = True
                                    else:
                                        is_success = False
                                        message = result_rb['message']
                    elif int(today_month) < int(orlogo_month) - 1:
                        messages.error(request, 'Та зөвхөн өмнөх сарын орлого л устгах боломжтой. Тэрнээс өмнөх сарын орлого устгах боломжгүй!')
                        return redirect('/home/borluulalt/orlogo_list')
                elif int(orlogo_month) == 12:
                    customer = Customer.objects.filter(code=code).first()
                    if customer is not None:
                        fiba = Final_Balance.objects.filter(year=orlogo_year, month=orlogo_month, customer_id=customer.id).first()
                        if fiba is not None:
                            posapi = PosAPI.objects.filter(customer__code=code, pay_his_id=id).first()
                            if posapi is not None:
                                if posapi.is_send == True:
                                    messages.error(request, "Татварлуу илгээгдсэн тул устгах боломжгүй!")
                                    return redirect('/home/borluulalt/orlogo_list')

                            if posapi is not None:
                                result_rb = PosapiMTA().return_bill(posapi.billId, posapi.date)
                                if result_rb['success']:
                                    posapi.is_active = '0'
                                    posapi.pay_his = None
                                    posapi.save()

                                    avlagas = Avlaga.objects.filter(customer__code=code, payment_history_id=id)
                                    if avlagas is not None:
                                        for avlaga in avlagas:
                                            avlaga.payment_history_id = None
                                            avlaga.save()

                                        fiba.balance = Decimal(round(fiba.balance + Decimal(orlogo), 2))
                                        fiba.save()

                                        payment_histoty.is_active = '0'
                                        payment_histoty.save()

                                        is_success = True
                                else:
                                    is_success = False
                                    message = result_rb['message']
                else:
                    messages.error(request, 'Та зөвхөн өмнөх сарын орлого л устгах боломжтой. Тэрнээс өмнөх сарын орлого устгах боломжгүй!')
                    return redirect('/home/borluulalt/orlogo_list')
            else:
                customer = Customer.objects.filter(code=code).first()
                if customer is not None:
                    if customer is not None:
                        if payment_histoty.bank_id == 6 or payment_histoty.bank_id == 5:
                            posapi = PosAPI.objects.filter(customer__code=code, pay_his_id=id).first()
                            if posapi is not None:
                                if posapi.is_send == True:
                                    messages.error(request, "Татварлуу илгээгдсэн тул устгах боломжгүй!")
                                    return redirect('/home/borluulalt/orlogo_list')

                            if posapi is not None:
                                result_rb = PosapiMTA().return_bill(posapi.billId, posapi.date)
                                if result_rb['success']:
                                    posapi.is_active = '0'
                                    posapi.pay_his = None
                                    posapi.save()
                                    is_success2 = True
                                else:
                                    is_success2 = False
                                    message = result_rb['message']
                        else:
                            is_success2 = True
                        avlagas = Avlaga.objects.filter(customer__code=code, payment_history_id=id)
                        if avlagas is not None:
                            for avlaga in avlagas:
                                avlaga.payment_history_id = None
                                avlaga.save()

                        payment_histoty.is_active = '0'

                        payment_histoty.save()


            if is_success2:
                messages.success(request, "Татварлуу илгээх гэж байсан билл хүчингүй боллоо.")
            else:
                messages.error(request, "Татварлуу илгээх гэж байсан билл хүчингүй болгоход алдаа гарлаа. %s" % message)

        return redirect('/home/borluulalt/orlogo_list')

    def post(self, request, *args, **kwargs):
        return None


class OrlogoEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_paymenthistory'
    template_name = 'homepage/borluulalt/orlogo_edit.html'
    menu = '3'
    sub = '4'

    def get(self, request, id, *args, **kwargs):
        payment_history = PaymentHistory.objects.filter(id=id).first()
        banks = Bank.objects.filter(is_active=1)
        address = Address.objects.filter(customer=payment_history.customer).first()

        context = {
            'payment_history': payment_history,
            'menu': self.menu,
            'sub': self.sub,
            'banks': banks,
            'address': '' if address is None else address.address_name
        }
        return render(request, self.template_name, context)

    def post(self, request, id, *args, **kwargs):
        orlogo_date = request.POST['orlogo_date']
        select_bank = request.POST['select_bank']

        pay_date = datetime.strptime(orlogo_date + ' 00:00', '%Y-%m-%d %H:%M')

        payment_history = PaymentHistory.objects.filter(id=id).first()
        payment_history.pay_date = pay_date
        payment_history.bank_id = int(select_bank)
        payment_history.save()

        messages.success(request, "Амжилттай хадгалагдлаа.")
        return redirect('/home/borluulalt/orlogo_list')


def orlogo_nehemjleh(request):
    user_code = request.GET['user_code']
    balance_type = 'balance'
    now = datetime.now()
    today = str(now)
    cur_year = year = today[:4]
    month = today[5:7]
    cur_month = today[5:7]
    day = today[8:10]
    now_month = today[5:7]

    if '0' == month[0]:
        month = month[1]
    if '0' == day[0]:
        day = day[1]
    if '1' == month:
        year = str(int(year) - 1)
        month = '12'
    elif '8' == month and year == '2017':
        balance_type = 'ehnii'
    else:
        month = str(int(month) - 1)
    try:
        user = Customer.objects.get(code=user_code, is_active='1')
        if balance_type == 'balance':
            ehnii_balance = Final_Balance.objects.filter(customer_id=user.id, year=year, month=month).first().balance
        else:
            ehnii_balance = Final_Balance.objects.filter(customer_id=user.id, year=year, month=month).first().ehnii
        address = Address.objects.filter(customer=user, is_active='1').first()

        payment_history = None

        bichilt = Avlaga.objects.filter(customer=user, is_active='1').order_by('-created_date').first()
        if bichilt is not None:
            if len(month) == 1:
                month += '0' + month
            pay_date = cur_year + '-' + now_month + '-01 00:00:00.000000'

            payment_history = list(PaymentHistory.objects.raw("""SELECT cust.id, IFNULL(SUM(pahi.pay_total), 0) AS pay_total FROM data_customer cust
                JOIN data_paymenthistory pahi ON cust.id = pahi.customer_id
                WHERE pahi.is_active = '1' AND pahi.customer_id = """ + str(user.id) + """ AND pahi.pay_date >= '""" + pay_date + """';"""))

            if bichilt.uilchilgeenii_tulbur is not None:
                uilchilgeenii_tulbur = bichilt.uilchilgeenii_tulbur
            else:
                uilchilgeenii_tulbur = Decimal(0)
            if bichilt.tv_huraamj is not None:
                tv_huraamj = bichilt.tv_huraamj
            else:
                uilchilgeenii_tulbur = Decimal(0)
            bichilt = str(bichilt.heregleenii_tulbur + uilchilgeenii_tulbur + bichilt.barimt_une + tv_huraamj)
        else:
            bichilt = 0.00
            payment = Payment.objects.filter(customer=user).first()
            ehnii = 0.00 if payment is None else -payment.uldegdel

        if '0' == cur_month[0]:
            cur_month = cur_month[1]
        cur_month_avlaga = Avlaga.objects.filter(customer=user, is_active='1', month=cur_month, year=cur_year).first()
        if cur_month_avlaga is None:
            ehnii = round(float(ehnii_balance) - float(bichilt), 2)
            # ehnii = round(ehnii - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)
            balance = round(float(ehnii_balance) - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)
        else:
            ehnii = float(ehnii_balance)
            balance = round(float(ehnii_balance) + float(bichilt), 2)
            balance = round(balance - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)

        data = {'last_name': '' if user.last_name is None else user.last_name,
                'first_name': user.first_name,
                'register': '' if user.register is None else user.register,
                'address': '' if address is None else address.address_name,
                'pay_total': '0' if len(payment_history) < 1 else payment_history[0].pay_total,
                'bichilt': bichilt,
                'ehnii': ehnii,
                'balance': balance
        }
        return HttpResponse(simplejson.dumps(data), content_type='application/json')
    except ObjectDoesNotExist:
        return HttpResponse("not_found")