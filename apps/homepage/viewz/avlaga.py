# coding=utf-8
from time import sleep
import simplejson
import xlwt
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect
from django.template.loader import render_to_string
from django.utils.dateformat import DateFormat
from django.views import View
from lxml.etree import strip_tags
from apps.homepage.viewz.services.posapi import PosapiMTA
from mcsi.utils import *


class AvlagaList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = 'homepage/borluulalt/avlaga.html'
    permission_required = 'data.view_avlaga'
    today = datetime.datetime.now()
    menu = "3"
    sub = "3"

    def get(self, request, type, *args, **kwargs):
        avlaga_list = Avlaga.objects.filter(Q(out_of_date=None) | Q(out_of_date='0'))
        cycle = Cycle.objects.filter(is_active='1')
        for avlaga in avlaga_list:
            if self.today > avlaga.tulbur_date:
                avlaga.out_of_date = '1'
                avlaga.save()

        data = {
            "menu": self.menu,
            "sub": self.sub,
            "cycle": cycle
        }
        return render(request, self.template_name, data)

    def post(self, request, type, *args, **kwargs):
        rq = request.POST
        start_date = rq.get('start_date', '') + ' 00:00:00.000000'
        end_date = rq.get('end_date', '') + ' 23:59:59.999999'
        customer_code = rq.get('customer_code', '')
        customer_name = rq.get('customer_name', '')
        address = rq.get('address', '')
        customer_angilal = rq.get('customer_angilal', '')
        balance_type = 'balance'
        cycle = rq.get('select_cycle','')
        cycles = Cycle.objects.filter(is_active='1')
        if 'avlaga_confirm' in rq:
            par0 = {"is_active": "1", "created_date__range": (start_date, end_date)}
            if customer_code != '':
                par0.update({"customer__code": customer_code})
            if customer_angilal != '':
                par0.update({"customer__customer_angilal": customer_angilal})

            selected_ids = request.GET.getlist('selected_ids[]')
            if len(selected_ids) > 0:
                messages.success(request, "Авлага амжилттай баталгаажлаа.")
            else:
                messages.warning(request, "Та хэрэглэгчээ сонгоно уу!")

            avlagas = Avlaga.objects.filter(**par0)
            if avlagas is not None:
                start_year = bef_year = start_date[:4]
                start_month = bef_month = start_date[5:7]
                if bef_month == '01' or bef_month == '1':
                    bef_year = str(int(bef_year) - 1)
                    bef_month = '12'
                else:
                    bef_month = str(int(bef_month) - 1)
                if '0' == bef_month[0]:
                    bef_month = bef_month[1]

                customer = Customer.objects.filter(code=customer_code).first()
                if customer is not None:
                    customer_id = customer.id
                    cursor = connection.cursor()
                    try:
                        cursor.callproc('make_final_balance', [bef_year, bef_month, start_year, start_month, end_date, customer_id])
                        results = cursor.fetchall()

                        for avlaga in avlagas:
                            avlaga.is_confirm = True
                            avlaga.save()
                    except:
                        messages.error(request, "Авлага баталгаажуулахад алдаа гарлаа.")
                    finally:
                        cursor.close()

                    for result in results:
                        print(str("result : " + str(result)))
                    messages.success(request, "Авлага амжилттай баталгаажлаа.")
                else:
                    messages.error(request, "Сонгосон хэрэглэгч олдсонгүй.")
            else:
                messages.error(request, "Авлага баталгаажуулахад алдаа гарлаа.")

        year = start_date[:4]
        month = start_date[5:7]
        day = start_date[8:10]

        if '0' == month[0]:
            month = month[1]
        if '1' == month:
            year = str(int(year) - 1)
            month = '12'
        elif '8' == month and year == '2017':
            balance_type = 'ehnii'
        else:
            month = str(int(month) - 1)

        if '0' == day[0]:
            day = day[1]

        if int(day) == 1:
            qry = """SELECT tocu.id, cust.code, cust.register, cust.phone, cust.last_name, cust.first_name, cust.customer_angilal, addr.toot, addr.building_number, addr.address_name, cust.email, a.is_confirm,
                IFNULL((SELECT fiba.""" + balance_type + """ FROM data_final_balance fiba WHERE fiba.year = '""" + year + """' AND fiba.month = '""" + month + """' AND tocu.customer_id = fiba.customer_id), 0) AS ehnii,
                IFNULL((SELECT SUM(avbi.heregleenii_tulbur + avbi.uilchilgeenii_tulbur + avbi.tv_huraamj + IFNULL(avbi.light, 0.00) + IFNULL(avbi.ten, 0.00) + avbi.barimt_une) FROM data_avlaga avbi WHERE avbi.created_date >= '""" + start_date + """'
                AND avbi.created_date <= '""" + end_date + """' AND avbi.is_active = '1' AND tocu.customer_id = avbi.customer_id), 0) AS bichilt,
                IFNULL((SELECT SUM(pahi.pay_total) FROM data_paymenthistory pahi WHERE pahi.is_active = '1' AND pahi.pay_date >= '""" + start_date + """' AND pahi.pay_date <= '""" + end_date + """'
                AND pahi.is_active = '1' AND tocu.customer_id = pahi.customer_id), 0) AS payment,
                (SELECT COUNT(tc.id) FROM data_tooluurcustomer tc WHERE tc.customer_id = cust.id) AS tool_count
                , count( distinct a.id ) avlaga_count
                , h.head_tool_cus_id
                , a.id avlaga_id
                FROM data_tooluurcustomer tocu 
                JOIN data_customer cust ON tocu.customer_id = cust.id
                left join data_avlaga a on cust.id = a.customer_id
                and a.created_date between '""" + str(start_date) + """' AND '""" + str(end_date) + """'
                LEFT JOIN data_address addr ON cust.id = addr.customer_id
                LEFT JOIN data_geree geree ON cust.code = geree.customer_code
                left join data_hasagdahtooluur h on tocu.id = h.head_tool_cus_id
                WHERE tocu.is_active = '1' AND tocu.customer_angilal = '1'"""
        else:
            if len(month) == 0:
                month = '0' + month
            sub_start_date = year + '-' + month + '-01'
            qry = """SELECT tocu.id, cust.code, cust.register, cust.phone, cust.last_name, cust.first_name, cust.customer_angilal, addr.toot, addr.building_number, addr.address_name, cust.email, a.is_confirm,
                (IFNULL((SELECT fiba.""" + balance_type + """ FROM data_final_balance fiba WHERE fiba.year = '""" + year + """' AND fiba.month = '""" + month + """' AND tocu.customer_id = fiba.customer_id), 0) - 
                IFNULL((SELECT SUM(pahi.pay_total) FROM data_paymenthistory pahi WHERE pahi.is_active = '1' AND pahi.pay_date >= '""" + sub_start_date + """' AND pahi.pay_date <= '""" + start_date + """"'
                AND pahi.is_active = '1' AND tocu.customer_id = pahi.customer_id), 0)) AS ehnii,
                IFNULL((SELECT SUM(avbi.heregleenii_tulbur + avbi.uilchilgeenii_tulbur + avbi.tv_huraamj + IFNULL(avbi.light, 0.00) + IFNULL(avbi.ten, 0.00) + avbi.barimt_une) FROM data_avlaga avbi WHERE avbi.created_date >= '""" + start_date + """"'
                AND avbi.created_date <= '""" + end_date + """' AND avbi.is_active = '1' AND tocu.customer_id = avbi.customer_id), 0) AS bichilt,
                IFNULL((SELECT SUM(pahi.pay_total) FROM data_paymenthistory pahi WHERE pahi.is_active = '1' AND pahi.is_active = '1' AND pahi.pay_date >= '""" + start_date + """"' AND pahi.pay_date <= '""" + end_date + """'
                AND pahi.is_active = '1' AND tocu.customer_id = pahi.customer_id), 0) AS payment,
                (SELECT COUNT(tc.id) FROM data_tooluurcustomer tc WHERE tc.customer_id = cust.id) AS tool_count
                , count( distinct a.id ) avlaga_count
                , h.head_tool_cus_id
                , a.id avlaga_id
                FROM data_tooluurcustomer tocu 
                JOIN data_customer cust ON tocu.customer_id = cust.id
                left join data_avlaga a on cust.id = a.customer_id
                and a.created_date between '""" + start_date + """ 00:00:00.000000' AND '""" + end_date + """'
                LEFT JOIN data_address addr ON cust.id = addr.customer_id
                LEFT JOIN data_geree geree ON cust.code = geree.customer_code
                left join data_hasagdahtooluur h on tocu.id = h.head_tool_cus_id
                WHERE tocu.is_active = '1' AND tocu.customer_angilal = '1'"""

        if customer_angilal != '':
            qry = qry + " AND cust.customer_angilal = '" + customer_angilal + "'"
        if customer_code != '':
            qry = qry + " AND cust.code LIKE '%%" + customer_code + "'"
        if customer_name != '':
            qry = qry + " AND (cust.first_name LIKE '%%" + customer_name + "%%' OR cust.last_name LIKE '%%" + customer_name + "%%')"
        if cycle != '':
            qry = qry + " AND geree.cycle_code = '" + cycle + "'"
        if address != '':
            qry = qry + " AND addr.address_name LIKE '%%" + address + "%%'"
        qry = qry + " GROUP BY tocu.customer_id ORDER BY cust.code;"

        res_list = list(TooluurCustomer.objects.raw(qry))

        if 'export_all_xls' in rq:
            return export_all(res_list, year, month)
        if 'export_av_xls' in rq:
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="avlaga.xls"'

            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Users')

            # Sheet header, first row
            row_num = 0

            font_style = xlwt.XFStyle()
            bold_style = xlwt.XFStyle()
            bold_style.font.bold = True

            columns = ['Хэрэглэгчийн код', 'Хэрэглэгчийн нэр', 'Утасны дугаар', 'Хаяг', 'Эхний үлдэгдэл', 'Бичилт', 'Орлого', 'Эцсийн үлдэгдэл']

            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], bold_style)

            total_ehnii = total_bichilt = total_payment = total_total = 0

            for row in res_list:
                row_num += 1
                col_num = 0
                full_name = row.last_name + ' ' + row.first_name

                ehnii = 0
                bichilt = 0
                payment = 0
                total = 0

                if row.ehnii is not None:
                    ehnii = float(row.ehnii)
                    total += ehnii
                if row.bichilt is not None:
                    bichilt = float(row.bichilt)
                    total += bichilt
                if row.payment is not None:
                    payment = float(row.payment)
                total = round(float(row.ehnii) + float(row.bichilt), 2)
                total = round(total - float(row.payment), 2)

                ws.write(row_num, col_num, row.code, font_style)
                col_num += 1
                ws.write(row_num, col_num, full_name, font_style)
                col_num += 1
                ws.write(row_num, col_num, row.phone, font_style)
                col_num += 1
                ws.write(row_num, col_num, row.address_name, font_style)
                col_num += 1
                ws.write(row_num, col_num, ehnii, font_style)
                total_ehnii = round(total_ehnii + ehnii, 2)
                col_num += 1
                ws.write(row_num, col_num, bichilt, font_style)
                total_bichilt = round(total_bichilt + bichilt, 2)
                col_num += 1
                ws.write(row_num, col_num, payment, font_style)
                total_payment = round(total_payment + payment, 2)
                col_num += 1
                ws.write(row_num, col_num, total, font_style)
                total_total = round(total_total + total, 2)

            row_num += 1
            col_num = 4
            ws.write(row_num, col_num, total_ehnii, bold_style)
            col_num += 1
            ws.write(row_num, col_num, total_bichilt, bold_style)
            col_num += 1
            ws.write(row_num, col_num, total_payment, bold_style)
            col_num += 1
            ws.write(row_num, col_num, total_total, bold_style)

            wb.save(response)
            return response

        ehnii_total = 0
        bichilt_total = 0
        payment_total = 0
        balance_total = 0

        for item in res_list:
            if item.ehnii is not None:
                ehnii_total += float(item.ehnii)
            if item.bichilt is not None:
                bichilt_total += float(item.bichilt)
            if item.payment is not None:
                payment_total += float(item.payment)
            balance_total += float(item.ehnii) + float(item.bichilt) - float(item.payment)

        # if cycle != '':
        #     cycle = int(cycle)
        search = {'start_date': start_date[:10], 'end_date': end_date[:10], 'customer_code': customer_code,
            'customer_name': customer_name, 'address': address, 'customer_angilal': customer_angilal, 'cycle':cycle }

        if type == '1':
            request.session['avlaga_list'] = res_list
            return HttpResponseRedirect('/home/call_customerdetail/' + customer_code + '/')

        data = {
            "data": res_list,
            "search": search,
            "ehnii_total": ehnii_total,
            "bichilt_total": bichilt_total,
            "payment_total": payment_total,
            "balance_total": balance_total,
            "menu": self.menu,
            "sub": self.sub,
            "cycle": cycles
        }
        return render(request, self.template_name, data)


class AvlagaDelete(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_avlaga'

    def get(self, request, id, code, *args, **kwargs):
        try:
            bichilts = Bichilt.objects.filter(avlaga_id=id)
            if bichilts is not None:
                for bichilt in bichilts:
                    bichilt.type = '0'
                    bichilt.avlaga_id = None
                    bichilt.save()

                avlaga = Avlaga.objects.filter(id=id).first()
                if avlaga is not None:
                    avlaga.delete()
                    messages.success(request, str(code) + " кодтой хэрэглэгчийн авлага амжилттай устлаа! ")
                else:
                    messages.error(request, str(code) + " кодтой хэрэглэгчийн авлага устгах үед алдаа гарлаа! ")
        except ObjectDoesNotExist:
            messages.error(request, str(code) + " кодтой хэрэглэгчийн авлага устгах үед алдаа гарлаа! ")
        return redirect('/home/borluulalt/avlaga/0/')

    def post(self, request, id, code, *args, **kwargs):
        return redirect('/home/borluulalt/avlaga/0/')


def salgalt_one(request):
    cus_id = request.GET['cus_id']
    tas = Salgalt.objects.filter(customer_id=cus_id)

    if len(tas) == 1:
        tas[0].status = 0
        tas[0].save()
    else:
        if len(tas) > 1:
            for t in tas:
                t.delete()

        customer = Customer.objects.get(id=cus_id)
        taslalt = Salgalt.objects.create(customer=customer, status=0)
        taslalt.save()

    return HttpResponse("Success")


def salgalt_all(request):
    cus_ids = request.GET.getlist('ids[]')

    for cus_id in cus_ids:

        tas = Salgalt.objects.filter(customer_id=cus_id)

        if len(tas) == 1:
            tas[0].status = 0
            tas[0].save()
        else:
            if len(tas) > 1:
                for t in tas:
                    t.delete()

            customer = Customer.objects.get(id=cus_id)
            taslalt = Salgalt.objects.create(customer=customer, status=0)
            taslalt.save()

    return HttpResponse("Success")


def av_nehemjleh(request):
    cus_id = request.GET['cus_id']
    start_date = request.GET['start_date']
    end_date = request.GET['end_date']
    result_set = []

    cus = Customer.objects.get(id=cus_id)
    tc = TooluurCustomer.objects.filter(customer=cus)
    bich = Bichilt.objects.filter(tooluur__in=tc, bichilt_date__range=(start_date, end_date))

    geree = Geree.objects.filter(customer_code=cus.code).first()
    cycle = Cycle.objects.filter(code=geree.cycle_code).first()
    dedstsants = DedStants.objects.filter(code=geree.dedstants_code).first()
    bank = Bank.objects.filter(code=geree.bank_code).first()

    for b in bich:
        try:
            a = Avlaga.objects.get(bichilt=b.id)
            uilchilgee = a.uilchilgeenii_tulbur
            uil_nuat = float(a.uilchilgeenii_tulbur) - float(a.uilchilgeenii_tulbur) / float(1.1)
        except:
            uilchilgee = 0
            uil_nuat = 0

        df = DateFormat(b.bichilt_date)

        result_set.append({'id': b.id, 'bichilt_date': df.format('Y-m-d'), 'tooluur': b.tooluur.tooluur.number,
                           'total_diff': b.total_diff, 'hereglee_price': b.hereglee_price,
                           'sergeegdeh_price': b.sergeegdeh_price, 'suuri_price': b.suuri_price,
                           'chadal_price': b.chadal_price,
                           'nuat': float(b.total_price) - float(b.total_price) / float(1.1),
                           'total_price': b.total_price, 'uilchilgee': uilchilgee, 'uil_nuat': uil_nuat})

    result = {
        'cycle': cycle.name, 'dedstants': dedstsants.name, 'start_date': start_date, 'end_date': end_date,
        'kod': cus.code, 'bank': bank.name, 'name': cus.first_name, 'dans': bank.dans,
        'address': cus.address.address_name, 'printed_date': datetime.datetime.now().strftime("%Y-%m-%d"),
        'result_set': result_set
    }

    return HttpResponse(simplejson.dumps(result), content_type='application/json')


def avlaga_confirm(request):
    selected_ids = request.GET.getlist('selected_ids[]')
    if len(selected_ids) > 0:
        for cus_id in selected_ids:
            print(str(cus_id))
            # TODO HIIH YUM BAIGAA SHUU!!!
        return HttpResponse("Success")
    else:
        return HttpResponse("Selected")


def disconnect(request):
    selected_ids = request.GET.getlist('selected_ids[]')
    if len(selected_ids) > 0:
        for cus_id in selected_ids:
            taslalts = Salgalt.objects.filter(customer_id=cus_id, is_active='1')
            for taslalt in taslalts:
                taslalt.delete()

            taslalt = Salgalt.objects.create(customer_id=cus_id, status='0')
            taslalt.created_user_id = request.user.id
            taslalt.is_active = '1'
            taslalt.save()
        return HttpResponse("Success")
    else:
        return HttpResponse("Selected")


def send_invoice(request):
    selected_ids = request.GET.getlist('selected_ids[]')
    failed_aan = []
    successed_aan = []
    today = datetime.datetime.now()

    posapiMTA = PosapiMTA()
    if len(selected_ids) > 0:
        tocus = TooluurCustomer.objects.filter(id__in=selected_ids)
        if tocus is not None:
            for tocu in tocus:
                avla = Avlaga.objects.filter(year=today.year, month=today.month, customer=tocu.customer).first()
                if posapiMTA.pos_init():
                    print(str(posapiMTA.pos_init()))
                    if len(tocu.customer.register) >= 7 and avla is not None:
                        bichilt = avla.heregleenii_tulbur + avla.uilchilgeenii_tulbur + avla.barimt_une
                        print("customer : " + str(tocu.customer_code) + ", register : " + str(str(tocu.customer.register)) + ", bichilt : " + str(bichilt))

                        if int(bichilt) > 330:
                            return_json = PosapiMTA().pos_put_aan(str(tocu.customer.register), bichilt)
                            print(str(return_json))

                            if return_json['success']:
                                pay_his = PaymentHistory.objects.latest('id')
                                posapi = PosAPI.objects.create(pay_his_id=pay_his.id, success=1 if return_json['success'] else 0)
                                posapi.created_user_id = '1'
                                posapi.is_active = '1'
                                posapi.registerNo = return_json['registerNo'] if return_json['registerNo'] else '0'
                                posapi.billType = return_json['billType'] if return_json['billType'] else '0'
                                posapi.cityTax = return_json['cityTax'] if return_json['cityTax'] else '0'
                                posapi.vat = return_json['vat'] if return_json['vat'] else Decimal(0.00)
                                posapi.invoiceId = return_json['invoiceId'] if return_json['invoiceId'] else '0'
                                posapi.billId = return_json['billId'] if return_json['billId'] else '0'
                                posapi.returnBillId = return_json['returnBillId'] if return_json['returnBillId'] else '0'
                                posapi.posNo = return_json['posNo'] if return_json['posNo'] else '0'
                                posapi.date = return_json['date'] if return_json['date'] else datetime.datetime.now()
                                posapi.cashAmount = return_json['cashAmount'] if return_json['cashAmount'] else Decimal(0.00)
                                posapi.merchantId = return_json['merchantId'] if return_json['merchantId'] else '0'
                                posapi.districtCode = return_json['districtCode'] if return_json['districtCode'] else '0'
                                posapi.branchNo = return_json['branchNo'] if return_json['branchNo'] else '0'
                                posapi.nonCashAmount = return_json['nonCashAmount'] if return_json['nonCashAmount'] else Decimal(0.00)
                                posapi.taxType = return_json['taxType'] if return_json['taxType'] else '0'
                                posapi.macAddress = return_json['macAddress'] if return_json['macAddress'] else '0'
                                posapi.amount = return_json['amount'] if return_json['amount'] else Decimal(0.00)
                                posapi.billIdSuffix = return_json['billIdSuffix'] if return_json['billIdSuffix'] else '0'
                                posapi.customerNo = return_json['customerNo'] if return_json['customerNo'] else '0'
                                posapi.reportMonth = return_json['reportMonth'] if return_json['reportMonth'] else '0000-00'
                                posapi.save()

                                # messages.success(request, "Амжилттай! Код : " + str(tocu.customer_code) + ", регистр : " + str(tocu.customer.register))
                                successed_aan.append(str(tocu.customer_code))
                            else:
                                # messages.error(request, "Алдаа гарлаа! Код : " + str(tocu.customer_code) + ", регистр : " + str(tocu.customer.register))
                                failed_aan.append(str(tocu.customer_code))
                sleep(0.5)
    else:
        return HttpResponse("Selected")

    return HttpResponse("Success")


def send_email(request):
    results = AvlagaList.xlslist

    for result in results:
        if '@' in str(result.email) and result.email is not None:
            try:
                template_name = ""
                if str(result.customer_angilal) == '0':
                    template_name = "user/email_aan.html"
                elif str(result.customer_angilal) == '1':
                    template_name = "user/email_ahui.html"

                html_context = render_to_string(template_name, {})
                text_context = strip_tags(html_context)
                email = EmailMultiAlternatives('BMEDIA: Барааны захиалга', text_context, from_email='info@odi.mn',
                                               to=list)
            except Exception as e:
                print("%s" % e)

    # try:
    #     html_context = render_to_string('user/email.html', {"email_products": email_products, "user": request.user, "customer": customer, "total_price": total_price})
    #     text_context = strip_tags(html_context)
    #     email = EmailMultiAlternatives('BMEDIA: Барааны захиалга', text_context, from_email='info@odi.mn', to=list)
    #     email.attach_alternative(html_context, 'text/html')
    #     email.send()
    #     messages.success(request, 'Имэйл амжилттай илгээгдлээ!')
    # except Exception as e:
    #     messages.error(request, 'Имэйл илгээхэд алдаа гарлаа!')
    #     logging.error('%s (%s)' % (type(e), e))

    data = {
        "menu": "3",
        "sub": "3",
        # "result_json": data_returns['data_results'] if data_returns['data_results'] is not None else '',
        # "no_registers": data_returns['no_registers'] if data_returns['no_registers'] is not None else ''
    }

    return render(request, "homepage/borluulalt/avlaga.html", data)

def export_all(res_list, year, month):
    month = int(month)  + 1
    month = str(month)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="avlaga.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    bold_style = xlwt.XFStyle()
    bold_style.font.bold = True

    columns = ['Төлбөрийн код', 'Сар', 'Бүгд', 'Нэхэмжлэхийн дугаар', 'Нэр', 'Байр', 'Тоот', 'Өдрийн эхний заалт', 'Өдрийн сүүлийн заалт',
               'Өдрийн хэрэглээ', 'Өдрийн тариф', 'Шөнийн эхний заалт', 'Шөнийн эцсийн заалт', 'Шөнийн хэрэглээ', 'Шөнийн тариф', 'Техник үйлчилгээ',
               'Суурь хураамж', 'ТВ-ийн хураамж', 'Дэвтрийн үнэ', 'НӨАТ', 'Өмнөх үлдэгдэл', 'Бичилт']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], bold_style)

    total_ehnii = total_bichilt = total_payment = total_total = 0

    for row in res_list:
        tooluur_data = Bichilt.objects.filter(tooluur_id = row.id, year = year, month = month).first()
        avlaga = Avlaga.objects.filter(customer__code = row.code, year = year, month = month).first()
        day_balance = 0
        night_balance = 0
        day_diff = 0
        night_diff = 0
        day_prev = 0
        night_prev = 0
        tv_huraamj = 0
        uilchilgee = 0
        if(avlaga is not None):
            tv_huraamj = avlaga.tv_huraamj
            uilchilgee = avlaga.uilchilgeenii_tulbur
        if(tooluur_data is not None):
            day_balance = tooluur_data.day_balance
            night_balance = tooluur_data.night_balance
            day_diff = tooluur_data.day_diff
            night_diff = tooluur_data.night_diff
            day_prev = float(tooluur_data.day_balance) - float(tooluur_data.day_diff)
            night_prev = float(tooluur_data.night_balance) - float(tooluur_data.night_diff)
        row_num += 1
        col_num = 0
        full_name = row.last_name + ' ' + row.first_name
        ehnii = 0
        bichilt = 0
        payment = 0
        total = 0
        if row.ehnii is not None:
            ehnii = float(row.ehnii)
            total += ehnii
        if row.bichilt is not None:
            bichilt = float(row.bichilt)
            total += bichilt
        if row.payment is not None:
            payment = float(row.payment)
        total = round(float(row.ehnii) + float(row.bichilt), 2)
        total = round(total - float(row.payment), 2)
        ws.write(row_num, col_num, row.code, font_style)
        col_num += 1
        ws.write(row_num, col_num, str(year) + str(month), font_style)
        col_num += 1
        ws.write(row_num, col_num, total, font_style)
        col_num += 1
        ws.write(row_num, col_num, str(year) + str(month) + str(row.code), font_style)
        col_num += 1
        ws.write(row_num, col_num, str(row.last_name) + " " + str(row.first_name), font_style)
        col_num += 1
        ws.write(row_num, col_num, str(row.building_number), font_style)
        col_num += 1
        ws.write(row_num, col_num, str(row.toot), font_style)
        col_num += 1
        ws.write(row_num, col_num, str(day_prev), font_style)
        col_num += 1
        ws.write(row_num, col_num, str(day_balance), font_style)
        col_num += 1
        ws.write(row_num, col_num, str(day_diff), font_style)
        col_num += 1
        ws.write(row_num, col_num, 116.18, font_style)
        col_num += 1
        ws.write(row_num, col_num, str(night_prev), font_style)
        col_num += 1
        ws.write(row_num, col_num, str(night_balance), font_style)
        col_num += 1
        ws.write(row_num, col_num, str(night_diff), font_style)
        col_num += 1
        ws.write(row_num, col_num, 88.98, font_style)
        col_num += 1
        ws.write(row_num, col_num, uilchilgee, font_style)
        col_num += 1
        ws.write(row_num, col_num, 2000, font_style)
        col_num += 1
        ws.write(row_num, col_num, tv_huraamj, font_style)
        col_num += 1
        ws.write(row_num, col_num, '', font_style)
        col_num += 1
        nuat = float(row.bichilt) * 0.1
        ws.write(row_num, col_num, nuat, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.ehnii, font_style)
        col_num += 1
        ws.write(row_num, col_num, row.bichilt, font_style)
        col_num += 1

    # row_num += 1
    # col_num = 4
    # ws.write(row_num, col_num, total_ehnii, bold_style)
    # col_num += 1
    # ws.write(row_num, col_num, total_bichilt, bold_style)
    # col_num += 1
    # ws.write(row_num, col_num, total_payment, bold_style)
    # col_num += 1
    # ws.write(row_num, col_num, total_total, bold_style)

    wb.save(response)
    return response