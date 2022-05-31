# coding=utf-8
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist

__author__ = 'L'
from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import simplejson
import datetime
from calendar import monthrange
from apps.data.helper import *
from mcsi.utils import getPayDate
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
import xlwt


class CallList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_call'
    template_name = "homepage/call/call_center.html"
    menu = "6"

    starter_q = """SELECT ca.id, ifnull(ca.customer_code, '') as customer_code, ca.call_created_date, ca.completed_date, ca.call_phone, cu.phone, cu.code, 
		ifnull(cu.first_name, '') as first_name, ifnull(cu.last_name, '') as last_name, ca.status, ca.note,
        ca.created_date, ca.call_type_id, au.first_name AS as_first_name, au.last_name AS as_last_name, au.id AS user_id, ad.toot, ad.building_number, ad.address_name
        FROM data_call AS ca LEFT JOIN data_customer AS cu ON ca.customer_code=cu.code INNER JOIN data_userprofile AS up ON ca.assigning_user=up.id
        INNER JOIN auth_user AS au ON up.user_id = au.id LEFT JOIN data_address AS ad ON cu.id=ad.customer_id WHERE ca.is_active='1'"""

    call_list = None

    def get(self, request, *args, **kwargs):
        today = datetime.datetime.now()
        # minus1_month = today + relativedelta(months=-1)
        month_last_day = str(monthrange(int(today.year), int(today.month))).split(',')
        month_last_day = str(month_last_day[1].replace(' ', '').replace(')', ''))

        start_date = today.strftime("%Y-%m-01")
        end_date = today.strftime("%Y-%m-" + month_last_day)

        q = self.starter_q + " AND ca.call_created_date BETWEEN '%s' AND '%s' ORDER BY ca.call_created_date DESC" % (
        start_date, end_date)
        calls = list(Call.objects.raw(q))
        CallList.call_list = calls
        call_types = CallType.objects.filter(is_active="1")

        users = UserProfile.objects.filter(is_active="1")
        aimags = Aimag.objects.filter(is_active="1")

        data = {
            "datas": calls,
            "call_types": call_types,
            "users": users,
            "aimags": aimags,
            "now": today,
            "search_q": {
                "start_created_date": start_date,
                "end_created_date": end_date,
            },
            "menu": self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        if "check_by_user_code" in rq:
            return self.post_check_user(request, "check_by_user_code")
        if "check_by_address" in rq:
            return self.post_check_user(request, "check_by_address")
        if "unregister_code" in rq:
            return self.post_check_user(request, "unregister_code")
        start_created_date = rq.get('start_date', '')
        end_created_date = rq.get('end_date', '')
        customer_code = rq.get('user_code', '')
        customer_name = rq.get('customer_name', '')
        call_phone = rq.get('call_phone', '')
        address = rq.get('address', '')
        select_call_type = rq.get('select_call_type', '')
        assigning_user = rq.get('assigning_user', '')
        status_type = rq.get('select_status_type', '')
        note = rq.get('note', '')
        start_completed_date = rq.get('start_completed_date', '')
        end_completed_date = rq.get('end_completed_date', '')
        q = self.starter_q
        if start_created_date != '' and end_created_date != '':
            start_created_date += ' 00:00:00.00000'
            end_created_date += ' 23:59:59.999999'
            q += " AND ca.created_date BETWEEN '" + start_created_date + "' AND '" + end_created_date + "'"
        else:
            if start_created_date != '':
                start_created_date += ' 00:00:00.00000'
                q += " AND ca.created_date >= '" + start_created_date + "'"
            if end_created_date != '':
                end_created_date += ' 23:59:59.999999'
                q += " AND ca.created_date <= '" + end_created_date + "'"
        if customer_code != '':
            q += " AND ca.customer_code = '" + customer_code + "'"
        if customer_name != '':
            q += " AND cu.first_name LIKE '%%" + customer_name + "%%' OR cu.last_name LIKE '%%" + customer_name + "%%'"
        if address != '':
            q += " AND ad.address_name LIKE '%%" + address + "%%'"
        if status_type != '':
            q += " AND ca.status = '" + status_type + "'"
        if call_phone != '':
            q += " AND ca.call_phone LIKE '%%" + call_phone + "%%'"
        if note != '':
            q += " AND ca.note LIKE '%%" + note + "%%'"
        if assigning_user != '':
            q += " AND ca.assigning_user = " + assigning_user + ""
        if select_call_type != '':
            q += " AND ca.call_type_id = " + select_call_type + ""
        if start_completed_date != '' and end_completed_date != '':
            start_completed_date += ' 00:00:00.00000'
            end_completed_date += ' 23:59:59.999999'
            q += " AND ca.completed_date BETWEEN '" + start_completed_date + "' AND '" + end_completed_date + "'"
        else:
            if start_completed_date != '':
                start_completed_date += ' 00:00:00.00000'
                q += " AND ca.completed_date >= '" + start_completed_date + "'"
            if end_completed_date != '':
                end_completed_date += ' 23:59:59.999999'
                q += " AND ca.completed_date <= '" + end_completed_date + "'"

        q += ' ORDER BY ca.call_created_date DESC'
        calls = list(Call.objects.raw(q))

        if 'export_xls' in rq:
            response = HttpResponse(content_type='application/ms-excel')
            now = datetime.datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            filename = "call_list-" + current_date + ".xls"
            response['Content-Disposition'] = 'attachment; filename="%s"' % filename

            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Bichilt')

            # Sheet header, first row
            row_num = 0

            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            columns = ['Хэрэглэгчийн код', 'Хэрэглэгчийн нэр', 'Хаяг', 'Төрөл', 'Төлөв', 'Шийдвэрлэсэн огноо',
                       'Бүртгэсэн огноо',
                       'Тайлбар', ]
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)

            # Sheet body, remaining rows
            font_style = xlwt.XFStyle()

            for row in calls:
                row_num += 1
                col_num = 0
                customer_code = row.customer_code
                full_name = row.last_name + ' ' + row.first_name
                address = row.address_name
                if address == None:
                    address = " - "
                sub_type = row.call_type.name
                if sub_type == None:
                    sub_type = " - "
                if row.status == "0":
                    status = "Шийдвэрлээгүй"
                elif row.status == "1":
                    status = "Шийдвэрлэсэн"
                else:
                    status = " - "
                completed_date = row.completed_date
                if completed_date == None:
                    completed_date = " - "
                created_date = row.created_date
                if created_date == None:
                    created_date = " - "
                note = row.note
                if note == None and note == '':
                    note = ' - '
                ws.write(row_num, col_num, customer_code, font_style)
                col_num += 1
                ws.write(row_num, col_num, full_name, font_style)
                col_num += 1
                ws.write(row_num, col_num, address, font_style)
                col_num += 1
                ws.write(row_num, col_num, sub_type, font_style)
                col_num += 1
                ws.write(row_num, col_num, status, font_style)
                col_num += 1
                ws.write(row_num, col_num, str(completed_date), font_style)
                col_num += 1
                ws.write(row_num, col_num, str(created_date), font_style)
                col_num += 1
                ws.write(row_num, col_num, note, font_style)
            ws.col(0).width = 5000
            ws.col(1).width = 5000
            ws.col(2).width = 9000
            ws.col(3).width = 3000
            ws.col(4).width = 4000
            ws.col(5).width = 6000
            ws.col(6).width = 6900
            ws.col(7).width = 4000
            wb.save(response)
            return response

        call_types = CallType.objects.filter(is_active="1")
        users = UserProfile.objects.filter(is_active="1")

        data = {
            "datas": calls,
            "call_types": call_types,
            "users": users,
            "now": datetime.datetime.now(),
            "search_q": {
                "start_created_date": start_created_date[:10],
                "end_created_date": end_created_date[:10],
                "customer_code": customer_code,
                "customer_name": customer_name,
                "address": address,
                "select_call_type": int(select_call_type) if select_call_type != '' else 0,
                "status_type": status_type,
                "note": note,
                "assigning_user": int(assigning_user) if assigning_user != '' else 0,
                "start_completed_date": start_completed_date[:10],
                "end_completed_date": end_completed_date[:10],
            },
            "menu": self.menu,
        }
        return render(request, self.template_name, data)

    def post_check_user(self, request, type):
        user_code = customer_id = ''
        if type == 'unregister_code':
            call_phone = request.POST.get('call_phone', '')
            created_date = request.POST.get('created_date', '')
            select_user = request.POST.get('select_user', '')
            select_call_type = request.POST.get('select_call_type', '')
            completed_date = request.POST.get('completed_date', '')
            note = request.POST.get('note', '')

            if call_phone != '':
                if select_user != '':
                    if select_call_type != '':
                        if note != '':
                            call = Call.objects.create(call_type_id = int(select_call_type))
                            call.created_user_id = request.user.id
                            call.call_phone = call_phone
                            call.call_created_date = created_date


                            call.assigning_user = select_user
                            call.note = note
                            if completed_date != '':
                                call.status = 1
                                call.completed_date = completed_date
                            else:
                                call.status = 0
                            call.save()
                            messages.success(request, "Амжилттай хадгалагдлаа.")
                        else:
                            messages.warning(request, 'Тайлбараа оруулна уу!')
                    else:
                        messages.warning(request, 'Дуудлагын төрлөө сонгоно уу!')
                else:
                    messages.warning(request, 'Хариуцах ажилтанаа сонгоно уу!')
            else:
                messages.warning(request, 'Утасны дугаараа оруулна уу!')
            return redirect('/home/call_list')

        if type == 'check_by_user_code':
            user_code = request.POST['user_code']
        elif type == 'check_by_address':
            try:
                customer_id = request.POST['toot']
            except MultiValueDictKeyError:
                customer_id = 0
            if customer_id=='':
                customer_id = 0
            customer = Customer.objects.filter(id=customer_id).first()
            if customer is not None:
                user_code = customer.code
        try:
            if type == 'check_by_user_code':
                Customer.objects.get(code=user_code)
            elif type == 'check_by_address':
                Customer.objects.get(id=customer_id)
        except ObjectDoesNotExist:
            now = datetime.datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            if now.day > 1:
                now = now.replace(day=1)
            start_date = now.strftime("%Y-%m-%d")
            q = self.starter_q + " AND ca.call_created_date BETWEEN '%s' AND '%s' ORDER BY ca.call_created_date DESC" % (
                start_date, current_date)
            calls = list(Call.objects.raw(q))
            CallList.call_list = calls
            data = {
                "datas": calls,
                "menu": self.menu,
                "user": {
                    "type": 400,
                    "description": "Not existed user."
                },
                "search_q": {
                    "start_created_date": start_date,
                    "end_created_date": current_date,
                },
            }
            messages.warning(request,
                             'Энэ хэрэглэгчийн кодоор бүртгэлтэй хэрэглэгч олдсонгүй. Та хэрэглэгчийн кодоо шалгана уу.')
            return render(request, self.template_name, data)
        url = "/home/call_customerdetail/" + user_code
        return redirect(url)


class CustomerDetail(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_call'
    template_name = "homepage/call/user_detail2.html"
    menu = "6"

    query_bichilt = "select * from data_bichilt as b left join data_tooluurcustomer as tc on tc.id=b.tooluur_id left join data_customer as c on c.id=tc.customer_id "
    query_tooluur = "select * from data_tooluur as t left join data_tooluurcustomer as tc on tc.tooluur_id=t.id left join data_customer as c on c.id=tc.customer_id "

    def get(self, request, id, *args, **kwargs):
        user_code = id
        customer = Customer.objects.get(code=id)
        geree = Geree.objects.get(customer_code=id)
        cycle = Cycle.objects.filter(code=geree.cycle_code).first()
        address_name = Address.objects.filter(customer=customer).first()
        if address_name is not None:
            address_name = address_name.address_name
        bank = Bank.objects.filter(code=geree.bank_code).first()

        try:
            # TODO: Gereenii dedstants_code-s avahguigeer TooluurCustomer-s dedstants-g avah ystoi shuu. /TooluurCustomer deer chini ded stantsiin holbolt chini dutuu baina./
            ded = DedStants.objects.get(code=geree.dedstants_code)
        except DedStants.DoesNotExist:
            ded = None

        tooluur_q = self.query_tooluur + " where c.code = '" + user_code + "' "
        bichilt_q = self.query_bichilt + " where c.code = '" + user_code + "' " + " order by b.created_date desc limit 1 "
        call_list = Call.objects.filter(is_active="1", customer_code=user_code).order_by('-created_date')[:5]

        bichilt = Bichilt.objects.raw(bichilt_q)
        tooluur = Tooluur.objects.raw(tooluur_q)
        if len(list(bichilt)) > 0:
            zaalt_date = bichilt[0].bichilt_date
            day_bal = bichilt[0].day_balance
            if day_bal == None:
                day_bal = '0.00'
            night_bal = bichilt[0].night_balance
            if night_bal == None:
                night_bal = '0.00'
            rush_bal = bichilt[0].rush_balance
            if rush_bal == None:
                rush_bal = '0.00'
        else:
            zaalt_date = '-'
            day_bal = '0.00'
            night_bal = '0.00'
            rush_bal = '0.00'

        balance_type = 'balance'
        now = datetime.datetime.now()
        minus_month = now + relativedelta(months=-1)
        today = str(now)
        now_year = year = today[:4]
        month = today[5:7]
        cur_month = today[5:7]
        day = today[8:10]
        now_month = today[5:7]
        minus1_month = str(minus_month)[5:7]

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

        payment_history = payment_history_obj = before_orlogo = None
        bichil_price = '0.00'
        try:
            if balance_type == 'balance':
                ehnii_balance = Final_Balance.objects.filter(customer_id=customer.id, year=year, month=month).first()
                if ehnii_balance is not None:
                    ehnii_balance = ehnii_balance.balance
                else:
                    ehnii_balance = 0.00
            else:
                ehnii_balance = Final_Balance.objects.filter(customer_id=customer.id, year=year, month=month).first()
                if ehnii_balance is not None:
                    ehnii_balance = ehnii_balance.ehnii
                else:
                    ehnii_balance = 0.00

            bichilt = Avlaga.objects.filter(customer=customer, is_active='1').order_by('-created_date').first()
            if bichilt is not None:
                pay_date = now_year + '-' + now_month + '-01 00:00:00.000000'
                payment_history = list(PaymentHistory.objects.raw("""SELECT cust.id, IFNULL(SUM(pahi.pay_total), 0) AS pay_total, pahi.pay_date FROM data_customer cust
                    JOIN data_paymenthistory pahi ON cust.id = pahi.customer_id
                    WHERE pahi.is_active = '1' AND pahi.customer_id = """ + str(
                    customer.id) + """ AND pahi.pay_date >= '""" + pay_date + """';"""))

                if len(month) == 1:
                    month += '0' + month
                pay_date = year + '-' + month + '-01 00:00:00.000000'
                before_orlogo = list(PaymentHistory.objects.raw("""SELECT cust.id, IFNULL(SUM(pahi.pay_total), 0) AS pay_total, pahi.pay_date FROM data_customer cust
                    JOIN data_paymenthistory pahi ON cust.id = pahi.customer_id
                    WHERE pahi.is_active = '1' AND pahi.customer_id = """ + str(
                    customer.id) + """ AND pahi.pay_date >= '""" + pay_date + """';"""))

                if bichilt.uilchilgeenii_tulbur is not None:
                    uilchilgeenii_tulbur = bichilt.uilchilgeenii_tulbur
                else:
                    uilchilgeenii_tulbur = Decimal(0)
                bichil_price = str(bichilt.heregleenii_tulbur + uilchilgeenii_tulbur + bichilt.tv_huraamj +
                                   0.00 if bichilt.light is None else bichilt.light +
                                   0.00 if bichilt.ten is None else bichilt.ten + bichilt.barimt_une)
        except ObjectDoesNotExist:
            return HttpResponse("not_found")

        if ehnii_balance is None:
            ehnii_balance = 0
        if '0' == cur_month[0]:
            cur_month = cur_month[1]
        cur_month_avlaga = Avlaga.objects.filter(customer=customer, is_active='1', month=cur_month,
                                                 year=now_year).first()
        if cur_month_avlaga is None:
            ehnii = round(float(ehnii_balance) - float(bichil_price), 2)
            if payment_history is not None:
                balance = round(
                    float(ehnii_balance) - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)
            else:
                balance = round(float(ehnii_balance) - 0, 2)
        else:
            ehnii = float(ehnii_balance)
            balance = round(float(ehnii_balance) + float(bichil_price), 2)
            if payment_history is not None:
                balance = round(balance - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)
            else:
                balance = round(balance - 0, 2)

        call_types = CallType.objects.filter(is_active="1")
        users = UserProfile.objects.filter(is_active="1")

        if int(day) < 26:
            before_balance = Final_Balance.objects.filter(customer_id=customer.id, year=year, month=month).first()
            if before_balance is not None:
                before_balance = before_balance.ehnii
            else:
                before_balance = 0.00
        else:
            before_balance = Final_Balance.objects.filter(customer_id=customer.id, year=year, month=month).first()
            if before_balance is not None:
                before_balance = before_balance.balance
            else:
                before_balance = 0.00

        print("bichil_price : " + str(bichil_price))

        if ded is None:
            data = {
                "urlz": "/home/user_detail/" + user_code + "/",
                "customer": customer,
                "geree": geree,
                "call_list": call_list,
                "before_orlogo": before_orlogo[0].pay_total if before_orlogo is not None else '0.00',
                "tulbur": payment_history[0].pay_total if payment_history is not None else '0.00',
                "paydate": payment_history_obj[0].pay_date if payment_history_obj is not None else '0.00',
                "zdate": zaalt_date,
                "day": day_bal,
                "night": night_bal,
                "rush": rush_bal,
                "bichilt": bichil_price,
                "last_uld": str(balance),
                "tooluur": tooluur,
                "first_uld": str(ehnii),
                "menu": self.menu,
                "bank": bank,
                "address_name": address_name,
                "cycle": cycle,
                "call_types": call_types,
                "now": now,
                "users": users,
                "before_balance": '0.00' if before_balance is None else before_balance
            }
        else:
            data = {
                "urlz": "/home/user_detail/" + user_code + "/",
                "customer": customer,
                "geree": geree,
                "ded": ded,
                "call_list": call_list,
                "before_orlogo": before_orlogo[0].pay_total if before_orlogo is not None else '0.00',
                "tulbur": payment_history[0].pay_total if payment_history is not None else '0.00',
                "paydate": payment_history_obj[0].pay_date if payment_history_obj is not None else '0.00',
                "zdate": zaalt_date,
                "day": day_bal,
                "night": night_bal,
                "rush": rush_bal,
                "bichilt": bichil_price,
                "last_uld": str(balance),
                "tooluur": tooluur,
                "first_uld": str(ehnii),
                "menu": self.menu,
                "bank": bank,
                "address_name": address_name,
                "cycle": cycle,
                "call_types": call_types,
                "now": now,
                "users": users,
                "before_balance": '0.00' if before_balance is None else before_balance
            }
        return render(request, self.template_name, data)


class CallAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_call'
    template_name = "homepage/call/call_add.html"
    menu = "6"

    def get(self, request, id, *args, **kwargs):
        customer = Customer.objects.get(code=id)
        call_types = CallType.objects.filter(is_active="1")
        now = datetime.datetime.now()
        users = UserProfile.objects.filter(is_active="1")

        data = {
            "urlz": "/home/call_add/" + id + "/",
            "customer": customer,
            "call_types": call_types,
            "now": now,
            "users": users,
            "menu": self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        user_code = id
        type = str(rq.get('type', ''))
        select_call_type = rq.get('select_call_type', '')
        call_created_date = rq.get('created_date', '')
        completed_date = rq.get('completed_date', '')
        asigning_user = rq.get('select_user', '')
        call_phone = rq.get('call_phone', '')
        phone = rq.get('phone', '')
        note = rq.get('note', '')
        call = Call.objects.create(call_type_id=int(select_call_type))
        call.created_user_id = request.user.id
        call.customer_code = user_code
        created_date = datetime.datetime.strptime(call_created_date, '%Y-%m-%d %H:%M')
        call.call_created_date = created_date
        if call_phone == '':
            call.call_phone = phone
        else:
            call.call_phone = call_phone
        call.status = "0"
        call.type = type
        call.assigning_user = asigning_user
        if completed_date != "":
            call.status = "1"
            call.completed_date = completed_date
        call.note = note
        call.save()
        firstActivity = CallActivity.objects.create(call=call)
        firstActivity.note = "Дуудлага бүртгэсэн"
        firstActivity.activity_type = "0"
        firstActivity.assigning_user = asigning_user
        firstActivity.save()

        messages.success(request, 'Амжилттай бүртгэгдлээ!')

        return redirect('/home/call_customerdetail/' + str(user_code))


class CallEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_call'
    template_name = "homepage/call/call_add.html"
    menu = "6"

    def get(self, request, user_id, call_id, *args, **kwargs):
        call = Call.objects.get(id=call_id)
        customer = None
        if user_id != '0':
            customer = Customer.objects.get(code=user_id)
        call_types = CallType.objects.filter(is_active="1")
        users = UserProfile.objects.filter(is_active="1")
        if call.call_created_date != None:
            now = call.call_created_date.strftime("%Y-%m-%d %H:%H")
        if call.completed_date != None:
            completed_date = call.completed_date.strftime("%Y-%m-%d %H:%M")
        else:
            completed_date = None


        data = {
            "urlz": "/home/call_edit/" + user_id + "/" + call_id + "/",
            "edit_call": call,
            "customer": customer,
            "call_types": call_types,
            "now": now,
            "users": users,
            "completed_date": completed_date,
            "menu": self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, user_code, id, *args, **kwargs):
        rq = request.POST
        completed_date = rq.get('completed_date', '')
        note = rq.get('note', '')
        select_call_type = rq.get('select_call_type', '')
        select_user = rq.get('select_user', '')

        call = Call.objects.filter(id=int(id)).first()
        if call is not None:
            if completed_date != "":
                call.status = "1"
                call.completed_date = datetime.datetime.strptime(completed_date, '%Y-%m-%d %H:%M')
            else:
                call.status = "0"
            call.assigning_user = select_user
            call.call_type_id = select_call_type
            call.note = note
            call.save()

        if 'save' in rq:
            return redirect("/home/call_list")
        elif 'save_and_continue' in rq:
            return redirect("/home/call_add/" + id + "/")
        elif 'save_and_go_activity' in rq:
            return redirect("/home/call_activity_add/" + str(call.id) + "/")
        data = {
            "menu": self.menu
        }
        return render(request, self.template_name, data)


class CallDelete(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_call'
    template_name = "homepage/call/call_center.html"

    def get(self, request, id, *args, **kwargs):
        selected_call = Call.objects.get(id=id)
        selected_call.is_active = "0"
        selected_call.save()
        return redirect("/home/call_list")


class CallDetail(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_call'
    template_name = "homepage/call/call_detail.html"
    menu = "6"

    def get(self, request, id, *args, **kwargs):
        try:
            call = Call.objects.get(id=id)
        except ObjectDoesNotExist:
            call = None

        users = UserProfile.objects.filter(is_active="1")

        if call is None:
            return redirect("/home/check_list")
        else:
            hasView = 1
        if call.customer_code is None:
            activity = call.callactivity_set.filter(is_active='1')
            data = {
                "call_data": call,
                "users": users,
                "activities": activity,
                "hasView": hasView,
                "menu": self.menu
            }
        else:
            customer = Customer.objects.get(code=call.customer_code)
            activity = call.callactivity_set.filter(is_active='1')
            data = {
                "call_data": call,
                "users": users,
                "activities": activity,
                "customer": customer,
                "hasView": hasView,
                "menu": self.menu
            }
        return render(request, self.template_name, data)


class CallActivityAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_call'
    template_name = "homepage/call/call_activity_add.html"
    menu = "6"

    def get(self, request, id, *args, **kwargs):
        call = Call.objects.get(id=id)
        customer = Customer.objects.get(code=call.customer_code)
        activity = call.callactivity_set.filter(is_active="1")
        call_types = CallType.objects.filter(is_active="1")
        sub_call_types = CallSubType.objects.filter(is_active="1")
        users = UserProfile.objects.filter(is_active="1")
        vilchilgee = TulburtUilchilgee.objects.filter(is_active="1")
        now = call.call_created_date.strftime("%Y-%m-%d %H:%M")
        data = {
            "urlz": "/home/call_activity_add/" + id + "/",
            "call_data": call,
            "activities": activity,
            "customer": customer,
            "call_types": call_types,
            "now": now,
            "users": users,
            "uilchilgee": vilchilgee,
            "menu": self.menu,
            "header_link": '/home/call_detail/' + id + "/"
        }

        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        call = Call.objects.get(id=id)
        call_sub_type = rq.get('select_sub_type', '')
        call_created_date = rq.get('start_date', '')
        type = rq.get('type', '')
        assgning_user = rq.get('select_user', '')
        assgning_company = rq.get('assigning_company', '')
        note = rq.get('note', '')
        uilchil = rq.get('select_uil', '')

        if (call_sub_type != ""):
            if call.call_sub_type != call:
                call.call_sub_type = CallSubType.objects.get(name=call_sub_type)
                call.save()

        if call_created_date != "":
            now = call.call_created_date.strftime("%Y-%m-%d %H:%M")
            if call_created_date != now:
                call.call_created_date = datetime.datetime.strptime(call_created_date, '%Y-%m-%d %H:%M')
                call.save()

        activity = CallActivity.objects.create(call=call)
        activity.note = note
        if type == "3":
            call.status = "1"
            call.completed_date = datetime.now()
        if assgning_company != "":
            activity.assigning_user_name = assgning_company
        elif assgning_user != "":
            activity.assigning_user = assgning_user
            if assgning_user != '':
                userz = UserProfile.objects.get(id=assgning_user)
                activity.assigning_user_name = userz.user.first_name + " " + userz.user.last_name
        activity.activity_type = type
        activity.save()

        if (uilchil != ""):
            current = datetime.datetime.now()
            year = current.year
            month = current.month
            cus = Customer.objects.get(code=call.customer_code)
            tool = TooluurCustomer.objects.filter(customer=cus)
            u = CustomerUilchilgeeTulbur.objects.create(created_user_id=request.user.id,
                                                        customer_id=cus.id,
                                                        tooluur_id=Tooluur.objects.get(id=tool[0].tooluur.id).id,
                                                        uilchilgee_id=uilchil,
                                                        uil_date=current)
            u.year = year
            u.month = month
            u.payment = TulburtUilchilgee.objects.get(id=uilchil).payment
            u.save()
            try:
                a = Avlaga.objects.filter(tooluur_cus=tool[0], year=year, month=month + 1)
                b = a[0]
                if (b.uilchilgeenii_tulbur != None):
                    print("not none")
                    b.uilchilgeenii_tulbur += u.payment
                else:
                    print("none")
                    b.uilchilgeenii_tulbur = u.payment
                b.save()
            except:
                tulbur_date = getPayDate(tool[0], year, month)
                a = Avlaga.objects.create(created_user_id=request.user.id, year=u.year, month=u.month + 1,
                                          tooluur_cus=tool[0], tulbur_date=tulbur_date)
                a.uilchilgeenii_tulbur = u.payment
                a.save()
        return redirect("/home/call_detail/" + id + "/")


class CallActivityDelete(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_call'

    def get(self, request, call_id, activity_id, *args, **kwargs):
        call = Call.objects.get(id=call_id)
        # if len(call.calactivity_set.all())
        selected_activity = CallActivity.objects.get(id=activity_id)
        selected_activity.is_active = "0"
        selected_activity.save()
        return redirect("/home/call_detail/" + call_id + "/")


class CallActivityEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_call'
    template_name = "homepage/call/call_activity_add.html"

    def get(self, request, id, activity_id, *args, **kwargs):
        call = Call.objects.get(id=id)
        customer = Customer.objects.get(code=call.customer_code)
        call_types = CallType.objects.filter(is_active='1')
        users = UserProfile.objects.all()
        edit_activity = CallActivity.objects.get(id=activity_id)
        tuuis = TulburtUilchilgee.objects.filter(is_active='1')
        if call.call_created_date != None:
            now = call.call_created_date.strftime("%Y-%m-%d")
        else:
            now = datetime.datetime.now()
        data = {
            "urlz": "/home/call_activity_edit/" + id + "/" + activity_id + "/",
            "call_data": call,
            "customer": customer,
            "edit_activity": edit_activity,
            "call_types": call_types,
            "now": now,
            "tuuis": tuuis,
            "users": users,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, activity_id, *args, **kwargs):
        rq = request.POST
        call = Call.objects.get(id=id)
        select_call_type = rq.get('select_call_type', '')
        call_created_date = rq.get('start_date', '')
        select_uil = rq.get('select_uil', '')
        type = rq.get('type', '')
        assgning_user = rq.get('select_user', '')
        assgning_company = rq.get('assigning_company', '')
        note = rq.get('note', '')

        if (select_call_type != ""):
            if call.call_sub_type != call:
                call.call_type = select_call_type
                call.save()

        if call_created_date != "":
            now = call.call_created_date.strftime("%Y-%m-%d")
            if call_created_date != now:
                call.call_created_date = datetime.datetime.strptime(call_created_date, '%Y-%m-%d').date()
                call.save()

        activity = CallActivity.objects.get(id=activity_id)
        activity.note = note
        if type == "3":
            call.status = "1"
            call.completed_date = datetime.now()
        # if assgning_company != "":
        #     activity.assigning_org = assgning_company
        elif assgning_user != "":
            activity.assigning_user = assgning_user
        activity.activity_type = type
        if select_uil != "":
            activity.tulburt_uilchilgee_id = int(select_uil)
        activity.save()

        return redirect("/home/call_detail/" + id + "/")


def get_sub_call_types(request):
    name = request.GET['name']
    result_set = []
    selected_type = CallGeneralType.objects.get(name=name)
    all_sub_types = selected_type.callsubtype_set.all()
    for sub_type in all_sub_types:
        print("sub_type name", sub_type.name)
        result_set.append({'name': sub_type.name, 'id': sub_type.id})

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def get_tooluur_detail(request):
    data = {}
    last_bichilt = {}
    tooluur_id = request.GET['tooluur_id']
    user_code = request.GET['code']
    tooluur_det = Tooluur.objects.get(number=tooluur_id)
    tooluur_customer = TooluurCustomer.objects.filter(tooluur__number=tooluur_id, customer_code=user_code)
    tooluur_customer = tooluur_customer[0]
    bichilt_list = tooluur_customer.bichilt_set.all().order_by('created_date')
    if len(bichilt_list) > 0 and len(bichilt_list) < 2:
        suuliin_bichilt = bichilt_list[0]
        last_bichilt[
            'initial'] = 'Өдөр: ' + tooluur_det.initial_value + ', Шөнө: ' + tooluur_det.initial_value_night + ', Оргил цаг: ' + tooluur_det.initial_value_rush
        last_day_balance = suuliin_bichilt.day_balance
        if last_day_balance == None:
            last_day_balance = "0.0"
        last_night_balance = suuliin_bichilt.night_balance
        if last_night_balance == None:
            last_night_balance = "0.0"
        last_rush_balance = suuliin_bichilt.rush_balance
        if last_rush_balance == None:
            last_rush_balance = "0.0"
        last_bichilt[
            'balance'] = 'Өдөр: ' + last_day_balance + ', Шөнө: ' + last_night_balance + ', Оргил цаг: ' + last_rush_balance
    elif len(bichilt_list) > 1:
        suuliin_bichilt = bichilt_list[0]
        ehnii_bichil = bichilt_list[1]
        last_bichilt[
            'initial'] = 'Өдөр: ' + ehnii_bichil.day_balance + ', Шөнө: ' + ehnii_bichil.night_balance + ', Оргил цаг: ' + ehnii_bichil.rush_balance
        last_bichilt[
            'balance'] = 'Өдөр: ' + suuliin_bichilt.day_balance + ', Шөнө: ' + suuliin_bichilt.night_balance + ', Оргил цаг: ' + suuliin_bichilt.rush_balance
    else:
        last_bichilt[
            'initial'] = 'Өдөр: ' + tooluur_det.initial_value + ', Шөнө: ' + tooluur_det.initial_value_night + ', Оргил цаг: ' + tooluur_det.initial_value_rush
        last_bichilt[
            'balance'] = 'Өдөр: ' + tooluur_det.balance_value + ', Шөнө: ' + tooluur_det.balance_value_night + ', Оргил цаг: ' + tooluur_det.balance_value_rush

    last_bichilt['day'] = tooluur_det.initial_value
    last_bichilt['mark'] = tooluur_det.mark
    last_bichilt['installed_date'] = tooluur_det.installed_date.strftime("%Y-%m-%d")
    last_bichilt['verified_date'] = tooluur_det.verified_date.strftime("%Y-%m-%d")
    if tooluur_det.tariff == '0':
        last_bichilt['tariff'] = '1 тариф'
    elif tooluur_det.tariff == '1':
        last_bichilt['tariff'] = '2 тариф'
    else:
        last_bichilt['tariff'] = '3 тариф'
    last_bichilt['amper'] = tooluur_det.amper
    last_bichilt['voltage'] = tooluur_det.voltage

    if tooluur_det.status == '0':
        stat = 'Ашиглагдаагүй'
    elif tooluur_det.status == '1':
        stat = 'Ашиглагдаж байгаа'
    else:
        stat = 'Ашиглалтаас гарсан'
    last_bichilt['status'] = stat

    volt_coff = "1.0"
    amp_coff = "1.0"
    if tooluur_customer.guidliin_trans != None:
        amp_coff = tooluur_customer.guidliin_trans.multiply_coef
    if tooluur_customer.huchdeliin_trans != None:
        volt_coff = tooluur_customer.huchdeliin_trans.multiply_coef
    last_bichilt['tr_koef'] = amp_coff
    last_bichilt['u_koef'] = volt_coff
    last_bichilt['angilal'] = tooluur_customer.customer_angilal
    data['last_bichilt'] = last_bichilt
    return HttpResponse(simplejson.dumps(data), content_type='application/json')


def get_default_start(request):
    aimag_list = Aimag.objects.filter(is_active='1')
    duureg_list = Duureg.objects.filter(aimag_id=1, is_active='1')
    horoo_list = Horoo.objects.filter(duureg_id=3, is_active='1')
    hothon_list = Hothon.objects.filter(horoo_id=2, is_active='1')
    block_list = Block.objects.filter(is_active='1')
    result_set = []

    for aimag in aimag_list:
        result_set.append({'type': '1', 'name': aimag.name, 'code': aimag.code})
    for duureg in duureg_list:
        result_set.append({'type': '2', 'name': duureg.name, 'code': duureg.code})
    for horoo in horoo_list:
        result_set.append({'type': '3', 'name': horoo.name, 'code': horoo.code})
    for hothon in hothon_list:
        result_set.append({'type': '4', 'name': hothon.name, 'code': hothon.code})
    for block in block_list:
        result_set.append({'type': '5', 'name': block.name, 'code': block.code})

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def get_bairs(request):
    code = request.GET['code']
    result_set = []

    bairs = Address.objects.raw("SELECT id, building_number FROM mcsi.data_address WHERE block_code = '" + str(
        code) + "' GROUP BY building_number ORDER BY building_number;")
    if len(list(bairs)) > 0:
        for obj in bairs:
            if obj.building_number != '':
                result_set.append({'name': obj.building_number, 'code': obj.building_number})

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def get_toots(request):
    code = request.GET.get('code', False)
    blockCode = request.GET.get('blockCode', False)
    hothonCode = request.GET.get('hothonCode', False)

    result_set = []

    if hothonCode == '1341':
        toots = Address.objects.filter(building_number=code, block_code=blockCode, hothon_code=hothonCode).order_by(
            'toot')
    else:
        toots = Address.objects.filter(building_number=code, hothon_code=hothonCode).order_by('toot')
    if len(list(toots)) > 0:
        for obj in toots:
            if obj.building_number != '':
                result_set.append({'name': obj.toot, 'code': obj.customer_id})

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def get_bair_block(request):
    khothonCode = request.GET['khothonCode']

    result_set = []
    khothon = Hothon.objects.filter(code=str(khothonCode)).first()
    if khothon is not None:
        blocks = Block.objects.filter(hothon_id=int(khothon.id))
        if len(list(blocks)) > 0:
            for obj in blocks:
                result_set.append({'name': obj.name, 'code': obj.code})
            result_set.append({'type': '1'})
        else:
            bairs = Address.objects.raw("SELECT id, building_number FROM mcsi.data_address WHERE hothon_code = '" + str(
                khothon.code) + "' GROUP BY building_number ORDER BY building_number;")
            if len(list(bairs)) > 0:
                for obj in bairs:
                    if obj.building_number != '':
                        result_set.append({'name': obj.building_number, 'code': obj.building_number})
                result_set.append({'type': '2'})

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def get_khotkhon(request):
    code = request.GET['code']
    result_set = []
    parent = Horoo.objects.get(code=code)
    list = parent.hothon_set.filter(is_active="1").order_by('name')
    for obj in list:
        result_set.append({'name': obj.name, 'code': str(obj.code)})

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
