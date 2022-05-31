import xlwt
from apps.data.models import *
from django.shortcuts import HttpResponse


def report_contract_org(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="tseh-r_hangah_aan.xls"'

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

    ws.write(0, 4, 'ЦЭХ-ээр хангах гэрээ байгуулсан ААН-н мэдээлэл', title_style)

    row_num = 2
    row_counter = 0
    columns = ['№', 'Хэрэглэгчийн код', 'Байгууллагын нэр', 'Байгууллагын регистр', 'Хаяг', 'Утасны дугаар',
               'Мэйл хаяг', 'Гэрээ байгуулсан огноо',
               'Гэрээ дуусах огноо', 'Үйл ажиллагааны төрөл', 'Түрээслэгчийн утасны дугаар', 'Гэрээний дугаар']
    col_width = [int(5 * 260), int(14 * 260), int(35 * 260), int(14 * 260), int(40 * 260), int(10 * 260), int(25 * 260),
                 int(12 * 260),
                 int(12 * 260), int(35 * 260), int(15 * 260), int(25 * 260)]

    for col_num in range(len(columns)):
        ws.col(col_num).width = col_width[col_num]
        ws.write(row_num, col_num, columns[col_num], header_style)

    qry = """
        SELECT co.id, cu.code, cu.first_name, cu.last_name, cu.register
        , ad.address_name, cu.phone, cu.email, co.contract_made_date
        ,co.contract_expire_date, aan.name AS customer_type, cu.phone2, co.contract_number 
        FROM data_geree AS co 
        JOIN data_customer AS cu ON co.customer_code=cu.code 
        JOIN data_aanangilal AS aan ON cu.customer_type=aan.code 
        and cu.is_active = '1' 
        AND co.is_active = '1' 
        AND cu.customer_angilal = 0
        left JOIN data_address ad ON cu.id=ad.customer_id
        """

    rows = list(Geree.objects.raw(qry))

    for row in rows:
        row_num += 1
        row_counter += 1
        col_num = 0
        full_name = row.first_name + ' ' + row.last_name

        ws.write(row_num, col_num, row_counter, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.code, row_style)
        col_num += 1
        ws.write(row_num, col_num, full_name, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.register, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.address_name, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.phone, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.email, row_style)
        col_num += 1
        ws.write(row_num, col_num, str(row.contract_made_date.date()), row_style)
        col_num += 1
        ws.write(row_num, col_num, str(row.contract_expire_date.date()), row_style)
        col_num += 1
        ws.write(row_num, col_num, row.customer_type, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.phone2, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.contract_number, row_style)

    wb.save(response)
    return response


def report_contract_resident(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="tseh-r_hangah_ahui.xls"'

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

    ws.write(0, 4, 'ЦЭХ-ээр хангах гэрээ байгуулсан айл өрхийн мэдээлэл', title_style)

    row_num = 2
    row_counter = 0
    columns = ['№', 'Хэрэглэгчийн код', 'Хэрэглэгчийн овог нэр', 'Хэрэглэгчийн регистр', 'Хаяг', 'Утасны дугаар',
               'Мэйл хаяг', 'Гэрээ байгуулсан огноо',
               'Гэрээ дуусах огноо', 'Эзэмшигчийн төлөв', 'Түрээслэгчийн утасны дугаар', 'Гэрээний дугаар']
    col_width = [int(5 * 260), int(14 * 260), int(35 * 260), int(14 * 260), int(40 * 260), int(10 * 260), int(25 * 260),
                 int(12 * 260),
                 int(12 * 260), int(14 * 260), int(15 * 260), int(25 * 260)]

    for col_num in range(len(columns)):
        ws.col(col_num).width = col_width[col_num]
        ws.write(row_num, col_num, columns[col_num], header_style)

    qry = """
        SELECT co.id, cu.code, cu.first_name, cu.last_name, cu.register
        , a.address_name
        , cu.phone, cu.email, co.contract_made_date
        , co.contract_expire_date, ahui.name AS customer_type, cu.phone2, co.contract_number 
        FROM data_geree AS co 
        JOIN data_customer AS cu ON co.customer_code=cu.code 
        JOIN data_ahuinhereglegch AS ahui ON cu.customer_type=ahui.code 
        and cu.is_active = '1' 
        AND co.is_active = '1' 
        AND cu.customer_angilal = 1 
        left join data_address a on cu.id = a.customer_id
        """

    rows = list(Geree.objects.raw(qry))

    for row in rows:
        row_num += 1
        row_counter += 1
        col_num = 0
        full_name = row.first_name + ' ' + row.last_name

        ws.write(row_num, col_num, row_counter, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.code, row_style)
        col_num += 1
        ws.write(row_num, col_num, full_name, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.register, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.address_name, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.phone, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.email, row_style)
        col_num += 1
        ws.write(row_num, col_num, str(row.contract_made_date.date()), row_style)
        col_num += 1
        ws.write(row_num, col_num, str(row.contract_expire_date.date()), row_style)
        col_num += 1
        ws.write(row_num, col_num, row.customer_type, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.phone2, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.contract_number, row_style)

    wb.save(response)
    return response


def report_geree_3(request):
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="geree_duusch_bga.xls"'

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

    ws.write(0, 4, 'ЦЭХ-ээр хангах гэрээний хугацаа дуусч байгаа хэрэглэгчийн тайлан', title_style)
    ws.write(2, 5, 'Хамрах хугацаа: ' + start_date + ' - ' + end_date, xlwt.XFStyle())

    row_num = 3
    row_counter = 0
    columns = ['№', 'Гэрээний дугаар', 'Хэрэглэгчийн код', 'Хэрэглэгчийн нэр', 'Хаяг', 'Тэжээгдэж буй дэд станц',
               'Цахилгааны төлбөрийн үлдэгдэл (төгрөгөөр)', 'Гэрээний хугацаа дууссан огноо']
    col_width = [int(5 * 260), int(25 * 260), int(14 * 260), int(30 * 260), int(40 * 260), int(20 * 260), int(24 * 260),
                 int(12 * 260)]

    for col_num in range(len(columns)):
        ws.col(col_num).width = col_width[col_num]
        ws.write(row_num, col_num, columns[col_num], header_style)

    qry = """
        SELECT co.id, co.contract_number, cu.code, cu.first_name, cu.last_name
        , ad.address_name, ds.name AS dedstants
        , sum(a.pay_uld ) - sum(ifnull(p.uldegdel,0)) pay_uld
        , co.contract_expire_date 
        FROM data_geree AS co 
        JOIN data_customer AS cu ON co.customer_code=cu.code 
        JOIN data_address AS ad ON cu.id=ad.customer_id 
        JOIN data_dedstants AS ds ON co.dedstants_code=ds.code 
        and cu.is_active = '1' 
        AND co.contract_expire_date BETWEEN '""" + start_date + " 00:00:00.000000' AND '" + end_date + """ 23:59:59.999999'
        left join data_avlaga a on cu.id = a.customer_id and a.is_active=1 and a.pay_type=0
        left join data_payment p on cu.id=p.customer_id and p.is_active=1
        group by co.id
        , co.contract_number
        , cu.code
        , cu.first_name
        , cu.last_name
        , ad.address_name
        , ds.name 
        , co.contract_expire_date
        """

    rows = list(Geree.objects.raw(qry))

    for row in rows:
        row_num += 1
        row_counter += 1
        col_num = 0
        full_name = row.first_name + ' ' + row.last_name

        ws.write(row_num, col_num, row_counter, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.contract_number, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.code, row_style)
        col_num += 1
        ws.write(row_num, col_num, full_name, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.address_name, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.dedstants, row_style)
        col_num += 1
        ws.write(row_num, col_num, row.pay_uld, row_style)
        col_num += 1
        ws.write(row_num, col_num, str(row.contract_expire_date.date()), row_style)

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
