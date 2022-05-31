from datetime import date
from calendar import monthrange
import logging
import xlwt
from django.core.exceptions import ObjectDoesNotExist
from apps.data.models import *
from django.views import View
from django.shortcuts import render, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class report(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_report'
    template_name = "homepage/report.html"

    def get(self, request, id, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.filter(is_active='1').order_by('name')
        except ObjectDoesNotExist:
            ded_stants = None

        try:
            cycle = Cycle.objects.filter(is_active='1').order_by('code')
        except ObjectDoesNotExist:
            cycle = None

        data = {
            'activeTab': id,
            'ded_stants': ded_stants,
            'cycle': cycle
        }
        return render(request, self.template_name, data)


def report_geree_4(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="niit_her_tovchoo.xls"'

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

    ws.write(0, 1, 'Нийт бүртгэлтэй хэрэглэгчдийн товчоо', title_style)
    ws.write(2, 1, '', xlwt.XFStyle())

    row_num = 3
    row_counter = 1
    columns = ['№', 'Хэрэглэгчийн ангилал', 'Хэрэглэгчийн тоо']
    col_width = [int(5 * 260), int(25 * 260), int(14 * 260)]

    for col_num in range(len(columns)):
        ws.col(col_num).width = col_width[col_num]
        ws.write(row_num, col_num, columns[col_num], header_style)

    ahui = Customer.objects.filter(is_active='1', customer_angilal='1')

    ws.write(4, 0, '1', row_style)
    ws.write(4, 1, 'Ахуйн хэрэглэгч', row_style)
    ws.write(4, 2, len(ahui), row_style)

    row_num = 4
    qry = "SELECT aan.id, aan.name, COUNT(*) AS count " \
          "FROM data_aanangilal AS aan " \
          "LEFT JOIN data_customer AS cu ON cu.customer_type=aan.code " \
          "WHERE cu.is_active = '1' AND cu.customer_angilal = 0 GROUP BY aan.name ORDER BY aan.code DESC"

    rows = list(Customer.objects.raw(qry))

    for row in rows:
        row_num += 1
        row_counter += 1
        col_num = 0

        ws.write(row_num, col_num, row_counter, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.name, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.count, row_style)

    wb.save(response)
    return response


def report_service_1(request):
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="uilchilgee_delgerengui.xls"'

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

    ws.write(0, 3, 'Төлбөрт үйлчилгээний дэлгэрэнгүй тайлан', title_style)
    ws.write(2, 6, 'Хамрах хугацаа: ' + start_date + ' - ' + end_date, xlwt.XFStyle())

    row_num = 3
    row_counter = 0
    total_payment = 0

    columns = ['№', 'Хэрэглэгчийн код', 'Хэрэглэгчийн нэр', 'Үйлчилгээний нэршил', 'Дүн', 'Огноо', 'Хаяг', 'Ажилтны нэр']
    col_width = [int(5 * 260), int(14 * 260), int(30 * 260), int(40 * 260), int(15 * 260), int(12 * 260), int(40 * 260), int(25 * 260)]

    for col_num in range(len(columns)):
        ws.col(col_num).width = col_width[col_num]
        ws.write(row_num, col_num, columns[col_num], header_style)
    q = """
        select t.*
        , a.address_name
        from data_customeruilchilgeetulbur t
        left join data_address a on t.customer_id = a.customer_id
        where t.uil_date between '""" + start_date + """ 00:00:00.000000' and '""" + end_date + """ 00:00:00.000000'
        and t.is_active = 1
    """
    rows = CustomerUilchilgeeTulbur.objects.raw(q)
    for row in rows:
        row_num += 1
        row_counter += 1
        col_num = 0
        full_name = row.customer.first_name if row.customer.first_name else '' + ' ' + row.customer.last_name if row.customer.last_name else ''
        monter_name = row.customer.first_name if row.customer.first_name else '' + ' ' + row.customer.last_name if row.customer.last_name else ''

        ws.write(row_num, col_num, row_counter, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.customer.code, row_style)
        col_num += 1
        ws.write(row_num, col_num, full_name, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.uilchilgee.name, row_style)
        col_num += 1
        total_payment += row.payment
        ws.write(row_num, col_num, row.payment, row_style)
        col_num += 1
        ws.write(row_num, col_num, str(row.uil_date), row_style)
        col_num += 1
        ws.write(row_num, col_num, row.address_name, row_style)
        col_num += 1
        ws.write(row_num, col_num, monter_name, row_style)
    row_style.alignment.horz = row_style.alignment.HORZ_RIGHT
    ws.write(row_num + 1, 3, 'Нийт дүн:', row_style)
    ws.write(row_num + 1, 4, str(total_payment), row_style)

    wb.save(response)
    return response


def report_service_2(request):
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="uilchilgee_huraangui.xls"'

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

    ws.write(0, 1, 'Төлбөрт үйлчилгээний хураангуй тайлан', title_style)
    ws.write(2, 1, 'Хамрах хугацаа: ' + start_date + ' - ' + end_date, xlwt.XFStyle())

    row_num = 3
    row_counter = 0
    ttl_count = 0
    ttl_payment = 0

    columns = ['№', 'Төрөл', 'Тоо', 'Мөнгөн дүн']
    col_width = [int(5 * 260), int(20 * 260), int(8 * 260), int(12 * 260)]

    for col_num in range(len(columns)):
        ws.col(col_num).width = col_width[col_num]
        ws.write(row_num, col_num, columns[col_num], header_style)

    qry = "SELECT ser.id, cu.customer_angilal AS angilal, SUM(ser.payment) AS ttl, COUNT(ser.id) AS cnt " \
          "FROM data_customeruilchilgeetulbur ser " \
          "JOIN data_customer cu ON ser.customer_id = cu.id " \
          "WHERE ser.is_active = '1' AND cu.is_active = '1' AND ser.uil_date >= '" + str(start_date) + "' AND ser.uil_date <= '" + str(end_date) + "' " \
          "GROUP BY cu.customer_angilal"

    rows = list(Customer.objects.raw(qry))

    for row in rows:

        row_num += 1
        row_counter += 1
        col_num = 0

        ws.write(row_num, col_num, row_counter, row_style)
        col_num += 1
        if row.angilal == '0':
            ws.write(row_num, col_num, 'Аж ахуй нэгж', row_style)
        else:
            ws.write(row_num, col_num, 'Ахуйн хэрэглэгч', row_style)
        col_num += 1
        ttl_count += row.cnt
        ws.write(row_num, col_num, row.cnt, row_style)
        col_num += 1
        ttl_payment += row.ttl
        ws.write(row_num, col_num, row.ttl, row_style)

    ws.write(row_num + 1, 1, 'Нийт:', row_style)
    ws.write(row_num + 1, 2, ttl_count, row_style)
    ws.write(row_num + 1, 3, ttl_payment, row_style)

    wb.save(response)
    return response


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
header_style.alignment.vert = xlwt.Alignment.VERT_CENTER
header_style.borders = borders

row_style = xlwt.XFStyle()
row_style.borders = borders

orange_style = xlwt.easyxf('pattern: pattern solid, fore_colour orange')
orange_style.font.bold = True
orange_style.borders = borders
orange_style.alignment.vert = xlwt.Alignment.VERT_CENTER
orange_style.alignment.horz = xlwt.Alignment.HORZ_CENTER

rotate_style = xlwt.easyxf('align: rotation 90')
rotate_style.font.bold = True
rotate_style.alignment.wrap = True
rotate_style.alignment.vert = xlwt.Alignment.VERT_CENTER
rotate_style.alignment.horz = xlwt.Alignment.HORZ_CENTER
rotate_style.borders = borders

rotate_text_style = xlwt.easyxf('align: rotation 90')
rotate_text_style.alignment.wrap = True
rotate_text_style.alignment.vert = xlwt.Alignment.VERT_CENTER
rotate_text_style.alignment.horz = xlwt.Alignment.HORZ_CENTER
rotate_text_style.borders = borders

text_style = xlwt.XFStyle()
text_style.alignment.horz = xlwt.Alignment.HORZ_CENTER


def report_bichilt_2_old(request):
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="TSEH_nii_bichilt_orlogo_uldegdliin_delgerengui_tailan.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 3, 'ЦЭХ-ний бичилт, орлого, үлдэгдлийн дэлгэрэнгүй тайлан /циклээр/', title_style)
    ws.write(2, 0, 'Тайлангийн хамрах хугацаа : ' + start_date + ' - ' + end_date, xlwt.XFStyle())
    ws.write(2, 6, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())

    row_num = 3
    row_counter = 0

    columns = ['№', 'Хэрэглэгчийн код', 'Хэрэглэгчийн нэр', 'Хаяг', 'Эхний үлдэгдэл', 'Бичилт', 'Орлого',
               'Эцсийн үлдэгдэл']
    col_width = [int(5 * 260), int(12 * 260), int(30 * 260), int(40 * 260), int(12 * 260), int(12 * 260), int(12 * 260),
                 int(12 * 260)]

    for col_num in range(len(columns)):
        ws.col(col_num).width = col_width[col_num]
        ws.write(row_num, col_num, columns[col_num], header_style)

    qry = "SELECT bich.id, cust.code, cust.first_name, cust.last_name, addr.address_name,"
    qry += " (SELECT (SUM(avla.heregleenii_tulbur) + SUM(avla.uilchilgeenii_tulbur)) FROM data_avlaga avla"
    qry += " JOIN data_tooluurcustomer tc ON avla.customer_id=tc.customer_id"
    qry += " WHERE avla.is_active='1' AND avla.pay_type='0' AND cust.id=tc.customer_id) AS uldegdel,"
    qry += " SUM(bich.total_price) AS bichilt,"
    qry += " (SELECT SUM(pahi.pay_total) FROM data_paymenthistory pahi WHERE pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'"
    qry += " AND pahi.is_active='1' AND pahi.customer_id=cust.id) AS orlogo"
    qry += " FROM data_bichilt bich JOIN data_tooluurcustomer tocu ON bich.tooluur_id=tocu.tooluur_id"
    qry += " JOIN data_customer cust ON tocu.customer_id=cust.id LEFT JOIN data_address addr ON cust.id=addr.customer_id"
    qry += " WHERE bich.is_active='1' AND cust.is_active='1' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"

    ah_total = [0, 0, 0, 0]
    try:
        row_num += 1
        bichilts = Bichilt.objects.raw(qry + " AND cust.customer_angilal='1' GROUP BY cust.id;")
        if bichilts is not None:
            for bichilt in bichilts:
                row_counter += 1
                ws.write(row_num, 0, row_counter, row_style)
                ws.write(row_num, 1, bichilt.code, row_style)
                ws.write(row_num, 2, bichilt.first_name + " " + bichilt.last_name, row_style)
                ws.write(row_num, 3, bichilt.address_name, row_style)
                ws.write(row_num, 4, round(bichilt.uldegdel, 2) if bichilt.uldegdel else 0, row_style)
                ah_total[0] += round(bichilt.uldegdel, 2) if bichilt.uldegdel else 0
                ws.write(row_num, 5, round(bichilt.bichilt, 2) if bichilt.bichilt else 0, row_style)
                ah_total[1] += round(bichilt.bichilt, 2) if bichilt.bichilt else 0
                ws.write(row_num, 6, round(bichilt.orlogo, 2) if bichilt.orlogo else 0, row_style)
                ah_total[2] += round(bichilt.orlogo, 2) if bichilt.orlogo else 0
                etssiin_uld = (float(bichilt.uldegdel) if bichilt.uldegdel else 0) + (
                    float(bichilt.bichilt) if bichilt.bichilt else 0)
                etssiin_uld = float(etssiin_uld) - (float(bichilt.orlogo) if bichilt.orlogo else 0)
                ws.write(row_num, 7, round(etssiin_uld, 2), row_style)
                ah_total[3] += round(etssiin_uld, 2)
                row_num += 1
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" object has no objects: %s', e)

    ws.write(row_num, 0, '', header_style)
    ws.write_merge(row_num, row_num, 1, 2, 'Дүн:  Хэрэглэгчийн тоо: ' + str(row_counter), header_style)
    ws.write(row_num, 3, '', header_style)
    ws.write(row_num, 4, ah_total[0], header_style)
    ws.write(row_num, 5, ah_total[1], header_style)
    ws.write(row_num, 6, ah_total[2], header_style)
    ws.write(row_num, 7, ah_total[3], header_style)

    row_num += 1
    ws.write(row_num, 1, 'Байгууллага ААН', xlwt.XFStyle())

    aan_total = [0, 0, 0, 0]
    row_counter_aan = 0
    try:
        row_num += 1
        bichilts = Bichilt.objects.raw(qry + " AND cust.customer_angilal='0' GROUP BY cust.id;")
        if bichilts is not None:
            for bichilt in bichilts:
                row_counter_aan += 1
                ws.write(row_num, 0, row_counter_aan, row_style)
                ws.write(row_num, 1, bichilt.code, row_style)
                ws.write(row_num, 2, bichilt.first_name + " " + bichilt.last_name, row_style)
                ws.write(row_num, 3, bichilt.address_name, row_style)
                ws.write(row_num, 4, round(bichilt.uldegdel, 2) if bichilt.uldegdel else 0, row_style)
                aan_total[0] += round(bichilt.uldegdel, 2) if bichilt.uldegdel else 0
                ws.write(row_num, 5, round(bichilt.bichilt, 2) if bichilt.bichilt else 0, row_style)
                aan_total[1] += round(bichilt.bichilt, 2) if bichilt.bichilt else 0
                ws.write(row_num, 6, round(bichilt.orlogo, 2) if bichilt.orlogo else 0, row_style)
                aan_total[2] += round(bichilt.orlogo, 2) if bichilt.orlogo else 0
                etssiin_uld = (float(bichilt.uldegdel) if bichilt.uldegdel else 0) + (
                    float(bichilt.bichilt) if bichilt.bichilt else 0)
                etssiin_uld = float(etssiin_uld) - (float(bichilt.orlogo) if bichilt.orlogo else 0)
                ws.write(row_num, 7, round(etssiin_uld, 2), row_style)
                aan_total[3] += round(etssiin_uld, 2)
                row_num += 1
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" object has no objects: %s', e)

    ws.write(row_num, 0, '', header_style)
    ws.write_merge(row_num, row_num, 1, 2, 'Дүн:  Хэрэглэгчийн тоо: ' + str(row_counter_aan), header_style)
    ws.write(row_num, 3, '', header_style)
    ws.write(row_num, 4, aan_total[0], row_style)
    ws.write(row_num, 5, aan_total[1], row_style)
    ws.write(row_num, 6, aan_total[2], row_style)
    ws.write(row_num, 7, aan_total[3], row_style)
    row_num += 1
    ws.write(row_num, 0, '', row_style)
    ws.write_merge(row_num, row_num, 1, 2, 'Нийт:  Хэрэглэгчийн тоо: ' + str(row_counter_aan + row_counter), row_style)
    ws.write(row_num, 3, '', row_style)
    ws.write(row_num, 4, aan_total[0] + ah_total[0], header_style)
    ws.write(row_num, 5, aan_total[1] + ah_total[1], header_style)
    ws.write(row_num, 6, aan_total[2] + ah_total[2], header_style)
    ws.write(row_num, 7, aan_total[3] + ah_total[3], header_style)

    wb.save(response)
    return response


def report_bichilt_3_old(request):
    year = request.POST['year']
    month = request.POST['month']

    response = HttpResponse(content_type='application/ms-excel')
    response[
        'Content-Disposition'] = 'attachment; filename="' + year + '_onii_' + month + '_sariin_tsahilgaan_erchim_huchnii_bichilt.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 1, year + ' оны ' + month + '-р сарын цахилгаан эрчим хүчний бичилт', title_style)
    ws.write(2, 4, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())
    row_num = 3
    columns = ['Хэрэглэгчийн код', 'Нэр', 'Регистр', 'Бичилт', 'НӨАТ-гүй дүн', 'НӨАТ']
    col_width = [int(12 * 260), int(30 * 260), int(12 * 260), int(18 * 260), int(18 * 260), int(18 * 260)]

    for col_num in range(len(columns)):
        ws.col(col_num).width = col_width[col_num]
        ws.write(row_num, col_num, columns[col_num], header_style)
    row_num += 1
    ws.write_merge(row_num, row_num, 0, 2, 'Нийт Ахуйн хэрэглэгч', header_style)

    ah_total_bichilt = 0
    ah_total_nuatgui = 0
    ah_total_nuat = 0

    qry = "SELECT bich.id, SUM(bich.total_diff) AS total_diff, SUM(bich.total_price) AS total_price"
    qry += " FROM data_bichilt bich"
    qry += " JOIN data_tooluurcustomer tocu ON bich.tooluur_id=bich.tooluur_id"
    qry += " JOIN data_customer cust ON tocu.customer_id=cust.id"
    qry += " WHERE bich.is_active='1' AND bich.year='" + year + "' AND bich.month='" + month + "' AND cust.customer_angilal='1'"

    try:
        bichilts = Bichilt.objects.raw(qry)
        if bichilts is not None:
            for bichilt in bichilts:
                ah_total_bichilt += round(bichilt.total_diff, 2) if bichilt.total_diff else 0
                ws.write(row_num, 3, round(bichilt.total_diff, 2) if bichilt.total_diff else 0, header_style)
                ah_total_nuatgui += (
                    round(bichilt.total_price, 2) - (round(bichilt.total_price, 2) * 0.1)) if bichilt.total_price else 0
                ws.write(row_num, 4, (
                    round(bichilt.total_price, 2) - (
                        round(bichilt.total_price, 2) * 0.1)) if bichilt.total_price else 0,
                         header_style)
                ah_total_nuat += round(bichilt.total_price, 2) if bichilt.total_price else 0
                ws.write(row_num, 5, round(bichilt.total_price, 2) if bichilt.total_price else 0, header_style)
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" object has no objects: %s', e)

    row_num += 1
    ws.write_merge(row_num, row_num, 0, 5, 'ААН', header_style)

    aan_total_bichilt = 0
    aan_total_nuatgui = 0
    aan_total_nuat = 0

    qry = "SELECT bich.id, cust.code, cust.first_name, cust.register, SUM(bich.total_diff) AS total_diff, SUM(bich.total_price) AS total_price"
    qry += " FROM data_bichilt bich"
    qry += " JOIN data_tooluurcustomer tocu ON bich.tooluur_id=bich.tooluur_id"
    qry += " JOIN data_customer cust ON tocu.customer_id=cust.id"
    qry += " WHERE bich.is_active='1' AND bich.year='" + year + "' AND bich.month='" + month + "' AND cust.customer_angilal='0' GROUP BY cust.code"

    row_num += 1
    try:
        bichilts = Bichilt.objects.raw(qry)
        if bichilts is not None:
            for bichilt in bichilts:
                ws.write(row_num, 0, bichilt.code, row_style)
                ws.write(row_num, 1, bichilt.first_name, row_style)
                ws.write(row_num, 2, bichilt.register, row_style)
                aan_total_bichilt += round(bichilt.total_diff, 2) if bichilt.total_diff else 0
                ws.write(row_num, 3, round(bichilt.total_diff, 2) if bichilt.total_diff else 0, row_style)
                aan_total_nuatgui += (
                    round(bichilt.total_price, 2) - (round(bichilt.total_price, 2) * 0.1)) if bichilt.total_price else 0
                ws.write(row_num, 4, (
                    round(bichilt.total_price, 2) - (
                        round(bichilt.total_price, 2) * 0.1)) if bichilt.total_price else 0,
                         row_style)
                aan_total_nuat += round(bichilt.total_price, 2) if bichilt.total_price else 0
                ws.write(row_num, 5, round(bichilt.total_price, 2) if bichilt.total_price else 0, row_style)
                row_num += 1
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" object has no objects: %s', e)

    ws.write_merge(row_num, row_num, 0, 2, 'Нийт ААН', header_style)
    ws.write(row_num, 3, round(aan_total_bichilt, 2), header_style)
    ws.write(row_num, 4, round(aan_total_nuatgui, 2), header_style)
    ws.write(row_num, 5, round(aan_total_nuat, 2), header_style)

    row_num += 1
    ws.write_merge(row_num, row_num, 0, 2, 'Нийт', header_style)
    ws.write(row_num, 3, (ah_total_bichilt + aan_total_bichilt), header_style)
    ws.write(row_num, 4, (ah_total_nuatgui + aan_total_nuatgui), header_style)
    ws.write(row_num, 5, (ah_total_nuat + aan_total_nuat), header_style)

    wb.save(response)
    return response


def report_bichilt_4_old(request):
    start_year = request.POST['start_year']
    start_month = request.POST['start_month']
    start_date = start_year + '-' + start_month + '-01'
    end_year = request.POST['end_year']
    end_month = request.POST['end_month']
    month_last = str(monthrange(int(end_year), int(end_month))).split(',')
    month_last = str(month_last[1].replace(' ', '').replace(')', ''))
    end_date = end_year + '-' + end_month + '-' + month_last

    response = HttpResponse(content_type='application/ms-excel')
    response[
        'Content-Disposition'] = 'attachment; filename="AAN_baiguullaguudiin_heregleenii_delgerengui_sudalgaa_Chadal_Hyazgaar_Bichilt.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 5, 'ААН байгууллагуудын хэрэглээний дэлгэрэнгүй судалгаа /Чадлын хязгаар, Бичилт/', title_style)
    ws.write(2, 0, 'Тайлангийн хамрах хугацаа : ' + start_date + ' - ' + end_date, xlwt.XFStyle())
    ws.write(2, 13, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())

    col_widths = [int(5 * 260), int(20 * 260), int(15 * 260), int(10 * 260), int(15 * 260), int(15 * 260),
                  int(10 * 260), int(15 * 260), int(15 * 260), int(10 * 260), int(15 * 260), int(15 * 260),
                  int(10 * 260), int(15 * 260), int(15 * 260)]
    for i in range(len(col_widths)):
        ws.col(i).width = col_widths[i]

    row_num = 3
    ws.write_merge(row_num, row_num + 1, 0, 0, '№', header_style)
    ws.write_merge(row_num, row_num + 1, 1, 1, 'Хэрэглээний ангилал', header_style)
    ws.write_merge(row_num, row_num + 1, 2, 2, 'Нэгж', header_style)
    ws.write_merge(row_num, row_num, 3, 5, 'Худалдаа үйлчилгээний байгууллага', header_style)
    ws.write(row_num + 1, 3, 'Тоо', header_style)
    ws.write(row_num + 1, 4, 'Нийт хэрэглээ', header_style)
    ws.write(row_num + 1, 5, 'Бичилтийн мөнгөн дүн /төг/', header_style)
    ws.write_merge(row_num, row_num, 6, 8, 'Үйлдвэрлэлийн байгууллага', header_style)
    ws.write(row_num + 1, 6, 'Тоо', header_style)
    ws.write(row_num + 1, 7, 'Нийт хэрэглээ', header_style)
    ws.write(row_num + 1, 8, 'Бичилтийн мөнгөн дүн /төг/', header_style)
    ws.write_merge(row_num, row_num, 9, 11, 'Төсвийн байгууллага', header_style)
    ws.write(row_num + 1, 9, 'Тоо', header_style)
    ws.write(row_num + 1, 10, 'Нийт хэрэглээ', header_style)
    ws.write(row_num + 1, 11, 'Бичилтийн мөнгөн дүн /төг/', header_style)
    ws.write_merge(row_num, row_num, 12, 14, 'Нийт', header_style)
    ws.write(row_num + 1, 12, 'Тоо', header_style)
    ws.write(row_num + 1, 13, 'Нийт хэрэглээ', header_style)
    ws.write(row_num + 1, 14, 'Бичилтийн мөнгөн дүн /төг/', header_style)

    row_titles = ['0-1000', '1001-5000', '5001-10000', '10001-50000', '50001-200000', '200001-500000', '500001-2000000',
                  '2 саяас дээш']

    row_num += 2
    for i in range(8):
        ws.write(row_num + i, 0, i + 1, header_style)
        ws.write(row_num + i, 1, row_titles[i], row_style)
        ws.write(row_num + i, 2, 'кВтц', row_style)

    qry = "SELECT bich.id, COUNT(tocu.customer_id) AS too, IF(COUNT(tocu.customer_id)=0, 0, SUM(bich.total_diff)) AS niit_hereglee, " \
          " IF(COUNT(tocu.customer_id)=0, 0, SUM(bich.total_price)) AS mungun_dun FROM data_bichilt bich" \
          " JOIN data_tooluurcustomer tocu ON tocu.tooluur_id=bich.tooluur_id" \
          " JOIN data_customer cust ON tocu.customer_id=cust.id" \
          " WHERE bich.is_active='1' AND (bich.bichilt_date BETWEEN '" + start_date + "' AND '" + end_date + "') AND cust.customer_angilal = '0'"

    queries = [" AND cust.customer_type = '1' AND (bich.total_diff >= 0 AND bich.total_diff <= 1000)",
               " AND cust.customer_type = '2' AND (bich.total_diff >= 0 AND bich.total_diff <= 1000)",
               " AND cust.customer_type = '3' AND (bich.total_diff >= 0 AND bich.total_diff <= 1000)",
               " AND cust.customer_type = '1' AND (bich.total_diff >= 1001 AND bich.total_diff <= 5000)",
               " AND cust.customer_type = '2' AND (bich.total_diff >= 1001 AND bich.total_diff <= 5000)",
               " AND cust.customer_type = '3' AND (bich.total_diff >= 1001 AND bich.total_diff <= 5000)",
               " AND cust.customer_type = '1' AND (bich.total_diff >= 5001 AND bich.total_diff <= 10000)",
               " AND cust.customer_type = '2' AND (bich.total_diff >= 5001 AND bich.total_diff <= 10000)",
               " AND cust.customer_type = '3' AND (bich.total_diff >= 5001 AND bich.total_diff <= 10000)",
               " AND cust.customer_type = '1' AND (bich.total_diff >= 10001 AND bich.total_diff <= 50000)",
               " AND cust.customer_type = '2' AND (bich.total_diff >= 10001 AND bich.total_diff <= 50000)",
               " AND cust.customer_type = '3' AND (bich.total_diff >= 10001 AND bich.total_diff <= 50000)",
               " AND cust.customer_type = '1' AND (bich.total_diff >= 50001 AND bich.total_diff <= 200000)",
               " AND cust.customer_type = '2' AND (bich.total_diff >= 50001 AND bich.total_diff <= 200000)",
               " AND cust.customer_type = '3' AND (bich.total_diff >= 50001 AND bich.total_diff <= 200000)",
               " AND cust.customer_type = '1' AND (bich.total_diff >= 200001 AND bich.total_diff <= 500000)",
               " AND cust.customer_type = '2' AND (bich.total_diff >= 200001 AND bich.total_diff <= 500000)",
               " AND cust.customer_type = '3' AND (bich.total_diff >= 200001 AND bich.total_diff <= 500000)",
               " AND cust.customer_type = '1' AND (bich.total_diff >= 500001 AND bich.total_diff <= 2000000)",
               " AND cust.customer_type = '2' AND (bich.total_diff >= 500001 AND bich.total_diff <= 2000000)",
               " AND cust.customer_type = '3' AND (bich.total_diff >= 500001 AND bich.total_diff <= 2000000)",
               " AND cust.customer_type = '1' AND bich.total_diff >= 2000001",
               " AND cust.customer_type = '2' AND bich.total_diff >= 2000001",
               " AND cust.customer_type = '3' AND bich.total_diff >= 2000001"]

    try:
        row_num = 5
        col_nums = [2, 2, 2, 2, 2, 2, 2, 2]
        toos = [0, 0, 0, 0, 0, 0, 0, 0]
        niit_hereglees = [0, 0, 0, 0, 0, 0, 0, 0]
        mungun_duns = [0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(len(queries)):
            if i <= 2:
                index = 0
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
            if i >= 3 and i <= 5:
                index = 1
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num + 1, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num + 1, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num + 1, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
            if i >= 6 and i <= 8:
                index = 2
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num + 2, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num + 2, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num + 2, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
            if i >= 9 and i <= 11:
                index = 3
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num + 3, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num + 3, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num + 3, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
            if i >= 12 and i <= 14:
                index = 4
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num + 4, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num + 4, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num + 4, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
            if i >= 15 and i <= 17:
                index = 5
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num + 5, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num + 5, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num + 5, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
            if i >= 18 and i <= 20:
                index = 6
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num + 6, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num + 6, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num + 6, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
            if i >= 21 and i <= 23:
                index = 7
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num + 7, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num + 7, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num + 7, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
        for i in range(8):
            ws.write(row_num + i, 12, toos[i], header_style)
            ws.write(row_num + i, 13, niit_hereglees[i], header_style)
            ws.write(row_num + i, 14, mungun_duns[i], header_style)
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" object has no objects: %s', e)

    wb.save(response)
    return response


def report_bichilt_6_old(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="AAN_baiguullaguudiin_heregleenii_sudalgaa_Sar_Bureer.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 5, 'ААН байгууллагуудын хэрэглээний судалгаа /сар бүрээр/', title_style)
    ws.write(2, 14, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())
    row_num = 3

    ws.col(0).width = int(5 * 260)
    ws.write_merge(row_num, row_num + 1, 0, 0, '№', header_style)
    ws.col(1).width = int(12 * 260)
    ws.write_merge(row_num, row_num + 1, 1, 1, 'Хэрэглэгчийн код', header_style)
    ws.col(2).width = int(30 * 260)
    ws.write_merge(row_num, row_num + 1, 2, 2, 'Хэрэглэгчийн нэр', header_style)
    ws.write_merge(row_num, row_num, 3, 15, 'Хэрэглээ /кВтц/', header_style)
    row_num += 1
    columns = ['1 сар', '2 сар', '3 сар', '4 сар', '5 сар', '6 сар', '7 сар', '8 сар', '9 сар', '10 сар', '11 сар',
               '12 сар', ]
    col_with = [int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260),
                int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(15 * 260)]
    for col_num in range(len(columns)):
        ws.col(col_num + 3).width = col_with[col_num]
        ws.write(row_num, (col_num + 3), columns[col_num], row_style)
    ws.col(15).width = int(15 * 260)
    ws.write(row_num, 15, 'Нийт', header_style)

    current_year = str(date.today().year)

    qry = "SELECT bich.id, tocu.customer_code, cust.first_name,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='1')) AS jan,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='2')) AS feb,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='3')) AS mar,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='4')) AS apr,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='5')) AS may,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='6')) AS jun,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='7')) AS jul,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='8')) AS aug,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='9')) AS sep,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='10')) AS oct,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='11')) AS nov,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='12')) AS decem"
    qry += " FROM data_bichilt bich"
    qry += " JOIN data_tooluurcustomer tocu ON bich.tooluur_id=tocu.tooluur_id"
    qry += " JOIN data_customer cust ON tocu.customer_id=cust.id"
    qry += " JOIN data_address addr ON cust.id=addr.customer_id"
    qry += " WHERE bich.is_active='1' AND cust.customer_angilal='0'"

    row_num = 5
    row_counter = 0
    total_ktv_month = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ws.write_merge(row_num, row_num, 0, 15, 'Вива сити', header_style)
    try:
        bichilts = Bichilt.objects.raw(qry + " AND addr.address_name LIKE '%% Вива %%' GROUP BY cust.code")
        if bichilts is not None:
            for bichilt in bichilts:
                row_counter += 1
                row_num += 1
                total_ktv_year = 0
                col_num = 0
                ws.write(row_num, col_num, row_counter, row_style)
                col_num += 1
                ws.write(row_num, col_num, bichilt.customer_code, row_style)
                col_num += 1
                ws.write(row_num, col_num, bichilt.first_name, row_style)
                col_num += 1
                total_ktv_month[0] += round(bichilt.jan, 2) if bichilt.jan else 0
                total_ktv_year += round(bichilt.jan, 2) if bichilt.jan else 0
                ws.write(row_num, col_num, round(bichilt.jan, 2) if bichilt.jan else 0, row_style)
                col_num += 1
                total_ktv_month[1] += round(bichilt.feb, 2) if bichilt.feb else 0
                total_ktv_year += round(bichilt.feb, 2) if bichilt.feb else 0
                ws.write(row_num, col_num, round(bichilt.feb, 2) if bichilt.feb else 0, row_style)
                col_num += 1
                total_ktv_month[2] += round(bichilt.mar, 2) if bichilt.mar else 0
                total_ktv_year += round(bichilt.mar, 2) if bichilt.mar else 0
                ws.write(row_num, col_num, round(bichilt.mar, 2) if bichilt.mar else 0, row_style)
                col_num += 1
                total_ktv_month[3] += round(bichilt.apr, 2) if bichilt.apr else 0
                total_ktv_year += round(bichilt.apr, 2) if bichilt.apr else 0
                ws.write(row_num, col_num, round(bichilt.apr, 2) if bichilt.apr else 0, row_style)
                col_num += 1
                total_ktv_month[4] += round(bichilt.may, 2) if bichilt.may else 0
                total_ktv_year += round(bichilt.may, 2) if bichilt.may else 0
                ws.write(row_num, col_num, round(bichilt.may, 2) if bichilt.may else 0, row_style)
                col_num += 1
                total_ktv_month[5] += round(bichilt.jun, 2) if bichilt.jun else 0
                total_ktv_year += round(bichilt.jun, 2) if bichilt.jun else 0
                ws.write(row_num, col_num, round(bichilt.jun, 2) if bichilt.jun else 0, row_style)
                col_num += 1
                total_ktv_month[6] += round(bichilt.jul, 2) if bichilt.jul else 0
                total_ktv_year += round(bichilt.jul, 2) if bichilt.jul else 0
                ws.write(row_num, col_num, round(bichilt.jul, 2) if bichilt.jul else 0, row_style)
                col_num += 1
                total_ktv_month[7] += round(bichilt.aug, 2) if bichilt.aug else 0
                total_ktv_year += round(bichilt.aug, 2) if bichilt.aug else 0
                ws.write(row_num, col_num, round(bichilt.aug, 2) if bichilt.aug else 0, row_style)
                col_num += 1
                total_ktv_month[8] += round(bichilt.sep, 2) if bichilt.sep else 0
                total_ktv_year += round(bichilt.sep, 2) if bichilt.sep else 0
                ws.write(row_num, col_num, round(bichilt.sep, 2) if bichilt.sep else 0, row_style)
                col_num += 1
                total_ktv_month[9] += round(bichilt.oct, 2) if bichilt.oct else 0
                total_ktv_year += round(bichilt.oct, 2) if bichilt.oct else 0
                ws.write(row_num, col_num, round(bichilt.oct, 2) if bichilt.oct else 0, row_style)
                col_num += 1
                total_ktv_month[10] += round(bichilt.nov, 2) if bichilt.nov else 0
                total_ktv_year += round(bichilt.nov, 2) if bichilt.nov else 0
                ws.write(row_num, col_num, round(bichilt.nov, 2) if bichilt.nov else 0, row_style)
                col_num += 1
                total_ktv_month[11] += round(bichilt.decem, 2) if bichilt.decem else 0
                total_ktv_year += round(bichilt.decem, 2) if bichilt.decem else 0
                ws.write(row_num, col_num, round(bichilt.decem, 2) if bichilt.decem else 0, row_style)
                col_num += 1
                total_ktv_month[12] += round(total_ktv_year, 2)
                ws.write(row_num, col_num, round(total_ktv_year, 2), header_style)
            row_num += 1
            col_num = 2
            ws.write(row_num, 0, '', header_style)
            ws.write(row_num, 1, '', header_style)
            ws.write(row_num, 2, 'Нийт дүн', header_style)
            for i in range(len(total_ktv_month)):
                col_num += 1
                ws.write(row_num, col_num, round(total_ktv_month[i], 2), header_style)
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" object has no objects: %s', e)

    row_num += 1
    row_counter = 0
    total_ktv_month = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ws.write_merge(row_num, row_num, 0, 15, 'Будда виста', header_style)
    try:
        bichilts = Bichilt.objects.raw(
            qry + " AND addr.address_name LIKE '%% Будда виста %%' GROUP BY tocu.customer_code")
        if bichilts is not None:
            for bichilt in bichilts:
                row_counter += 1
                row_num += 1
                total_ktv_year = 0
                col_num = 0
                ws.write(row_num, col_num, row_counter, row_style)
                col_num += 1
                ws.write(row_num, col_num, bichilt.customer_code, row_style)
                col_num += 1
                ws.write(row_num, col_num, bichilt.first_name, row_style)
                col_num += 1
                total_ktv_month[0] += round(bichilt.jan, 2) if bichilt.jan else 0
                total_ktv_year += round(bichilt.jan, 2) if bichilt.jan else 0
                ws.write(row_num, col_num, round(bichilt.jan, 2) if bichilt.jan else 0, row_style)
                col_num += 1
                total_ktv_month[1] += round(bichilt.feb, 2) if bichilt.feb else 0
                total_ktv_year += round(bichilt.feb, 2) if bichilt.feb else 0
                ws.write(row_num, col_num, round(bichilt.feb, 2) if bichilt.feb else 0, row_style)
                col_num += 1
                total_ktv_month[2] += round(bichilt.mar, 2) if bichilt.mar else 0
                total_ktv_year += round(bichilt.mar, 2) if bichilt.mar else 0
                ws.write(row_num, col_num, round(bichilt.mar, 2) if bichilt.mar else 0, row_style)
                col_num += 1
                total_ktv_month[3] += round(bichilt.apr, 2) if bichilt.apr else 0
                total_ktv_year += round(bichilt.apr, 2) if bichilt.apr else 0
                ws.write(row_num, col_num, round(bichilt.apr, 2) if bichilt.apr else 0, row_style)
                col_num += 1
                total_ktv_month[4] += round(bichilt.may, 2) if bichilt.may else 0
                total_ktv_year += round(bichilt.may, 2) if bichilt.may else 0
                ws.write(row_num, col_num, round(bichilt.may, 2) if bichilt.may else 0, row_style)
                col_num += 1
                total_ktv_month[5] += round(bichilt.jun, 2) if bichilt.jun else 0
                total_ktv_year += round(bichilt.jun, 2) if bichilt.jun else 0
                ws.write(row_num, col_num, round(bichilt.jun, 2) if bichilt.jun else 0, row_style)
                col_num += 1
                total_ktv_month[6] += round(bichilt.jul, 2) if bichilt.jul else 0
                total_ktv_year += round(bichilt.jul, 2) if bichilt.jul else 0
                ws.write(row_num, col_num, round(bichilt.jul, 2) if bichilt.jul else 0, row_style)
                col_num += 1
                total_ktv_month[7] += round(bichilt.aug, 2) if bichilt.aug else 0
                total_ktv_year += round(bichilt.aug, 2) if bichilt.aug else 0
                ws.write(row_num, col_num, round(bichilt.aug, 2) if bichilt.aug else 0, row_style)
                col_num += 1
                total_ktv_month[8] += round(bichilt.sep, 2) if bichilt.sep else 0
                total_ktv_year += round(bichilt.sep, 2) if bichilt.sep else 0
                ws.write(row_num, col_num, round(bichilt.sep, 2) if bichilt.sep else 0, row_style)
                col_num += 1
                total_ktv_month[9] += round(bichilt.oct, 2) if bichilt.oct else 0
                total_ktv_year += round(bichilt.oct, 2) if bichilt.oct else 0
                ws.write(row_num, col_num, round(bichilt.oct, 2) if bichilt.oct else 0, row_style)
                col_num += 1
                total_ktv_month[10] += round(bichilt.nov, 2) if bichilt.nov else 0
                total_ktv_year += round(bichilt.nov, 2) if bichilt.nov else 0
                ws.write(row_num, col_num, round(bichilt.nov, 2) if bichilt.nov else 0, row_style)
                col_num += 1
                total_ktv_month[11] += round(bichilt.decem, 2) if bichilt.decem else 0
                total_ktv_year += round(bichilt.decem, 2) if bichilt.decem else 0
                ws.write(row_num, col_num, round(bichilt.decem, 2) if bichilt.decem else 0, row_style)
                col_num += 1
                total_ktv_month[12] += round(total_ktv_year, 2)
                ws.write(row_num, col_num, round(total_ktv_year, 2), header_style)
            row_num += 1
            col_num = 2
            ws.write(row_num, 0, '', header_style)
            ws.write(row_num, 1, '', header_style)
            ws.write(row_num, 2, 'Нийт дүн', header_style)
            for i in range(len(total_ktv_month)):
                col_num += 1
                ws.write(row_num, col_num, round(total_ktv_month[i], 2), header_style)
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" object has no objects: %s', e)

    wb.save(response)
    return response


def report_bichilt_7_old(request):
    start_year = request.POST['start_year']
    start_month = request.POST['start_month']
    start_date = start_year + '-' + start_month + '-01'
    end_year = request.POST['end_year']
    end_month = request.POST['end_month']
    month_last = str(monthrange(int(end_year), int(end_month))).split(',')
    month_last = str(month_last[1].replace(' ', '').replace(')', ''))
    end_date = end_year + '-' + end_month + '-' + month_last

    response = HttpResponse(content_type='application/ms-excel')
    response[
        'Content-Disposition'] = 'attachment; filename="Ahuin_hereglegchdiin_heregleenii_delgerengui_sudalgaa_Chadal_Hyazgaar_Bichilt.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 4, 'Ахуйн хэрэглэгчдийн хэрэглээний дэлгэрэнгүй судалгаа /Чадлын хязгаар, Бичилт/', title_style)
    ws.write(2, 0, 'Тайлангийн хамрах хугацаа : ' + start_date + ' - ' + end_date, xlwt.XFStyle())
    ws.write(2, 10, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())

    row_num = 3
    ws.col(0).width = int(5 * 260)
    ws.write_merge(row_num, row_num + 1, 0, 0, '№', header_style)
    ws.col(1).width = int(20 * 260)
    ws.write_merge(row_num, row_num + 1, 1, 1, 'Хэрэглээний ангилал', header_style)
    ws.col(2).width = int(15 * 260)
    ws.write_merge(row_num, row_num + 1, 2, 2, 'Нэгж', header_style)
    ws.col(3).width = int(10 * 260)
    ws.col(4).width = int(15 * 260)
    ws.col(5).width = int(15 * 260)
    ws.write_merge(row_num, row_num, 3, 5, 'Түрээслэгч', header_style)
    ws.write(row_num + 1, 3, 'Тоо', header_style)
    ws.write(row_num + 1, 4, 'Нийт хэрэглээ', header_style)
    ws.write(row_num + 1, 5, 'Бичилтийн мөнгөн дүн /төг/', header_style)
    ws.col(6).width = int(10 * 260)
    ws.col(7).width = int(15 * 260)
    ws.col(8).width = int(15 * 260)
    ws.write_merge(row_num, row_num, 6, 8, 'Оршин суугч', header_style)
    ws.write(row_num + 1, 6, 'Тоо', header_style)
    ws.write(row_num + 1, 7, 'Нийт хэрэглээ', header_style)
    ws.write(row_num + 1, 8, 'Бичилтийн мөнгөн дүн /төг/', header_style)
    ws.col(9).width = int(10 * 260)
    ws.col(10).width = int(15 * 260)
    ws.col(11).width = int(15 * 260)
    ws.write_merge(row_num, row_num, 9, 11, 'Нийт', header_style)
    ws.write(row_num + 1, 9, 'Тоо', header_style)
    ws.write(row_num + 1, 10, 'Нийт хэрэглээ', header_style)
    ws.write(row_num + 1, 11, 'Бичилтийн мөнгөн дүн /төг/', header_style)

    row_titles = ['0-1000', '1001-5000', '5001-10000', '10001-50000', '50001-200000', '200001-500000', '500001-2000000',
                  '2 саяас дээш']

    row_num += 2
    for i in range(8):
        ws.write(row_num + i, 0, i + 1, header_style)
        ws.write(row_num + i, 1, row_titles[i], row_style)
        ws.write(row_num + i, 2, 'кВтц', row_style)

    qry = "SELECT bich.id, COUNT(tocu.customer_id) AS too, IF(COUNT(tocu.customer_id)=0, 0, SUM(bich.total_diff)) AS niit_hereglee, " \
          " IF(COUNT(tocu.customer_id)=0, 0, SUM(bich.total_price)) AS mungun_dun FROM data_bichilt bich" \
          " JOIN data_tooluurcustomer tocu ON tocu.tooluur_id=bich.tooluur_id" \
          " JOIN data_customer cust ON tocu.customer_id=cust.id" \
          " WHERE bich.is_active='1' AND (bich.bichilt_date BETWEEN '" + start_date + "' AND '" + end_date + "') AND cust.customer_angilal = '1'"

    queries = [" AND cust.customer_type = '0' AND (bich.total_diff >= 0 AND bich.total_diff <= 1000)",
               " AND cust.customer_type = '1' AND (bich.total_diff >= 0 AND bich.total_diff <= 1000)",
               " AND cust.customer_type = '0' AND (bich.total_diff >= 1001 AND bich.total_diff <= 5000)",
               " AND cust.customer_type = '1' AND (bich.total_diff >= 1001 AND bich.total_diff <= 5000)",
               " AND cust.customer_type = '0' AND (bich.total_diff >= 5001 AND bich.total_diff <= 10000)",
               " AND cust.customer_type = '1' AND (bich.total_diff >= 5001 AND bich.total_diff <= 10000)",
               " AND cust.customer_type = '0' AND (bich.total_diff >= 10001 AND bich.total_diff <= 50000)",
               " AND cust.customer_type = '1' AND (bich.total_diff >= 10001 AND bich.total_diff <= 50000)",
               " AND cust.customer_type = '0' AND (bich.total_diff >= 50001 AND bich.total_diff <= 200000)",
               " AND cust.customer_type = '1' AND (bich.total_diff >= 50001 AND bich.total_diff <= 200000)",
               " AND cust.customer_type = '0' AND (bich.total_diff >= 200001 AND bich.total_diff <= 500000)",
               " AND cust.customer_type = '1' AND (bich.total_diff >= 200001 AND bich.total_diff <= 500000)",
               " AND cust.customer_type = '0' AND (bich.total_diff >= 500001 AND bich.total_diff <= 2000000)",
               " AND cust.customer_type = '1' AND (bich.total_diff >= 500001 AND bich.total_diff <= 2000000)",
               " AND cust.customer_type = '0' AND bich.total_diff >= 2000001",
               " AND cust.customer_type = '1' AND bich.total_diff >= 2000001"]

    try:
        row_num = 5
        col_nums = [2, 2, 2, 2, 2, 2, 2, 2]
        toos = [0, 0, 0, 0, 0, 0, 0, 0]
        niit_hereglees = [0, 0, 0, 0, 0, 0, 0, 0]
        mungun_duns = [0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(len(queries)):
            if i == 0 or i == 1:
                index = 0
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
            if i == 2 or i == 3:
                index = 1
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num + 1, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num + 1, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num + 1, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
            if i == 4 or i == 5:
                index = 2
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num + 2, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num + 2, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num + 2, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
            if i == 6 or i == 7:
                index = 3
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num + 3, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num + 3, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num + 3, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
            if i == 8 or i == 9:
                index = 4
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num + 4, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num + 4, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num + 4, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
            if i == 10 or i == 11:
                index = 5
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num + 5, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num + 5, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num + 5, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
            if i == 12 or i == 13:
                index = 6
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num + 6, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num + 6, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num + 6, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
            if i == 14 or i == 15:
                index = 7
                bichilts = Bichilt.objects.raw(qry + queries[i])
                for bichilt in bichilts:
                    col_nums[index] += 1
                    toos[index] += bichilt.too
                    ws.write(row_num + 7, col_nums[index], bichilt.too, row_style)
                    col_nums[index] += 1
                    niit_hereglees[index] += round(bichilt.niit_hereglee, 2)
                    ws.write(row_num + 7, col_nums[index], round(bichilt.niit_hereglee, 2), row_style)
                    col_nums[index] += 1
                    mungun_duns[index] += round(bichilt.mungun_dun, 2)
                    ws.write(row_num + 7, col_nums[index], round(bichilt.mungun_dun, 2), row_style)
        for i in range(8):
            ws.write(row_num + i, 9, toos[i], header_style)
            ws.write(row_num + i, 10, niit_hereglees[i], header_style)
            ws.write(row_num + i, 11, mungun_duns[i], header_style)
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" object has no objects: %s', e)

    wb.save(response)
    return response


def report_bichilt_9_old(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Ahui_hereglegchdiin_heregleenii_sudalgaa_sar_bureer.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 5, 'Ахуйн хэрэглэгчдийн хэрэглээний судалгаа /сар бүрээр/', title_style)
    ws.write(2, 14, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())
    row_num = 3

    ws.col(0).width = int(5 * 260)
    ws.write_merge(row_num, row_num + 1, 0, 0, '№', header_style)
    ws.col(1).width = int(12 * 260)
    ws.write_merge(row_num, row_num + 1, 1, 1, 'Хэрэглэгчийн код', header_style)
    ws.col(2).width = int(20 * 260)
    ws.write_merge(row_num, row_num + 1, 2, 2, 'Хэрэглэгчийн нэр', header_style)
    ws.write_merge(row_num, row_num, 3, 15, 'Хэрэглээ /кВтц/', header_style)
    row_num += 1
    columns = ['1 сар', '2 сар', '3 сар', '4 сар', '5 сар', '6 сар', '7 сар', '8 сар', '9 сар', '10 сар', '11 сар',
               '12 сар', ]
    col_with = [int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260),
                int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(15 * 260)]
    for col_num in range(len(columns)):
        ws.col(col_num + 3).width = col_with[col_num]
        ws.write(row_num, (col_num + 3), columns[col_num], row_style)
    ws.col(15).width = int(15 * 260)
    ws.write(row_num, 15, 'Нийт', header_style)

    current_year = str(date.today().year)

    qry = "SELECT bich.id, tocu.customer_code, cust.first_name,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='1')) AS jan,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='2')) AS feb,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='3')) AS mar,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='4')) AS apr,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='5')) AS may,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='6')) AS jun,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='7')) AS jul,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='8')) AS aug,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='9')) AS sep,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='10')) AS oct,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='11')) AS nov,"
    qry += " SUM((SELECT SUM(b.total_diff) FROM data_bichilt b WHERE b.tooluur_id=tocu.tooluur_id AND b.year='" + current_year + "' AND b.month='12')) AS decem"
    qry += " FROM data_bichilt bich"
    qry += " JOIN data_tooluurcustomer tocu ON bich.tooluur_id=tocu.tooluur_id"
    qry += " JOIN data_customer cust ON tocu.customer_id=cust.id"
    qry += " JOIN data_address addr ON cust.id=addr.customer_id"
    qry += " WHERE bich.is_active='1' AND cust.customer_angilal='1'"

    row_num = 5
    row_counter = 0
    total_ktv_month = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ws.write_merge(row_num, row_num, 0, 15, 'Вива сити', header_style)
    try:
        bichilts = Bichilt.objects.raw(qry + " AND addr.address_name LIKE '%% Вива %%' GROUP BY cust.code")
        if bichilts is not None:
            for bichilt in bichilts:
                row_counter += 1
                row_num += 1
                total_ktv_year = 0
                col_num = 0
                ws.write(row_num, col_num, row_counter, row_style)
                col_num += 1
                ws.write(row_num, col_num, bichilt.customer_code, row_style)
                col_num += 1
                ws.write(row_num, col_num, bichilt.first_name, row_style)
                col_num += 1
                total_ktv_month[0] += round(bichilt.jan, 2) if bichilt.jan else 0
                total_ktv_year += round(bichilt.jan, 2) if bichilt.jan else 0
                ws.write(row_num, col_num, round(bichilt.jan, 2) if bichilt.jan else 0, row_style)
                col_num += 1
                total_ktv_month[1] += round(bichilt.feb, 2) if bichilt.feb else 0
                total_ktv_year += round(bichilt.feb, 2) if bichilt.feb else 0
                ws.write(row_num, col_num, round(bichilt.feb, 2) if bichilt.feb else 0, row_style)
                col_num += 1
                total_ktv_month[2] += round(bichilt.mar, 2) if bichilt.mar else 0
                total_ktv_year += round(bichilt.mar, 2) if bichilt.mar else 0
                ws.write(row_num, col_num, round(bichilt.mar, 2) if bichilt.mar else 0, row_style)
                col_num += 1
                total_ktv_month[3] += round(bichilt.apr, 2) if bichilt.apr else 0
                total_ktv_year += round(bichilt.apr, 2) if bichilt.apr else 0
                ws.write(row_num, col_num, round(bichilt.apr, 2) if bichilt.apr else 0, row_style)
                col_num += 1
                total_ktv_month[4] += round(bichilt.may, 2) if bichilt.may else 0
                total_ktv_year += round(bichilt.may, 2) if bichilt.may else 0
                ws.write(row_num, col_num, round(bichilt.may, 2) if bichilt.may else 0, row_style)
                col_num += 1
                total_ktv_month[5] += round(bichilt.jun, 2) if bichilt.jun else 0
                total_ktv_year += round(bichilt.jun, 2) if bichilt.jun else 0
                ws.write(row_num, col_num, round(bichilt.jun, 2) if bichilt.jun else 0, row_style)
                col_num += 1
                total_ktv_month[6] += round(bichilt.jul, 2) if bichilt.jul else 0
                total_ktv_year += round(bichilt.jul, 2) if bichilt.jul else 0
                ws.write(row_num, col_num, round(bichilt.jul, 2) if bichilt.jul else 0, row_style)
                col_num += 1
                total_ktv_month[7] += round(bichilt.aug, 2) if bichilt.aug else 0
                total_ktv_year += round(bichilt.aug, 2) if bichilt.aug else 0
                ws.write(row_num, col_num, round(bichilt.aug, 2) if bichilt.aug else 0, row_style)
                col_num += 1
                total_ktv_month[8] += round(bichilt.sep, 2) if bichilt.sep else 0
                total_ktv_year += round(bichilt.sep, 2) if bichilt.sep else 0
                ws.write(row_num, col_num, round(bichilt.sep, 2) if bichilt.sep else 0, row_style)
                col_num += 1
                total_ktv_month[9] += round(bichilt.oct, 2) if bichilt.oct else 0
                total_ktv_year += round(bichilt.oct, 2) if bichilt.oct else 0
                ws.write(row_num, col_num, round(bichilt.oct, 2) if bichilt.oct else 0, row_style)
                col_num += 1
                total_ktv_month[10] += round(bichilt.nov, 2) if bichilt.nov else 0
                total_ktv_year += round(bichilt.nov, 2) if bichilt.nov else 0
                ws.write(row_num, col_num, round(bichilt.nov, 2) if bichilt.nov else 0, row_style)
                col_num += 1
                total_ktv_month[11] += round(bichilt.decem, 2) if bichilt.decem else 0
                total_ktv_year += round(bichilt.decem, 2) if bichilt.decem else 0
                ws.write(row_num, col_num, round(bichilt.decem, 2) if bichilt.decem else 0, row_style)
                col_num += 1
                total_ktv_month[12] += round(total_ktv_year, 2)
                ws.write(row_num, col_num, round(total_ktv_year, 2), header_style)
            row_num += 1
            col_num = 2
            ws.write(row_num, 0, '', header_style)
            ws.write(row_num, 1, '', header_style)
            ws.write(row_num, 2, 'Нийт дүн', header_style)
            for i in range(len(total_ktv_month)):
                col_num += 1
                ws.write(row_num, col_num, round(total_ktv_month[i], 2), header_style)
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" object has no objects: %s', e)

    row_num += 1
    row_counter = 0
    total_ktv_month = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ws.write_merge(row_num, row_num, 0, 15, 'Будда виста', header_style)
    try:
        bichilts = Bichilt.objects.raw(
            qry + " AND addr.address_name LIKE '%% Будда виста %%' GROUP BY cust.code")
        if bichilts is not None:
            for bichilt in bichilts:
                row_counter += 1
                row_num += 1
                total_ktv_year = 0
                col_num = 0
                ws.write(row_num, col_num, row_counter, row_style)
                col_num += 1
                ws.write(row_num, col_num, bichilt.customer_code, row_style)
                col_num += 1
                ws.write(row_num, col_num, bichilt.first_name, row_style)
                col_num += 1
                total_ktv_month[0] += round(bichilt.jan, 2) if bichilt.jan else 0
                total_ktv_year += round(bichilt.jan, 2) if bichilt.jan else 0
                ws.write(row_num, col_num, round(bichilt.jan, 2) if bichilt.jan else 0, row_style)
                col_num += 1
                total_ktv_month[1] += round(bichilt.feb, 2) if bichilt.feb else 0
                total_ktv_year += round(bichilt.feb, 2) if bichilt.feb else 0
                ws.write(row_num, col_num, round(bichilt.feb, 2) if bichilt.feb else 0, row_style)
                col_num += 1
                total_ktv_month[2] += round(bichilt.mar, 2) if bichilt.mar else 0
                total_ktv_year += round(bichilt.mar, 2) if bichilt.mar else 0
                ws.write(row_num, col_num, round(bichilt.mar, 2) if bichilt.mar else 0, row_style)
                col_num += 1
                total_ktv_month[3] += round(bichilt.apr, 2) if bichilt.apr else 0
                total_ktv_year += round(bichilt.apr, 2) if bichilt.apr else 0
                ws.write(row_num, col_num, round(bichilt.apr, 2) if bichilt.apr else 0, row_style)
                col_num += 1
                total_ktv_month[4] += round(bichilt.may, 2) if bichilt.may else 0
                total_ktv_year += round(bichilt.may, 2) if bichilt.may else 0
                ws.write(row_num, col_num, round(bichilt.may, 2) if bichilt.may else 0, row_style)
                col_num += 1
                total_ktv_month[5] += round(bichilt.jun, 2) if bichilt.jun else 0
                total_ktv_year += round(bichilt.jun, 2) if bichilt.jun else 0
                ws.write(row_num, col_num, round(bichilt.jun, 2) if bichilt.jun else 0, row_style)
                col_num += 1
                total_ktv_month[6] += round(bichilt.jul, 2) if bichilt.jul else 0
                total_ktv_year += round(bichilt.jul, 2) if bichilt.jul else 0
                ws.write(row_num, col_num, round(bichilt.jul, 2) if bichilt.jul else 0, row_style)
                col_num += 1
                total_ktv_month[7] += round(bichilt.aug, 2) if bichilt.aug else 0
                total_ktv_year += round(bichilt.aug, 2) if bichilt.aug else 0
                ws.write(row_num, col_num, round(bichilt.aug, 2) if bichilt.aug else 0, row_style)
                col_num += 1
                total_ktv_month[8] += round(bichilt.sep, 2) if bichilt.sep else 0
                total_ktv_year += round(bichilt.sep, 2) if bichilt.sep else 0
                ws.write(row_num, col_num, round(bichilt.sep, 2) if bichilt.sep else 0, row_style)
                col_num += 1
                total_ktv_month[9] += round(bichilt.oct, 2) if bichilt.oct else 0
                total_ktv_year += round(bichilt.oct, 2) if bichilt.oct else 0
                ws.write(row_num, col_num, round(bichilt.oct, 2) if bichilt.oct else 0, row_style)
                col_num += 1
                total_ktv_month[10] += round(bichilt.nov, 2) if bichilt.nov else 0
                total_ktv_year += round(bichilt.nov, 2) if bichilt.nov else 0
                ws.write(row_num, col_num, round(bichilt.nov, 2) if bichilt.nov else 0, row_style)
                col_num += 1
                total_ktv_month[11] += round(bichilt.decem, 2) if bichilt.decem else 0
                total_ktv_year += round(bichilt.decem, 2) if bichilt.decem else 0
                ws.write(row_num, col_num, round(bichilt.decem, 2) if bichilt.decem else 0, row_style)
                col_num += 1
                total_ktv_month[12] += round(total_ktv_year, 2)
                ws.write(row_num, col_num, round(total_ktv_year, 2), header_style)
            row_num += 1
            col_num = 2
            ws.write(row_num, 0, '', header_style)
            ws.write(row_num, 1, '', header_style)
            ws.write(row_num, 2, 'Нийт дүн', header_style)
            for i in range(len(total_ktv_month)):
                col_num += 1
                ws.write(row_num, col_num, round(total_ktv_month[i], 2), header_style)
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" object has no objects: %s', e)

    wb.save(response)
    return response


def report_avlaga_1(request):
    ded_stant = request.POST['ded_stants']
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Avlaga_nasjiltiin_delgerengui_tailan.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    try:
        ded_stants = DedStants.objects.get(id=int(ded_stant))
    except ObjectDoesNotExist:
        ded_stants = None

    ws.write(0, 3, 'Авлагын насжилтын дэлгэрэнгүй тайлан', title_style)
    ws.write(2, 0, 'Дэд станцын нэр : ' + ded_stants.name, xlwt.XFStyle())
    ws.write(3, 0, 'Тайлангийн хамрах хугацаа : ' + start_date + ' - ' + end_date, xlwt.XFStyle())
    ws.write(3, 6, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())

    row_num = 4
    ws.col(0).width = int(5 * 260)
    ws.write_merge(row_num, row_num + 1, 0, 0, '№', header_style)
    ws.col(1).width = int(12 * 260)
    ws.col(2).width = int(20 * 260)
    ws.write_merge(row_num, row_num, 1, 2, 'Хэрэглэгчийн', header_style)
    ws.write(row_num + 1, 1, 'Код', header_style)
    ws.write(row_num + 1, 2, 'Нэр', header_style)
    ws.col(3).width = int(12 * 260)
    ws.write_merge(row_num, row_num + 1, 3, 3, 'Авлагын дүн', header_style)
    ws.col(4).width = int(12 * 260)
    ws.col(5).width = int(12 * 260)
    ws.col(6).width = int(12 * 260)
    ws.col(7).width = int(12 * 260)
    ws.write_merge(row_num, row_num, 4, 7, 'Насжилт /хоног, авлагын дүнгээр/', header_style)
    ws.write(row_num + 1, 4, '0-30 хоног', header_style)
    ws.write(row_num + 1, 5, '31-60 хоног', header_style)
    ws.write(row_num + 1, 6, '61-90 хоног', header_style)
    ws.write(row_num + 1, 7, '90 хоногоос дээш', header_style)

    qry = """
        SELECT avla.id
        , cust.code
        , cust.first_name
        , cust.last_name
        , (avla.heregleenii_tulbur + avla.uilchilgeenii_tulbur) avlaga_dun
        , DATEDIFF( IFNULL ( avla.paid_date , sysdate() ) , avla.created_date) day_diff 
        FROM data_avlaga avla
        JOIN data_customer cust ON avla.customer_id=cust.id
        join data_geree g on cust.code = g.customer_code
        join data_dedstants d on g.dedstants_code = d.code
        and avla.is_active='1' 
        AND avla.out_of_date='1' 
        AND d.id=""" + str(ded_stants.id) + """ 
        AND avla.created_date between '""" + start_date + " 00:00:00.000000' AND '" + end_date + """ 23:59:59.999999'"""

    row_num += 2
    alds = [0, 0, 0, 0, 0]
    try:
        avlagas = Avlaga.objects.raw(qry)
        if avlagas is not None:
            row_style.alignment.horz = xlwt.Alignment.HORZ_RIGHT
            for avlaga in avlagas:
                ws.write(row_num, 0, row_num - 5, row_style)
                ws.write(row_num, 1, avlaga.code, row_style)
                ws.write(row_num, 2, str(avlaga.first_name) + " " + str(avlaga.last_name), row_style)
                ws.write(row_num, 3, '{0:.2f}'.format(avlaga.avlaga_dun), row_style)
                alds[4] += round(avlaga.avlaga_dun, 2)
                if int(avlaga.day_diff) <= 30:
                    ald = float(avlaga.avlaga_dun)
                    alds[0] += ald
                    ws.write(row_num, 4, '{0:.2f}'.format(ald), row_style)
                    ws.write(row_num, 5, 0, row_style)
                    ws.write(row_num, 6, 0, row_style)
                    ws.write(row_num, 7, 0, row_style)
                if int(avlaga.day_diff) >= 31 and int(avlaga.day_diff) <= 60:
                    ald = float(avlaga.avlaga_dun)
                    alds[1] += ald
                    ws.write(row_num, 4, 0, row_style)
                    ws.write(row_num, 5, '{0:.2f}'.format(ald), row_style)
                    ws.write(row_num, 6, 0, row_style)
                    ws.write(row_num, 7, 0, row_style)
                if int(avlaga.day_diff) >= 61 and int(avlaga.day_diff) <= 90:
                    ald = float(avlaga.avlaga_dun)
                    alds[2] += ald
                    ws.write(row_num, 4, 0, row_style)
                    ws.write(row_num, 5, 0, row_style)
                    ws.write(row_num, 6, round(ald, 2), row_style)
                    ws.write(row_num, 7, 0, row_style)
                if int(avlaga.day_diff) >= 91:
                    ald = float(avlaga.avlaga_dun)
                    alds[3] += ald
                    ws.write(row_num, 4, 0, row_style)
                    ws.write(row_num, 5, 0, row_style)
                    ws.write(row_num, 6, 0, row_style)
                    ws.write(row_num, 7, round(ald, 2), row_style)
                row_num += 1
    except ObjectDoesNotExist as e:
        logging.error('"Avlaga" object has no objects: %s', e)
    header_style.alignment.horz = xlwt.Alignment.HORZ_RIGHT
    ws.write(row_num, 0, '', header_style)
    ws.write_merge(row_num, row_num, 1, 2, 'Нийт', header_style)
    ws.write(row_num, 3, '{0:.2f}'.format(alds[4]), header_style)
    ws.write(row_num, 4, '{0:.2f}'.format(alds[0]), header_style)
    ws.write(row_num, 5, round(alds[1], 2), header_style)
    ws.write(row_num, 6, alds[2], header_style)
    ws.write(row_num, 7, alds[3], header_style)

    wb.save(response)
    return response


def report_avlaga_2(request):
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Avlaga_nasjiltiin_tovch_tailan.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 5, 'Авлагын насжилтын товч тайлан', title_style)
    ws.write(2, 1, 'Тайлангийн хамрах хугацаа : ' + start_date + ' - ' + end_date, xlwt.XFStyle())
    ws.write(2, 10, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())

    row_num = 3
    ws.col(0).width = int(5 * 260)
    ws.write_merge(row_num, row_num + 2, 0, 0, '№', header_style)
    ws.col(1).width = int(20 * 260)
    ws.write_merge(row_num, row_num + 2, 1, 1, 'Дэд станцын нэр', header_style)
    ws.col(2).width = int(10 * 260)
    ws.col(3).width = int(12 * 260)
    ws.write_merge(row_num, row_num, 2, 3, 'Хэрэглэгчийн', header_style)
    ws.write_merge(row_num + 1, row_num + 2, 2, 2, 'Тоо', header_style)
    ws.write_merge(row_num + 1, row_num + 2, 3, 3, 'Авлагын дүнгээр', header_style)
    ws.write_merge(row_num, row_num, 4, 11, 'Насжилт /хоног, авлагын дүнгээр/', header_style)
    ws.col(4).width = int(12 * 260)
    ws.col(5).width = int(15 * 260)
    ws.write_merge(row_num + 1, row_num + 1, 4, 5, '0-30 хоног', header_style)
    ws.write(row_num + 2, 4, 'Хэрэглэгчийн тоо', header_style)
    ws.write(row_num + 2, 5, 'Авлагын дүн /төгрөгөөр/', header_style)
    ws.col(6).width = int(12 * 260)
    ws.col(7).width = int(15 * 260)
    ws.write_merge(row_num + 1, row_num + 1, 6, 7, '31-60 хоног', header_style)
    ws.write(row_num + 2, 6, 'Хэрэглэгчийн тоо', header_style)
    ws.write(row_num + 2, 7, 'Авлагын дүн /төгрөгөөр/', header_style)
    ws.col(8).width = int(12 * 260)
    ws.col(9).width = int(15 * 260)
    ws.write_merge(row_num + 1, row_num + 1, 8, 9, '61-90 хоног', header_style)
    ws.write(row_num + 2, 8, 'Хэрэглэгчийн тоо', header_style)
    ws.write(row_num + 2, 9, 'Авлагын дүн /төгрөгөөр/', header_style)
    ws.col(10).width = int(12 * 260)
    ws.col(11).width = int(15 * 260)
    ws.write_merge(row_num + 1, row_num + 1, 10, 11, '90 хоногоос дээш', header_style)
    ws.write(row_num + 2, 10, 'Хэрэглэгчийн тоо', header_style)
    ws.write(row_num + 2, 11, 'Авлагын дүн /төгрөгөөр/', header_style)
    qry = """
        select 
        distinct a.id
        , d.name
        , count( distinct c.id ) too
        , sum( ifnull( a.heregleenii_tulbur , 0 ) + ifnull( a.uilchilgeenii_tulbur , 0 ) )  avlaga_dun
        , count( distinct a0.customer_id ) teg_guch_too
        , sum( ifnull( a0.heregleenii_tulbur , 0 ) + ifnull( a0.uilchilgeenii_tulbur , 0 ) ) teg_guch
        , count( distinct a30.customer_id ) guch_jar_too
        , sum( ifnull( a30.heregleenii_tulbur , 0 ) + ifnull( a30.uilchilgeenii_tulbur , 0 ) ) guch_jar
        , count( distinct a60.customer_id ) jar_yer_too
        , sum( ifnull( a60.heregleenii_tulbur , 0 ) + ifnull( a60.uilchilgeenii_tulbur , 0 ) ) jar_yer
        , count( distinct a90.customer_id ) yer_deesh_too
        , sum( ifnull( a90.heregleenii_tulbur , 0 ) + ifnull( a90.uilchilgeenii_tulbur , 0 ) ) yer_deesh
        from data_dedstants d
        left join data_geree g on d.code = g.dedstants_code
        left join data_customer c on g.customer_code = c.code 
        left join data_avlaga a on c.id = a.customer_id
        and a.created_date between '""" + start_date + """ 00:00:00.000000' and '""" + end_date + """ 23:59:59.999999'
        and a.pay_type = 1
        left join data_avlaga a0 on a.id = a0.id
        and datediff( ifnull( a0.paid_date, sysdate() ) , a0.created_date ) < 30
        and a0.pay_type = 1
        left join data_avlaga a30 on a.id = a30.id
        and datediff( ifnull( a30.paid_date, sysdate() ) , a30.created_date ) between 30 and 60
        and a30.pay_type = 1
        left join data_avlaga a60 on a.id = a60.id
        and datediff( ifnull( a60.paid_date, sysdate() ) , a60.created_date ) between 61 and 90
        and a60.pay_type = 1
        left join data_avlaga a90 on a.id = a90.id
        and datediff( ifnull( a90.paid_date, sysdate() ) , a90.created_date ) > 90
        and a90.pay_type = 1
        group by d.name 
    """
    row_counter = 0
    row_num += 3
    niit_dun = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    try:
        avlagas = Avlaga.objects.raw(qry)
        if avlagas is not None:
            row_style.alignment.horz = xlwt.Alignment.HORZ_RIGHT
            for avlaga in avlagas:
                row_counter += 1
                ws.write(row_num, 0, row_counter, row_style)
                ws.write(row_num, 1, avlaga.name, row_style)
                niit_dun[0] += avlaga.too
                ws.write(row_num, 2, avlaga.too, row_style)
                niit_dun[1] += avlaga.avlaga_dun
                ws.write(row_num, 3, '{0:.2f}'.format(avlaga.avlaga_dun), row_style)
                niit_dun[2] += avlaga.teg_guch_too
                ws.write(row_num, 4, avlaga.teg_guch_too, row_style)
                niit_dun[3] += avlaga.teg_guch
                ws.write(row_num, 5, '{0:.2f}'.format(avlaga.teg_guch), row_style)
                niit_dun[4] += avlaga.guch_jar_too
                ws.write(row_num, 6, avlaga.guch_jar_too, row_style)
                niit_dun[5] += avlaga.guch_jar
                ws.write(row_num, 7, '{0:.2f}'.format(avlaga.guch_jar), row_style)
                niit_dun[6] += avlaga.jar_yer_too
                ws.write(row_num, 8, avlaga.jar_yer_too, row_style)
                niit_dun[7] += avlaga.jar_yer
                ws.write(row_num, 9, avlaga.jar_yer, row_style)
                niit_dun[8] += avlaga.yer_deesh_too
                ws.write(row_num, 10, avlaga.yer_deesh_too, row_style)
                niit_dun[9] += avlaga.yer_deesh
                ws.write(row_num, 11, avlaga.yer_deesh, row_style)
                row_num += 1
    except ObjectDoesNotExist as e:
        logging.error('"Avlaga" object has no objects: %s', e)
    header_style.alignment.horz = xlwt.Alignment.HORZ_RIGHT
    ws.col(3).width = 4000
    ws.write(row_num, 0, '', header_style)
    ws.write(row_num, 1, 'Нийт', header_style)
    ws.write(row_num, 2, niit_dun[0], header_style)
    ws.write(row_num, 3, '{0:.2f}'.format(niit_dun[1]), header_style)
    ws.write(row_num, 4, niit_dun[2], header_style)
    ws.write(row_num, 5, '{0:.2f}'.format(niit_dun[3]), header_style)
    ws.write(row_num, 6, niit_dun[4], header_style)
    ws.write(row_num, 7, '{0:.2f}'.format(niit_dun[5]), header_style)
    ws.write(row_num, 8, niit_dun[6], header_style)
    ws.write(row_num, 9, niit_dun[7], header_style)
    ws.write(row_num, 10, niit_dun[8], header_style)
    ws.write(row_num, 11, niit_dun[9], header_style)

    wb.save(response)
    return response


def report_avlaga_3(request):
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Noogduulsan_aldangi_orson_orlogiin_tailan.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 1, 'Ногдуулсан алданги, алдангиас орсон орлогын тайлан', title_style)
    ws.write(2, 0, 'Борлуулалтын цикл')
    ws.write(3, 0, 'Тайлангийн хамрах хугацаа : ' + start_date + ' - ' + end_date, xlwt.XFStyle())
    ws.write(3, 4, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())

    row_num = 4
    ws.col(0).width = int(12 * 260)
    ws.col(1).width = 9999
    ws.col(2).width = 11111
    ws.write_merge(row_num, row_num, 0, 2, 'Хэрэглэгчийн', header_style)
    ws.write(row_num + 1, 0, 'Код', header_style)
    ws.write(row_num + 1, 1, 'Нэр', header_style)
    ws.write(row_num + 1, 2, 'Хаяг', header_style)
    ws.col(3).width = int(15 * 260)
    ws.col(4).width = int(15 * 260)
    ws.col(5).width = int(15 * 260)
    ws.write_merge(row_num, row_num + 1, 3, 3, 'Ногдуулсан алданги', header_style)
    ws.write_merge(row_num, row_num + 1, 4, 4, 'Алдангиас орсон орлого', header_style)
    ws.write_merge(row_num, row_num + 1, 5, 5, 'Зөрүү', header_style)

    row_num += 1
    qry = """
        select a.*
        , ( orlogo - aldangi ) zuruu
        from (
            SELECT avla.id, cust.code, cust.first_name, cust.last_name, addr.address_name , 
            sum(
                if ( datediff ( sysdate() , avla.tulbur_date )>0 ,
                    ( avla.pay_uld * datediff ( sysdate() , avla.tulbur_date ) / 100 * avla.ald_huvi ) 
                    , 0
                ) 
            ) aldangi
            , IFNULL(SUM(avla.ald_hemjee), 0) orlogo
            FROM data_avlaga avla
            JOIN data_tooluurcustomer tocu ON avla.customer_id=tocu.customer_id
            JOIN data_customer cust ON tocu.customer_id=cust.id
            LEFT JOIN data_paymenthistory pahi ON cust.id=pahi.customer_id
            LEFT JOIN data_address addr ON cust.id=addr.customer_id
            WHERE avla.is_active='1' AND avla.out_of_date='1'
            and avla.created_date between '""" + start_date + " 00:00:00.000000' and '" + end_date + """ 23:59:59.999999' 
            GROUP BY cust.code
        ) a
        where a.aldangi > 0
        """

    niit = [0, 0, 0]

    try:
        avlagas = Avlaga.objects.raw(qry)
        if avlagas is not None:
            for avlaga in avlagas:
                row_num += 1
                ws.write(row_num, 0, avlaga.code, row_style)
                ws.write(row_num, 1, str(avlaga.first_name) + " " + str(avlaga.last_name), row_style)
                ws.write(row_num, 2, avlaga.address_name, row_style)
                niit[0] += round(avlaga.aldangi, 2)
                ws.write(row_num, 3, round(avlaga.aldangi, 2), row_style)
                niit[1] += round(avlaga.orlogo, 2)
                ws.write(row_num, 4, round(avlaga.orlogo, 2), row_style)
                niit[2] += round(avlaga.zuruu, 2)
                ws.write(row_num, 5, round(avlaga.zuruu, 2), row_style)
    except ObjectDoesNotExist as e:
        logging.error('"Avlaga" object has no objects: %s', e)

    row_num += 1
    ws.write_merge(row_num, row_num, 0, 2, 'Дүн: Хэрэглэгчийн тоо : ' + str(row_num - 7), row_style)
    ws.write(row_num, 3, niit[0], row_style)
    ws.write(row_num, 4, niit[1], row_style)
    ws.write(row_num, 5, niit[2], header_style)

    wb.save(response)
    return response


def report_ehzh_1(request):
    year = request.POST['year']
    ex_dir = request.POST['ex_dir']
    dep_man = request.POST['dep_man']
    sale_est_eng = request.POST['sale_est_eng']

    response = HttpResponse(content_type='application/ms-excel')
    response[
        'Content-Disposition'] = 'attachment; filename="Erchim_suljee_XXK_' + year + '_onii_TSEH_heregleenii_butets_borluulaltiin_orlogiin_medee_1.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 4, 'Эрчим сүлжээ ХХК-ийн ' + year + ' оны ЦЭХ-ний хэрэглээний бүтэц, борлуулалтын орлогын мэдээ',
             title_style)
    ws.write(2, 0, 'Хэрэглэгчдэд борлуулах цахилгаан эрчим хүч', title_style)
    ws.write(2, 13, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())

    row_num = 3
    row_widths = [int(5 * 260), int(20 * 260), int(10 * 260), int(10 * 260), int(10 * 260), int(10 * 260),
                  int(10 * 260), int(10 * 260), int(10 * 260), int(10 * 260), int(10 * 260), int(10 * 260),
                  int(10 * 260), int(10 * 260), int(10 * 260), int(12 * 260)]
    for row_width in range(len(row_widths)):
        ws.col(row_width).width = row_widths[row_width]
    ws.write_merge(row_num, row_num + 1, 0, 0, '№', header_style)
    ws.write_merge(row_num, row_num + 1, 1, 1, 'Үзүүлэлт', header_style)
    ws.write_merge(row_num, row_num + 1, 2, 2, 'Хэмжих нэгж', header_style)
    ws.write_merge(row_num, row_num, 3, 15, 'Сараар', header_style)
    months_title = ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар',
                    '10-р сар', '11-р сар', '12-р сар', 'Нийт']
    for i in range(len(months_title)):
        ws.write(row_num + 1, i + 3, months_title[i], header_style)
    ws.write_merge(row_num + 2, row_num + 2, 0, 1, 'Худалдаж авах ЦЭХ', header_style)
    ws.write_merge(row_num + 3, row_num + 3, 0, 1, 'Түгээлтийн алдагдал /хувь/', header_style)
    ws.write_merge(row_num + 4, row_num + 4, 0, 1, 'Түгээлтийн алдагдал /биет/', header_style)
    ws.write_merge(row_num + 5, row_num + 5, 0, 1, 'Борлуулах ЦЭХ', header_style)
    ws.write(row_num + 2, 2, 'мян.кВт.ц', row_style)
    ws.write(row_num + 3, 2, '%', row_style)
    ws.write_merge(row_num + 6, row_num + 6, 0, 1, 'ҮААНБ-ын дүн', header_style)
    ws.write_merge(row_num + 7, row_num + 12, 0, 0, '1.1', header_style)
    ws.write(row_num + 7, 1, 'Бусад ҮААНБ', header_style)
    ws.write(row_num + 8, 1, 'ААН /1 тариф/', header_style)
    ws.write(row_num + 9, 1, 'ААН /3 тариф/', header_style)
    ws.write(row_num + 10, 1, 'Өдрийн /06.00-17.00/', header_style)
    ws.write(row_num + 11, 1, 'Оройн /17.00-22.00/', header_style)
    ws.write(row_num + 12, 1, 'Шөнийн /22.00-06.00/', header_style)
    ws.write(row_num + 13, 0, '1.2', header_style)
    ws.write(row_num + 13, 1, 'Төсөв /1 тариф/', header_style)
    row_num += 14
    ws.write(row_num, 0, '2', header_style)
    ws.write(row_num, 1, 'Ахуйн хэрэглэгч нийт', header_style)
    ws.write_merge(row_num + 1, row_num + 4, 0, 0, '2.1', header_style)
    ws.write(row_num + 1, 1, 'Орон сууц нийт', header_style)
    ws.write(row_num + 2, 1, '/энгийн тоолуур/', header_style)
    ws.write(row_num + 3, 1, '150 кВт.ц хүртэл', header_style)
    ws.write(row_num + 4, 1, '151-с дээш', header_style)
    ws.write_merge(row_num + 5, row_num + 7, 0, 0, '2.1.2', header_style)
    ws.write(row_num + 5, 1, 'Орон сууц /2 тариф/', header_style)
    ws.write(row_num + 6, 1, 'Өдрийн /06.00-21.00/', header_style)
    ws.write(row_num + 7, 1, 'Шөнийн /21.00-06.00/', header_style)

    row_num = 4
    query = [
        "pahi.pay_date>='" + year + "-01-01' AND pahi.pay_date<=LAST_DAY('" + year + "-01-01') LIMIT 1",
        "pahi.pay_date>='" + year + "-02-01' AND pahi.pay_date<=LAST_DAY('" + year + "-02-01') LIMIT 1",
        "pahi.pay_date>='" + year + "-03-01' AND pahi.pay_date<=LAST_DAY('" + year + "-03-01') LIMIT 1",
        "pahi.pay_date>='" + year + "-04-01' AND pahi.pay_date<=LAST_DAY('" + year + "-04-01') LIMIT 1",
        "pahi.pay_date>='" + year + "-05-01' AND pahi.pay_date<=LAST_DAY('" + year + "-05-01') LIMIT 1",
        "pahi.pay_date>='" + year + "-06-01' AND pahi.pay_date<=LAST_DAY('" + year + "-06-01') LIMIT 1",
        "pahi.pay_date>='" + year + "-07-01' AND pahi.pay_date<=LAST_DAY('" + year + "-07-01') LIMIT 1",
        "pahi.pay_date>='" + year + "-08-01' AND pahi.pay_date<=LAST_DAY('" + year + "-08-01') LIMIT 1",
        "pahi.pay_date>='" + year + "-09-01' AND pahi.pay_date<=LAST_DAY('" + year + "-09-01') LIMIT 1",
        "pahi.pay_date>='" + year + "-10-01' AND pahi.pay_date<=LAST_DAY('" + year + "-10-01') LIMIT 1",
        "pahi.pay_date>='" + year + "-11-01' AND pahi.pay_date<=LAST_DAY('" + year + "-11-01') LIMIT 1",
        "pahi.pay_date>='" + year + "-12-01' AND pahi.pay_date<=LAST_DAY('" + year + "-12-01') LIMIT 1",
        "pahi.pay_date>='" + year + "-01-01' AND pahi.pay_date<=LAST_DAY('" + year + "-12-01') LIMIT 1"
    ]
    for i in range(20):
        row_num += 1
        col_num = 3

        if i > 1:
            ws.write(row_num, 2, 'мян.кВт.ц', row_style)

        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, header_style)
        col_num += 1

    row_num = 25
    ws.write(row_num, 0, 'Борлуулалтын орлого', title_style)
    ws.write_merge(row_num + 1, row_num + 2, 0, 0, '№', header_style)
    ws.write_merge(row_num + 1, row_num + 2, 1, 1, 'Үзүүлэлт', header_style)
    ws.write_merge(row_num + 1, row_num + 2, 2, 2, 'Хэмжих нэгж', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 3, 15, 'Сараар', header_style)
    months_title = ['1-р сар', '2-р сар', '3-р сар', '4-р сар', '5-р сар', '6-р сар', '7-р сар', '8-р сар', '9-р сар',
                    '10-р сар', '11-р сар', '12-р сар', 'Нийт']
    for i in range(len(months_title)):
        ws.write(row_num + 2, i + 3, months_title[i], header_style)
    ws.write_merge(row_num + 3, row_num + 3, 0, 1, 'ҮААНБ-ын дүн', header_style)
    ws.write_merge(row_num + 4, row_num + 9, 0, 0, '1.1', header_style)
    ws.write(row_num + 4, 1, 'Бусад ҮААНБ', header_style)
    ws.write(row_num + 5, 1, 'ААН /1 тариф/', header_style)
    ws.write(row_num + 6, 1, 'ААН /3 тариф/', header_style)
    ws.write(row_num + 7, 1, 'Өдрийн /06.00-17.00/', header_style)
    ws.write(row_num + 8, 1, 'Оройн /17.00-22.00/', header_style)
    ws.write(row_num + 9, 1, 'Шөнийн /22.00-06.00/', header_style)
    ws.write(row_num + 10, 0, '1.2', header_style)
    ws.write(row_num + 10, 1, 'Төсөв /1 тариф/', header_style)
    row_num += 11
    ws.write(row_num, 0, '2', header_style)
    ws.write(row_num, 1, 'Ахуйн хэрэглэгч нийт', header_style)
    ws.write_merge(row_num + 1, row_num + 4, 0, 0, '2.1', header_style)
    ws.write(row_num + 1, 1, 'Орон сууц нийт', header_style)
    ws.write(row_num + 2, 1, '/энгийн тоолуур/', header_style)
    ws.write(row_num + 3, 1, '150 кВт.ц хүртэл', header_style)
    ws.write(row_num + 4, 1, '151-с дээш', header_style)
    ws.write_merge(row_num + 5, row_num + 7, 0, 0, '2.1.2', header_style)
    ws.write(row_num + 5, 1, 'Орон сууц /2 тариф/', header_style)
    ws.write(row_num + 6, 1, 'Өдрийн /06.00-21.00/', header_style)
    ws.write(row_num + 7, 1, 'Шөнийн /21.00-06.00/', header_style)
    row_num += 8
    ws.write_merge(row_num, row_num, 0, 1, 'Нийт борлуулалтын орлого', header_style)
    ws.write_merge(row_num + 1, row_num + 6, 0, 0, '', header_style)
    ws.write(row_num + 1, 1, 'Үүнээс: ҮААНБ-ын дүн', header_style)
    ws.write(row_num + 2, 1, 'Ахуйн хэрэглэгчийн дүн', header_style)
    ws.write(row_num + 3, 1, 'Орон сууц', header_style)
    ws.write(row_num + 4, 1, 'Суурь тариф', header_style)
    ws.write(row_num + 5, 1, 'Чадлын орлого', header_style)
    ws.write(row_num + 6, 1, 'Борлуулах ЦЭХ-ний дунд үнэ', header_style)

    qry = "SELECT pahi.id, IFNULL(SUM(pahi.pay_total), 0) AS total FROM data_paymenthistory pahi"
    qry += " JOIN data_customer cust ON pahi.customer_id=cust.id WHERE pahi.is_active='1' AND cust.is_active='1' AND cust.customer_angilal='0' AND "
    row_style.alignment.horz = xlwt.Alignment.HORZ_RIGHT
    header_style.alignment.horz = xlwt.Alignment.HORZ_RIGHT
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(28, 3 + i, '{0:.2f}'.format(history.total), header_style)
                else:
                    ws.write(28, 3 + i, '{0:.2f}'.format(history.total), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(29, 3 + i, '{0:.2f}'.format(history.total), header_style)
                else:
                    ws.write(29, 3 + i, '{0:.2f}'.format(history.total), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = """
        SELECT pahi.id, IFNULL(SUM(pahi.pay_total), 0) AS total 
        FROM data_paymenthistory pahi 
        JOIN data_customer cust ON pahi.customer_id=cust.id
        WHERE pahi.is_active='1' 
        AND cust.is_active='1' 
        and cust.id in (
            select distinct customer_id
            from data_tooluurcustomer tc
            join data_tooluur t on tc.tooluur_id = t.id
            AND t.tariff = 0
            and t.is_active = 1 
        ) 
        AND cust.customer_angilal='0' 
        AND """
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(30, 3 + i, '{0:.2f}'.format(history.total), header_style)
                else:
                    ws.write(30, 3 + i, '{0:.2f}'.format(history.total), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)
    #
    qry = """
            SELECT pahi.id, IFNULL(SUM(pahi.pay_total), 0) AS total 
            FROM data_paymenthistory pahi 
            JOIN data_customer cust ON pahi.customer_id=cust.id
            WHERE pahi.is_active='1' 
            AND cust.is_active='1' 
            and cust.id in (
                select distinct customer_id
                from data_tooluurcustomer tc
                join data_tooluur t on tc.tooluur_id = t.id
                AND t.tariff = 2
                and t.is_active = 1 
            ) 
            AND cust.customer_angilal='0' 
            AND """
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(31, 3 + i, '{0:.2f}'.format(history.total), header_style)
                else:
                    ws.write(31, 3 + i, '{0:.2f}'.format(history.total), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = """
        SELECT pahi.id, IFNULL((SUM(bich.day_diff) * (SELECT odor_une FROM data_pricetariff WHERE une_type='1' AND is_active='1')), 0) AS total
        FROM data_paymenthistory pahi 
        JOIN data_customer cust ON pahi.customer_id=cust.id
        join data_tooluurcustomer tc on cust.id = tc.customer_id 
        join data_tooluur t on tc.tooluur_id = t.id
        JOIN data_bichilt bich ON tc.id=bich.tooluur_id
        WHERE pahi.is_active='1' 
        AND cust.is_active='1' 
        AND cust.customer_angilal='0' 
        and t.tariff = 2
        AND """
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(32, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(32, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = """
        SELECT pahi.id, IFNULL((SUM(bich.rush_diff) * (SELECT orgil_une FROM data_pricetariff WHERE une_type='1' AND is_active='1')), 0) AS total
        FROM data_paymenthistory pahi 
        JOIN data_customer cust ON pahi.customer_id=cust.id
        join data_tooluurcustomer tc on cust.id = tc.customer_id 
        join data_tooluur t on tc.tooluur_id = t.id
        JOIN data_bichilt bich ON tc.id=bich.tooluur_id
        WHERE pahi.is_active='1' 
        AND cust.is_active='1' 
        AND cust.customer_angilal='0' 
        AND """
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(33, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(33, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = """
        SELECT pahi.id, IFNULL((SUM(bich.night_diff) * (SELECT shono_une FROM data_pricetariff WHERE une_type='1' AND is_active='1')), 0) AS total
        FROM data_paymenthistory pahi 
        JOIN data_customer cust ON pahi.customer_id=cust.id 
        join data_tooluurcustomer tc on cust.id = tc.customer_id 
        join data_tooluur t on tc.tooluur_id = t.id
        JOIN data_bichilt bich ON tc.id=bich.tooluur_id
        WHERE pahi.is_active='1' 
        AND cust.is_active='1' 
        AND cust.customer_angilal='0' 
        AND """
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(34, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(34, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)
    # for i in range(13):
    #     if i == 13:
    #         ws.write(30, 3 + i, 0, header_style)
    #     else:
    #         ws.write(30, 3 + i, 0, row_style)
    qry = "SELECT pahi.id, IFNULL(SUM(pahi.pay_total), 0) AS total FROM data_paymenthistory pahi JOIN data_customer cust ON pahi.customer_id=cust.id"
    qry += " WHERE pahi.is_active='1' AND cust.is_active='1' AND cust.customer_angilal='0' AND cust.customer_type='3' AND "
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(35, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(35, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = "SELECT pahi.id, IFNULL(SUM(pahi.pay_total), 0) AS total FROM data_paymenthistory pahi"
    qry += " JOIN data_customer cust ON pahi.customer_id=cust.id WHERE pahi.is_active='1' AND cust.is_active='1' AND cust.customer_angilal='1' AND "
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(36, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(36, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = "SELECT pahi.id, IFNULL(SUM(pahi.pay_total), 0) AS total FROM data_paymenthistory pahi"
    qry += " JOIN data_customer cust ON pahi.customer_id=cust.id WHERE pahi.is_active='1' AND cust.is_active='1' AND cust.customer_angilal='1' AND "
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(37, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(37, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = """
        SELECT pahi.id, IFNULL(SUM(pahi.pay_total), 0) AS total 
        FROM data_paymenthistory pahi 
        JOIN data_customer cust ON pahi.customer_id=cust.id 
        WHERE pahi.is_active='1' 
        AND cust.is_active='1' 
        AND cust.customer_angilal='1' 
        and cust.id in (
                select distinct customer_id
                from data_tooluurcustomer tc
                join data_tooluur t on tc.tooluur_id = t.id
                AND t.tariff = 0
                and t.is_active = 1 
            ) 
        AND """
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(38, 3 + i, '{0:.2f}'.format(history.total), header_style)
                else:
                    ws.write(38, 3 + i, '{0:.2f}'.format(history.total), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)
    # for i in range(13):
    #     if i == 13:
    #         ws.write(38, 3 + i, 0, header_style)
    #     else:
    #         ws.write(38, 3 + i, 0, row_style)

    qry = """
        SELECT pahi.id,  IFNULL(SUM(b.day_diff)*(SELECT odor_une FROM data_pricetariff WHERE une_type='0' AND is_active='1'), 0) AS total 
        FROM data_paymenthistory pahi
        JOIN data_customer cust ON pahi.customer_id=cust.id 
        join data_tooluurcustomer tc on cust.id = tc.customer_id
        join data_bichilt b on tc.id = b.tooluur_id
        and b.day_diff < 150
        WHERE pahi.is_active='1' 
        AND cust.is_active='1' 
        AND cust.customer_angilal='1' 
        AND """
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(39, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(39, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = "SELECT pahi.id, IF(IFNULL(SUM(pahi.pay_total), 0)>=150, IFNULL(SUM(pahi.pay_total), 0), 0) AS total FROM data_paymenthistory pahi"
    qry += " JOIN data_customer cust ON pahi.customer_id=cust.id WHERE pahi.is_active='1' AND cust.is_active='1' AND cust.customer_angilal='1' AND "
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(40, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(40, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = """
        SELECT pahi.id, IFNULL(SUM(pahi.pay_total), 0) AS total 
        FROM data_paymenthistory pahi 
        JOIN data_customer cust ON pahi.customer_id=cust.id 
        WHERE pahi.is_active='1' 
        AND cust.is_active='1' 
        AND cust.customer_angilal='1' 
        and cust.id in (
                select distinct customer_id
                from data_tooluurcustomer tc
                join data_tooluur t on tc.tooluur_id = t.id
                AND t.tariff = 1
                and t.is_active = 1 
            ) 
        AND """
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(41, 3 + i, '{0:.2f}'.format(history.total), header_style)
                else:
                    ws.write(41, 3 + i, '{0:.2f}'.format(history.total), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = """
        SELECT pahi.id, IFNULL((SUM(bich.day_diff) * (SELECT odor_une FROM data_pricetariff WHERE une_type='0' AND is_active='1')), 0) AS total
        FROM data_paymenthistory pahi 
        JOIN data_customer cust ON pahi.customer_id=cust.id 
        join data_tooluurcustomer tc on cust.id = tc.customer_id
        JOIN data_bichilt bich ON tc.id=bich.tooluur_id
        join data_tooluur t on tc.tooluur_id = t.id
        and t.tariff = 1
        WHERE pahi.is_active='1' 
        AND cust.is_active='1' 
        AND cust.customer_angilal='1' 
        AND """
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(42, 3 + i, '{0:.2f}'.format(history.total), header_style)
                else:
                    ws.write(42, 3 + i, '{0:.2f}'.format(history.total), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = """
        SELECT pahi.id, IFNULL((SUM(bich.night_diff) * (SELECT shono_une FROM data_pricetariff WHERE une_type='0' AND is_active='1')), 0) AS total
        FROM data_paymenthistory pahi 
        JOIN data_customer cust ON pahi.customer_id=cust.id 
        join data_tooluurcustomer tc on cust.id = tc.customer_id
        JOIN data_bichilt bich ON tc.id=bich.tooluur_id
        join data_tooluur t on tc.tooluur_id = t.id
        and t.tariff = 1
        WHERE pahi.is_active='1' 
        AND cust.is_active='1' 
        AND cust.customer_angilal='1' 
        AND """
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(43, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(43, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)
    qry = "SELECT pahi.id, IFNULL(SUM(pahi.pay_total), 0) AS total FROM data_paymenthistory pahi"
    qry += " JOIN data_customer cust ON pahi.customer_id=cust.id WHERE pahi.is_active='1' AND cust.is_active='1' AND "
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(44, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(44, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = "SELECT pahi.id, IFNULL(SUM(pahi.pay_total), 0) AS total FROM data_paymenthistory pahi"
    qry += " JOIN data_customer cust ON pahi.customer_id=cust.id WHERE pahi.is_active='1' AND cust.is_active='1' AND cust.customer_angilal='0' AND "
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(45, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(45, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = "SELECT pahi.id, IFNULL(SUM(pahi.pay_total), 0) AS total FROM data_paymenthistory pahi"
    qry += " JOIN data_customer cust ON pahi.customer_id=cust.id WHERE pahi.is_active='1' AND cust.is_active='1' AND cust.customer_angilal='1' AND "
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(46, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(46, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = "SELECT pahi.id, IFNULL(SUM(pahi.pay_total), 0) AS total FROM data_paymenthistory pahi"
    qry += " JOIN data_customer cust ON pahi.customer_id=cust.id WHERE pahi.is_active='1' AND cust.is_active='1' AND cust.customer_angilal='1' AND "
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(47, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(47, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = "SELECT pahi.id, IFNULL(SUM(bich.suuri_price), 0) AS total FROM data_paymenthistory pahi JOIN data_tooluurcustomer tocu ON pahi.customer_id=tocu.tooluur_id"
    qry += " JOIN data_bichilt bich ON tocu.tooluur_id = bich.tooluur_id JOIN data_customer cust ON tocu.customer_id=cust.id WHERE pahi.is_active='1'"
    qry += " AND tocu.is_active='1' AND bich.is_active='1' AND cust.customer_angilal='1' AND "
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(48, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(48, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    qry = "SELECT pahi.id, IFNULL(SUM(bich.chadal_price), 0) AS total FROM data_paymenthistory pahi JOIN data_tooluurcustomer tocu ON pahi.customer_id=tocu.tooluur_id"
    qry += " JOIN data_bichilt bich ON tocu.tooluur_id = bich.tooluur_id JOIN data_customer cust ON tocu.customer_id=cust.id WHERE pahi.is_active='1'"
    qry += " AND tocu.is_active='1' AND bich.is_active='1' AND cust.customer_angilal='0' AND "
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(49, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(49, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)
    qry = "SELECT pahi.id, IFNULL((SUM(pahi.pay_total)/2), 0) AS total FROM data_paymenthistory pahi"
    qry += " JOIN data_customer cust ON pahi.customer_id=cust.id WHERE pahi.is_active='1' AND cust.is_active='1' AND "
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(qry + query[i])
            for history in histories:
                if i == (len(query) - 1):
                    ws.write(50, 3 + i, round(history.total, 2), header_style)
                else:
                    ws.write(50, 3 + i, round(history.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)

    row_num = 27
    for i in range(23):
        row_num += 1
        ws.write(row_num, 2, 'мян.төг', row_style)

    row_num += 2
    ws.write_merge(row_num, row_num, 3, 12, 'Гүйцэтгэх захирал: ......................... /' + ex_dir + '/', text_style)
    row_num += 2
    ws.write_merge(row_num, row_num, 3, 12, 'Албаны менежер: ......................... /' + dep_man + '/', text_style)
    row_num += 2
    ws.write_merge(row_num, row_num, 3, 12,
                   'Борлуулалт тооцооны ахлах инженер: ......................... /' + sale_est_eng + '/', text_style)
    ws.col(10).width = 4000
    ws.col(15).width = 4000
    wb.save(response)
    return response


def report_ehzh_6_old(request):
    year = request.POST['year']
    ex_dir = request.POST['ex_dir']
    dep_man = request.POST['dep_man']
    sale_est_eng = request.POST['sale_est_eng']

    response = HttpResponse(content_type='application/ms-excel')
    response[
        'Content-Disposition'] = 'attachment; filename="Erchim_suljee_XXK_' + year + '_onii_TSEH_heregleenii_butets_borluulaltiin_orlogiin_medee_2.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 4, 'Эрчим сүлжээ ХХК-ийн ' + year + ' оны ЦЭХ-ний хэрэглээний бүтэц, борлуулалтын орлогын мэдээ',
             title_style)
    ws.write(2, 0, 'Хэрэглэгчдэд борлуулах цахилгаан эрчим хүч', title_style)
    ws.write(2, 14, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())

    row_num = 3
    row_widths = [int(5 * 260), int(5 * 260), int(5 * 260), int(35 * 260), int(5 * 260), int(15 * 260), int(15 * 260),
                  int(15 * 260), int(15 * 260), int(15 * 260), int(15 * 260), int(15 * 260), int(15 * 260),
                  int(15 * 260), int(15 * 260), int(15 * 260)]
    for row_width in range(len(row_widths)):
        ws.col(row_width).width = row_widths[row_width]
    ws.write_merge(row_num, row_num + 2, 0, 0, '№', header_style)
    ws.write_merge(row_num, row_num + 2, 1, 3, 'Үзүүлэлт', header_style)
    ws.write_merge(row_num, row_num + 2, 4, 4, 'Мөрийн дугаар', rotate_style)
    ws.write_merge(row_num, row_num + 2, 5, 5, 'Мөрдөж буй тариф / төг/кВтц /', header_style)
    ws.write_merge(row_num, row_num + 1, 6, 7, 'Өмнөх оны мөн үеийн гүйцэтгэл', header_style)
    ws.write(row_num + 2, 6, 'Борлуулсан цахилгаан /мян.кВтц/', header_style)
    ws.write(row_num + 2, 7, 'Борлуулалтын орлого /саятөгрөг/', header_style)
    ws.write_merge(row_num, row_num, 8, 11, 'Тухайн улирлын', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 8, 9, 'төлөвлөгөө', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 10, 11, 'гүйцэтгэл', header_style)
    ws.write(row_num + 2, 8, 'Борлуулсан цахилгаан /мян.кВтц/', header_style)
    ws.write(row_num + 2, 9, 'Борлуулалтын орлого /саятөгрөг/', header_style)
    ws.write(row_num + 2, 10, 'Борлуулсан цахилгаан /мян.кВтц/', header_style)
    ws.write(row_num + 2, 11, 'Борлуулалтын орлого /саятөгрөг/', header_style)
    ws.write_merge(row_num, row_num, 12, 15, 'Өссөн дүнгээр', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 12, 13, 'төлөвлөгөө', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 14, 15, 'гүйцэтгэл', header_style)
    ws.write(row_num + 2, 12, 'Борлуулсан цахилгаан /мян.кВтц/', header_style)
    ws.write(row_num + 2, 13, 'Борлуулалтын орлого /саятөгрөг/', header_style)
    ws.write(row_num + 2, 14, 'Борлуулсан цахилгаан /мян.кВтц/', header_style)
    ws.write(row_num + 2, 15, 'Борлуулалтын орлого /саятөгрөг/', header_style)
    row_num += 3
    ws.write_merge(row_num, row_num, 0, 4, 'Нийт', header_style)
    ws.write(row_num + 1, 0, '1', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 1, 3, 'Үйлдвэрлэлийн байгууллага', header_style)
    for i in range(43):
        ws.write(row_num + i + 1, 4, i + 1, row_style)
    ws.write(row_num + 2, 0, '1.1', row_style)
    ws.write_merge(row_num + 3, row_num + 6, 0, 0, '1.2', row_style)
    ws.write(row_num + 2, 1, '', row_style)
    ws.write(row_num + 3, 1, '', row_style)
    ws.write_merge(row_num + 2, row_num + 2, 2, 3, 'ААН / 1 тариф /', row_style)
    ws.write_merge(row_num + 3, row_num + 3, 2, 3, 'ААН / 3 тариф /', row_style)
    ws.write_merge(row_num + 4, row_num + 4, 1, 2, '', row_style)
    ws.write_merge(row_num + 5, row_num + 5, 1, 2, '', row_style)
    ws.write_merge(row_num + 6, row_num + 6, 1, 2, '', row_style)
    ws.write(row_num + 4, 3, '- Өдрийн ачааллын /06.00-17.00/', row_style)
    ws.write(row_num + 5, 3, '- Оройн оргил ачааллын /17.00-22.00/', row_style)
    ws.write(row_num + 6, 3, '- Шөнийн бага ачааллын /22.00-06.00/', row_style)
    ws.write_merge(row_num + 7, row_num + 9, 0, 0, '1.3', row_style)
    ws.write(row_num + 7, 1, '', row_style)
    ws.write_merge(row_num + 7, row_num + 7, 2, 3, 'Гудамжны гэрэлтүүлэг / 2 тарифт /', row_style)
    ws.write_merge(row_num + 8, row_num + 8, 1, 2, '', row_style)
    ws.write_merge(row_num + 9, row_num + 9, 1, 2, '', row_style)
    ws.write(row_num + 8, 3, '- Өдрийн /06.00-19.00/', row_style)
    ws.write(row_num + 9, 3, '- Шөнийн /19.00-06.00/', row_style)
    ws.write_merge(row_num + 10, row_num + 12, 0, 0, '1.4', row_style)
    ws.write(row_num + 10, 1, '', row_style)
    ws.write_merge(row_num + 10, row_num + 10, 2, 3, 'СӨХ-ийн гэрэлтүүлэг / 2 тарифт /', row_style)
    ws.write_merge(row_num + 11, row_num + 11, 1, 2, '', row_style)
    ws.write_merge(row_num + 12, row_num + 12, 1, 2, '', row_style)
    ws.write(row_num + 11, 3, '- Өдрийн /06.00-19.00/', row_style)
    ws.write(row_num + 12, 3, '- Шөнийн /19.00-06.00/', row_style)
    ws.write(row_num + 13, 1, '', row_style)
    ws.write(row_num + 13, 0, '1.5', row_style)
    ws.write_merge(row_num + 13, row_num + 13, 2, 3, 'Цахилгаан тээвэр', row_style)
    ws.write(row_num + 14, 1, '', row_style)
    ws.write(row_num + 14, 0, '1.6', row_style)
    ws.write_merge(row_num + 14, row_num + 14, 2, 3, 'Төмөр зам', row_style)
    ws.write(row_num + 15, 0, '2', header_style)
    ws.write_merge(row_num + 15, row_num + 15, 1, 3, 'Худалдаа, үйлчилгээний байгууллага', header_style)
    ws.write(row_num + 16, 0, '2.1', row_style)
    ws.write_merge(row_num + 17, row_num + 20, 0, 0, '2.2', row_style)
    ws.write(row_num + 16, 1, '', row_style)
    ws.write(row_num + 17, 1, '', row_style)
    ws.write_merge(row_num + 16, row_num + 16, 2, 3, 'ААН / 1 тариф /', row_style)
    ws.write_merge(row_num + 17, row_num + 17, 2, 3, 'ААН / 3 тариф /', row_style)
    ws.write_merge(row_num + 18, row_num + 18, 1, 2, '', row_style)
    ws.write_merge(row_num + 19, row_num + 19, 1, 2, '', row_style)
    ws.write_merge(row_num + 20, row_num + 20, 1, 2, '', row_style)
    ws.write(row_num + 18, 3, '- Өдрийн ачааллын /06.00-17.00/', row_style)
    ws.write(row_num + 19, 3, '- Оройн оргил ачааллын /17.00-22.00/', row_style)
    ws.write(row_num + 20, 3, '- Шөнийн бага ачааллын /22.00-06.00/', row_style)
    ws.write_merge(row_num + 21, row_num + 23, 0, 0, '2.3', row_style)
    ws.write(row_num + 21, 1, '', row_style)
    ws.write_merge(row_num + 21, row_num + 21, 2, 3, 'Гудамжны гэрэлтүүлэг / 2 тарифт /', row_style)
    ws.write_merge(row_num + 22, row_num + 22, 1, 2, '', row_style)
    ws.write_merge(row_num + 23, row_num + 23, 1, 2, '', row_style)
    ws.write(row_num + 22, 3, '- Өдрийн /06.00-19.00/', row_style)
    ws.write(row_num + 23, 3, '- Шөнийн /19.00-06.00/', row_style)
    ws.write_merge(row_num + 24, row_num + 26, 0, 0, '2.4', row_style)
    ws.write(row_num + 24, 1, '', row_style)
    ws.write_merge(row_num + 24, row_num + 24, 2, 3, 'СӨХ-ийн гэрэлтүүлэг / 2 тарифт /', row_style)
    ws.write_merge(row_num + 25, row_num + 25, 1, 2, '', row_style)
    ws.write_merge(row_num + 26, row_num + 26, 1, 2, '', row_style)
    ws.write(row_num + 25, 3, '- Өдрийн /06.00-19.00/', row_style)
    ws.write(row_num + 26, 3, '- Шөнийн /19.00-06.00/', row_style)
    ws.write(row_num + 27, 1, '', row_style)
    ws.write(row_num + 27, 0, '2.5', row_style)
    ws.write_merge(row_num + 27, row_num + 27, 2, 3, 'Цахилгаан тээвэр', row_style)
    ws.write(row_num + 28, 1, '', row_style)
    ws.write(row_num + 28, 0, '2.6', row_style)
    ws.write_merge(row_num + 28, row_num + 28, 2, 3, 'Төмөр зам', row_style)
    ws.write(row_num + 29, 1, '', row_style)
    ws.write(row_num + 29, 0, '2.7', row_style)
    ws.write_merge(row_num + 29, row_num + 29, 2, 3, '...', row_style)
    row_num += 30
    ws.write(row_num, 0, '3', header_style)
    ws.write_merge(row_num, row_num, 1, 3, 'Оршин суугч, ахуйн хэрэглэгч - Орон сууц', header_style)
    ws.write(row_num + 1, 0, '3.1', row_style)
    ws.write(row_num + 1, 1, '', row_style)
    ws.write_merge(row_num + 1, row_num + 1, 2, 3, 'Орон сууц / 1 тариф /', row_style)
    ws.write_merge(row_num + 2, row_num + 4, 0, 0, '3.2', row_style)
    ws.write(row_num + 2, 1, '', row_style)
    ws.write_merge(row_num + 2, row_num + 2, 2, 3, 'Орон сууц / 2 тариф /', row_style)
    ws.write_merge(row_num + 3, row_num + 3, 1, 2, '', row_style)
    ws.write_merge(row_num + 4, row_num + 4, 1, 2, '', row_style)
    ws.write(row_num + 3, 3, '- Өдрийн /06.00-19.00/', row_style)
    ws.write(row_num + 4, 3, '- Шөнийн /19.00-06.00/', row_style)
    ws.write(row_num + 5, 0, '3.3', row_style)
    ws.write(row_num + 6, 0, '3.4', row_style)
    ws.write(row_num + 5, 1, '', row_style)
    ws.write(row_num + 6, 1, '', row_style)
    ws.write_merge(row_num + 5, row_num + 5, 2, 3, 'Суурь хураамж', row_style)
    ws.write_merge(row_num + 6, row_num + 6, 2, 3, '...', row_style)
    ws.write_merge(row_num + 7, row_num + 13, 0, 0, '4', header_style)
    ws.write_merge(row_num + 7, row_num + 7, 1, 3, 'Оршин суугч, ахуйн хэрэглэгч - Гэр хороолол', header_style)
    ws.write(row_num + 8, 1, '', row_style)
    ws.write_merge(row_num + 8, row_num + 8, 2, 3, 'Орон сууц / 1 тариф /', row_style)
    ws.write(row_num + 9, 1, '', row_style)
    ws.write_merge(row_num + 9, row_num + 9, 2, 3, 'Орон сууц / 2 тариф /', row_style)
    ws.write_merge(row_num + 10, row_num + 10, 1, 2, '', row_style)
    ws.write_merge(row_num + 11, row_num + 11, 1, 2, '', row_style)
    ws.write(row_num + 10, 3, '- Өдрийн /06.00-19.00/', row_style)
    ws.write(row_num + 11, 3, '- Шөнийн /19.00-06.00/', row_style)
    ws.write(row_num + 12, 1, '', row_style)
    ws.write_merge(row_num + 12, row_num + 12, 2, 3, 'Дэмжих тариф', row_style)
    ws.write(row_num + 13, 1, '', row_style)
    ws.write_merge(row_num + 13, row_num + 13, 2, 3, 'Чадлын төлбөр', row_style)
    ws.write(row_num + 15, 0, '5', header_style)
    ws.write_merge(row_num + 15, row_num + 15, 1, 3, 'Борлуулалтын дундаж тариф / төг/кВтц /', header_style)
    ws.write(row_num + 15, 4, 44, row_style)
    ws.write_merge(row_num + 17, row_num + 25, 0, 0, '6', header_style)
    ws.write_merge(row_num + 17, row_num + 17, 1, 3, 'Төвлөрүүлсэн орлого /сая төгрөг/', header_style)
    for i in range(9):
        ws.write(row_num + i + 17, 4, i + 45, row_style)
    ws.write(row_num + 18, 1, '', row_style)
    ws.write(row_num + 19, 1, '', row_style)
    ws.write_merge(row_num + 18, row_num + 18, 2, 3, 'Үүнээс: ЦДҮС ТӨХК-д', row_style)
    ws.write_merge(row_num + 19, row_num + 19, 2, 3, 'Бусад /хуучин өр барагдуулахад /', row_style)
    ws.write_merge(row_num + 20, row_num + 25, 1, 1, '', row_style)
    ws.write_merge(row_num + 20, row_num + 25, 2, 2, 'Үүнд:', row_style)
    ws.write_merge(row_num + 20, row_num + 20, 3, 3, 'ДЦС-2', row_style)
    ws.write_merge(row_num + 21, row_num + 21, 3, 3, 'ДЦС-3', row_style)
    ws.write_merge(row_num + 22, row_num + 22, 3, 3, 'ДЦС-4', row_style)
    ws.write_merge(row_num + 23, row_num + 23, 3, 3, 'ДДЦС', row_style)
    ws.write_merge(row_num + 24, row_num + 24, 3, 3, 'ЭДЦС', row_style)
    ws.write_merge(row_num + 25, row_num + 25, 3, 3, '...', row_style)

    row_num = 6
    for i in range(44):
        if i == 0:
            ws.write(row_num + i, 5, 0, header_style)
            ws.write(row_num + i, 6, 0, header_style)
            ws.write(row_num + i, 7, 0, header_style)
            ws.write(row_num + i, 8, 0, header_style)
            ws.write(row_num + i, 9, 0, header_style)
            ws.write(row_num + i, 10, 0, header_style)
            ws.write(row_num + i, 11, 0, header_style)
            ws.write(row_num + i, 12, 0, header_style)
            ws.write(row_num + i, 13, 0, header_style)
            ws.write(row_num + i, 14, 0, header_style)
            ws.write(row_num + i, 15, 0, header_style)
        else:
            ws.write(row_num + i, 5, 0, row_style)
            ws.write(row_num + i, 6, 0, row_style)
            ws.write(row_num + i, 7, 0, row_style)
            ws.write(row_num + i, 8, 0, row_style)
            ws.write(row_num + i, 9, 0, row_style)
            ws.write(row_num + i, 10, 0, row_style)
            ws.write(row_num + i, 11, 0, row_style)
            ws.write(row_num + i, 12, 0, row_style)
            ws.write(row_num + i, 13, 0, row_style)
            ws.write(row_num + i, 14, 0, row_style)
            ws.write(row_num + i, 15, 0, row_style)

    for i in range(11):
        ws.write(51, 5 + i, 0, header_style)

    row_num = 53
    for i in range(9):
        ws.write(row_num + i, 5, 0, row_style)
        ws.write(row_num + i, 6, 0, row_style)
        ws.write(row_num + i, 7, 0, row_style)
        ws.write(row_num + i, 8, 0, row_style)
        ws.write(row_num + i, 9, 0, row_style)
        ws.write(row_num + i, 10, 0, row_style)
        ws.write(row_num + i, 11, 0, row_style)
        ws.write(row_num + i, 12, 0, row_style)
        ws.write(row_num + i, 13, 0, row_style)
        ws.write(row_num + i, 14, 0, row_style)
        ws.write(row_num + i, 15, 0, row_style)

    row_num = 64
    ws.write_merge(row_num, row_num, 3, 12, 'Гүйцэтгэх захирал: ......................... /' + ex_dir + '/', text_style)
    row_num += 2
    ws.write_merge(row_num, row_num, 3, 12, 'Албаны менежер: ......................... /' + dep_man + '/', text_style)
    row_num += 2
    ws.write_merge(row_num, row_num, 3, 12,
                   'Борлуулалт тооцооны ахлах инженер: ......................... /' + sale_est_eng + '/', text_style)

    wb.save(response)
    return response


def report_ehzh_2(request):
    year = request.POST['year']
    season = request.POST['season']
    ex_dir = request.POST['ex_dir']
    dep_man = request.POST['dep_man']
    sale_est_eng = request.POST['sale_est_eng']

    response = HttpResponse(content_type='application/ms-excel')
    response[
        'Content-Disposition'] = 'attachment; filename="Tsahilgaan_tugeeh_TZE_Erchim_suljee_XXK_' + year + '_onii_' + season + '_ulirliin_borluulaltiin_medee.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 1,
             'Цахилгаан түгээх, хангах ТЗЭ Эрчим сүлжээ ХХК-ийн ' + year + ' оны ' + season + '-р улирлын борлуулалтын мэдээ',
             title_style)
    ws.write(2, 0, 'А. Хэрэглэгчдийн тоо, хэрэглээний бүтэц', title_style)
    ws.write(2, 6, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())

    row_num = 3
    row_widths = [int(5 * 260), int(10 * 260), int(10 * 260), int(15 * 260), int(5 * 260), int(10 * 260), int(10 * 260),
                  int(10 * 260), int(10 * 260)]
    for row_width in range(len(row_widths)):
        ws.col(row_width).width = row_widths[row_width]
    ws.row(3).height_mismatch = True
    ws.row(3).height = int(2 * 260)
    ws.row(4).height_mismatch = True
    ws.row(4).height = int(2 * 260)
    ws.write_merge(row_num, row_num + 1, 0, 0, '№', header_style)
    ws.write_merge(row_num, row_num + 1, 1, 3, 'Үзүүлэлт', header_style)
    ws.write_merge(row_num, row_num + 1, 4, 4, 'Мөрийн дугаар', rotate_style)
    ws.write_merge(row_num, row_num, 5, 6, 'Тухайн улирлын', header_style)
    ws.write(row_num + 1, 5, 'Хэрэглэгч /тоо/', header_style)
    ws.write(row_num + 1, 6, 'Хэрэглээ /мян.кВтц/', header_style)
    ws.write_merge(row_num, row_num, 7, 8, 'Өссөн дүнгээр', header_style)
    ws.write(row_num + 1, 7, 'Хэрэглэгч /тоо/', header_style)
    ws.write(row_num + 1, 8, 'Хэрэглээ /мян.кВтц/', header_style)
    row_num += 2
    ws.write_merge(row_num, row_num + 4, 0, 0, '1', header_style)
    ws.write_merge(row_num, row_num, 1, 3, 'Үйлдвэрлэлийн байгууллага', header_style)
    ws.write_merge(row_num + 1, row_num + 4, 1, 1, 'Үүнээс :', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 2, 3, '110 кВ', header_style)
    ws.write_merge(row_num + 2, row_num + 2, 2, 3, '35 кВ', header_style)
    ws.write_merge(row_num + 3, row_num + 3, 2, 3, '10/6 кВ', header_style)
    ws.write_merge(row_num + 4, row_num + 4, 2, 3, '0.4 кВ', header_style)
    for i in range(17):
        ws.write(row_num + i, 4, i + 1, header_style)
    row_num += 5
    ws.write_merge(row_num, row_num, 1, 3, 'Худалдаа, үйлчилгээний байгууллага', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 1, 3, 'Төсвийн байгууллага', header_style)
    ws.write_merge(row_num + 2, row_num + 2, 1, 3, 'Оршин суугч, ахуйн хэрэглэгчид', header_style)
    ws.write(row_num, 0, '2', header_style)
    ws.write(row_num + 1, 0, '3', header_style)
    ws.write_merge(row_num + 2, row_num + 8, 0, 0, '4', header_style)
    ws.write_merge(row_num + 3, row_num + 8, 1, 1, 'Үүнээс :', header_style)
    ws.write_merge(row_num + 3, row_num + 4, 2, 2, 'Орон сууц', header_style)
    ws.write_merge(row_num + 5, row_num + 6, 2, 2, 'Гэр хороолол', header_style)
    ws.write(row_num + 3, 3, '100 кВтц хүртэл', header_style)
    ws.write(row_num + 4, 3, '100 кВтц буюу түүнээс дээш', header_style)
    ws.write(row_num + 5, 3, '100 кВтц хүртэл', header_style)
    ws.write(row_num + 6, 3, '100 кВтц буюу түүнээс дээш', header_style)
    ws.write_merge(row_num + 7, row_num + 7, 2, 3, 'Эмзэг бүлгийн хэрэглэгчид', header_style)
    ws.write_merge(row_num + 8, row_num + 8, 2, 3, 'Цагийн ялгаварт тоолууртай хэрэглэгчид', header_style)
    ws.row(row_num + 8).height_mismatch = True
    ws.row(row_num + 8).height = int(2 * 260)
    row_num += 9
    ws.write_merge(row_num, row_num, 1, 3, 'Гудамжны гэрэлтүүлэг', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 1, 3, 'СӨХ-ны эзэмшлийн талбайн гэрэлтүүлэг ', header_style)
    ws.write_merge(row_num + 2, row_num + 2, 1, 3, 'НИЙТ', header_style)
    ws.write(row_num, 0, '5', header_style)
    ws.write(row_num + 1, 0, '6', header_style)
    ws.write(row_num + 2, 0, '7', header_style)

    qry = "SELECT bich.id, COUNT(cust.code) AS too, IF(SUM(bich.total_diff) IS NULL, 0, SUM(bich.total_diff)) AS hereglee FROM data_bichilt bich"
    qry += " JOIN data_tooluurcustomer tocu ON bich.tooluur_id=tocu.tooluur_id"
    qry += " JOIN data_tooluur tool ON tocu.tooluur_id=tool.id"
    qry += " JOIN data_customer cust ON tocu.customer_id=cust.id WHERE bich.is_active='1' AND tocu.is_active='1' AND tool.is_active='1' AND cust.is_active='1' AND "

    start_month = end_month = 0
    if season == '1':
        start_month = 1
        end_month = 3
    elif season == '2':
        start_month = 4
        end_month = 6
    elif season == '3':
        start_month = 7
        end_month = 9
    elif season == '4':
        start_month = 10
        end_month = 12

    def get_last_day(the_year, the_month):
        month_last_day = str(monthrange(int(the_year), int(the_month))).split(',')
        month_last_day = str(month_last_day[1].replace(' ', '').replace(')', ''))
        return month_last_day

    niit = [0, 0, 0, 0]
    try:
        start_date = year + '-' + str(start_month) + '-01'
        end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
        query = qry + " cust.customer_angilal='0' AND cust.customer_type='2' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
        bichilts = Bichilt.objects.raw(query)
        for bichilt in bichilts:
            ws.write(5, 5, bichilt.too if bichilt.too else 0, row_style)
            ws.write(5, 6, round(bichilt.hereglee, 2), row_style)
            niit[0] += bichilt.too if bichilt.too else 0
            niit[1] += round(bichilt.hereglee, 2)
            niit[2] += bichilt.too if bichilt.too else 0
            if season == '1':
                ws.write(5, 7, bichilt.too if bichilt.too else 0, row_style)
                ws.write(5, 8, round(bichilt.hereglee, 2), row_style)
                niit[3] += round(bichilt.hereglee, 2)
            if season == '2':
                start_month = 1
                end_month = 3
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + "cust.customer_angilal='0' AND cust.customer_type='2' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt2s = Bichilt.objects.raw(query)
                for bichilt2 in bichilt2s:
                    ws.write(5, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(5, 8, round(bichilt.hereglee, 2) + round(bichilt2.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt2.hereglee, 2)
            if season == '3':
                start_month = 4
                end_month = 6
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + " cust.customer_angilal='0' AND cust.customer_type='2' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt3s = Bichilt.objects.raw(query)
                for bichilt3 in bichilt3s:
                    ws.write(5, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(5, 8, round(bichilt.hereglee, 2) + round(bichilt3.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt3.hereglee, 2)
            if season == '4':
                start_month = 7
                end_month = 9
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + " cust.customer_angilal='0' AND cust.customer_type='2' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt4s = Bichilt.objects.raw(query)
                for bichilt4 in bichilt4s:
                    ws.write(5, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(5, 8, round(bichilt.hereglee, 2) + round(bichilt4.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt4.hereglee, 2)
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" model has no object: %s', e)
    try:
        start_date = year + '-' + str(start_month) + '-01'
        end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
        query = qry + " cust.customer_angilal='0' AND cust.customer_type='1' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
        bichilts = Bichilt.objects.raw(query)
        for bichilt in bichilts:
            ws.write(10, 5, bichilt.too if bichilt.too else 0, row_style)
            ws.write(10, 6, round(bichilt.hereglee, 2), row_style)
            niit[0] += bichilt.too if bichilt.too else 0
            niit[1] += round(bichilt.hereglee, 2)
            niit[2] += bichilt.too if bichilt.too else 0
            if season == '1':
                ws.write(10, 7, bichilt.too if bichilt.too else 0, row_style)
                ws.write(10, 8, round(bichilt.hereglee, 2), row_style)
                niit[3] += round(bichilt.hereglee, 2)
            if season == '2':
                start_month = 1
                end_month = 3
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + " cust.customer_angilal='0' AND cust.customer_type='1' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt2s = Bichilt.objects.raw(query)
                for bichilt2 in bichilt2s:
                    ws.write(10, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(10, 8, round(bichilt.hereglee, 2) + round(bichilt2.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt2.hereglee, 2)
            if season == '3':
                start_month = 4
                end_month = 6
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + "cust.customer_angilal='0' AND cust.customer_type='1' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt3s = Bichilt.objects.raw(query)
                for bichilt3 in bichilt3s:
                    ws.write(10, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(10, 8, round(bichilt.hereglee, 2) + round(bichilt3.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt3.hereglee, 2)
            if season == '4':
                start_month = 7
                end_month = 9
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + " cust.customer_angilal='0' AND cust.customer_type='1' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt4s = Bichilt.objects.raw(query)
                for bichilt4 in bichilt4s:
                    ws.write(10, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(10, 8, round(bichilt.hereglee, 2) + round(bichilt4.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt4.hereglee, 2)
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" model has no object: %s', e)
    try:
        start_date = year + '-' + str(start_month) + '-01'
        end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
        query = qry + " cust.customer_angilal='0' AND cust.customer_type='3' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
        bichilts = Bichilt.objects.raw(query)
        for bichilt in bichilts:
            ws.write(11, 5, bichilt.too if bichilt.too else 0, row_style)
            ws.write(11, 6, round(bichilt.hereglee, 2) if bichilt.hereglee else 0, row_style)
            niit[0] += bichilt.too if bichilt.too else 0
            niit[1] += round(bichilt.hereglee, 2)
            niit[2] += bichilt.too if bichilt.too else 0
            if season == '1':
                ws.write(11, 7, bichilt.too if bichilt.too else 0, row_style)
                ws.write(11, 8, round(bichilt.hereglee, 2), row_style)
                niit[3] += round(bichilt.hereglee, 2)
            if season == '2':
                start_month = 1
                end_month = 3
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + " cust.customer_angilal='0' AND cust.customer_type='3' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt2s = Bichilt.objects.raw(query)
                for bichilt2 in bichilt2s:
                    ws.write(11, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(11, 8, round(bichilt.hereglee, 2) + round(bichilt2.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt2.hereglee, 2)
            if season == '3':
                start_month = 4
                end_month = 6
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + " cust.customer_angilal='0' AND cust.customer_type='3' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt3s = Bichilt.objects.raw(query)
                for bichilt3 in bichilt3s:
                    ws.write(11, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(11, 8, round(bichilt.hereglee, 2) + round(bichilt3.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt3.hereglee, 2)
            if season == '4':
                start_month = 7
                end_month = 9
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + " cust.customer_angilal='0' AND cust.customer_type='3' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt4s = Bichilt.objects.raw(query)
                for bichilt4 in bichilt4s:
                    ws.write(11, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(11, 8, round(bichilt.hereglee, 2) + round(bichilt4.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt4.hereglee, 2)
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" model has no object: %s', e)
    try:
        start_date = year + '-' + str(start_month) + '-01'
        end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
        query = qry + " cust.customer_angilal='1' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
        bichilts = Bichilt.objects.raw(query)
        for bichilt in bichilts:
            ws.write(12, 5, bichilt.too if bichilt.too else 0, row_style)
            ws.write(12, 6, round(bichilt.hereglee, 2) if bichilt.hereglee else 0, row_style)
            niit[0] += bichilt.too if bichilt.too else 0
            niit[1] += round(bichilt.hereglee, 2)
            niit[2] += bichilt.too if bichilt.too else 0
            if season == '1':
                ws.write(12, 7, bichilt.too if bichilt.too else 0, row_style)
                ws.write(12, 8, round(bichilt.hereglee, 2), row_style)
                niit[3] += round(bichilt.hereglee, 2)
            if season == '2':
                start_month = 1
                end_month = 3
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + " cust.customer_angilal='1' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt2s = Bichilt.objects.raw(query)
                for bichilt2 in bichilt2s:
                    ws.write(12, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(12, 8, round(bichilt.hereglee, 2) + round(bichilt2.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt2.hereglee, 2)
            if season == '3':
                start_month = 4
                end_month = 6
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + " cust.customer_angilal='1' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt3s = Bichilt.objects.raw(query)
                for bichilt3 in bichilt3s:
                    ws.write(12, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(12, 8, round(bichilt.hereglee, 2) + round(bichilt3.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt3.hereglee, 2)
            if season == '4':
                start_month = 7
                end_month = 9
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + " cust.customer_angilal='1' AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt4s = Bichilt.objects.raw(query)
                for bichilt4 in bichilt4s:
                    ws.write(12, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(12, 8, round(bichilt.hereglee, 2) + round(bichilt4.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt4.hereglee, 2)
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" model has no object: %s', e)
    try:
        start_date = year + '-' + str(start_month) + '-01'
        end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
        query = qry + " (tool.tariff='1' OR tool.tariff='2') AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
        bichilts = Bichilt.objects.raw(query)
        for bichilt in bichilts:
            ws.write(18, 5, bichilt.too if bichilt.too else 0, row_style)
            ws.write(18, 6, round(bichilt.hereglee, 2) if bichilt.hereglee else 0, row_style)
            niit[0] += bichilt.too if bichilt.too else 0
            niit[1] += round(bichilt.hereglee, 2)
            niit[2] += bichilt.too if bichilt.too else 0
            if season == '1':
                ws.write(18, 7, bichilt.too if bichilt.too else 0, row_style)
                ws.write(18, 8, round(bichilt.hereglee, 2), row_style)
                niit[3] += round(bichilt.hereglee, 2)
            if season == '2':
                start_month = 1
                end_month = 3
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + " (tool.tariff='1' OR tool.tariff='2') AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt2s = Bichilt.objects.raw(query)
                for bichilt2 in bichilt2s:
                    ws.write(18, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(18, 8, round(bichilt.hereglee, 2) + round(bichilt2.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt2.hereglee, 2)
            if season == '3':
                start_month = 4
                end_month = 6
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + " (tool.tariff='1' OR tool.tariff='2') AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt3s = Bichilt.objects.raw(query)
                for bichilt3 in bichilt3s:
                    ws.write(18, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(18, 8, round(bichilt.hereglee, 2) + round(bichilt3.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt3.hereglee, 2)
            if season == '4':
                start_month = 7
                end_month = 9
                start_date = year + '-' + str(start_month) + '-01'
                end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
                query = qry + " (tool.tariff='1' OR tool.tariff='2') AND bich.bichilt_date>='" + start_date + "' AND bich.bichilt_date<='" + end_date + "'"
                bichilt4s = Bichilt.objects.raw(query)
                for bichilt4 in bichilt4s:
                    ws.write(18, 7, bichilt.too if bichilt.too else 0, row_style)
                    ws.write(18, 8, round(bichilt.hereglee, 2) + round(bichilt4.hereglee, 2), row_style)
                    niit[3] += round(bichilt.hereglee, 2) + round(bichilt4.hereglee, 2)
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" model has no object: %s', e)

    for i in range(3):
        ws.write(15 + i, 5, '', row_style)
        ws.write(15 + i, 6, '', row_style)
        ws.write(15 + i, 7, '', row_style)
        ws.write(15 + i, 8, '', row_style)

    for i in range(2):
        ws.write(19 + i, 5, '', row_style)
        ws.write(19 + i, 6, '', row_style)
        ws.write(19 + i, 7, '', row_style)
        ws.write(19 + i, 8, '', row_style)

    ws.write(21, 5, niit[0], header_style)
    ws.write(21, 6, niit[1], header_style)
    ws.write(21, 7, niit[2], header_style)
    ws.write(21, 8, niit[3], header_style)

    ws.write_merge(23, 23, 1, 8, 'Тайлбар: Хэрэглэгчийн холбогдсон хүчдэлийн түвшинг тодорхойлохдоо хэрэглэгчийн',
                   text_style)
    ws.write_merge(24, 24, 1, 8, 'өмчлөлийн шугам, дэд станцын өндөр талын хүчдэлийн түвшингээр тогтооно.', text_style)
    ws.write(26, 0, 'Б. Борлуулалтын орлого', title_style)
    ws.write(26, 8, '/сая төгрөгөөр/', title_style)
    row_num = 27
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = int(2 * 260)
    ws.row(row_num + 1).height_mismatch = True
    ws.row(row_num + 1).height = int(2 * 260)
    ws.write_merge(row_num, row_num + 1, 0, 0, '№', header_style)
    ws.write_merge(row_num, row_num + 1, 1, 3, 'Үзүүлэлт', header_style)
    ws.write_merge(row_num, row_num + 1, 4, 4, 'Мөрийн дугаар', rotate_style)
    ws.write_merge(row_num, row_num + 1, 5, 5, 'Өмнөх оны мөн үеийн гүйцэтгэл', header_style)
    ws.write_merge(row_num, row_num, 6, 7, 'Тухайн улирлын', header_style)
    ws.write(row_num + 1, 6, 'Төлөвлөгөө', header_style)
    ws.write(row_num + 1, 7, 'Гүйцэтгэл', header_style)
    ws.write_merge(row_num, row_num, 8, 9, 'Өссөн дүнгээр', header_style)
    ws.write(row_num + 1, 8, 'Төлөвлөгөө', header_style)
    ws.write(row_num + 1, 9, 'Гүйцэтгэл', header_style)
    row_num += 2
    ws.write_merge(row_num, row_num + 5, 0, 0, 8, header_style)
    ws.write_merge(row_num, row_num, 1, 3, 'Борлуулалтын орлого ', header_style)
    ws.write_merge(row_num + 1, row_num + 5, 1, 1, 'Үүнээс :', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 2, 3, 'Үйлдвэрлэлийн байгууллага', header_style)
    ws.write_merge(row_num + 2, row_num + 2, 2, 3, 'Худалдаа үйлчилгээний байгууллага', header_style)
    ws.write_merge(row_num + 3, row_num + 3, 2, 3, 'Төсвийн байгууллага', header_style)
    ws.write_merge(row_num + 4, row_num + 4, 2, 3, 'Орон сууц', header_style)
    ws.write_merge(row_num + 5, row_num + 5, 2, 3, 'Гэр хороолол', header_style)

    for i in range(6):
        ws.write(29 + i, 4, 18 + i, header_style)

    if season == '1':
        start_month = 1
        end_month = 3
    elif season == '2':
        start_month = 4
        end_month = 6
    elif season == '3':
        start_month = 7
        end_month = 9
    elif season == '4':
        start_month = 10
        end_month = 12

    qry = "SELECT pahi.id, IF(SUM(pahi.pay_total) IS NULL, 0, SUM(pahi.pay_total)) AS niit_orlogo"
    qry += " FROM data_paymenthistory pahi JOIN data_customer cust ON pahi.customer_id=cust.id"
    qry += " WHERE pahi.is_active='1' AND cust.is_active='1' AND "

    start_date = str(int(year) - 1) + '-' + str(start_month) + '-01'
    end_date = str(int(year) - 1) + '-' + str(end_month) + '-' + get_last_day(str(int(year) - 1), end_month)
    query = [qry + " pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'",
             qry + " cust.customer_angilal='0' AND cust.customer_type='2' AND pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'",
             qry + " cust.customer_angilal='0' AND cust.customer_type='1' AND pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'",
             qry + " cust.customer_angilal='0' AND cust.customer_type='3' AND pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'",
             qry + " cust.customer_angilal='1' AND pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'"]
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(query[i])
            for history in histories:
                ws.write(29 + i, 5, round(history.niit_orlogo, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)
    ws.write(34, 5, '', row_style)

    niit_orlogo = [0, 0, 0, 0, 0]
    start_date = year + '-' + str(start_month) + '-01'
    end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
    query = [qry + " pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'",
             qry + " cust.customer_angilal='0' AND cust.customer_type='2' AND pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'",
             qry + " cust.customer_angilal='0' AND cust.customer_type='1' AND pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'",
             qry + " cust.customer_angilal='0' AND cust.customer_type='3' AND pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'",
             qry + " cust.customer_angilal='1' AND pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'"]
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(query[i])
            for history in histories:
                ws.write(29 + i, 7, round(history.niit_orlogo, 2), row_style)
                niit_orlogo[i] += round(history.niit_orlogo, 2)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)
    ws.write(34, 7, '', row_style)

    if season == '1':
        start_month = 1
        end_month = 3
    elif season == '2':
        start_month = 1
        end_month = 3
    elif season == '3':
        start_month = 4
        end_month = 6
    elif season == '4':
        start_month = 7
        end_month = 9

    start_date = year + '-' + str(start_month) + '-01'
    end_date = year + '-' + str(end_month) + '-' + get_last_day(year, end_month)
    query = [qry + " pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'",
             qry + " cust.customer_angilal='0' AND cust.customer_type='2' AND pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'",
             qry + " cust.customer_angilal='0' AND cust.customer_type='1' AND pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'",
             qry + " cust.customer_angilal='0' AND cust.customer_type='3' AND pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'",
             qry + " cust.customer_angilal='1' AND pahi.pay_date>='" + start_date + "' AND pahi.pay_date<='" + end_date + "'"]
    for i in range(len(query)):
        try:
            histories = PaymentHistory.objects.raw(query[i])
            for history in histories:
                if season != '1':
                    niit_orlogo[i] += round(history.niit_orlogo, 2)
                ws.write(29 + i, 9, niit_orlogo[i], row_style)
        except ObjectDoesNotExist as e:
            logging.error('"PaymentHistory" model has no object: %s', e)
    ws.write(34, 9, '', row_style)
    ws.write(34, 6, '', row_style)
    ws.write(34, 8, '', row_style)

    row_num = 36
    ws.write_merge(row_num, row_num, 2, 7, 'Гүйцэтгэх захирал: ......................... /' + ex_dir + '/', text_style)
    row_num += 2
    ws.write_merge(row_num, row_num, 2, 7, 'Албаны менежер: ......................... /' + dep_man + '/', text_style)
    row_num += 2
    ws.write_merge(row_num, row_num, 2, 7,
                   'Борлуулалт тооцооны ахлах инженер: ......................... /' + sale_est_eng + '/', text_style)

    wb.save(response)
    return response


def report_ehzh_3_old(request):
    year = request.POST['year']
    season = request.POST['season']
    ex_dir = request.POST['ex_dir']
    dep_man = request.POST['dep_man']
    sale_est_eng = request.POST['sale_est_eng']

    response = HttpResponse(content_type='application/ms-excel')
    response[
        'Content-Disposition'] = 'attachment; filename="Erchim_suljee_XXK_' + year + '_onii_' + season + '_ulirliin_avlagiin_medee.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 4, 'Эрчим сүлжээ ХХК-ийн ' + year + ' оны ' + season + '-р улирлын авлагын мэдээ', title_style)
    ws.write(2, 0, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())
    ws.write(2, 11, '/сая төгрөгөөр/', xlwt.XFStyle())

    row_num = 3
    row_widths = [int(5 * 260), int(16 * 260), int(5 * 260), int(22 * 260), int(5 * 260), int(13 * 260), int(13 * 260),
                  int(13 * 260), int(13 * 260), int(15 * 260), int(15 * 260), int(15 * 260)]
    for row_width in range(len(row_widths)):
        ws.col(row_width).width = row_widths[row_width]
    ws.row(3).height_mismatch = True
    ws.row(3).height = int(2 * 260)
    ws.write_merge(row_num, row_num + 1, 0, 0, '№', header_style)
    ws.write_merge(row_num, row_num + 1, 1, 3, 'Үзүүлэлтүүд', header_style)
    ws.write_merge(row_num, row_num + 1, 4, 4, 'Мөрийн дугаар', rotate_style)
    ws.write_merge(row_num, row_num + 1, 5, 5, 'Өмнөх оны мөн үеийн гүйцэтгэл', header_style)
    ws.write_merge(row_num, row_num + 1, 6, 6, 'Тухайн оны эхний үлдэгдэл', header_style)
    ws.write_merge(row_num, row_num + 1, 7, 7, 'Улирлын эхний үлдэгдэл', header_style)
    ws.write_merge(row_num, row_num + 1, 8, 8, 'Улирлын эцсийн үлдэгдэл', header_style)
    ws.write_merge(row_num, row_num, 9, 11, 'Өөрчлөлт', header_style)
    ws.write(row_num + 1, 9, 'Өмнөх оны мөн үеэс', header_style)
    ws.write(row_num + 1, 10, 'Оны эхнээс', header_style)
    ws.write(row_num + 1, 11, 'Улирлын эхэнд байснаас', header_style)
    ws.write(row_num + 2, 0, 1, header_style)
    for i in range(35):
        ws.write(row_num + 2 + i, 4, i + 1, header_style)
    ws.write_merge(row_num + 2, row_num + 2, 1, 3, 'Нийт авлага', header_style)
    ws.write_merge(row_num + 3, row_num + 5, 0, 0, 2, header_style)
    ws.write_merge(row_num + 3, row_num + 5, 1, 1, 'Оршин суугч, ахуйн хэрэглэгчид', header_style)
    ws.write_merge(row_num + 3, row_num + 3, 2, 3, 'ДҮН', header_style)
    ws.write_merge(row_num + 4, row_num + 5, 2, 2, 'Үүнээс', rotate_text_style)
    ws.write(row_num + 4, 3, 'Орон сууц', row_style)
    ws.write(row_num + 5, 3, 'Гэр хороолол', row_style)
    row_num += 6
    ws.write_merge(row_num, row_num + 6, 0, 0, 3, header_style)
    ws.write_merge(row_num, row_num + 6, 1, 1, 'Үйлдвэрлэлийн байгууллага', header_style)
    ws.write_merge(row_num + 1, row_num + 6, 2, 2, 'Үүнээс', rotate_text_style)
    ws.write_merge(row_num, row_num, 2, 3, 'ДҮН', header_style)
    ws.write(row_num + 1, 3, 'Эрдэнэт ХХК', row_style)
    ws.write(row_num + 2, 3, 'Монросцветмет ХК', row_style)
    ws.write(row_num + 3, 3, 'Хөтөл цемент шохой ХК', row_style)
    ws.write(row_num + 4, 3, 'Хар төмөрлөг ХК', row_style)
    ws.write(row_num + 5, 3, '.....', row_style)
    ws.write(row_num + 6, 3, 'Бусад', row_style)
    row_num += 7
    ws.write_merge(row_num, row_num + 3, 0, 0, 4, header_style)
    ws.write_merge(row_num, row_num + 3, 1, 1, 'Худалдаа үйлчилгээний  байгууллага', header_style)
    ws.write_merge(row_num + 1, row_num + 3, 2, 2, 'Үүнээс', rotate_text_style)
    ws.write_merge(row_num, row_num, 2, 3, 'ДҮН', header_style)
    ws.write(row_num + 1, 3, 'ОСНААК', row_style)
    ws.write(row_num + 2, 3, '.....', row_style)
    ws.write(row_num + 3, 3, 'Бусад', row_style)
    row_num += 4
    ws.write_merge(row_num, row_num + 4, 0, 0, 5, header_style)
    ws.write_merge(row_num, row_num + 4, 1, 1, 'Төсвийн байгууллага', header_style)
    ws.write_merge(row_num + 1, row_num + 4, 2, 2, 'Үүнээс', rotate_text_style)
    ws.write_merge(row_num, row_num, 2, 3, 'ДҮН', header_style)
    ws.write(row_num + 1, 3, 'Улсын', row_style)
    ws.write(row_num + 2, 3, 'Аймаг, хотын', row_style)
    ws.write(row_num + 3, 3, 'Дүүргийн', row_style)
    ws.write(row_num + 4, 3, 'Бусад', row_style)
    row_num += 5
    ws.write_merge(row_num, row_num + 4, 0, 0, 6, header_style)
    ws.write_merge(row_num, row_num + 4, 1, 1, 'Бусад авлага', header_style)
    ws.write_merge(row_num + 1, row_num + 4, 2, 2, 'Үүнээс', rotate_text_style)
    ws.write_merge(row_num, row_num, 2, 3, 'ДҮН', header_style)
    ws.write(row_num + 1, 3, 'ҮААНБайгуулагаас', row_style)
    ws.write(row_num + 2, 3, 'Хувь хүмүүсээс', row_style)
    ws.write(row_num + 3, 3, 'Ажилтан албан хаагчдаас', row_style)
    ws.write(row_num + 4, 3, 'Бусад авлага', row_style)
    row_num += 5
    ws.write_merge(row_num, row_num + 9, 0, 0, 7, header_style)
    ws.write_merge(row_num, row_num + 9, 1, 1, 'Эрчим хүчний борлуулалтын авлага', header_style)
    ws.write_merge(row_num + 1, row_num + 9, 2, 2, 'Үүнээс', rotate_text_style)
    ws.write_merge(row_num, row_num, 2, 3, 'ДҮН', header_style)
    ws.write(row_num + 1, 3, 'УБЦТС ХК', row_style)
    ws.write(row_num + 2, 3, 'ДСЦТС ХК', row_style)
    ws.write(row_num + 3, 3, 'ЭБЦТС ХК', row_style)
    ws.write(row_num + 4, 3, 'БЗӨБЦТС ХК', row_style)
    ws.write(row_num + 5, 3, '1 худалдан авагчтай загвар', row_style)
    ws.write(row_num + 6, 3, 'УБДС ХК', row_style)
    ws.write(row_num + 7, 3, 'ДДС ХК', row_style)
    ws.write(row_num + 8, 3, 'Бусад', row_style)
    ws.write(row_num + 9, 3, 'ЦДҮСТӨХК', row_style)

    for i in range(7):
        ws.write(6, 5 + i, '', row_style)
        ws.write(8 + i, 5, '', row_style)
        ws.write(8 + i, 6, '', row_style)
        ws.write(8 + i, 7, '', row_style)
        ws.write(8 + i, 8, '', row_style)
        ws.write(8 + i, 9, '', row_style)
        ws.write(8 + i, 10, '', row_style)
        ws.write(8 + i, 11, '', row_style)
        ws.write(16, 5 + i, '', row_style)
        ws.write(17, 5 + i, '', row_style)
        ws.write(18, 5 + i, '', row_style)
        ws.write(20, 5 + i, '', row_style)
        ws.write(21, 5 + i, '', row_style)
        ws.write(22, 5 + i, '', row_style)
        ws.write(23, 5 + i, '', row_style)
    for i in range(15):
        ws.write(25 + i, 5, '', row_style)
        ws.write(25 + i, 6, '', row_style)
        ws.write(25 + i, 7, '', row_style)
        ws.write(25 + i, 8, '', row_style)
        ws.write(25 + i, 9, '', row_style)
        ws.write(25 + i, 10, '', row_style)
        ws.write(25 + i, 11, '', row_style)

    qry = "SELECT id, IFNULL((SUM(IFNULL(pay_total, 0))-(SUM(IFNULL(pay_total, 0)) * 0.1)), 0) AS total FROM data_paymenthistory"
    qry += " WHERE is_active='1' AND "
    qry_os = "SELECT pahi.id, IFNULL((SUM(IFNULL(pahi.pay_total, 0))-(SUM(IFNULL(pahi.pay_total, 0)) * 0.1)), 0) AS total FROM data_paymenthistory pahi"
    qry_os += " JOIN data_customer cust ON pahi.customer_id=cust.id WHERE pahi.is_active='1' AND cust.is_active='1' AND cust.customer_angilal='1' AND "
    qry_ub = "SELECT pahi.id, IFNULL((SUM(IFNULL(pahi.pay_total, 0))-(SUM(IFNULL(pahi.pay_total, 0)) * 0.1)), 0) AS total FROM data_paymenthistory pahi"
    qry_ub += " JOIN data_customer cust ON pahi.customer_id=cust.id WHERE pahi.is_active='1' AND cust.is_active='1' AND cust.customer_angilal='0' AND cust.customer_type='2' AND "
    qry_hu = "SELECT pahi.id, IFNULL((SUM(IFNULL(pahi.pay_total, 0))-(SUM(IFNULL(pahi.pay_total, 0)) * 0.1)), 0) AS total FROM data_paymenthistory pahi"
    qry_hu += " JOIN data_customer cust ON pahi.customer_id=cust.id WHERE pahi.is_active='1' AND cust.is_active='1' AND cust.customer_angilal='0' AND cust.customer_type='1' AND "
    qry_tb = "SELECT pahi.id, IFNULL((SUM(IFNULL(pahi.pay_total, 0))-(SUM(IFNULL(pahi.pay_total, 0)) * 0.1)), 0) AS total FROM data_paymenthistory pahi"
    qry_tb += " JOIN data_customer cust ON pahi.customer_id=cust.id WHERE pahi.is_active='1' AND cust.is_active='1' AND cust.customer_angilal='0' AND cust.customer_type='3' AND "
    qry_date = qry_nt = qry_nt_now = qry_now = ""
    if season == '1':
        qry_nt = " pay_date >= '" + str(int(year) - 1) + "-01-01' AND pay_date<=LAST_DAY('" + str(
            int(year) - 1) + "-03-01')"
        qry_nt_now = " pay_date >= '" + year + "-01-01' AND pay_date<=LAST_DAY('" + year + "-03-01')"
        qry_date = " pahi.pay_date >= '" + str(int(year) - 1) + "-01-01' AND pahi.pay_date<=LAST_DAY('" + str(
            int(year) - 1) + "-03-01')"
        qry_now = " pahi.pay_date >= '" + year + "-01-01' AND pahi.pay_date<=LAST_DAY('" + year + "-03-01')"
    elif season == '2':
        qry_nt = "pay_date >= '" + str(int(year) - 1) + "-04-01' AND pay_date<=LAST_DAY('" + str(
            int(year) - 1) + "-06-01')"
        qry_nt_now = " pay_date >= '" + year + "-04-01' AND pay_date<=LAST_DAY('" + year + "-06-01')"
        qry_date = " pahi.pay_date >= '" + str(int(year) - 1) + "-04-01' AND pahi.pay_date<=LAST_DAY('" + str(
            int(year) - 1) + "-06-01')"
        qry_now = " pahi.pay_date >= '" + year + "-04-01' AND pahi.pay_date<=LAST_DAY('" + year + "-06-01')"
    elif season == '3':
        qry_nt = "pay_date >= '" + str(int(year) - 1) + "-07-01' AND pay_date<=LAST_DAY('" + str(
            int(year) - 1) + "-09-01')"
        qry_nt_now = " pay_date >= '" + year + "-07-01' AND pay_date<=LAST_DAY('" + year + "-09-01')"
        qry_date += " pahi.pay_date >= '" + str(int(year) - 1) + "-07-01' AND pahi.pay_date<=LAST_DAY('" + str(
            int(year) - 1) + "-09-01')"
        qry_now = " pahi.pay_date >= '" + year + "-07-01' AND pahi.pay_date<=LAST_DAY('" + year + "-09-01')"
    elif season == '4':
        qry_nt = "pay_date >= '" + str(int(year) - 1) + "-10-01' AND pay_date<=LAST_DAY('" + str(
            int(year) - 1) + "-12-01')"
        qry_nt_now = " pay_date >= '" + year + "-10-01' AND pay_date<=LAST_DAY('" + year + "-12-01')"
        qry_date = " pahi.pay_date >= '" + str(int(year) - 1) + "-10-01' AND pahi.pay_date<=LAST_DAY('" + str(
            int(year) - 1) + "-12-01')"
        qry_now = " pahi.pay_date >= '" + year + "-10-01' AND pahi.pay_date<=LAST_DAY('" + year + "-12-01')"
    um_on_ul = [0, 0, 0, 0, 0]
    try:
        histories = PaymentHistory.objects.raw(qry + qry_nt)
        histories_os = PaymentHistory.objects.raw(qry_os + qry_date)
        histories_ub = PaymentHistory.objects.raw(qry_ub + qry_date)
        histories_hu = PaymentHistory.objects.raw(qry_hu + qry_date)
        histories_tb = PaymentHistory.objects.raw(qry_tb + qry_date)
        for history, history_os, history_ub, history_hu, history_tb in zip(histories, histories_os, histories_ub,
                                                                           histories_hu, histories_tb):
            um_on_ul[0] = round(history.total, 2)
            um_on_ul[1] = round(history_os.total, 2)
            um_on_ul[2] = round(history_ub.total, 2)
            um_on_ul[3] = round(history_hu.total, 2)
            um_on_ul[4] = round(history_tb.total, 2)
            ws.write(5, 5, round(history.total, 2), row_style)
            ws.write(7, 5, round(history_os.total, 2), row_style)
            ws.write(15, 5, round(history_ub.total, 2), row_style)
            ws.write(19, 5, round(history_hu.total, 2), row_style)
            ws.write(24, 5, round(history_tb.total, 2), row_style)
    except ObjectDoesNotExist as e:
        logging.error('"PaymentHistory" model has no object: %s', e)
    try:
        histories = PaymentHistory.objects.raw(qry + qry_nt_now)
        histories_os = PaymentHistory.objects.raw(qry_os + qry_now)
        histories_ub = PaymentHistory.objects.raw(qry_ub + qry_now)
        histories_hu = PaymentHistory.objects.raw(qry_hu + qry_now)
        histories_tb = PaymentHistory.objects.raw(qry_tb + qry_now)
        for history, history_os, history_ub, history_hu, history_tb in zip(histories, histories_os, histories_ub,
                                                                           histories_hu, histories_tb):
            ws.write(5, 9, round(history.total, 2) - um_on_ul[0], row_style)
            ws.write(7, 9, round(history_os.total, 2) - um_on_ul[1], row_style)
            ws.write(15, 9, round(history_ub.total, 2) - um_on_ul[2], row_style)
            ws.write(19, 9, round(history_hu.total, 2) - um_on_ul[3], row_style)
            ws.write(24, 9, round(history_tb.total, 2) - um_on_ul[4], row_style)
    except ObjectDoesNotExist as e:
        logging.error('"PaymentHistory" model has no object: %s', e)

    on_eh_uld = [0, 0, 0, 0, 0]
    qry = "SELECT id, IFNULL(((SUM(IFNULL(heregleenii_tulbur, 0) + IFNULL(uilchilgeenii_tulbur, 0))-(SUM(IFNULL(heregleenii_tulbur, 0) + IFNULL(uilchilgeenii_tulbur, 0)) * 0.1))), 0)"
    qry += " AS total FROM data_avlaga  WHERE out_of_date='1' AND is_active='1' AND "
    qry_gen = "SELECT avla.id, IFNULL(((SUM(IFNULL(avla.heregleenii_tulbur, 0) + IFNULL(avla.uilchilgeenii_tulbur, 0))-"
    qry_gen += " (SUM(IFNULL(avla.heregleenii_tulbur, 0) + IFNULL(avla.uilchilgeenii_tulbur, 0)) * 0.1))), 0) AS total FROM data_avlaga avla"
    qry_gen += " JOIN data_tooluurcustomer tocu ON avla.customer_id=tocu.customer_id JOIN data_customer cust ON tocu.customer_id=cust.id"
    qry_gen += " WHERE tocu.is_active='1' AND cust.is_active='1' AND avla.is_active='1' AND avla.out_of_date='1' AND "
    qry_nt = "paid_date>='" + str(int(year) - 1) + "-01-01' AND paid_date<='" + str(int(year) - 1) + "-12-31'"
    qry_os = "cust.customer_angilal='1' AND avla.paid_date>='" + str(
        int(year) - 1) + "-01-01' AND avla.paid_date<='" + str(int(year) - 1) + "-12-31'"
    qry_ub = "cust.customer_angilal='0' AND cust.customer_type='2' AND avla.paid_date>='" + str(
        int(year) - 1) + "-01-01' AND avla.paid_date<='" + str(int(year) - 1) + "-12-31'"
    qry_hu = "cust.customer_angilal='0' AND cust.customer_type='1' AND avla.paid_date>='" + str(
        int(year) - 1) + "-01-01' AND avla.paid_date<='" + str(int(year) - 1) + "-12-31'"
    qry_tb = "cust.customer_angilal='0' AND cust.customer_type='3' AND avla.paid_date>='" + str(
        int(year) - 1) + "-01-01' AND avla.paid_date<='" + str(int(year) - 1) + "-12-31'"
    try:
        avlagas = Avlaga.objects.raw(qry + qry_nt)
        avlagas_os = Avlaga.objects.raw(qry_gen + qry_os)
        avlagas_ub = Avlaga.objects.raw(qry_gen + qry_ub)
        avlagas_hu = Avlaga.objects.raw(qry_gen + qry_hu)
        avlagas_tb = Avlaga.objects.raw(qry_gen + qry_tb)
        for avlaga, avlaga_os, avlaga_ub, avlaga_hu, avlaga_tb in zip(avlagas, avlagas_os, avlagas_ub, avlagas_hu,
                                                                      avlagas_tb):
            on_eh_uld[0] = round(avlaga.total, 2)
            on_eh_uld[1] = round(avlaga_os.total, 2)
            on_eh_uld[2] = round(avlaga_ub.total, 2)
            on_eh_uld[3] = round(avlaga_hu.total, 2)
            on_eh_uld[4] = round(avlaga_tb.total, 2)
            ws.write(5, 6, round(avlaga.total, 2), row_style)
            ws.write(7, 6, round(avlaga_os.total, 2), row_style)
            ws.write(15, 6, round(avlaga_ub.total, 2), row_style)
            ws.write(19, 6, round(avlaga_hu.total, 2), row_style)
            ws.write(24, 6, round(avlaga_tb.total, 2), row_style)
    except ObjectDoesNotExist as e:
        logging.error('"Avlaga" model has no object: %s', e)
    qry_nt = "paid_date>='" + year + "-01-01' AND paid_date<='" + year + "-12-31'"
    qry_os = "cust.customer_angilal='1' AND avla.paid_date>='" + year + "-01-01' AND avla.paid_date<='" + year + "-12-31'"
    qry_ub = "cust.customer_angilal='0' AND cust.customer_type='2' AND avla.paid_date>='" + year + "-01-01' AND avla.paid_date<='" + year + "-12-31'"
    qry_hu = "cust.customer_angilal='0' AND cust.customer_type='1' AND avla.paid_date>='" + year + "-01-01' AND avla.paid_date<='" + year + "-12-31'"
    qry_tb = "cust.customer_angilal='0' AND cust.customer_type='3' AND avla.paid_date>='" + year + "-01-01' AND avla.paid_date<='" + year + "-12-31'"
    try:
        avlagas = Avlaga.objects.raw(qry + qry_nt)
        avlagas_os = Avlaga.objects.raw(qry_gen + qry_os)
        avlagas_ub = Avlaga.objects.raw(qry_gen + qry_ub)
        avlagas_hu = Avlaga.objects.raw(qry_gen + qry_hu)
        avlagas_tb = Avlaga.objects.raw(qry_gen + qry_tb)
        for avlaga, avlaga_os, avlaga_ub, avlaga_hu, avlaga_tb in zip(avlagas, avlagas_os, avlagas_ub, avlagas_hu,
                                                                      avlagas_tb):
            ws.write(5, 10, round(avlaga.total, 2) - on_eh_uld[0], row_style)
            ws.write(7, 10, round(avlaga_os.total, 2) - on_eh_uld[1], row_style)
            ws.write(15, 10, round(avlaga_ub.total, 2) - on_eh_uld[2], row_style)
            ws.write(19, 10, round(avlaga_hu.total, 2) - on_eh_uld[3], row_style)
            ws.write(24, 10, round(avlaga_tb.total, 2) - on_eh_uld[4], row_style)
    except ObjectDoesNotExist as e:
        logging.error('"Avlaga" model has no object: %s', e)

    qry = "SELECT id, IFNULL(((SUM(IFNULL(heregleenii_tulbur, 0) + IFNULL(uilchilgeenii_tulbur, 0))-"
    qry += " (SUM(IFNULL(heregleenii_tulbur, 0) + IFNULL(uilchilgeenii_tulbur, 0)) * 0.1))), 0) AS total FROM data_avlaga"
    qry += " WHERE out_of_date='1' AND is_active='1' AND "
    qry_gen = "SELECT avla.id, IFNULL(((SUM(IFNULL(avla.heregleenii_tulbur, 0) + IFNULL(avla.uilchilgeenii_tulbur, 0))-"
    qry_gen += " (SUM(IFNULL(avla.heregleenii_tulbur, 0) + IFNULL(avla.uilchilgeenii_tulbur, 0)) * 0.1))), 0) AS total FROM data_avlaga avla"
    qry_gen += " JOIN data_tooluurcustomer tocu ON avla.customer_id=tocu.customer_id JOIN data_customer cust ON tocu.customer_id=cust.id"
    qry_gen += " WHERE avla.is_active='1' AND tocu.is_active='1' AND cust.is_active='1' AND avla.out_of_date='1' AND "
    if season == '1':
        ws.write(5, 7, 0, row_style)
        ws.write(7, 7, 0, row_style)
        ws.write(15, 7, 0, row_style)
        ws.write(19, 7, 0, row_style)
        ws.write(24, 7, 0, row_style)
        qry_nt = " paid_date>='" + year + "-01-01' AND paid_date<=LAST_DAY('" + year + "-03-01')"
        qry_os = "cust.customer_angilal='1' AND avla.paid_date>='" + year + "-01-01' AND avla.paid_date<=LAST_DAY('" + year + "-03-01')"
        qry_ub = "cust.customer_angilal='0' AND cust.customer_type='2' AND avla.paid_date>='" + year + "-01-01' AND avla.paid_date<=LAST_DAY('" + year + "-03-01')"
        qry_hu = "cust.customer_angilal='0' AND cust.customer_type='1' AND avla.paid_date>='" + year + "-01-01' AND avla.paid_date<=LAST_DAY('" + year + "-03-01')"
        qry_tb = "cust.customer_angilal='0' AND cust.customer_type='3' AND avla.paid_date>='" + year + "-01-01' AND avla.paid_date<=LAST_DAY('" + year + "-03-01')"
        try:
            avlagas = Avlaga.objects.raw(qry + qry_nt)
            avlagas_os = Avlaga.objects.raw(qry_gen + qry_os)
            avlagas_ub = Avlaga.objects.raw(qry_gen + qry_ub)
            avlagas_hu = Avlaga.objects.raw(qry_gen + qry_hu)
            avlagas_tb = Avlaga.objects.raw(qry_gen + qry_tb)
            for avlaga, avlaga_os, avlaga_ub, avlaga_hu, avlaga_tb in zip(avlagas, avlagas_os, avlagas_ub, avlagas_hu,
                                                                          avlagas_tb):
                ws.write(5, 8, round(avlaga.total, 2), row_style)
                ws.write(7, 8, round(avlaga_os.total, 2), row_style)
                ws.write(15, 8, round(avlaga_ub.total, 2), row_style)
                ws.write(19, 8, round(avlaga_hu.total, 2), row_style)
                ws.write(24, 8, round(avlaga_tb.total, 2), row_style)
                ws.write(5, 11, round(avlaga.total, 2), row_style)
                ws.write(7, 11, round(avlaga_os.total, 2), row_style)
                ws.write(15, 11, round(avlaga_ub.total, 2), row_style)
                ws.write(19, 11, round(avlaga_hu.total, 2), row_style)
                ws.write(24, 11, round(avlaga_tb.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"Avlaga" model has no object: %s', e)
    elif season == '2':
        niit_eh = [0, 0, 0, 0, 0]
        qry_nt = " paid_date>='" + year + "-01-01' AND paid_date<=LAST_DAY('" + year + "-03-01')"
        qry_os = "cust.customer_angilal='1' AND avla.paid_date>='" + year + "-01-01' AND avla.paid_date<=LAST_DAY('" + year + "-03-01')"
        qry_ub = "cust.customer_angilal='0' AND cust.customer_type='2' AND avla.paid_date>='" + year + "-01-01' AND avla.paid_date<=LAST_DAY('" + year + "-03-01')"
        qry_hu = "cust.customer_angilal='0' AND cust.customer_type='1' AND avla.paid_date>='" + year + "-01-01' AND avla.paid_date<=LAST_DAY('" + year + "-03-01')"
        qry_tb = "cust.customer_angilal='0' AND cust.customer_type='3' AND avla.paid_date>='" + year + "-01-01' AND avla.paid_date<=LAST_DAY('" + year + "-03-01')"
        try:
            avlagas = Avlaga.objects.raw(qry + qry_nt)
            avlagas_os = Avlaga.objects.raw(qry_gen + qry_os)
            avlagas_ub = Avlaga.objects.raw(qry_gen + qry_ub)
            avlagas_hu = Avlaga.objects.raw(qry_gen + qry_hu)
            avlagas_tb = Avlaga.objects.raw(qry_gen + qry_tb)
            for avlaga, avlaga_os, avlaga_ub, avlaga_hu, avlaga_tb in zip(avlagas, avlagas_os, avlagas_ub, avlagas_hu,
                                                                          avlagas_tb):
                niit_eh[0] = round(avlaga.total, 2)
                niit_eh[1] = round(avlaga.total, 2)
                niit_eh[2] = round(avlaga.total, 2)
                niit_eh[3] = round(avlaga.total, 2)
                niit_eh[4] = round(avlaga.total, 2)
                ws.write(5, 7, round(avlaga.total, 2), row_style)
                ws.write(7, 7, round(avlaga_os.total, 2), row_style)
                ws.write(15, 7, round(avlaga_ub.total, 2), row_style)
                ws.write(19, 7, round(avlaga_hu.total, 2), row_style)
                ws.write(24, 7, round(avlaga_tb.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"Avlaga" model has no object: %s', e)
        niit_su = [0, 0, 0, 0, 0]
        qry_nt = " paid_date>='" + year + "-04-01' AND paid_date<=LAST_DAY('" + year + "-06-01')"
        qry_os = "cust.customer_angilal='1' AND avla.paid_date>='" + year + "-04-01' AND avla.paid_date<=LAST_DAY('" + year + "-06-01')"
        qry_ub = "cust.customer_angilal='0' AND cust.customer_type='2' AND avla.paid_date>='" + year + "-04-01' AND avla.paid_date<=LAST_DAY('" + year + "-06-01')"
        qry_hu = "cust.customer_angilal='0' AND cust.customer_type='1' AND avla.paid_date>='" + year + "-04-01' AND avla.paid_date<=LAST_DAY('" + year + "-06-01')"
        qry_tb = "cust.customer_angilal='0' AND cust.customer_type='3' AND avla.paid_date>='" + year + "-04-01' AND avla.paid_date<=LAST_DAY('" + year + "-06-01')"
        try:
            avlagas = Avlaga.objects.raw(qry + qry_nt)
            avlagas_os = Avlaga.objects.raw(qry_gen + qry_os)
            avlagas_ub = Avlaga.objects.raw(qry_gen + qry_ub)
            avlagas_hu = Avlaga.objects.raw(qry_gen + qry_hu)
            avlagas_tb = Avlaga.objects.raw(qry_gen + qry_tb)
            for avlaga, avlaga_os, avlaga_ub, avlaga_hu, avlaga_tb in zip(avlagas, avlagas_os, avlagas_ub, avlagas_hu,
                                                                          avlagas_tb):
                niit_su[0] = round(avlaga.total, 2)
                niit_su[1] = round(avlaga.total, 2)
                niit_su[2] = round(avlaga.total, 2)
                niit_su[3] = round(avlaga.total, 2)
                niit_su[4] = round(avlaga.total, 2)
                ws.write(5, 8, round(avlaga.total, 2), row_style)
                ws.write(7, 8, round(avlaga_os.total, 2), row_style)
                ws.write(15, 8, round(avlaga_ub.total, 2), row_style)
                ws.write(19, 8, round(avlaga_hu.total, 2), row_style)
                ws.write(24, 8, round(avlaga_tb.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"Avlaga" model has no object: %s', e)
        ws.write(5, 11, niit_su[0] - niit_eh[0], row_style)
        ws.write(7, 11, niit_su[1] - niit_eh[1], row_style)
        ws.write(15, 11, niit_su[2] - niit_eh[2], row_style)
        ws.write(19, 11, niit_su[3] - niit_eh[3], row_style)
        ws.write(24, 11, niit_su[4] - niit_eh[4], row_style)
    elif season == '3':
        niit_eh = [0, 0, 0, 0, 0]
        qry_nt = " paid_date>='" + year + "-04-01' AND paid_date<=LAST_DAY('" + year + "-06-01')"
        qry_os = "cust.customer_angilal='1' AND avla.paid_date>='" + year + "-04-01' AND avla.paid_date<=LAST_DAY('" + year + "-06-01')"
        qry_ub = "cust.customer_angilal='0' AND cust.customer_type='2' AND avla.paid_date>='" + year + "-04-01' AND avla.paid_date<=LAST_DAY('" + year + "-06-01')"
        qry_hu = "cust.customer_angilal='0' AND cust.customer_type='1' AND avla.paid_date>='" + year + "-04-01' AND avla.paid_date<=LAST_DAY('" + year + "-06-01')"
        qry_tb = "cust.customer_angilal='0' AND cust.customer_type='3' AND avla.paid_date>='" + year + "-04-01' AND avla.paid_date<=LAST_DAY('" + year + "-06-01')"
        try:
            avlagas = Avlaga.objects.raw(qry + qry_nt)
            avlagas_os = Avlaga.objects.raw(qry_gen + qry_os)
            avlagas_ub = Avlaga.objects.raw(qry_gen + qry_ub)
            avlagas_hu = Avlaga.objects.raw(qry_gen + qry_hu)
            avlagas_tb = Avlaga.objects.raw(qry_gen + qry_tb)
            for avlaga, avlaga_os, avlaga_ub, avlaga_hu, avlaga_tb in zip(avlagas, avlagas_os, avlagas_ub, avlagas_hu,
                                                                          avlagas_tb):
                niit_eh[0] = round(avlaga.total, 2)
                niit_eh[1] = round(avlaga.total, 2)
                niit_eh[2] = round(avlaga.total, 2)
                niit_eh[3] = round(avlaga.total, 2)
                niit_eh[4] = round(avlaga.total, 2)
                ws.write(5, 7, round(avlaga.total, 2), row_style)
                ws.write(7, 7, round(avlaga_os.total, 2), row_style)
                ws.write(15, 7, round(avlaga_ub.total, 2), row_style)
                ws.write(19, 7, round(avlaga_hu.total, 2), row_style)
                ws.write(24, 7, round(avlaga_tb.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"Avlaga" model has no object: %s', e)
        niit_su = [0, 0, 0, 0, 0]
        qry_nt = " paid_date>='" + year + "-07-01' AND paid_date<=LAST_DAY('" + year + "-09-01')"
        qry_os = "cust.customer_angilal='1' AND avla.paid_date>='" + year + "-07-01' AND avla.paid_date<=LAST_DAY('" + year + "-09-01')"
        qry_ub = "cust.customer_angilal='0' AND cust.customer_type='2' AND avla.paid_date>='" + year + "-07-01' AND avla.paid_date<=LAST_DAY('" + year + "-09-01')"
        qry_hu = "cust.customer_angilal='0' AND cust.customer_type='1' AND avla.paid_date>='" + year + "-07-01' AND avla.paid_date<=LAST_DAY('" + year + "-09-01')"
        qry_tb = "cust.customer_angilal='0' AND cust.customer_type='3' AND avla.paid_date>='" + year + "-07-01' AND avla.paid_date<=LAST_DAY('" + year + "-09-01')"
        try:
            avlagas = Avlaga.objects.raw(qry + qry_nt)
            avlagas_os = Avlaga.objects.raw(qry_gen + qry_os)
            avlagas_ub = Avlaga.objects.raw(qry_gen + qry_ub)
            avlagas_hu = Avlaga.objects.raw(qry_gen + qry_hu)
            avlagas_tb = Avlaga.objects.raw(qry_gen + qry_tb)
            for avlaga, avlaga_os, avlaga_ub, avlaga_hu, avlaga_tb in zip(avlagas, avlagas_os, avlagas_ub, avlagas_hu,
                                                                          avlagas_tb):
                niit_su[0] = round(avlaga.total, 2)
                niit_su[1] = round(avlaga.total, 2)
                niit_su[2] = round(avlaga.total, 2)
                niit_su[3] = round(avlaga.total, 2)
                niit_su[4] = round(avlaga.total, 2)
                ws.write(5, 8, round(avlaga.total, 2), row_style)
                ws.write(7, 8, round(avlaga_os.total, 2), row_style)
                ws.write(15, 8, round(avlaga_ub.total, 2), row_style)
                ws.write(19, 8, round(avlaga_hu.total, 2), row_style)
                ws.write(24, 8, round(avlaga_tb.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"Avlaga" model has no object: %s', e)
        ws.write(5, 11, niit_su[0] - niit_eh[0], row_style)
        ws.write(7, 11, niit_su[1] - niit_eh[1], row_style)
        ws.write(15, 11, niit_su[2] - niit_eh[2], row_style)
        ws.write(19, 11, niit_su[3] - niit_eh[3], row_style)
        ws.write(24, 11, niit_su[4] - niit_eh[4], row_style)
    elif season == '4':
        niit_eh = [0, 0, 0, 0, 0]
        qry_nt = " paid_date>='" + year + "-07-01' AND paid_date<=LAST_DAY('" + year + "-09-01')"
        qry_os = "cust.customer_angilal='1' AND avla.paid_date>='" + year + "-07-01' AND avla.paid_date<=LAST_DAY('" + year + "-09-01')"
        qry_ub = "cust.customer_angilal='0' AND cust.customer_type='2' AND avla.paid_date>='" + year + "-07-01' AND avla.paid_date<=LAST_DAY('" + year + "-09-01')"
        qry_hu = "cust.customer_angilal='0' AND cust.customer_type='1' AND avla.paid_date>='" + year + "-07-01' AND avla.paid_date<=LAST_DAY('" + year + "-09-01')"
        qry_tb = "cust.customer_angilal='0' AND cust.customer_type='3' AND avla.paid_date>='" + year + "-07-01' AND avla.paid_date<=LAST_DAY('" + year + "-09-01')"
        try:
            avlagas = Avlaga.objects.raw(qry + qry_nt)
            avlagas_os = Avlaga.objects.raw(qry_gen + qry_os)
            avlagas_ub = Avlaga.objects.raw(qry_gen + qry_ub)
            avlagas_hu = Avlaga.objects.raw(qry_gen + qry_hu)
            avlagas_tb = Avlaga.objects.raw(qry_gen + qry_tb)
            for avlaga, avlaga_os, avlaga_ub, avlaga_hu, avlaga_tb in zip(avlagas, avlagas_os, avlagas_ub, avlagas_hu,
                                                                          avlagas_tb):
                niit_eh[0] = round(avlaga.total, 2)
                niit_eh[1] = round(avlaga.total, 2)
                niit_eh[2] = round(avlaga.total, 2)
                niit_eh[3] = round(avlaga.total, 2)
                niit_eh[4] = round(avlaga.total, 2)
                ws.write(5, 7, round(avlaga.total, 2), row_style)
                ws.write(7, 7, round(avlaga_os.total, 2), row_style)
                ws.write(15, 7, round(avlaga_ub.total, 2), row_style)
                ws.write(19, 7, round(avlaga_hu.total, 2), row_style)
                ws.write(24, 7, round(avlaga_tb.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"Avlaga" model has no object: %s', e)
        niit_su = [0, 0, 0, 0, 0]
        qry_nt = " paid_date>='" + year + "-10-01' AND paid_date<=LAST_DAY('" + year + "-12-01')"
        qry_os = "cust.customer_angilal='1' AND avla.paid_date>='" + year + "-10-01' AND avla.paid_date<=LAST_DAY('" + year + "-12-01')"
        qry_ub = "cust.customer_angilal='0' AND cust.customer_type='2' AND avla.paid_date>='" + year + "-10-01' AND avla.paid_date<=LAST_DAY('" + year + "-12-01')"
        qry_hu = "cust.customer_angilal='0' AND cust.customer_type='1' AND avla.paid_date>='" + year + "-10-01' AND avla.paid_date<=LAST_DAY('" + year + "-12-01')"
        qry_tb = "cust.customer_angilal='0' AND cust.customer_type='3' AND avla.paid_date>='" + year + "-10-01' AND avla.paid_date<=LAST_DAY('" + year + "-12-01')"
        try:
            avlagas = Avlaga.objects.raw(qry + qry_nt)
            avlagas_os = Avlaga.objects.raw(qry_gen + qry_os)
            avlagas_ub = Avlaga.objects.raw(qry_gen + qry_ub)
            avlagas_hu = Avlaga.objects.raw(qry_gen + qry_hu)
            avlagas_tb = Avlaga.objects.raw(qry_gen + qry_tb)
            for avlaga, avlaga_os, avlaga_ub, avlaga_hu, avlaga_tb in zip(avlagas, avlagas_os, avlagas_ub, avlagas_hu,
                                                                          avlagas_tb):
                niit_su[0] = round(avlaga.total, 2)
                niit_su[1] = round(avlaga.total, 2)
                niit_su[2] = round(avlaga.total, 2)
                niit_su[3] = round(avlaga.total, 2)
                niit_su[4] = round(avlaga.total, 2)
                ws.write(5, 8, round(avlaga.total, 2), row_style)
                ws.write(7, 8, round(avlaga_os.total, 2), row_style)
                ws.write(15, 8, round(avlaga_ub.total, 2), row_style)
                ws.write(19, 8, round(avlaga_hu.total, 2), row_style)
                ws.write(24, 8, round(avlaga_tb.total, 2), row_style)
        except ObjectDoesNotExist as e:
            logging.error('"Avlaga" model has no object: %s', e)
        ws.write(5, 11, niit_su[0] - niit_eh[0], row_style)
        ws.write(7, 11, niit_su[1] - niit_eh[1], row_style)
        ws.write(15, 11, niit_su[2] - niit_eh[2], row_style)
        ws.write(19, 11, niit_su[3] - niit_eh[3], row_style)
        ws.write(24, 11, niit_su[4] - niit_eh[4], row_style)

    qry = ""
    qry += " "

    row_num = 40
    ws.write_merge(row_num, row_num, 0, 6,
                   'Жич: Авлагын мэдээнд онцгой өөрчлөлт гарсан бол нэмэлт тайлбартайгаар ирүүлнэ.', text_style)
    row_num += 4
    ws.write_merge(row_num, row_num, 4, 9, 'Гүйцэтгэх захирал: ......................... /' + ex_dir + '/', text_style)
    row_num += 2
    ws.write_merge(row_num, row_num, 4, 9, 'Албаны менежер: ......................... /' + dep_man + '/', text_style)
    row_num += 2
    ws.write_merge(row_num, row_num, 4, 9,
                   'Борлуулалт тооцооны ахлах инженер: ......................... /' + sale_est_eng + '/', text_style)

    wb.save(response)
    return response


def report_ehzh_4_old(request):
    year = request.POST['year']
    season = request.POST['season']
    ex_dir = request.POST['ex_dir']
    dep_man = request.POST['dep_man']
    sale_est_eng = request.POST['sale_est_eng']

    response = HttpResponse(content_type='application/ms-excel')
    response[
        'Content-Disposition'] = 'attachment; filename="Erchim_suljee_XXK_' + year + '_onii_' + season + '_ulirliin_uglugiin_medee.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 4, 'Эрчим хүчний ТЗЭ Эрчим сүлжээ ХХК-ийн ' + year + ' оны ' + season + '-р улирлын өглөгийн мэдээ',
             title_style)
    ws.write(2, 0, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())
    ws.write(2, 11, '/сая төгрөгөөр/', xlwt.XFStyle())

    row_num = 3
    row_widths = [int(5 * 260), int(16 * 260), int(5 * 260), int(33 * 260), int(5 * 260), int(13 * 260), int(13 * 260),
                  int(13 * 260), int(13 * 260), int(15 * 260), int(15 * 260), int(15 * 260)]
    for row_width in range(len(row_widths)):
        ws.col(row_width).width = row_widths[row_width]
    ws.row(3).height_mismatch = True
    ws.row(3).height = int(2 * 260)
    ws.write_merge(row_num, row_num + 1, 0, 0, '№', header_style)
    ws.write_merge(row_num, row_num + 1, 1, 3, 'Үзүүлэлтүүд', header_style)
    ws.write_merge(row_num, row_num + 1, 4, 4, 'Мөрийн дугаар', rotate_style)
    ws.write_merge(row_num, row_num + 1, 5, 5, 'Өмнөх оны мөн үеийн гүйцэтгэл', header_style)
    ws.write_merge(row_num, row_num + 1, 6, 6, 'Тухайн оны эхний үлдэгдэл', header_style)
    ws.write_merge(row_num, row_num + 1, 7, 7, 'Улирлын эхний үлдэгдэл', header_style)
    ws.write_merge(row_num, row_num + 1, 8, 8, 'Улирлын эцсийн үлдэгдэл', header_style)
    ws.write_merge(row_num, row_num, 9, 11, 'Өөрчлөлт', header_style)
    ws.write(row_num + 1, 9, 'Өмнөх оны мөн үеэс', header_style)
    ws.write(row_num + 1, 10, 'Оны эхнээс', header_style)
    ws.write(row_num + 1, 11, 'Улирлын эхэнд байснаас', header_style)
    for i in range(45):
        ws.write(row_num + 2 + i, 4, i + 1, header_style)
    ws.write(row_num + 2, 0, 1, header_style)
    ws.write_merge(row_num + 2, row_num + 2, 1, 3, 'Нийт өглөг', header_style)
    ws.write_merge(row_num + 3, row_num + 10, 0, 0, 2, header_style)
    ws.write_merge(row_num + 3, row_num + 10, 1, 1, 'Нүүрсний  өглөг', header_style)
    ws.write_merge(row_num + 3, row_num + 3, 2, 3, 'ДҮН', header_style)
    ws.write_merge(row_num + 4, row_num + 10, 2, 2, 'Үүнээс', rotate_text_style)
    ws.write(row_num + 4, 3, 'Багануур ХК', row_style)
    ws.write(row_num + 5, 3, 'Шивээ-Овоо ХК', row_style)
    ws.write(row_num + 6, 3, 'Шарын гол ХК', row_style)
    ws.write(row_num + 7, 3, 'Адуунчулуун ХК', row_style)
    ws.write(row_num + 8, 3, 'Таван толгой ХК', row_style)
    ws.write(row_num + 9, 3, 'Бусад', row_style)
    ws.write(row_num + 10, 3, '.....', row_style)
    row_num += 11
    ws.write_merge(row_num, row_num + 3, 0, 0, 3, header_style)
    ws.write_merge(row_num, row_num + 3, 1, 1, 'Тээврийн хөлсний өглөг', header_style)
    ws.write_merge(row_num, row_num, 2, 3, 'ДҮН', header_style)
    ws.write_merge(row_num + 1, row_num + 3, 2, 2, 'Үүнээс', rotate_text_style)
    ws.write(row_num + 1, 3, 'УБТЗХЭГ', row_style)
    ws.write(row_num + 2, 3, 'Бусад', row_style)
    ws.write(row_num + 3, 3, '.....', row_style)
    row_num += 4
    ws.write_merge(row_num, row_num + 6, 0, 0, 4, header_style)
    ws.write_merge(row_num, row_num + 6, 1, 1, 'Татварын  өглөг', header_style)
    ws.write_merge(row_num, row_num, 2, 3, 'ДҮН', header_style)
    ws.write_merge(row_num + 1, row_num + 6, 2, 2, 'Үүнээс', rotate_text_style)
    ws.write(row_num + 1, 3, 'ААНБОАТ', row_style)
    ws.write(row_num + 2, 3, 'ХХОАТ', row_style)
    ws.write(row_num + 3, 3, 'НӨАТ', row_style)
    ws.write(row_num + 4, 3, 'Гаалийн татвар', row_style)
    ws.write(row_num + 5, 3, 'ЭМНДШимтгэл', row_style)
    ws.write(row_num + 6, 3, 'Бусад татвар, хураамж', row_style)
    row_num += 7
    ws.write_merge(row_num, row_num + 5, 0, 0, 5, header_style)
    ws.write_merge(row_num, row_num + 5, 1, 1, 'Зээл, хүүгийн өглөг', header_style)
    ws.write_merge(row_num, row_num, 2, 3, 'ДҮН', header_style)
    ws.write_merge(row_num + 1, row_num + 5, 2, 2, 'Үүнээс', rotate_text_style)
    ws.write(row_num + 1, 3, 'Төслийн зээлийн тайлант үеийн өр', row_style)
    ws.write(row_num + 2, 3, 'Төслийн зээлийн  хүүгийн өр', row_style)
    ws.write(row_num + 3, 3, 'Дотоодын банкны БХЗ-ийн өр', row_style)
    ws.write(row_num + 4, 3, 'Дотоодын банкны зээлийн хүүгийн өр', row_style)
    ws.write(row_num + 5, 3, 'Бусад богино хугацаат зээлийн өр', row_style)
    row_num += 6
    ws.write_merge(row_num, row_num + 4, 0, 0, 6, header_style)
    ws.write_merge(row_num, row_num + 4, 1, 1, 'Бусад богино хугацаат өглөг', header_style)
    ws.write_merge(row_num, row_num, 2, 3, 'ДҮН', header_style)
    ws.write_merge(row_num + 1, row_num + 4, 2, 2, 'Үүнээс', rotate_text_style)
    ws.write(row_num + 1, 3, 'Бэлтгэн нийлүүлэгчийн', row_style)
    ws.write(row_num + 2, 3, 'Хувь хүмүүсийн', row_style)
    ws.write(row_num + 3, 3, 'Цалингийн', row_style)
    ws.write(row_num + 4, 3, 'Бусад', row_style)
    row_num += 5
    ws.write_merge(row_num, row_num + 13, 0, 0, 6, header_style)
    ws.write_merge(row_num, row_num + 13, 1, 1, 'Эрчим хүчний борлуулалтын өглөг', header_style)
    ws.write_merge(row_num, row_num, 2, 3, 'ДҮН', header_style)
    ws.write_merge(row_num + 1, row_num + 13, 2, 2, 'Үүнээс', rotate_text_style)
    ws.write(row_num + 1, 3, 'ДЦС-2 ХК', row_style)
    ws.write(row_num + 2, 3, 'ДЦС-3 ХК', row_style)
    ws.write(row_num + 3, 3, 'ДЦС-4 ХК', row_style)
    ws.write(row_num + 4, 3, 'ДДЦС ХК', row_style)
    ws.write(row_num + 5, 3, 'ЭДЦС ХК', row_style)
    ws.write(row_num + 6, 3, 'УБЦТС ХК', row_style)
    ws.write(row_num + 7, 3, 'ДСЦТС ХК', row_style)
    ws.write(row_num + 8, 3, 'ЭБЦТС ХК', row_style)
    ws.write(row_num + 9, 3, 'БЗӨБЦТС ХК', row_style)
    ws.write(row_num + 10, 3, 'Импортын ЦЭХ', row_style)
    ws.write(row_num + 11, 3, '1 худалдан авагчтай загвар', row_style)
    ws.write(row_num + 12, 3, 'Бусад', row_style)
    ws.write(row_num + 13, 3, 'ДҮТ ХХК', row_style)

    row_num = 5
    # for row in rows:
    for i in range(45):
        col_num = 5
        ws.write(row_num + i, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num + i, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num + i, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num + i, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num + i, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num + i, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num + i, col_num, 0, row_style)
        col_num += 1

    row_num = 51
    ws.write_merge(row_num, row_num, 0, 6,
                   'Жич: Өглөгийн мэдээнд онцгой өөрчлөлт гарсан бол нэмэлт тайлбартайгаар мэдээнд хавсаргаж  ирүүлнэ.',
                   text_style)
    row_num += 3
    ws.write_merge(row_num, row_num, 4, 9, 'Гүйцэтгэх захирал: ......................... /' + ex_dir + '/', text_style)
    row_num += 2
    ws.write_merge(row_num, row_num, 4, 9, 'Албаны менежер: ......................... /' + dep_man + '/', text_style)
    row_num += 2
    ws.write_merge(row_num, row_num, 4, 9,
                   'Борлуулалт тооцооны ахлах инженер: ......................... /' + sale_est_eng + '/', text_style)

    wb.save(response)
    return response


def report_ehzh_5_old(request):
    year = request.POST['year']

    response = HttpResponse(content_type='application/ms-excel')
    response[
        'Content-Disposition'] = 'attachment; filename="Erchim_Suljee_XXK_' + year + '_onii_borluulaltiin_orlogiin_medee.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 6, 'Эрчим Сүлжээ ХХК-ийн ' + year + ' оны борлуулалтын орлогын мэдээ', title_style)
    ws.write(2, 0, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())
    ws.write(2, 13, '/сая төгрөгөөр/', title_style)

    row_num = 3
    row_widths = [int(5 * 260), int(5 * 260), int(5 * 260), int(35 * 260), int(12 * 260), int(15 * 260), int(15 * 260),
                  int(15 * 260), int(15 * 260), int(15 * 260), int(15 * 260), int(12 * 260), int(15 * 260),
                  int(15 * 260), int(15 * 260)]
    for row_width in range(len(row_widths)):
        ws.col(row_width).width = row_widths[row_width]
    ws.write_merge(row_num, row_num + 1, 0, 0, '№', header_style)
    ws.write_merge(row_num, row_num + 1, 1, 3, 'Үзүүлэлтүүд', header_style)
    ws.write_merge(row_num, row_num, 4, 7, str(int(year) - 1) + ' оны гүйцэтгэл', header_style)
    ws.write(row_num + 1, 4, 'Хэрэглэгчийн тоо', header_style)
    ws.write(row_num + 1, 5, 'Борлуулсан цахилгаан /мян.кВтц/', header_style)
    ws.write(row_num + 1, 6, 'Борлуулалтын орлого /мян.төг/', header_style)
    ws.write(row_num + 1, 7, 'Бичилтийн дундаж үнэ /төг.кВтц/', header_style)
    ws.write_merge(row_num, row_num, 8, 10, year + ' оны төлөвлөгөө', header_style)
    ws.write(row_num + 1, 8, 'Борлуулсан цахилгаан /мян.кВтц/', header_style)
    ws.write(row_num + 1, 9, 'Борлуулалтын орлого /мян.төг/', header_style)
    ws.write(row_num + 1, 10, 'Бичилтийн дундаж үнэ /төг.кВтц/', header_style)
    ws.write_merge(row_num, row_num, 11, 14, year + ' оны гүйцэтгэл', header_style)
    ws.write(row_num + 1, 11, 'Хэрэглэгчийн тоо', header_style)
    ws.write(row_num + 1, 12, 'Борлуулсан цахилгаан /мян.кВтц/', header_style)
    ws.write(row_num + 1, 13, 'Борлуулалтын орлого /мян.төг/', header_style)
    ws.write(row_num + 1, 14, 'Бичилтийн дундаж үнэ /төг.кВтц/', header_style)
    row_num += 2
    ws.write(row_num, 0, '1', header_style)
    ws.write_merge(row_num, row_num, 1, 3, 'Үйлдвэрлэлийн байгууллага', header_style)
    ws.write(row_num + 1, 0, '1.1', header_style)
    ws.write(row_num + 1, 1, '', header_style)
    ws.write(row_num + 2, 1, '', header_style)
    ws.write(row_num + 3, 1, '', header_style)
    ws.write(row_num + 4, 1, '', header_style)
    ws.write(row_num + 5, 1, '', header_style)
    ws.write(row_num + 3, 2, '', header_style)
    ws.write(row_num + 4, 2, '', header_style)
    ws.write(row_num + 5, 2, '', header_style)
    ws.write_merge(row_num + 2, row_num + 5, 0, 0, '1.2', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 2, 3, '-Энгийн тоолуур', header_style)
    ws.write_merge(row_num + 2, row_num + 2, 2, 3, '-3 тарифт тоолууртай', header_style)
    ws.write(row_num + 3, 3, '-Өдрийн ачааллын /06.00-17.00/', header_style)
    ws.write(row_num + 4, 3, '-Оройн оргил ачааллын /17.00-22.00/', header_style)
    ws.write(row_num + 5, 3, '-Шөнийн бага ачааллын /22.00-06.00/', header_style)
    row_num += 6
    ws.write(row_num, 0, '2', header_style)
    ws.write_merge(row_num, row_num, 1, 3, 'Худалдаа, үйлчилгээний байгууллага', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 0, 0, '2.1', header_style)
    ws.write_merge(row_num + 2, row_num + 5, 0, 0, '2.2', header_style)
    ws.write(row_num + 1, 1, '', header_style)
    ws.write(row_num + 2, 1, '', header_style)
    ws.write(row_num + 3, 1, '', header_style)
    ws.write(row_num + 4, 1, '', header_style)
    ws.write(row_num + 5, 1, '', header_style)
    ws.write(row_num + 3, 2, '', header_style)
    ws.write(row_num + 4, 2, '', header_style)
    ws.write(row_num + 5, 2, '', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 2, 3, 'ААН /1 тариф/', header_style)
    ws.write_merge(row_num + 2, row_num + 2, 2, 3, 'ААН /3 тариф/', header_style)
    ws.write(row_num + 3, 3, '-Өдрийн ачааллын /06.00-17.00/', header_style)
    ws.write(row_num + 4, 3, '-Оройн оргил ачааллын /17.00-22.00/', header_style)
    ws.write(row_num + 5, 3, '-Шөнийн бага ачааллын /22.00-06.00/', header_style)
    row_num += 6
    ws.write_merge(row_num, row_num + 2, 0, 0, '2.3', header_style)
    ws.write_merge(row_num, row_num, 2, 3, 'Гудамжны гэрэлтүүлэг /2 тариф/', header_style)
    ws.write(row_num + 1, 3, '-Өдрийн /06.00-21.00/', header_style)
    ws.write(row_num + 2, 3, '-Шөнийн /21.00-06.00/', header_style)
    ws.write(row_num, 1, '', header_style)
    ws.write(row_num + 1, 1, '', header_style)
    ws.write(row_num + 1, 2, '', header_style)
    ws.write(row_num + 2, 1, '', header_style)
    ws.write(row_num + 2, 2, '', header_style)
    row_num += 3
    ws.write_merge(row_num, row_num + 2, 0, 0, '2.4', header_style)
    ws.write_merge(row_num, row_num, 2, 3, 'СӨХ-ийн гэрэлтүүлэг /2 тарифт/', header_style)
    ws.write(row_num + 1, 3, '-Өдрийн /06.00-21.00/', header_style)
    ws.write(row_num + 2, 3, '-Шөнийн /21.00-06.00/', header_style)
    ws.write(row_num, 1, '', header_style)
    ws.write(row_num + 1, 1, '', header_style)
    ws.write(row_num + 1, 2, '', header_style)
    ws.write(row_num + 2, 1, '', header_style)
    ws.write(row_num + 2, 2, '', header_style)
    row_num += 3
    ws.write_merge(row_num, row_num, 0, 0, '2.5', header_style)
    ws.write(row_num, 1, '', header_style)
    ws.write_merge(row_num, row_num, 2, 3, 'Цахилгаан тээвэр', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 0, 0, '2.6', header_style)
    ws.write(row_num + 1, 1, '', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 2, 3, 'Төмөр зам', header_style)
    ws.write_merge(row_num + 2, row_num + 2, 0, 0, '2.7', header_style)
    ws.write_merge(row_num + 2, row_num + 2, 1, 3, 'ЦЭХ-ийн чадлын төлбөр', header_style)
    ws.write_merge(row_num + 3, row_num + 3, 0, 0, '2.8', header_style)
    ws.write_merge(row_num + 3, row_num + 3, 1, 3, 'СЭХ-ийг дэмжих төлбөр', header_style)
    ws.write(row_num + 4, 0, '', orange_style)
    ws.write_merge(row_num + 4, row_num + 4, 1, 3, 'ААН-ийн нийт дүн', orange_style)
    row_num += 5
    ws.write(row_num, 0, '3', header_style)
    ws.write_merge(row_num, row_num, 1, 3, 'Ахуйн хэрэглэгч - Орон сууц', header_style)
    ws.write_merge(row_num + 1, row_num + 3, 0, 0, '3.1', header_style)
    ws.write(row_num + 2, 1, '', header_style)
    ws.write(row_num + 3, 1, '', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 1, 3, 'Энгийн тоолуур', header_style)
    ws.write_merge(row_num + 2, row_num + 2, 2, 3, 'Сарын хэрэглээний 150 кВтц хүртэлх', header_style)
    ws.write_merge(row_num + 3, row_num + 3, 2, 3, 'Сарын хэрэглээний 151 кВтц-с дээшхи', header_style)
    ws.write_merge(row_num + 4, row_num + 6, 0, 0, '3.2', header_style)
    ws.write(row_num + 4, 1, '', header_style)
    ws.write_merge(row_num + 4, row_num + 4, 2, 3, 'Орон сууц /2 тариф/', header_style)
    ws.write(row_num + 5, 3, '-Өдрийн /06.00-21.00/', header_style)
    ws.write(row_num + 6, 3, '-Шөнийн /21.00-06.00/', header_style)
    ws.write(row_num + 5, 1, '', header_style)
    ws.write(row_num + 6, 1, '', header_style)
    ws.write(row_num + 5, 2, '', header_style)
    ws.write(row_num + 6, 2, '', header_style)
    ws.write_merge(row_num + 7, row_num + 9, 0, 0, '3.3', header_style)
    ws.write_merge(row_num + 7, row_num + 7, 2, 3, 'Эмзэг бүлэг', header_style)
    ws.write(row_num + 7, 1, '', header_style)
    ws.write(row_num + 8, 1, '', header_style)
    ws.write(row_num + 8, 2, '', header_style)
    ws.write(row_num + 9, 1, '', header_style)
    ws.write(row_num + 9, 2, '', header_style)
    ws.write(row_num + 8, 3, '-хөнгөлөлттэй', header_style)
    ws.write(row_num + 9, 3, '-хөнгөлөлтгүй', header_style)
    ws.write(row_num + 10, 0, '3.4', header_style)
    ws.write_merge(row_num + 10, row_num + 10, 1, 3, 'Суурь хураамж', header_style)
    ws.write(row_num + 11, 0, '3.5', header_style)
    ws.write_merge(row_num + 11, row_num + 11, 1, 3, 'СЭХ-ийг дэмжих төлбөр', header_style)
    ws.write(row_num + 12, 0, '', orange_style)
    ws.write_merge(row_num + 12, row_num + 12, 1, 3, 'Орон сууцны хэрэглэгчийн нийт дүн', orange_style)
    row_num += 13
    ws.write(row_num, 0, '4', header_style)
    ws.write_merge(row_num, row_num, 1, 3, 'Ахуйн хэрэглэгч - Гэр хороолол', header_style)
    ws.write_merge(row_num + 1, row_num + 3, 0, 0, '4.1', header_style)
    ws.write(row_num + 2, 1, '', header_style)
    ws.write(row_num + 3, 1, '', header_style)
    ws.write_merge(row_num + 1, row_num + 1, 1, 3, 'Энгийн тоолуур', header_style)
    ws.write_merge(row_num + 2, row_num + 2, 2, 3, 'Сарын хэрэглээний 150 кВтц хүртэлх', header_style)
    ws.write_merge(row_num + 3, row_num + 3, 2, 3, 'Сарын хэрэглээний 151 кВтц-с дээшхи', header_style)
    ws.write_merge(row_num + 4, row_num + 6, 0, 0, '4.2', header_style)
    ws.write(row_num + 4, 1, '', header_style)
    ws.write_merge(row_num + 4, row_num + 4, 2, 3, 'Орон сууц /2 тариф/', header_style)
    ws.write(row_num + 5, 3, '-Өдрийн /06.00-21.00/', header_style)
    ws.write(row_num + 6, 3, '-Шөнийн /21.00-06.00/', header_style)
    ws.write(row_num + 5, 1, '', header_style)
    ws.write(row_num + 6, 1, '', header_style)
    ws.write(row_num + 5, 2, '', header_style)
    ws.write(row_num + 6, 2, '', header_style)
    ws.write_merge(row_num + 7, row_num + 9, 0, 0, '4.3', header_style)
    ws.write_merge(row_num + 7, row_num + 7, 2, 3, 'Эмзэг бүлэг', header_style)
    ws.write(row_num + 7, 1, '', header_style)
    ws.write(row_num + 8, 1, '', header_style)
    ws.write(row_num + 8, 2, '', header_style)
    ws.write(row_num + 9, 1, '', header_style)
    ws.write(row_num + 9, 2, '', header_style)
    ws.write(row_num + 8, 3, '-хөнгөлөлттэй', header_style)
    ws.write(row_num + 9, 3, '-хөнгөлөлтгүй', header_style)
    ws.write(row_num + 10, 0, '4.4', header_style)
    ws.write_merge(row_num + 10, row_num + 10, 1, 3, 'Суурь хураамж', header_style)
    ws.write(row_num + 11, 0, '4.5', header_style)
    ws.write_merge(row_num + 11, row_num + 11, 1, 3, 'СЭХ-ийг дэмжих төлбөр', header_style)
    ws.write(row_num + 12, 0, '', orange_style)
    ws.write_merge(row_num + 12, row_num + 12, 1, 3, 'Гэр хорооллын хэрэглэгчийн нийт дүн', orange_style)
    ws.write_merge(row_num + 13, row_num + 13, 0, 3, 'НИЙТ ДҮН', orange_style)
    row_num = 4

    # for row in rows
    for i in range(22):
        col_num = 4
        row_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)

    col_num = 4
    row_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)

    # for row in rows
    for i in range(12):
        col_num = 4
        row_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)

    col_num = 4
    row_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)

    # for row in rows
    for i in range(12):
        col_num = 4
        row_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)
        col_num += 1
        ws.write(row_num, col_num, 0, row_style)

    col_num = 4
    row_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)

    col_num = 4
    row_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)
    col_num += 1
    ws.write(row_num, col_num, 0, orange_style)

    wb.save(response)
    return response
