import logging
from calendar import monthrange

import xlwt
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from datetime import date
from apps.data.models import TooluurCustomer, Bichilt

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


def report_bichilt_2(request):
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

    columns = ['№', 'Хэрэглэгчийн код', 'Хэрэглэгчийн нэр', 'Хаяг', 'Эхний үлдэгдэл', 'Бичилт', 'Орлого', 'Эцсийн үлдэгдэл']
    col_width = [int(5 * 260), int(12 * 260), int(30 * 260), int(40 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260)]

    for col_num in range(len(columns)):
        ws.col(col_num).width = col_width[col_num]
        ws.write(row_num, col_num, columns[col_num], header_style)

    start_date = start_date + ' 00:00:00.000000'
    end_date = end_date + ' 23:59:59.999999'

    qry = """SELECT tocu.id, cust.code, cust.register, cust.last_name, cust.first_name, cust.customer_angilal, addr.address_name, cust.email,
        IFNULL((SELECT SUM(aveh.heregleenii_tulbur) + SUM(aveh.uilchilgeenii_tulbur) + SUM(aveh.barimt_une)
        FROM data_avlaga aveh WHERE aveh.created_date <= '"""+start_date+""""' AND aveh.is_active = '1' AND tocu.customer_id = aveh.customer_id),
        IFNULL((SELECT -paym.uldegdel FROM data_payment paym WHERE paym.customer_id = tocu.customer_id), 0.00)) AS ehnii,
        IFNULL((SELECT (SUM(avbi.heregleenii_tulbur) + SUM(avbi.uilchilgeenii_tulbur) + SUM(avbi.ald_hemjee) + SUM(avbi.barimt_une)) FROM data_avlaga avbi
        WHERE avbi.created_date >= '"""+start_date+""""' AND avbi.created_date <= '"""+end_date+""""' AND avbi.is_active = '1' AND tocu.customer_id = avbi.customer_id), 0.00) AS bichilt,
        IFNULL((SELECT SUM(pahi.pay_total) FROM data_paymenthistory pahi WHERE pahi.pay_date >= '"""+start_date+""""' AND pahi.is_active = '1' AND tocu.customer_id = pahi.customer_id), 0.00) AS payment,
        ((IFNULL((SELECT SUM(pahi.pay_total) FROM data_paymenthistory pahi WHERE pahi.pay_date >= '"""+start_date+""""' AND pahi.is_active = '1' AND tocu.customer_id = pahi.customer_id), 0.00) -
        IFNULL((SELECT SUM(aveh.heregleenii_tulbur) + SUM(aveh.uilchilgeenii_tulbur) + SUM(aveh.barimt_une)
        FROM data_avlaga aveh WHERE aveh.created_date <= '"""+start_date+""""' AND aveh.is_active = '1' AND tocu.customer_id = aveh.customer_id),
        IFNULL((SELECT -paym.uldegdel FROM data_payment paym WHERE paym.customer_id = tocu.customer_id), 0.00))-
        IFNULL((SELECT (SUM(avbi.heregleenii_tulbur) + SUM(avbi.uilchilgeenii_tulbur) + SUM(avbi.ald_hemjee) + SUM(avbi.barimt_une)) FROM data_avlaga avbi
        WHERE avbi.created_date >= '"""+start_date+""""' AND avbi.created_date <= '"""+end_date+""""' AND avbi.is_active = '1' AND tocu.customer_id = avbi.customer_id), 0.00)) * -1) AS balance,
        (SELECT COUNT(tc.id) FROM data_tooluurcustomer tc WHERE tc.customer_id = cust.id) AS tool_count
        FROM data_tooluurcustomer tocu JOIN data_customer cust ON tocu.customer_id = cust.id
        LEFT JOIN data_avlaga avla ON tocu.customer_id = avla.customer_id LEFT JOIN data_address addr ON cust.id = addr.customer_id
        WHERE tocu.is_active = '1'"""

    ah_total = [0, 0, 0, 0]
    try:
        row_num += 1
        bichilts = TooluurCustomer.objects.raw(qry + " AND cust.customer_angilal='1' GROUP BY tocu.customer_id;")
        if bichilts is not None:
            for bichilt in bichilts:
                row_counter += 1
                ws.write(row_num, 0, row_counter, row_style)
                ws.write(row_num, 1, bichilt.code, row_style)
                ws.write(row_num, 2, bichilt.first_name + " " +bichilt.last_name, row_style)
                ws.write(row_num, 3, bichilt.address_name, row_style)
                ws.write(row_num, 4, round(bichilt.ehnii, 2) if bichilt.ehnii else 0, row_style)
                ah_total[0] += round(bichilt.ehnii, 2) if bichilt.ehnii else 0
                ws.write(row_num, 5, round(bichilt.bichilt, 2) if bichilt.bichilt else 0, row_style)
                ah_total[1] += round(bichilt.bichilt, 2) if bichilt.bichilt else 0
                ws.write(row_num, 6, round(bichilt.payment, 2) if bichilt.payment else 0, row_style)
                ah_total[2] += round(bichilt.payment, 2) if bichilt.payment else 0
                balance = (float(bichilt.ehnii) if bichilt.ehnii else 0) + (float(bichilt.bichilt) if bichilt.bichilt else 0)
                balance = float(balance) - (float(bichilt.payment) if bichilt.payment else 0)
                ws.write(row_num, 7, round(balance, 2), row_style)
                ah_total[3] += round(balance, 2)
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
        bichilts = TooluurCustomer.objects.raw(qry + " AND cust.customer_angilal='0' GROUP BY cust.id;")
        if bichilts is not None:
            for bichilt in bichilts:
                row_counter_aan += 1
                ws.write(row_num, 0, row_counter_aan, row_style)
                ws.write(row_num, 1, bichilt.code, row_style)
                ws.write(row_num, 2, bichilt.first_name + " " + bichilt.last_name, row_style)
                ws.write(row_num, 3, bichilt.address_name, row_style)
                ws.write(row_num, 4, round(bichilt.ehnii, 2) if bichilt.ehnii else 0, row_style)
                aan_total[0] += round(bichilt.ehnii, 2) if bichilt.ehnii else 0
                ws.write(row_num, 5, round(bichilt.bichilt, 2) if bichilt.bichilt else 0, row_style)
                aan_total[1] += round(bichilt.bichilt, 2) if bichilt.bichilt else 0
                ws.write(row_num, 6, round(bichilt.payment, 2) if bichilt.payment else 0, row_style)
                aan_total[2] += round(bichilt.payment, 2) if bichilt.payment else 0
                balance = (float(bichilt.ehnii) if bichilt.ehnii else 0) + (
                float(bichilt.bichilt) if bichilt.bichilt else 0)
                balance = float(balance) - (float(bichilt.payment) if bichilt.payment else 0)
                ws.write(row_num, 7, round(balance, 2), row_style)
                aan_total[3] += round(balance, 2)
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
    ws.write_merge(row_num, row_num, 1, 2, 'Нийт:  Хэрэглэгчийн тоо: ' + str(row_counter_aan+row_counter), row_style)
    ws.write(row_num, 3, '', row_style)
    ws.write(row_num, 4, aan_total[0]+ah_total[0], header_style)
    ws.write(row_num, 5, aan_total[1]+ah_total[1], header_style)
    ws.write(row_num, 6, aan_total[2]+ah_total[2], header_style)
    ws.write(row_num, 7, aan_total[3]+ah_total[3], header_style)

    wb.save(response)
    return response


def report_bichilt_3(request):
    year = request.POST['year']
    month = request.POST['month']

    if len(month) == 2:
        if '0' == month[0]:
            month = month[1]

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="'+year+'_onii_'+ month +'_sariin_tsahilgaan_erchim_huchnii_bichilt.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 1, year+' оны '+month+'-р сарын цахилгаан эрчим хүчний бичилт', title_style)
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

    qry = """SELECT bich.id, SUM(bich.total_price) AS total_price FROM data_bichilt bich
        JOIN data_tooluurcustomer tocu ON bich.tooluur_id = tocu.id
        JOIN data_customer cust ON tocu.customer_id = cust.id
        WHERE bich.is_active='1' AND bich.year='"""+year+"""' AND bich.month='"""+month+"""' AND cust.customer_angilal = '1'"""

    try:
        bichilts = Bichilt.objects.raw(qry)
        if bichilts is not None:
            for bichilt in bichilts:
                ah_total_bichilt = round(float(0 if bichilt.total_price is None else bichilt.total_price), 2)
                ah_total_nuatgui = round(float(0 if bichilt.total_price is None else bichilt.total_price) / 1.1, 2)
                ah_total_nuat = round(float(0 if bichilt.total_price is None else bichilt.total_price) - (float(0 if bichilt.total_price is None else bichilt.total_price) / 1.1), 2)
                ws.write(row_num, 3, ah_total_bichilt, header_style)
                ws.write(row_num, 4, ah_total_nuatgui, header_style)
                ws.write(row_num, 5, ah_total_nuat, header_style)
    except ObjectDoesNotExist as e:
        logging.error('"Bichilt" object has no objects: %s', e)

    row_num += 1
    ws.write_merge(row_num, row_num, 0, 5, 'ААН', header_style)

    aan_total_bichilt = 0
    aan_total_nuatgui = 0
    aan_total_nuat = 0

    qry = """SELECT bich.id, cust.code, cust.first_name, cust.register, SUM(bich.total_price) AS total_price
        FROM data_bichilt bich JOIN data_tooluurcustomer tocu ON bich.tooluur_id=tocu.id JOIN data_customer cust ON tocu.customer_id=cust.id
        WHERE bich.is_active='1' AND bich.year='"""+year+"""' AND bich.month='"""+month+"""' AND cust.customer_angilal='0' GROUP BY tocu.customer_id ORDER BY cust.code"""

    row_num += 1
    try:
        bichilts = Bichilt.objects.raw(qry)
        if bichilts is not None:
            for bichilt in bichilts:
                ws.write(row_num, 0, bichilt.code, row_style)
                ws.write(row_num, 1, bichilt.first_name, row_style)
                ws.write(row_num, 2, bichilt.register, row_style)

                aan_total_bichilt += round(float(0 if bichilt.total_price is None else bichilt.total_price), 2)
                aan_total_nuatgui += round(float(0 if bichilt.total_price is None else bichilt.total_price) / 1.1, 2)
                aan_total_nuat += round(float(0 if bichilt.total_price is None else bichilt.total_price) - (float(0 if bichilt.total_price is None else bichilt.total_price) / 1.1), 2)

                ws.write(row_num, 3, round(float(0 if bichilt.total_price is None else bichilt.total_price), 2), row_style)
                ws.write(row_num, 4, round(float(0 if bichilt.total_price is None else bichilt.total_price) / 1.1, 2), row_style)
                ws.write(row_num, 5, round(float(0 if bichilt.total_price is None else bichilt.total_price) - (float(0 if bichilt.total_price is None else bichilt.total_price) / 1.1), 2), row_style)
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


def report_bichilt_4(request):
    start_year = request.POST['start_year']
    start_month = request.POST['start_month']
    start_date = start_year+'-'+start_month+'-01'
    end_year = request.POST['end_year']
    end_month = request.POST['end_month']
    month_last = str(monthrange(int(end_year), int(end_month))).split(',')
    month_last = str(month_last[1].replace(' ', '').replace(')', ''))
    end_date = end_year+'-'+end_month+'-'+month_last

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="AAN_baiguullaguudiin_heregleenii_delgerengui_sudalgaa_Chadal_Hyazgaar_Bichilt.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sheet1')

    ws.write(0, 5, 'ААН байгууллагуудын хэрэглээний дэлгэрэнгүй судалгаа /Чадлын хязгаар, Бичилт/', title_style)
    ws.write(2, 0, 'Тайлангийн хамрах хугацаа : ' + start_date + ' - ' + end_date, xlwt.XFStyle())
    ws.write(2, 13, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())

    col_widths = [int(5 * 260), int(20 * 260), int(15 * 260), int(10 * 260), int(15 * 260), int(15 * 260), int(10 * 260), int(15 * 260), int(15 * 260), int(10 * 260), int(15 * 260), int(15 * 260), int(10 * 260), int(15 * 260), int(15 * 260)]
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

    row_titles = ['0-1000', '1001-5000', '5001-10000', '10001-50000', '50001-200000', '200001-500000', '500001-2000000', '2 саяас дээш']

    row_num += 2
    for i in range(8):
        ws.write(row_num + i, 0, i + 1, header_style)
        ws.write(row_num + i, 1, row_titles[i], row_style)
        ws.write(row_num + i, 2, 'кВтц', row_style)

    start_date = start_date + ' 00:00:00.000000'
    end_date = end_date + ' 23:59:59.999999'

    qry = """SELECT bich.id, COUNT(tocu.customer_id) AS too, IF(COUNT(tocu.customer_id)=0, 0,
        (SUM(bich.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)))) AS niit_hereglee,
        IF(COUNT(tocu.customer_id)=0, 0, SUM(bich.total_price)) AS mungun_dun FROM data_bichilt bich
        JOIN data_tooluurcustomer tocu ON tocu.id=bich.tooluur_id LEFT JOIN data_transformator guid ON tocu.guidliin_trans_id = guid.id
        LEFT JOIN data_transformator huch ON tocu.huchdeliin_trans_id = huch.id JOIN data_customer cust ON tocu.customer_id=cust.id
        WHERE bich.is_active='1' AND (bich.bichilt_date BETWEEN '"""+start_date+"""' AND '"""+end_date+"""') AND cust.customer_angilal = '0'"""

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


def report_bichilt_6(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="AAN_baiguullaguudiin_heregleenii_sudalgaa_sar_bureer.xls"'

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
    columns = ['1 сар', '2 сар', '3 сар', '4 сар', '5 сар', '6 сар', '7 сар', '8 сар', '9 сар', '10 сар', '11 сар', '12 сар', ]
    col_with = [int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260),
                int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(15 * 260)]
    for col_num in range(len(columns)):
        ws.col(col_num + 3).width = col_with[col_num]
        ws.write(row_num, (col_num + 3), columns[col_num], row_style)
    ws.col(15).width = int(15 * 260)
    ws.write(row_num, 15, 'Нийт', header_style)

    current_year = str(date.today().year)

    qry = """SELECT bich.id, cust.code, cust.first_name,
        IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='"""+current_year+"""' AND b.month='1')), 0) AS jan,
        IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='"""+current_year+"""' AND b.month='2')), 0) AS feb,
        IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='"""+current_year+"""' AND b.month='3')), 0) AS mar,
        IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='"""+current_year+"""' AND b.month='4')), 0) AS apr,
        IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='"""+current_year+"""' AND b.month='5')), 0) AS may,
        IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='"""+current_year+"""' AND b.month='6')), 0) AS jun,
        IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='"""+current_year+"""' AND b.month='7')), 0) AS jul,
        IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='"""+current_year+"""' AND b.month='8')), 0) AS aug,
        IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='"""+current_year+"""' AND b.month='9')), 0) AS sep,
        IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='"""+current_year+"""' AND b.month='10')), 0) AS oct,
        IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='"""+current_year+"""' AND b.month='11')), 0) AS nov,
        IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='"""+current_year+"""' AND b.month='12')), 0) AS decem
        FROM data_bichilt bich JOIN data_tooluurcustomer tocu ON bich.tooluur_id=tocu.id LEFT JOIN data_transformator guid ON tocu.guidliin_trans_id = guid.id
        LEFT JOIN data_transformator huch ON tocu.huchdeliin_trans_id = huch.id JOIN data_customer cust ON tocu.customer_id=cust.id
        JOIN data_address addr ON cust.id=addr.customer_id WHERE bich.is_active='1' AND cust.customer_angilal='0'"""

    row_num = 5
    row_counter = 0
    total_ktv_month = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ws.write_merge(row_num, row_num, 0, 15, 'Вива сити', header_style)
    try:
        bichilts = Bichilt.objects.raw(qry + " AND addr.hothon_code = '1341' GROUP BY tocu.customer_id")
        if bichilts is not None:
            for bichilt in bichilts:
                row_counter += 1
                row_num += 1
                total_ktv_year = 0
                col_num = 0
                ws.write(row_num, col_num, row_counter, row_style)
                col_num += 1
                ws.write(row_num, col_num, bichilt.code, row_style)
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
                total_ktv_month[8] += round(bichilt.sep, 2)
                total_ktv_year += round(bichilt.sep, 2)
                ws.write(row_num, col_num, round(bichilt.sep, 2), row_style)
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
    ws.write_merge(row_num, row_num, 0, 15, 'Белла виста', header_style)
    try:
        bichilts = Bichilt.objects.raw(qry + " AND addr.hothon_code = '13112' OR addr.hothon_code = '13113' GROUP BY tocu.customer_id")
        if bichilts is not None:
            for bichilt in bichilts:
                row_counter += 1
                row_num += 1
                total_ktv_year = 0
                col_num = 0
                ws.write(row_num, col_num, row_counter, row_style)
                col_num += 1
                ws.write(row_num, col_num, bichilt.code, row_style)
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


def report_bichilt_7(request):
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

    row_titles = ['0-1000', '1001-5000', '5001-10000', '10001-50000', '50001-200000', '200001-500000', '500001-2000000', '2 саяас дээш']

    row_num += 2
    for i in range(8):
        ws.write(row_num + i, 0, i + 1, header_style)
        ws.write(row_num + i, 1, row_titles[i], row_style)
        ws.write(row_num + i, 2, 'кВтц', row_style)

    start_date = start_date + ' 00:00:00.000000'
    end_date = end_date + ' 23:59:59.999999'

    qry = """SELECT bich.id, COUNT(tocu.customer_id) AS too, IF(COUNT(tocu.customer_id)=0, 0,
            (SUM(bich.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)))) AS niit_hereglee,
            IF(COUNT(tocu.customer_id)=0, 0, SUM(bich.total_price)) AS mungun_dun FROM data_bichilt bich
            JOIN data_tooluurcustomer tocu ON tocu.id=bich.tooluur_id LEFT JOIN data_transformator guid ON tocu.guidliin_trans_id = guid.id
            LEFT JOIN data_transformator huch ON tocu.huchdeliin_trans_id = huch.id JOIN data_customer cust ON tocu.customer_id=cust.id
            WHERE bich.is_active='1' AND (bich.bichilt_date BETWEEN '""" + start_date + """' AND '""" + end_date + """') AND cust.customer_angilal = '1'"""

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


def report_bichilt_9(request):
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

    qry = """SELECT bich.id, cust.code, cust.first_name,
            IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='""" + current_year + """' AND b.month='1')), 0) AS jan,
            IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='""" + current_year + """' AND b.month='2')), 0) AS feb,
            IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='""" + current_year + """' AND b.month='3')), 0) AS mar,
            IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='""" + current_year + """' AND b.month='4')), 0) AS apr,
            IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='""" + current_year + """' AND b.month='5')), 0) AS may,
            IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='""" + current_year + """' AND b.month='6')), 0) AS jun,
            IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='""" + current_year + """' AND b.month='7')), 0) AS jul,
            IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='""" + current_year + """' AND b.month='8')), 0) AS aug,
            IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='""" + current_year + """' AND b.month='9')), 0) AS sep,
            IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='""" + current_year + """' AND b.month='10')), 0) AS oct,
            IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='""" + current_year + """' AND b.month='11')), 0) AS nov,
            IFNULL(SUM((SELECT SUM(b.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) FROM data_bichilt b WHERE b.tooluur_id=tocu.id AND b.year='""" + current_year + """' AND b.month='12')), 0) AS decem
            FROM data_bichilt bich JOIN data_tooluurcustomer tocu ON bich.tooluur_id=tocu.id LEFT JOIN data_transformator guid ON tocu.guidliin_trans_id = guid.id
            LEFT JOIN data_transformator huch ON tocu.huchdeliin_trans_id = huch.id JOIN data_customer cust ON tocu.customer_id=cust.id
            JOIN data_address addr ON cust.id=addr.customer_id WHERE bich.is_active='1' AND cust.customer_angilal='1'"""

    row_num = 5
    row_counter = 0
    total_ktv_month = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ws.write_merge(row_num, row_num, 0, 15, 'Вива сити', header_style)
    try:
        bichilts = Bichilt.objects.raw(qry + " AND addr.hothon_code = '1341' GROUP BY tocu.customer_id")
        if bichilts is not None:
            for bichilt in bichilts:
                row_counter += 1
                row_num += 1
                total_ktv_year = 0
                col_num = 0
                ws.write(row_num, col_num, row_counter, row_style)
                col_num += 1
                ws.write(row_num, col_num, bichilt.code, row_style)
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
    ws.write_merge(row_num, row_num, 0, 15, 'Белла виста', header_style)
    try:
        bichilts = Bichilt.objects.raw(qry + " AND addr.hothon_code = '13112' OR addr.hothon_code = '13113' GROUP BY tocu.customer_id")
        if bichilts is not None:
            for bichilt in bichilts:
                row_counter += 1
                row_num += 1
                total_ktv_year = 0
                col_num = 0
                ws.write(row_num, col_num, row_counter, row_style)
                col_num += 1
                ws.write(row_num, col_num, bichilt.code, row_style)
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
        bichilts = Bichilt.objects.raw(qry + " AND addr.hothon_code = '13114' GROUP BY tocu.customer_id")
        if bichilts is not None:
            for bichilt in bichilts:
                row_counter += 1
                row_num += 1
                total_ktv_year = 0
                col_num = 0
                ws.write(row_num, col_num, row_counter, row_style)
                col_num += 1
                ws.write(row_num, col_num, bichilt.code, row_style)
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
    ws.write_merge(row_num, row_num, 0, 15, 'Асем вилла', header_style)
    try:
        bichilts = Bichilt.objects.raw(qry + " AND addr.hothon_code = '12111' GROUP BY tocu.customer_id")
        if bichilts is not None:
            for bichilt in bichilts:
                row_counter += 1
                row_num += 1
                total_ktv_year = 0
                col_num = 0
                ws.write(row_num, col_num, row_counter, row_style)
                col_num += 1
                ws.write(row_num, col_num, bichilt.code, row_style)
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