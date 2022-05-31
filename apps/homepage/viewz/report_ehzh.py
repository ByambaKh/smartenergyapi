import logging
import xlwt
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from apps.data.models import PaymentHistory, Avlaga, Customer, Bichilt, HasagdahTooluur, TooluurHistory, PriceTariff, PriceHistory, CustomerUilchilgeeTulbur, HasagdahHistory
from apps.homepage.templatetags.homepage_tags_new import get_niitiin
from decimal import Decimal
from datetime import datetime

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


def report_ehzh_3(request):
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
        qry_nt = " pay_date >= '" + str(int(year) - 1) + "-01-01' AND pay_date<=LAST_DAY('" + str(int(year) - 1) + "-03-01')"
        qry_nt_now = " pay_date >= '" + year + "-01-01' AND pay_date<=LAST_DAY('" + year + "-03-01')"
        qry_date = " pahi.pay_date >= '" + str(int(year) - 1) + "-01-01' AND pahi.pay_date<=LAST_DAY('" + str(int(year) - 1) + "-03-01')"
        qry_now = " pahi.pay_date >= '" + year + "-01-01' AND pahi.pay_date<=LAST_DAY('" + year + "-03-01')"
    elif season == '2':
        qry_nt = "pay_date >= '" + str(int(year) - 1) + "-04-01' AND pay_date<=LAST_DAY('" + str(int(year) - 1) + "-06-01')"
        qry_nt_now = " pay_date >= '" + year + "-04-01' AND pay_date<=LAST_DAY('" + year + "-06-01')"
        qry_date = " pahi.pay_date >= '" + str(int(year) - 1) + "-04-01' AND pahi.pay_date<=LAST_DAY('" + str(int(year) - 1) + "-06-01')"
        qry_now = " pahi.pay_date >= '" + year + "-04-01' AND pahi.pay_date<=LAST_DAY('" + year + "-06-01')"
    elif season == '3':
        qry_nt = "pay_date >= '" + str(int(year) - 1) + "-07-01' AND pay_date<=LAST_DAY('" + str(int(year) - 1) + "-09-01')"
        qry_nt_now = " pay_date >= '" + year + "-07-01' AND pay_date<=LAST_DAY('" + year + "-09-01')"
        qry_date += " pahi.pay_date >= '" + str(int(year) - 1) + "-07-01' AND pahi.pay_date<=LAST_DAY('" + str(int(year) - 1) + "-09-01')"
        qry_now = " pahi.pay_date >= '" + year + "-07-01' AND pahi.pay_date<=LAST_DAY('" + year + "-09-01')"
    elif season == '4':
        qry_nt = "pay_date >= '" + str(int(year) - 1) + "-10-01' AND pay_date<=LAST_DAY('" + str(int(year) - 1) + "-12-01')"
        qry_nt_now = " pay_date >= '" + year + "-10-01' AND pay_date<=LAST_DAY('" + year + "-12-01')"
        qry_date = " pahi.pay_date >= '" + str(int(year) - 1) + "-10-01' AND pahi.pay_date<=LAST_DAY('" + str(int(year) - 1) + "-12-01')"
        qry_now = " pahi.pay_date >= '" + year + "-10-01' AND pahi.pay_date<=LAST_DAY('" + year + "-12-01')"
    um_on_ul = [0, 0, 0, 0, 0]
    try:
        histories = PaymentHistory.objects.raw(qry + qry_nt)
        histories_os = PaymentHistory.objects.raw(qry_os + qry_date)
        histories_ub = PaymentHistory.objects.raw(qry_ub + qry_date)
        histories_hu = PaymentHistory.objects.raw(qry_hu + qry_date)
        histories_tb = PaymentHistory.objects.raw(qry_tb + qry_date)
        for history, history_os, history_ub, history_hu, history_tb in zip(histories, histories_os, histories_ub, histories_hu, histories_tb):
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
            for avlaga, avlaga_os, avlaga_ub, avlaga_hu, avlaga_tb in zip(avlagas, avlagas_os, avlagas_ub, avlagas_hu, avlagas_tb):
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
    ws.write_merge(row_num, row_num, 0, 6, 'Жич: Авлагын мэдээнд онцгой өөрчлөлт гарсан бол нэмэлт тайлбартайгаар ирүүлнэ.', text_style)
    row_num += 4
    ws.write_merge(row_num, row_num, 4, 9, 'Гүйцэтгэх захирал: ......................... /' + ex_dir + '/', text_style)
    row_num += 2
    ws.write_merge(row_num, row_num, 4, 9, 'Албаны менежер: ......................... /' + dep_man + '/', text_style)
    row_num += 2
    ws.write_merge(row_num, row_num, 4, 9, 'Борлуулалт тооцооны ахлах инженер: ......................... /' + sale_est_eng + '/', text_style)

    wb.save(response)
    return response


def report_ehzh_4(request):
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


def report_ehzh_5(request):
    year = request.POST['year']

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Erchim_Suljee_XXK_' + year + '_onii_borluulaltiin_orlogiin_medee.xls"'

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


    ####################################################################################################################

    head_tooluurs = []
    try:
        qry = "SELECT hato.id, hato.head_tool_cus_id FROM data_hasagdahtooluur hato GROUP BY hato.head_tool_cus_id;"
        hasagdah_tooluurs = list(HasagdahTooluur.objects.raw(qry))
        for hasagdah_tooluur in hasagdah_tooluurs:
            head_tooluurs.append(hasagdah_tooluur.head_tool_cus_id)
    except ObjectDoesNotExist:
        print("HasagdahTooluur does not exist a object!")

    uil_count = 0
    uil_total_kvts = 0
    uil_total_price = 0
    uil_total_avg = 0

    try:
        qry = """SELECT bich.id, tocu.id AS head_tocu_id, (SELECT COUNT(*) AS uil_count FROM data_customer cu WHERE cu.customer_type = '2') AS uil_count, SUM(bich.total_price) / 1000 AS uil_total_price,
            SUM(bich.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) / 1000 AS uil_total_kvts,
            SUM(bich.total_price) / SUM(bich.total_diff * IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) AS uil_total_avg
            FROM data_bichilt bich JOIN data_tooluurcustomer tocu ON bich.tooluur_id = tocu.id
            LEFT JOIN data_transformator guid ON tocu.guidliin_trans_id = guid.id LEFT JOIN data_transformator huch ON tocu.huchdeliin_trans_id = huch.id
            JOIN data_customer cust ON tocu.customer_id = cust.id WHERE cust.customer_type = '2' AND bich.year = '""" + year + """' GROUP BY tocu.id;"""
        bichilts = Bichilt.objects.raw(qry)
        for bichilt in bichilts:
            uil_count = bichilt.uil_count
            if bichilt.head_tocu_id in head_tooluurs:
                chtcs = HasagdahTooluur.objects.filter(head_tool_cus=bichilt.head_tocu_id)
                head_tool_cust = chtcs.first().head_tool_cus
                head_tool_cust2 = chtcs.first().head_tool_cus2

                amp_coff = huch_coff = 1
                if head_tool_cust.guidliin_trans != None and head_tool_cust.guidliin_trans != '':
                    amp_coff = round(float(head_tool_cust.guidliin_trans.multiply_coef if head_tool_cust.guidliin_trans.multiply_coef else 1), 2)
                if head_tool_cust.huchdeliin_trans != None and head_tool_cust.huchdeliin_trans != '':
                    huch_coff = round(float(head_tool_cust.huchdeliin_trans.multiply_coef if head_tool_cust.huchdeliin_trans.multiply_coef else 1), 2)

                if head_tool_cust.tooluur.tariff == "0":
                    total_diff = round(float(bichilt.total_diff) * amp_coff * huch_coff, 2)

            else:
                uil_total_kvts += bichilt.uil_total_kvts
                uil_total_price += bichilt.uil_total_price
                uil_total_avg += bichilt.uil_total_avg
    except ObjectDoesNotExist:
        print("Bichilt does not exist a object!")
    ws.write(5, 11, uil_count, row_style)
    ws.write(5, 12, round(uil_total_kvts, 2), row_style)
    ws.write(5, 13, round(uil_total_price, 2), row_style)
    ws.write(5, 14, round(uil_total_avg, 2), row_style)

    ####################################################################################################################


    # for row in rows
    # row_num = 4
    # for i in range(22):
    #     col_num = 4
    #     row_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #
    # col_num = 4
    # row_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    #
    # # for row in rows
    # for i in range(12):
    #     col_num = 4
    #     row_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #
    # col_num = 4
    # row_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    #
    # # for row in rows
    # for i in range(12):
    #     col_num = 4
    #     row_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #     col_num += 1
    #     ws.write(row_num, col_num, 0, row_style)
    #
    # col_num = 4
    # row_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    #
    # col_num = 4
    # row_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)
    # col_num += 1
    # ws.write(row_num, col_num, 0, orange_style)

    wb.save(response)
    return response


def report_ehzh_6(request):
    year = request.POST['year']
    ex_dir = request.POST['ex_dir']
    dep_man = request.POST['dep_man']
    sale_est_eng = request.POST['sale_est_eng']

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Erchim_suljee_XXK_' + year + '_onii_TSEH_heregleenii_butets_borluulaltiin_orlogiin_medee_2.xls"'

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
    ws.write_merge(row_num, row_num, 3, 12, 'Борлуулалт тооцооны ахлах инженер: ......................... /' + sale_est_eng + '/', text_style)

    wb.save(response)
    return response

def report_negtgel(request):
    year = request.POST['year']
    month = request.POST['month']
    # ex_dir = request.POST['ex_dir']
    # dep_man = request.POST['dep_man']
    # sale_est_eng = request.POST['sale_est_eng']
    cycles = request.POST.getlist('cycles', '')
    # for cycle in cycles:
    #     print(cycle)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="negtgel.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Тайлан')

    ws.write(0, 4, 'Ухаалаг эрчим хүч ХХК -ийн '+str(year)+' оны '+str(month)+'-р сарын нэгтгэл тайлан',
             title_style)
    # ws.write(2, 0, 'Хэрэглэгчдэд борлуулах цахилгаан эрчим хүч', title_style)
    ws.write(2, 14, date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())

    columns = ['Д/д', 'ААН-ийн нэр', 'Хэрэглээ','Төг', 'Бодит төг', 'Чадлын тариф', 'Сэргээгдэх', 'Баримтын үнэ',
               'Суурь хураамж', 'Дэвтрийн үнэ', 'ТВ-ийн хураамж', 'Техник үйлчилгээ', 'НӨАТ', 'Нийт дүн /төг/']
    col_width = [int(5 * 260), int(30 * 260), int(14 * 260),int(14 * 260), int(14 * 260), int(14 * 260), int(14 * 260), int(14 * 260),
                 int(14 * 260), int(14 * 260), int(14 * 260), int(14 * 260), int(14 * 260), int(14 * 260)]

    hothon_list_all = []
    hothon_codes = []
    row_num = 4
    for col_num in range(len(columns)):
        ws.col(col_num).width = col_width[col_num]
        ws.write(row_num, col_num, columns[col_num], header_style)

    row_num += 1

    res_list = get_avlaga_list(year, month, cycles)
    count = 1
    sum1 = ['', 'ААН-ийн дүн',0,0,0,0,0,0,0,0,0,0,0,0]
    sum2 = ['', 'Ахуйн дүн',0,0,0,0,0,0,0,0,0,0,0,0]
    for data in res_list:

        col_num = 0
        tooluurs = TooluurHistory.objects.filter(customer_code = data.code, year = year, month = month)
        if data.customer_angilal == '0':
            tariff = PriceTariff.objects.filter(une_type=0)[:1].get()

            total_diff = 0
            diff_cost = 0
            serg_cost = 0
            chadal_cost = 0
            if(float(data.ten) > 0):
                chadal_cost = Decimal(data.ten)
            barimt_une = int(float(data.barimt_une) / 1.1)

            suuri_une = 0
            devter_une = 0

            real_cost = 0

            try:
                devter = CustomerUilchilgeeTulbur.objects.filter(customer__code = data.code, year = year, month = month,uilchilgee_id = 5).first()
                devter_une = devter.payment
            except Exception:
                devter_une = 0
            tv = 0
            try:
                uilch = int(float(data.uilchilgeenii_tulbur))
            except Exception:
                uilch = 0
            if tooluurs is not None:
                for tooluur in tooluurs:
                    price = PriceHistory.objects.filter(number = tooluur.number, customer_code = data.code, year = year, month = month).first()
                    total_diff += tooluur.total_diff_coef
                    diff_cost += (tooluur.day_diff_coef * tariff.odor_une) + (tooluur.night_diff_coef * tariff.shono_une) + (tooluur.rush_diff_coef * tariff.orgil_une)
                    serg_cost += (tooluur.day_diff_coef * tariff.serg_une) + (
                    tooluur.night_diff_coef * tariff.serg_une) + (tooluur.rush_diff_coef * tariff.serg_une)

                    if price is not None and price.chadal_price is not None:
                        chadal_cost += price.chadal_price




            hasagdah = HasagdahHistory.objects.filter(customer_code=data.code, year=year, month=month)

            if hasagdah is not None:
                #print(len(hasagdah))
                for htooluur in hasagdah:
                    h_tooluur = TooluurHistory.objects.filter(id=int(htooluur.child_tool_his)).first()

                    if h_tooluur is not None:
                        #h_price = PriceHistory.objects.filter(number=h_tooluur.number, year=year, month=month).first()

                        total_diff = total_diff - h_tooluur.total_diff_coef
                        # if h_price.chadal_price is not None:
                        #     print(h_price.chadal_price)
                        chadal_cost = chadal_cost - htooluur.chadal_price

                        h_diff_cost = (h_tooluur.total_diff_coef * tariff.odor_une)
                        h_serg_cost = (h_tooluur.total_diff_coef * tariff.serg_une)

                        diff_cost = diff_cost - h_diff_cost
                        serg_cost = serg_cost - h_serg_cost

            real_cost = diff_cost + serg_cost


            try:
                niitiinMonth = str(month)
                if len(str(month)) == 1:
                    niitiinMonth = '0' + niitiinMonth


                dateNiitiin = datetime.strptime(str(year) + '-' + niitiinMonth + '-01', '%Y-%m-%d')

                niitiin = get_niitiin(data.code, dateNiitiin)
                if niitiin is not None:
                    if niitiin.light_zuruu:
                        total_diff += niitiin.light_zuruu

                        real_cost += niitiin.light_price

                        diff_cost += Decimal(niitiin.light_zuruu) * Decimal(128.5)

                        serg_cost += Decimal(niitiin.light_zuruu) * Decimal(11.88)

                        print(diff_cost)
                    if niitiin.ten_zuruu:
                        total_diff += niitiin.ten_zuruu

                        real_cost += niitiin.ten_price

                        diff_cost += niitiin.ten_zuruu * 128.5

                        serg_cost += niitiin.ten_zuruu * 11.88
            except Exception as lol:
                print(lol)
                test = True

            ws.write(row_num, col_num, str(count), row_style)
            col_num += 1
            ws.write(row_num, col_num, str(data.first_name), row_style)
            col_num += 1

            ws.write(row_num, col_num, total_diff, row_style)
            col_num += 1
            sum1[2] += total_diff
            ws.write(row_num, col_num, real_cost, row_style)
            col_num += 1
            sum1[3] += (diff_cost + serg_cost)
            ws.write(row_num, col_num, diff_cost, row_style)
            col_num += 1
            sum1[4] += (diff_cost)
            ws.write(row_num, col_num, chadal_cost, row_style)
            col_num += 1
            sum1[5] += (chadal_cost)
            ws.write(row_num, col_num, serg_cost, row_style)
            col_num += 1
            sum1[6] += (serg_cost)
            ws.write(row_num, col_num, barimt_une, row_style)
            col_num += 1
            sum1[7] += (barimt_une)
            ws.write(row_num, col_num, suuri_une, row_style)
            col_num += 1
            sum1[8] += (suuri_une)
            ws.write(row_num, col_num, devter_une, row_style)
            col_num += 1
            sum1[9] += (devter_une)
            ws.write(row_num, col_num, tv, row_style)
            col_num += 1
            sum1[10] += (tv)
            ws.write(row_num, col_num, uilch, row_style)
            col_num += 1
            sum1[11] += (uilch)
            all = real_cost + chadal_cost + barimt_une + tv + uilch
            nuat = float(all - uilch) * 0.1
            all = float(all) + float(nuat)
            ws.write(row_num, col_num, nuat, row_style)
            col_num += 1
            sum1[12] += (nuat)
            ws.write(row_num, col_num, all, row_style)
            col_num += 1
            sum1[13] += (all)
            row_num += 1
            count += 1
        else:
            tariff = PriceTariff.objects.filter(une_type=1)[:1].get()


            total_diff = 0
            diff_cost = 0
            serg_cost = 0
            chadal_cost = 0
            barimt_une = int(int(data.barimt_une) / 11) * 10

            suuri_une = 0
            devter_une = 0

            real_cost = 0
            tv = int(int(data.tv_huraamj) / 11) * 10
            try:
                devter = CustomerUilchilgeeTulbur.objects.filter(customer__code = data.code, year = year, month = month,uilchilgee_id = 5).first()
                devter_une = devter.payment
            except Exception:
                devter_une = 0
            try:
                uilch = int(float(data.uilchilgeenii_tulbur))
            except Exception:
                uilch = 0
            #print(hothon_codes)
            if data.hothon is not None:
                if (data.hothon in hothon_codes):
                    if tooluurs is not None:
                        for tooluur in tooluurs:
                            price = PriceHistory.objects.filter(number=tooluur.number, customer_code=data.code, year=year,
                                                                month=month).first()

                            if  tooluur.tariff == '0':

                                serg_cost += (tooluur.day_diff_coef * tariff.serg_une)

                                if(price is not None):
                                    diff_cost += price.low150_price + price.high150_price - serg_cost

                                real_cost = diff_cost + serg_cost
                            else:
                                diff_cost += (tooluur.day_diff_coef * tariff.odor_une) + (
                                    tooluur.night_diff_coef * tariff.shono_une) + (
                                             tooluur.rush_diff_coef * tariff.orgil_une)
                                serg_cost += (tooluur.day_diff_coef * tariff.serg_une) + (
                                    tooluur.night_diff_coef * tariff.serg_une) + (
                                             tooluur.rush_diff_coef * tariff.serg_une)


                                real_cost = diff_cost + serg_cost
                                if (price is not None):
                                    pcost = (price.day_price + price.night_price + price.rush_price) - real_cost

                                if (pcost >= 1 or pcost <= -1) and len(tooluurs) == 1:
                                    real_cost = (price.day_price + price.night_price + price.rush_price)

                            if (price is not None):
                                suuri_une += price.suuri_price
                            total_diff += tooluur.total_diff_coef

                            if(data.code == '55000443'):
                                print(total_diff)

                    index = hothon_codes.index(data.hothon)

                    hothon_list_all[index]['total_diff'] += total_diff
                    hothon_list_all[index]['all_cost'] += real_cost
                    hothon_list_all[index]['diff_cost'] += (diff_cost)
                    hothon_list_all[index]['chadal_cost'] += (chadal_cost)
                    hothon_list_all[index]['serg_cost'] += (serg_cost)
                    hothon_list_all[index]['barimt_une'] += (barimt_une)
                    hothon_list_all[index]['suuri_une'] += (suuri_une)
                    hothon_list_all[index]['devter_une'] += (devter_une)
                    hothon_list_all[index]['tv'] += (tv)
                    hothon_list_all[index]['uilch'] += (uilch)

                    all = round(real_cost + chadal_cost + barimt_une + tv + uilch + suuri_une, 2)
                    #nuat = round(float(all),2) * 0.1
                    nuat = round(round(float(all - uilch), 2) * 0.1, 2)
                    all = float(all) + float(nuat)

                    hothon_list_all[index]['nuat'] += (nuat)
                    hothon_list_all[index]['all'] += (all)

                else:
                    hothon_codes.append(data.hothon)

                    if tooluurs is not None:
                        for tooluur in tooluurs:
                            price = PriceHistory.objects.filter(number=tooluur.number, customer_code=data.code, year=year,
                                                                month=month).first()

                            if  tooluur.tariff == '0':

                                serg_cost += (tooluur.day_diff_coef * tariff.serg_une)

                                diff_cost += price.low150_price + price.high150_price - serg_cost

                                real_cost = diff_cost + serg_cost
                            else:

                                serg_cost += (tooluur.day_diff_coef * tariff.serg_une) + (
                                    tooluur.night_diff_coef * tariff.serg_une) + (
                                             tooluur.rush_diff_coef * tariff.serg_une)

                                diff_cost += (tooluur.day_diff_coef * tariff.odor_une) + (
                                    tooluur.night_diff_coef * tariff.shono_une) + (
                                                 tooluur.rush_diff_coef * tariff.orgil_une)

                                real_cost = diff_cost + serg_cost

                                pcost = (price.day_price + price.night_price + price.rush_price) - real_cost

                                if (pcost >= 1 or pcost <= -1) and len(tooluurs) == 1:
                                    real_cost = (price.day_price + price.night_price + price.rush_price)

                            suuri_une += price.suuri_price
                            total_diff += tooluur.total_diff_coef
                            if (data.code == '55000443'):
                                print(total_diff)
                            # diff_cost += (tooluur.day_diff_coef * tariff.odor_une) + (
                            # tooluur.night_diff_coef * tariff.shono_une) + (tooluur.rush_diff_coef * tariff.orgil_une)
                            # serg_cost += (tooluur.day_diff_coef * tariff.serg_une) + (
                            #     tooluur.night_diff_coef * tariff.serg_une) + (tooluur.rush_diff_coef * tariff.serg_une)

                    #index = hothon_codes.index(data.hothon)
                    hothon_list = {}
                    hothon_list['name'] = data.hothon_name
                    hothon_list['total_diff'] = total_diff
                    hothon_list['all_cost'] = real_cost
                    hothon_list['diff_cost'] = (diff_cost)
                    hothon_list['chadal_cost'] = (chadal_cost)
                    hothon_list['serg_cost'] = (serg_cost)
                    hothon_list['barimt_une'] = (barimt_une)
                    hothon_list['suuri_une'] = (suuri_une)
                    hothon_list['devter_une'] = (devter_une)
                    hothon_list['tv'] = (tv)
                    hothon_list['uilch'] = (uilch)

                    all = round(real_cost + chadal_cost + barimt_une + tv + uilch + suuri_une, 2)
                    #nuat = float(all) * 0.1
                    nuat = round(round(float(all - uilch), 2) * 0.1,2)
                    all = float(all) + float(nuat)

                    hothon_list['nuat'] = (nuat)
                    hothon_list['all'] = (all)

                    hothon_list_all.append(hothon_list)
        #count += 1

    for num in range(len(sum1)):
        ws.write(row_num, num, sum1[num], header_style)

    row_num += 1
    for item in hothon_list_all:
        col_num = 0
        ws.write(row_num, col_num, str(count), row_style)
        col_num += 1
        ws.write(row_num, col_num, str(item['name']), row_style)
        col_num += 1
        ws.write(row_num, col_num, item['total_diff'], row_style)
        col_num += 1
        sum2[2] += item['total_diff']
        ws.write(row_num, col_num, item['all_cost'], row_style)
        col_num += 1
        sum2[3] += item['all_cost']
        ws.write(row_num, col_num, item['diff_cost'], row_style)
        col_num += 1
        sum2[4] += item['diff_cost']
        ws.write(row_num, col_num, item['chadal_cost'], row_style)
        col_num += 1
        sum2[5] += item['chadal_cost']
        ws.write(row_num, col_num, item['serg_cost'], row_style)
        col_num += 1
        sum2[6] += item['serg_cost']
        ws.write(row_num, col_num, item['barimt_une'], row_style)
        col_num += 1
        sum2[7] += item['barimt_une']
        ws.write(row_num, col_num, item['suuri_une'], row_style)
        col_num += 1
        sum2[8] += item['suuri_une']
        ws.write(row_num, col_num, item['devter_une'], row_style)
        col_num += 1
        sum2[9] += item['devter_une']
        ws.write(row_num, col_num, item['tv'], row_style)
        col_num += 1
        sum2[10] += item['tv']
        ws.write(row_num, col_num, item['uilch'], row_style)
        col_num += 1
        sum2[11] += item['uilch']
        ws.write(row_num, col_num, item['nuat'], row_style)
        col_num += 1
        sum2[12] += item['nuat']
        ws.write(row_num, col_num, item['all'], row_style)
        col_num += 1
        sum2[13] += item['all']

        row_num += 1
        count += 1

    for num in range(len(sum2)):
        ws.write(row_num, num, sum2[num], header_style)

        if num == 0:
            ws.write(row_num + 1, num, '', header_style)
        elif num == 1:
            ws.write(row_num + 1, num, 'Нийт дүн', header_style)
        else:
            sum_all = float(sum1[num]) + float(sum2[num])
            ws.write(row_num + 1, num, sum_all, header_style)
    wb.save(response)
    return response

def report_zaalt(request):
    year = request.POST['year']
    month = request.POST['month']
    cycles = request.POST.getlist('cycles', '')


    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="negtgel.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Тайлан')



    columns = ['Д/д', 'Нэр', 'Тоолуур','Өдөр өмнө','Өдөр одоо','Өдөр зөрүү', 'Шөнө өмнө', 'Шөнө одоо','Шөнө зөрүү', 'Оргил өмнө', 'Оргил одоо', 'Оргил Зөрүү', 'Гүйдэл', 'Хүчдэл']
    col_width = [int(5 * 260), int(30 * 260), int(14 * 260), int(14 * 260), int(14 * 260), int(14 * 260), int(14 * 260), int(14 * 260),
                 int(14 * 260), int(14 * 260), int(14 * 260), int(14 * 260), int(14 * 260), int(14 * 260)]

    hothon_list_all = []
    hothon_codes = []
    row_num = 0
    for col_num in range(len(columns)):
        ws.col(col_num).width = col_width[col_num]
        ws.write(row_num, col_num, columns[col_num], header_style)

    row_num += 1

    res_list = get_avlaga_list(year, month, cycles)
    count = 1
    sum = ['', 'Нийт дүн', '', '', '', 0, '', '', 0, '', '', 0, '', '']
    for data in res_list:
        col_num = 0
        tooluurs = TooluurHistory.objects.filter(customer_code = data.code, year = year, month = month)
        if tooluurs is not None:


            day_old = 0
            day_now = 0
            day_diff = 0
            night_old = 0
            night_now = 0
            night_diff = 0
            rush_old = 0
            rush_now = 0
            rush_diff = 0
            guidel = 1.00
            huchdel = 1.00

            if tooluurs is not None:
                for tooluur in tooluurs:
                    day_old = tooluur.day_balance_prev
                    day_now = tooluur.day_balance
                    day_diff = tooluur.day_diff_coef
                    night_old = tooluur.night_balance_prev
                    night_now = tooluur.night_balance
                    night_diff = tooluur.night_diff_coef
                    rush_old = tooluur.rush_balance_prev
                    rush_now = tooluur.rush_balance
                    rush_diff = tooluur.rush_diff_coef
                    guidel = tooluur.guid_coef
                    huchdel = tooluur.huch_coef


                    ws.write(row_num, col_num, str(count), row_style)
                    col_num += 1
                    ws.write(row_num, col_num, str(data.first_name), row_style)
                    col_num += 1
                    ws.write(row_num, col_num, str(tooluur.number), row_style)
                    col_num += 1

                    ws.write(row_num, col_num, day_old, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, day_now, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, day_diff, row_style)
                    col_num += 1
                    sum[5] += day_diff
                    ws.write(row_num, col_num, night_old, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, night_now, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, night_diff, row_style)
                    col_num += 1
                    sum[8] += night_diff
                    ws.write(row_num, col_num, rush_old, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, rush_now, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, rush_diff, row_style)
                    col_num += 1
                    sum[11] += rush_diff

                    ws.write(row_num, col_num, guidel, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, huchdel, row_style)
                    col_num += 1

                    row_num += 1
                    count += 1

        #count += 1

    for num in range(len(sum)):
        ws.write(row_num, num, sum[num], header_style)


    wb.save(response)
    return response


def get_avlaga_list(year, month, select_cycle):
    btype = "balance"

    # year = start_date[:4]
    # month = start_date[5:7]

    month = int(month)

    qry = """SELECT cus.id, cus.code, cus.first_name,hothon.name as hothon_name, hothon.code as hothon, cus.customer_angilal, addr.address_name, avbi.heregleenii_tulbur , avbi.uilchilgeenii_tulbur , avbi.barimt_une, avbi.tv_huraamj, avbi.ten FROM data_avlaga avbi
                				join data_customer cus on avbi.customer_id = cus.id
                				left join data_address addr on cus.id = addr.customer_id
                				left join data_geree geree on cus.code = geree.customer_code
                				left join data_hothon hothon on hothon.code = addr.hothon_code
                				WHERE avbi.month = '""" + str(month) + """' and cus.code not in ('55500100','55500102','55500175')
                                AND avbi.year <= '""" + str(year) + """' AND avbi.is_active = '1'
                				"""

    #qry = qry + " AND fb.year = '" + str(year) + "' and fb.month = '" + str(month) + "' "

    # if customer_angilal != '':
    #     qry = qry + " AND cus.customer_angilal = '" + customer_angilal + "'"
    # if customer_code != '':
    #     qry = qry + " AND cus.code LIKE '%%" + customer_code + "'"
    if select_cycle != '':
        cycle = ''
        for i, val in enumerate(select_cycle):
            cycle += val
            if(i != len(select_cycle) - 1):
                cycle += ","

        qry = qry + " AND geree.cycle_code in (" + cycle + ")"
    qry = qry + " group by avbi.customer_id ORDER BY cus.code asc"
    print(qry)
    res_list = list(Avlaga.objects.raw(qry))



    return res_list