import xlwt
import simplejson
from django.contrib import messages
from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from apps.homepage.forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin


class TooluurList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_tooluurcustomer'
    template_name = "homepage/burtgel/tooluur_list.html"
    qry = "SELECT tc.id, cu.code, cu.first_name, cu.last_name, dt.name, dt.code AS dtcode, t.number, t.name AS toolname, t.mark, t.expire_date, bair.name AS flatname, guid_trans.multiply_coef AS guidel, huch_trans.multiply_coef AS huchdel " \
        "FROM data_tooluurcustomer AS tc " \
        "INNER JOIN data_tooluur AS t ON tc.tooluur_id=t.id " \
        "LEFT JOIN data_customer AS cu ON tc.customer_id=cu.id " \
        "LEFT JOIN data_dedstants AS dt ON tc.dedstants_id=dt.id " \
        "LEFT JOIN data_bair AS bair ON tc.bair_id=bair.id " \
        "LEFT JOIN data_transformator AS guid_trans ON tc.guidliin_trans_id=guid_trans.id " \
        "LEFT JOIN data_transformator AS huch_trans ON tc.huchdeliin_trans_id=huch_trans.id " \
        "WHERE tc.is_active = 1"
    xlslist = None
    menu = "2"
    sub = "3"

    def get(self, request, *args, **kwargs):

        q = self.qry + " ORDER BY tc.created_date DESC"
        toolCus = list(TooluurCustomer.objects.raw(q))
        mark_list = Tooluur.objects.raw("SELECT id, mark FROM data_tooluur WHERE is_active = '1' GROUP BY mark ORDER BY mark")

        TooluurList.xlslist = toolCus

        data = {
            "list": toolCus,
            "mark_list": mark_list,
            "menu": self.menu,
            "sub": self.sub
        }

        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST

        customer_angilal = rq.get('select_angilal', '')
        customer_code = rq.get('customer_code', '')
        customer_name = rq.get('customer_name', '')
        tooluur_number = rq.get('tooluur_number', '')
        tooluur_name = rq.get('tooluur_name', '')
        tooluur_mark = rq.get('tooluur_mark', '')
        srchQry = self.qry

        if customer_angilal != '':
            srchQry = srchQry + " AND tc.customer_angilal = '" + customer_angilal + "'"

            if customer_angilal == '0':
                if customer_code != '':
                    srchQry = srchQry + " AND dt.code = '" + customer_code + "'"

                if customer_name != '':
                    srchQry = srchQry + " AND dt.name = '" + customer_name + "'"
            if customer_angilal == '1':
                if customer_code != '':
                    srchQry = srchQry + " AND cu.code = '" + customer_code + "'"

                if customer_name != '':
                    srchQry = srchQry + " AND (cu.first_name LIKE '%%" + customer_name + "%%' OR cu.last_name LIKE '%%" + customer_name + "%%')"
            if customer_angilal == '2':

                if customer_name != '':
                    srchQry = srchQry + " AND bair.name LIKE '%%" + customer_name + "%%'"
        else:
            if customer_code != '':
                srchQry = srchQry + " AND (cu.code LIKE '%%" + customer_code + "%%' OR dt.code LIKE '%%" + customer_code + "%%')"
            if customer_name != '':
                srchQry = srchQry + " AND (cu.first_name LIKE '%%" + customer_name + "%%' OR cu.last_name LIKE '%%" + customer_name + "%%' OR dt.name LIKE '%%" + customer_name + "%%')"

        if tooluur_number != '':
            srchQry = srchQry + " AND t.number LIKE '%%" + tooluur_number + "%%'"
        if tooluur_name != '':
            srchQry = srchQry + " AND t.name LIKE '%%" + tooluur_name + "%%'"
        if tooluur_mark != '':
            srchQry = srchQry + " AND t.mark LIKE '%%" + tooluur_mark + "%%'"

        search_q = {'customer_angilal': customer_angilal, 'customer_code': customer_code, 'customer_name': customer_name,
                  'tooluur_number': tooluur_number, 'tooluur_name': tooluur_name, 'tooluur_mark': tooluur_mark}

        toolCus = list(TooluurCustomer.objects.raw(srchQry + ' ORDER BY tc.created_date DESC'))

        mark_list = Tooluur.objects.raw("SELECT id, mark FROM data_tooluur WHERE is_active = '1' GROUP BY mark ORDER BY mark")

        if 'export_xls' in rq:
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="hemjih_heregsel.xls"'

            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Sheet1')

            borders = xlwt.Borders()
            borders.left = xlwt.Borders.THIN
            borders.right = xlwt.Borders.THIN
            borders.top = xlwt.Borders.THIN
            borders.bottom = xlwt.Borders.THIN

            title_style = xlwt.XFStyle()
            title_style.font.bold = True

            header_style = xlwt.XFStyle()
            header_style.font.bold = True
            header_style.alignment.wrap = True
            header_style.alignment.vert = header_style.alignment.VERT_CENTER
            header_style.borders = borders

            row_style = xlwt.XFStyle()
            row_style.borders = borders

            ws.write(0, 3, 'Хэмжих хэрэгсэл', title_style)

            row_num = 2
            row_counter = 0

            columns = ['№', 'Хэрэглэгчийн код', 'Хэрэглэгчийн нэр', 'Тоолуурын дугаар', 'Тоолуурын нэршил',
                       'Тоолуурын марк',
                       'Баталгаа дуусах', 'Гүйдлийн трансформаторын коеффицент', 'Хүчдэлийн трансформаторын коеффицент']
            col_width = [int(5 * 260), int(14 * 260), int(30 * 260), int(12 * 260), int(20 * 260), int(12 * 260),
                         int(20 * 260), int(30 * 260), int(30 * 260)]

            for col_num in range(len(columns)):
                ws.col(col_num).width = col_width[col_num]
                ws.write(row_num, col_num, columns[col_num], header_style)

            for row in toolCus:

                row_num += 1
                row_counter += 1
                col_num = 0

                code = ''
                full_name = ''

                if row.code is None:
                    if row.dtcode is not None:
                        code = row.dtcode
                    else:
                        code = '- Байр -'
                else:
                    code = row.code

                if row.name is None:
                    if row.first_name is not None:
                        full_name = row.first_name
                    if row.last_name is not None:
                        full_name = full_name + ' ' + row.last_name
                else:
                    full_name = row.name

                ws.write(row_num, col_num, row_counter, row_style)
                col_num += 1
                ws.write(row_num, col_num, code, row_style)
                col_num += 1
                ws.write(row_num, col_num, full_name, row_style)
                col_num += 1
                ws.write(row_num, col_num, row.number, row_style)
                col_num += 1
                ws.write(row_num, col_num, row.toolname, row_style)
                col_num += 1
                ws.write(row_num, col_num, row.mark, row_style)
                col_num += 1
                ws.write(row_num, col_num, str(row.expire_date), row_style)
                col_num += 1
                if row.guidel is not None:
                    ws.write(row_num, col_num, row.guidel, row_style)
                else:
                    ws.write(row_num, col_num, '-', row_style)
                col_num += 1
                if row.huchdel is not None:
                    ws.write(row_num, col_num, row.huchdel, row_style)
                else:
                    ws.write(row_num, col_num, '-', row_style)

            wb.save(response)
            return response


        data = {
            "list": toolCus,
            "mark_list": mark_list,
            "search_q": search_q,
            "menu": self.menu,
            "sub": self.sub
        }

        return render(request, self.template_name, data)


class TooluurAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = ('data.add_tooluurcustomer', 'data.change_tooluurcustomer')
    template_name = "homepage/burtgel/tooluur_add.html"
    form_class = OrgAddForm
    menu = "2"
    sub = "3"

    def get(self, request, *args, **kwargs):

        tooluur = Tooluur.objects.filter(status='0', is_active='1')

        trans_amp = []
        trans_volt = []
        amp_list = []
        volt_list = []

        trans_list = Transformator.objects.filter(is_active='1')

        for trans in trans_list:

            if trans.type == '0':
                if trans.multiply_coef not in amp_list:
                    amp_list.append(trans.multiply_coef)
                    trans_amp.append({'det_id': trans.id, 'mult_coef': trans.multiply_coef, 'type': trans.type, })

            if trans.type == '1':
                if trans.multiply_coef not in volt_list:
                    volt_list.append(trans.multiply_coef)
                    trans_volt.append({'det_id': trans.id, 'mult_coef': trans.multiply_coef, 'type': trans.type, })

        data = {
            "urlz": "/home/tooluur_add",
            "tooluur": tooluur,
            "trans_amp": trans_amp,
            "trans_volt": trans_volt,
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):

        rq = request.POST

        tool_num = rq.get('select_tooluur', '')
        day_balance = rq.get('balance_value', '')
        night_balance = rq.get('balance_value_night', '')
        rush_balance = rq.get('balance_value_rush', '')

        tooluur = Tooluur.objects.get(number=tool_num)
        tooluur.balance_value = day_balance
        tooluur.balance_value_night = night_balance
        tooluur.balance_value_rush = rush_balance
        tooluur.status = 1
        tooluur.save()
        cus_angilal = rq.get('select_angilal', '')
        cus = rq.get('select_customer', '')
        light = rq.get('light', '0')
        ten = rq.get('ten', '0')

        tCus = TooluurCustomer.objects.create(tooluur=tooluur)
        tCus.customer_angilal = cus_angilal

        if tCus.customer_angilal == '0':

            dedstants_angilal = rq.get('select_dedstants_angilal', '')
            tool_input = rq.get('select_tooluur_input', '')

            dedStants = DedStants.objects.get(id=int(cus))
            tCus.flow_type = dedstants_angilal
            tCus.dedstants = dedStants
            tCus.customer_code = dedStants.code
            tCus.input_type = tool_input
        if tCus.customer_angilal == '1':
            customer = Customer.objects.get(id=int(cus))
            tCus.customer = customer
            tCus.flow_type = "0"
            tCus.customer_code = customer.code
            tCus.input_type = "1"
        if tCus.customer_angilal == '2':
            bair = Bair.objects.get(id=int(cus))
            tCus.flow_type = "0"
            tCus.bair = bair
            tCus.input_type = "1"
            bair.input_id = tCus.id
            bair.save()

        ampTransId = rq.get('select_amp_trans', '')
        voltTransId = rq.get('select_volt_trans', '')

        if ampTransId != "":
            tCus.guidliin_trans = Transformator.objects.get(id=ampTransId)

        if voltTransId != "":
            tCus.huchdeliin_trans = Transformator.objects.get(id=voltTransId)

        tCus.light = True if light == '1' else False
        tCus.ten = True if ten == '1' else False
        tCus.save()

        messages.success(request, "Амжилттай хадгалагдлаа.")

        return redirect('/home/tooluur_list')


class TooluurEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = ('data.add_tooluurcustomer', 'data.change_tooluurcustomer')
    template_name = "homepage/burtgel/tooluur_add.html"
    menu = "2"
    sub = "3"

    def get(self, request, id, *args, **kwargs):

        tooluurCus = TooluurCustomer.objects.get(id=id)

        ampertrans_list = []
        volttrans_list = []
        amp_list = []
        volt_list = []

        trans_list = Transformator.objects.filter(is_active='1')

        for trans in trans_list:

            if trans.type == '0':
                if trans.multiply_coef not in amp_list:
                    amp_list.append(trans.multiply_coef)
                    ampertrans_list.append({'det_id': trans.id, 'mult_coef': trans.multiply_coef, 'type': trans.type, })

            if trans.type == '1':
                if trans.multiply_coef not in volt_list:
                    volt_list.append(trans.multiply_coef)
                    volttrans_list.append({'det_id': trans.id, 'mult_coef': trans.multiply_coef, 'type': trans.type, })

        tooluur = Tooluur.objects.filter(status='0', is_active='1')
        verified_date = tooluurCus.tooluur.verified_date.strftime("%Y-%m-%d")
        installed_date = tooluurCus.tooluur.installed_date.strftime("%Y-%m-%d")
        expire_date = tooluurCus.tooluur.expire_date.strftime("%Y-%m-%d")

        am = Amper.objects.filter(id=tooluurCus.tooluur.amper).first()
        vol = Voltage.objects.filter(id=tooluurCus.tooluur.voltage).first()

        customer_type = 'Хэрэглэгчийн ангилал байхгүй байна.'
        if tooluurCus.customer_angilal == '0':
            customer_type = DedStants.objects.filter(is_active="1").order_by('name')
        if tooluurCus.customer_angilal == '1':
            customer_type = Customer.objects.filter(is_active="1").order_by('code')
        if tooluurCus.customer_angilal == '2':
            customer_type = Bair.objects.filter(is_active="1").order_by('name')

        tariff = 'Тариф байхгүй байна.'
        if tooluurCus.tooluur.tariff == '0':
            tariff = "1 тарифт"
        if tooluurCus.tooluur.tariff == '1':
            tariff = "2 тарифт"
        if tooluurCus.tooluur.tariff == '2':
            tariff = "3 тарифт"

        data = {
            "urlz": "/home/tooluur_edit/" + id + "/",
            "tooluur": tooluur,
            "trans_amp": ampertrans_list,
            "trans_volt": volttrans_list,
            "tooluurCus": tooluurCus,
            "verified_date": verified_date,
            "installed_date": installed_date,
            "expire_date": expire_date,
            "customer_type": customer_type,
            "tariff": tariff,
            "am": am,
            "vol": vol,
            "menu": self.menu,
            "sub": self.sub
        }

        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST

        tool_num = rq.get('select_tooluur', '')
        day_balance = rq.get('balance_value', '')
        night_balance = rq.get('balance_value_night', '')
        rush_balance = rq.get('balance_value_rush', '')

        tooluur = Tooluur.objects.filter(number=tool_num,is_active=1).first()

        tooluur.balance_value = day_balance
        tooluur.balance_value_night = night_balance
        tooluur.balance_value_rush = rush_balance
        tooluur.status = 1
        tooluur.save()

        cus_angilal = rq.get('select_angilal', '')
        cus = rq.get('select_customer', '')
        light = rq.get('light', '0')
        ten = rq.get('ten', '0')

        tCus = TooluurCustomer.objects.get(id=id)
        tCus.tooluur = tooluur
        tCus.customer_angilal = cus_angilal

        if tCus.customer_angilal == '0':

            dedstants_angilal = rq.get('select_dedstants_angilal', '')
            tool_input = rq.get('select_tooluur_input', '')

            dedStants = DedStants.objects.get(id=int(cus))
            tCus.flow_type = dedstants_angilal
            tCus.dedstants = dedStants
            tCus.customer_code = dedStants.code
            tCus.input_type = tool_input
        if tCus.customer_angilal == '1':
            customer = Customer.objects.get(id=int(cus))
            tCus.flow_type = "0"
            tCus.customer = customer
            tCus.customer_code = customer.code
            tCus.input_type = "1"
        if tCus.customer_angilal == '2':
            bair = Bair.objects.get(id=int(cus))
            tCus.flow_type = "0"
            tCus.bair = bair
            tCus.input_type = "1"
            bair.input_id = tCus.id
            bair.save()

        ampTransId = rq.get('select_amp_trans', '')
        voltTransId = rq.get('select_volt_trans', '')

        if ampTransId != "":
            tCus.guidliin_trans = Transformator.objects.get(id=ampTransId)
        else:
            tCus.guidliin_trans = None


        if voltTransId != "":
            tCus.huchdeliin_trans = Transformator.objects.get(id=voltTransId)
        else:
            tCus.huchdeliin_trans = None

        tCus.light = True if light == '1' else False
        tCus.ten = True if ten == '1' else False
        tCus.save()

        messages.success(request, "Амжилттай хадгалагдлаа.")

        return redirect('/home/tooluur_list')


class TooluurDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login'
    permission_required = ('data.add_tooluurcustomer', 'data.delete_tooluurcustomer')
    template_name = "homepage/burtgel/tooluur_list.html"

    def get(self, request, id, *args, **kwargs):
        tooluurCus = TooluurCustomer.objects.get(id=id)
        tooluurCus.is_active = 0
        tooluurCus.save()

        tooluurCus.tooluur.status = 0
        tooluurCus.tooluur.save()

        return redirect("/home/tooluur_list")


def getTooluur(request):
    result_set = []
    number = request.GET['code']
    try:
        tooluur = Tooluur.objects.get(number=number, is_active='1')
        result_set.append({'number': tooluur.number, 'mark': tooluur.mark, 'name': tooluur.name,
                           'initial_value': tooluur.initial_value,
                           'balance_value': tooluur.balance_value,
                           'initial_value_night': tooluur.initial_value_night,
                           'balance_value_night': tooluur.balance_value_night,
                           'initial_value_rush': tooluur.initial_value_rush,
                           'balance_value_rush': tooluur.balance_value_rush,
                           'verified_date': tooluur.verified_date.strftime("%Y-%m-%d"),
                           'installed_date': tooluur.installed_date.strftime("%Y-%m-%d"),
                           'expire_date': tooluur.expire_date.strftime("%Y-%m-%d"), 'status': tooluur.status,
                           'tariff': tooluur.tariff, 'amper': Amper.objects.get(id=tooluur.amper).value,
                           'voltage': Voltage.objects.get(id=tooluur.voltage).value})

    except Tooluur.DoesNotExist:
        error = "not exist"
    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def getCus(request):
    code = request.GET['code']
    result_set = []

    if code == '0':
        list = DedStants.objects.filter(is_active="1").order_by('name')
        for obj in list:
            if obj.name != '':
                result_set.append({'name': obj.name, 'code': obj.code, 'id': obj.id})
    if code == '1':
        list = Customer.objects.filter(is_active="1").order_by('code')
        for obj in list:
            if obj.code != '':
                result_set.append({'code': obj.code, 'id': obj.id})
    if code == '2':
        list = Bair.objects.filter(is_active="1").order_by('name')
        for obj in list:
            if obj.name != '':
                result_set.append({'name': obj.name, 'id': obj.id})

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')