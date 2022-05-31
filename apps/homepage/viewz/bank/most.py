# coding=utf-8
from lxml import objectify, etree
from rest_framework.decorators import api_view
from apps.data.models import *
from django.shortcuts import HttpResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@api_view(['post'])
def most_request(request):
    xml_res = etree.Element("GCM01Res")

    try:
        xml_req = objectify.fromstring(request.body)        
        if xml_req.tag == 'GCM01':
            etree.SubElement(xml_res, "ResponseCode").text = '0'
            etree.SubElement(xml_res, "ResponseDesc").text = 'Амжилттай'            
        elif xml_req.tag == 'GCM02':
            xml_res = etree.Element("GCM02Res")

            cus_code = xml_req.UserCode.text
            cus = Customer.objects.filter(code=cus_code).first()            

            if cus is not None:                
                etree.SubElement(xml_res, "ResponseCode").text = '0'
                etree.SubElement(xml_res, "ResponseDesc").text = 'Амжилттай'
                etree.SubElement(xml_res, "FName").text = cus.first_name
                etree.SubElement(xml_res, "LName").text = cus.last_name
                etree.SubElement(xml_res, "IsCorporate").text = '1' if cus.customer_angilal == '0' else '0'
                etree.SubElement(xml_res, "OrgName").text = cus.first_name + ' ' + cus.last_name
                etree.SubElement(xml_res, "RegisterNo").text = cus.register
                etree.SubElement(xml_res, "ZipCode").text = ""
                address = Address.objects.filter(customer=cus).first()
                etree.SubElement(xml_res, "AddressShort").text = address.address_name[0:200]
                etree.SubElement(xml_res, "AddressRegister").text = ""
                etree.SubElement(xml_res, "Fax").text = ""
                etree.SubElement(xml_res, "PhoneNo").text = cus.phone
                etree.SubElement(xml_res, "MobileNo").text = cus.phone2
                etree.SubElement(xml_res, "Email").text = cus.email
                etree.SubElement(xml_res, "CityCode").text = address.aimag_code
                etree.SubElement(xml_res, "DistCode").text = address.duureg_code
                etree.SubElement(xml_res, "Khoroolol").text = Hothon.objects.filter(code=address.hothon_code).first().name
                etree.SubElement(xml_res, "SubDistCode").text = ""
                etree.SubElement(xml_res, "BairGudamj").text = address.building_number
                etree.SubElement(xml_res, "Haalga").text = address.toot
            else:
                etree.SubElement(xml_res, "ResponseCode").text = '2001'
                etree.SubElement(xml_res, "ResponseDesc").text = 'Хэрэглэгчийн мэдээлэл олдсонгүй'

        elif xml_req.tag == 'GCM03':
            
            xml_res = etree.Element("GCM03Res")
            res_list = etree.SubElement(xml_res, "GCM03ResList")

            balance_type = 'balance'
            now = datetime.now()
            today = str(now)
            year = cur_year = today[:4]
            month = today[5:7]
            cur_month = today[5:7]
            now_month = today[5:7]
            day = today[8:10]

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

            for item in xml_req.GCM03List.GCM03ListItem:
                cus_code = item.UserCode.text
                cus = Customer.objects.filter(code=cus_code, is_active="1").first()

                res_list_item = etree.SubElement(res_list, "GCM03ResListItem")

                if cus is not None:
                    # if cus.customer_angilal == '1':
                        # not_ebarimt = ['‎1910004', '‎1910009', '‎1911292', '‎1910611', '‎1910618', '‎1914052', '‎1914062', '1911002']
                        # if str(cus.code) not in not_ebarimt:
                            last_avlaga = Avlaga.objects.filter(customer=cus, is_active='1').order_by('-created_date').first()
                            if last_avlaga is not None:
                                befo_bich_date = last_bich_date = last_year = last_month = ''

                                if int(last_avlaga.month) <= 3 and int(last_avlaga.year) <= 2018:
                                    last_bichilt = Bichilt.objects.filter(avlaga=last_avlaga, is_active='1').first()
                                    before_bichilt = Bichilt.objects.filter(id=int(last_bichilt.prev_bichilt_id), is_active='1').first()

                                    befo_bich_date = str(before_bichilt.bichilt_date)[:10]
                                    last_bich_date = str(last_bichilt.bichilt_date)[:10]
                                    last_year = str(last_avlaga.year)
                                    last_month = str(last_avlaga.month)

                                else:

                                    tooluur_history = TooluurHistory.objects.filter(customer_code=str(cus_code), is_active='1').first()
                                    if tooluur_history is not None:
                                        last_year = str(tooluur_history.year)
                                        last_month = str(tooluur_history.month)
                                        befo_bich_date = str(tooluur_history.umnu_bichdate)[:10]
                                        last_bich_date = str(tooluur_history.odoo_bichdate)[:10]

                                pay_date = cur_year + '-' + now_month + '-01 00:00:00.000000'
                                # print("CusID: ", cus.id)

                                payment = list(PaymentHistory.objects.raw("""SELECT cust.id, IFNULL(SUM(pahi.pay_total), 0) AS pay_total FROM data_customer cust
                                    JOIN data_paymenthistory pahi ON cust.id = pahi.customer_id
                                    WHERE pahi.is_active = '1' AND pahi.customer_id = """ + str(cus.id) + """ AND pahi.pay_date >= '""" + pay_date + """';"""))

                                if balance_type == 'balance':
                                    before_balance = Final_Balance.objects.filter(customer_id=cus.id, year=year, month=month).first().balance
                                else:
                                    before_balance = Final_Balance.objects.filter(customer_id=cus.id, year=year, month=month).first().ehnii
                                last_amount = last_avlaga.heregleenii_tulbur + last_avlaga.uilchilgeenii_tulbur + last_avlaga.barimt_une

                                if '0' == cur_month[0]:
                                    cur_month = cur_month[1]
                                cur_month_avlaga = Avlaga.objects.filter(customer=cus, is_active='1', month=cur_month, year=cur_year).first()
                                if cur_month_avlaga is None:
                                    before_amount = round(float(before_balance) - float(last_amount), 2)
                                    # before_amount = round(before_amount - float(0 if len(payment) < 1 else payment[0].pay_total), 2)
                                    amount = round(float(before_balance) - float(0 if len(payment) < 1 else payment[0].pay_total), 2)
                                else:
                                    before_amount = float(before_balance)
                                    amount = round(float(before_balance) + float(last_amount), 2)
                                    amount = round(amount - float(0 if len(payment) < 1 else payment[0].pay_total), 2)

                                etree.SubElement(res_list_item, "UserCode").text = str(cus_code)
                                etree.SubElement(res_list_item, "ResponseCode").text = '0'
                                etree.SubElement(res_list_item, "ResponseDesc").text = 'Амжилттай'
                                etree.SubElement(res_list_item, "BillID").text = last_year + last_month + str(cus_code)
                                etree.SubElement(res_list_item, "Amount").text = str(round(amount, 2))
                                etree.SubElement(res_list_item, "CurCode").text = "MNT"
                                etree.SubElement(res_list_item, "BillStartDate").text = befo_bich_date
                                etree.SubElement(res_list_item, "BillEndDate").text = last_bich_date
                                etree.SubElement(res_list_item, "BillRecDate").text = last_bich_date
                                etree.SubElement(res_list_item, "BillDescription").text = last_year + "-" + last_month + " сарын цахилгааны төлбөр"
                                etree.SubElement(res_list_item, "VATAmount").text = str(round(((float(amount) / 1.1) * 0.1), 2))

                                res_bill_detail_list = etree.SubElement(res_list_item, "BillDetailList")

                                if cus.customer_angilal == '0':
                                    res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                    etree.SubElement(res_bill_detail_list_item, "DetailID").text = "1"
                                    etree.SubElement(res_bill_detail_list_item, "Name").text = "Регистр"
                                    etree.SubElement(res_bill_detail_list_item, "Value").text = str(cus.register)
                                    etree.SubElement(res_bill_detail_list_item, "Description").text = "Регистрын дугаар"
                                    etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "1"

                                if int(last_avlaga.month) <= 3 and int(last_avlaga.year) <= 2018:
                                    counter = 0
                                    detail_counter = 1
                                    total_diff = heregleenii_tulbur = chadal_price = suuri_price = 0

                                    last_bichs = Bichilt.objects.filter(avlaga=last_avlaga, is_active='1')
                                    for last_bich in last_bichs:
                                        counter += 1
                                        detail_counter += 1
                                        before_bich = Bichilt.objects.filter(id=int(last_bich.prev_bichilt_id), is_active='1').first()

                                        amp_coff = huch_coff = 1
                                        if last_bich.tooluur.guidliin_trans != None and last_bich.tooluur.guidliin_trans != '':
                                            amp_coff = Decimal(last_bich.tooluur.guidliin_trans.multiply_coef)
                                        if last_bich.tooluur.huchdeliin_trans != None and last_bich.tooluur.huchdeliin_trans != '':
                                            huch_coff = Decimal(last_bich.tooluur.huchdeliin_trans.multiply_coef)

                                        if len(list(last_bichs)) <= 2:
                                            if before_bich is not None:
                                                res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                                etree.SubElement(res_bill_detail_list_item, "DetailID").text = str(detail_counter)
                                                etree.SubElement(res_bill_detail_list_item, "Name").text = str(before_bich.tooluur.tooluur.number) + " Эхний заалт"
                                                etree.SubElement(res_bill_detail_list_item, "Value").text = str(before_bich.day_balance)
                                                etree.SubElement(res_bill_detail_list_item, "Description").text = "Огноо : " + str(before_bich.bichilt_date)[:10]
                                                etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "1"
                                                detail_counter += 1

                                            if last_bich is not None:
                                                res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                                etree.SubElement(res_bill_detail_list_item, "DetailID").text = str(detail_counter)
                                                etree.SubElement(res_bill_detail_list_item, "Name").text = str(last_bich.tooluur.tooluur.number) + " Эцсийн заалт"
                                                etree.SubElement(res_bill_detail_list_item, "Value").text = str(last_bich.day_balance)
                                                etree.SubElement(res_bill_detail_list_item, "Description").text = "Огноо : " + str(last_bich.bichilt_date)[:10]
                                                etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "1"
                                                detail_counter += 1

                                            if last_bich is not None:
                                                res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                                etree.SubElement(res_bill_detail_list_item, "DetailID").text = str(detail_counter)
                                                etree.SubElement(res_bill_detail_list_item, "Name").text = "Тоолуурын нийт зөрүү"
                                                etree.SubElement(res_bill_detail_list_item, "Value").text = str(round(Decimal(last_bich.total_diff), 2)) + " x " + str(round(amp_coff * huch_coff, 2)) + " = " + str(round(round(Decimal(last_bich.total_diff), 2) * round(amp_coff * huch_coff, 2), 2))
                                                etree.SubElement(res_bill_detail_list_item, "Description").text = "Коэф : " + str(round(amp_coff * huch_coff, 2))
                                                etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "1"
                                        else:
                                            total_diff += Decimal(last_bich.total_diff) * amp_coff * huch_coff

                                        heregleenii_tulbur += round((Decimal(last_bich.hereglee_price) + Decimal(last_bich.sergeegdeh_price)), 2)

                                        if cus.customer_angilal == '0':
                                            chadal_price += round(Decimal(last_bich.chadal_price), 2)
                                        else:
                                            suuri_price += round(Decimal(last_bich.suuri_price), 2)

                                    if counter > 2:
                                        res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                        etree.SubElement(res_bill_detail_list_item, "DetailID").text = "5"
                                        etree.SubElement(res_bill_detail_list_item, "Name").text = "Нийт тоолуурын нийт зөрүү"
                                        etree.SubElement(res_bill_detail_list_item, "Value").text = str(round(total_diff, 2))
                                        etree.SubElement(res_bill_detail_list_item, "Description").text = ""
                                        etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "1"

                                    res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                    etree.SubElement(res_bill_detail_list_item, "DetailID").text = "1"
                                    etree.SubElement(res_bill_detail_list_item, "Name").text = "Эхний үлдэгдэл"
                                    etree.SubElement(res_bill_detail_list_item, "Value").text = str(round(before_amount, 2))
                                    etree.SubElement(res_bill_detail_list_item,"Description").text = "Эхний үлдэгдэл (НӨАТ)"
                                    etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                                    payment = 0 if len(payment) < 1 else -payment[0].pay_total
                                    if payment < 0:
                                        res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                        etree.SubElement(res_bill_detail_list_item, "DetailID").text = "1"
                                        etree.SubElement(res_bill_detail_list_item, "Name").text = "Энэ сарын орлого"
                                        etree.SubElement(res_bill_detail_list_item, "Value").text = str(payment)
                                        etree.SubElement(res_bill_detail_list_item, "Description").text = "Энэ сарын орлого"
                                        etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                                    if heregleenii_tulbur > 0:
                                        res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                        etree.SubElement(res_bill_detail_list_item, "DetailID").text = "2"
                                        etree.SubElement(res_bill_detail_list_item, "Name").text = "Хэрэглээний төлбөр"
                                        etree.SubElement(res_bill_detail_list_item, "Value").text = str(heregleenii_tulbur)
                                        etree.SubElement(res_bill_detail_list_item, "Description").text = "ЦЭХ хэрэглэсэн төлбөр (НӨАТ)"
                                        etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                                    if last_avlaga.uilchilgeenii_tulbur is not None and Decimal(last_avlaga.uilchilgeenii_tulbur) > 0:
                                        res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                        etree.SubElement(res_bill_detail_list_item, "DetailID").text = "4"
                                        etree.SubElement(res_bill_detail_list_item, "Name").text = "Төлбөрт үйлчилгээ"
                                        etree.SubElement(res_bill_detail_list_item, "Value").text = str(last_avlaga.uilchilgeenii_tulbur)
                                        etree.SubElement(res_bill_detail_list_item, "Description").text = "Төлбөрт үйлчилгээний төлбөр (НӨАТ)"
                                        etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                                    if suuri_price > 0:
                                        res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                        etree.SubElement(res_bill_detail_list_item, "DetailID").text = "3"
                                        etree.SubElement(res_bill_detail_list_item, "Name").text = "ЦЭХ-ний суурь үнэ"
                                        etree.SubElement(res_bill_detail_list_item, "Value").text = str(suuri_price)
                                        etree.SubElement(res_bill_detail_list_item, "Description").text = "Цахилгаан эрчим хүчний суурь үнэ (НӨАТ)"
                                        etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                                    if chadal_price > 0:
                                        res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                        etree.SubElement(res_bill_detail_list_item, "DetailID").text = "5"
                                        etree.SubElement(res_bill_detail_list_item, "Name").text = "Чадлын төлбөр"
                                        etree.SubElement(res_bill_detail_list_item, "Value").text = str(chadal_price)
                                        etree.SubElement(res_bill_detail_list_item, "Description").text = "Чадлын төлбөр (НӨАТ)"
                                        etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                                    res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                    etree.SubElement(res_bill_detail_list_item, "DetailID").text = "6"
                                    etree.SubElement(res_bill_detail_list_item, "Name").text = "Алданги"
                                    etree.SubElement(res_bill_detail_list_item, "Value").text = '0.00'
                                    etree.SubElement(res_bill_detail_list_item, "Description").text = "Алданги (НӨАТ)"
                                    etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                                    if last_avlaga.barimt_une is not None and Decimal(last_avlaga.barimt_une) > 0:
                                        res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                        etree.SubElement(res_bill_detail_list_item, "DetailID").text = "7"
                                        etree.SubElement(res_bill_detail_list_item, "Name").text = "Баримтын үнэ"
                                        etree.SubElement(res_bill_detail_list_item, "Value").text = str(round(last_avlaga.barimt_une, 2))
                                        etree.SubElement(res_bill_detail_list_item, "Description").text = "Баримтын үнэ (НӨАТ)"
                                        etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                                else:

                                    tooluur_histories = TooluurHistory.objects.filter(customer_code=str(cus_code), is_active='1', year=last_year, month=last_month)
                                    if tooluur_histories is not None:
                                        cnter = det_counter = total_diff = heregleenii_tulbur = chadal_price = suuri_price = 0

                                        for tooluur_history in tooluur_histories:
                                            cnter += 1
                                            det_counter += 1
                                            if len(list(tooluur_histories)) <= 2:

                                                res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                                etree.SubElement(res_bill_detail_list_item, "DetailID").text = str(det_counter)
                                                etree.SubElement(res_bill_detail_list_item, "Name").text = str(tooluur_history.number) + " Эхний заалт"
                                                etree.SubElement(res_bill_detail_list_item, "Value").text = str(tooluur_history.day_balance_prev)
                                                etree.SubElement(res_bill_detail_list_item, "Description").text = "Огноо : " + str(tooluur_history.umnu_bichdate)[:10]
                                                etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "1"
                                                det_counter += 1

                                                res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                                etree.SubElement(res_bill_detail_list_item, "DetailID").text = str(det_counter)
                                                etree.SubElement(res_bill_detail_list_item, "Name").text = str(tooluur_history.number) + " Эцсийн заалт"
                                                etree.SubElement(res_bill_detail_list_item, "Value").text = str(tooluur_history.day_balance)
                                                etree.SubElement(res_bill_detail_list_item, "Description").text = "Огноо : " + str(tooluur_history.odoo_bichdate)[:10]
                                                etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "1"
                                                det_counter += 1

                                                res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                                etree.SubElement(res_bill_detail_list_item, "DetailID").text = str(det_counter)
                                                etree.SubElement(res_bill_detail_list_item, "Name").text = "Тоолуурын нийт зөрүү"
                                                etree.SubElement(res_bill_detail_list_item, "Value").text = str(tooluur_history.total_diff) + " x " + str(round(float(tooluur_history.guid_coef) * float(tooluur_history.huch_coef), 2)) + " = " + str(tooluur_history.total_diff_coef)
                                                etree.SubElement(res_bill_detail_list_item, "Description").text = "Коэф : " + str(round(float(tooluur_history.guid_coef) * float(tooluur_history.huch_coef), 2))
                                                etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "1"
                                            else:
                                                total_diff += Decimal(tooluur_history.total_diff_coef)

                                        if cnter > 2:
                                            res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                            etree.SubElement(res_bill_detail_list_item, "DetailID").text = "5"
                                            etree.SubElement(res_bill_detail_list_item, "Name").text = "Нийт тоолуурын нийт зөрүү"
                                            etree.SubElement(res_bill_detail_list_item, "Value").text = str(round(total_diff, 2))
                                            etree.SubElement(res_bill_detail_list_item, "Description").text = ""
                                            etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "1"

                                        res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                        etree.SubElement(res_bill_detail_list_item, "DetailID").text = "1"
                                        etree.SubElement(res_bill_detail_list_item, "Name").text = "Эхний үлдэгдэл"
                                        etree.SubElement(res_bill_detail_list_item, "Value").text = str(round(before_amount, 2))
                                        etree.SubElement(res_bill_detail_list_item, "Description").text = "Эхний үлдэгдэл (НӨАТ)"
                                        etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                                        payment = 0 if len(payment) < 1 else -payment[0].pay_total
                                        if payment < 0:
                                            res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                            etree.SubElement(res_bill_detail_list_item, "DetailID").text = "2"
                                            etree.SubElement(res_bill_detail_list_item, "Name").text = "Энэ сарын орлого"
                                            etree.SubElement(res_bill_detail_list_item, "Value").text = str(payment)
                                            etree.SubElement(res_bill_detail_list_item, "Description").text = "Энэ сарын орлого"
                                            etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                                        price_histories = PriceHistory.objects.filter(customer_code=str(cus_code), is_active='1', year=last_year, month=last_month)
                                        if price_histories is not None:
                                            for price_history in price_histories:
                                                if str(price_history.customer_angilal) == '1':
                                                    if price_history.suuri_price is not None:
                                                        suuri_price += round(suuri_price + float(price_history.suuri_price))
                                                else:
                                                    if price_history.chadal_price is not None:
                                                        chadal_price += round(chadal_price + float(price_history.chadal_price))
                                                if price_history.total_price is not None:
                                                    heregleenii_tulbur += round(heregleenii_tulbur + float(price_history.total_price), 2)

                                        if heregleenii_tulbur > 0:
                                            heregleenii_tulbur = round(heregleenii_tulbur * 1.1, 2)
                                            res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                            etree.SubElement(res_bill_detail_list_item, "DetailID").text = "3"
                                            etree.SubElement(res_bill_detail_list_item, "Name").text = "Хэрэглээний төлбөр"
                                            etree.SubElement(res_bill_detail_list_item, "Value").text = str(heregleenii_tulbur)
                                            etree.SubElement(res_bill_detail_list_item, "Description").text = "ЦЭХ хэрэглэсэн төлбөр (НӨАТ)"
                                            etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                                        if last_avlaga.uilchilgeenii_tulbur is not None and Decimal(last_avlaga.uilchilgeenii_tulbur) > 0:
                                            res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                            etree.SubElement(res_bill_detail_list_item, "DetailID").text = "4"
                                            etree.SubElement(res_bill_detail_list_item, "Name").text = "Төлбөрт үйлчилгээ"
                                            etree.SubElement(res_bill_detail_list_item, "Value").text = str(last_avlaga.uilchilgeenii_tulbur)
                                            etree.SubElement(res_bill_detail_list_item, "Description").text = "Төлбөрт үйлчилгээний төлбөр (НӨАТ)"
                                            etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                                        if suuri_price > 0:
                                            suuri_price = round(suuri_price * 1.1, 2)
                                            res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                            etree.SubElement(res_bill_detail_list_item, "DetailID").text = "5"
                                            etree.SubElement(res_bill_detail_list_item, "Name").text = "ЦЭХ-ний суурь үнэ"
                                            etree.SubElement(res_bill_detail_list_item, "Value").text = str(suuri_price)
                                            etree.SubElement(res_bill_detail_list_item, "Description").text = "Цахилгаан эрчим хүчний суурь үнэ (НӨАТ)"
                                            etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                                        if chadal_price > 0:
                                            chadal_price = round(chadal_price * 1.1, 2)
                                            res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                            etree.SubElement(res_bill_detail_list_item, "DetailID").text = "6"
                                            etree.SubElement(res_bill_detail_list_item, "Name").text = "Чадлын төлбөр"
                                            etree.SubElement(res_bill_detail_list_item, "Value").text = str(chadal_price)
                                            etree.SubElement(res_bill_detail_list_item, "Description").text = "Чадлын төлбөр (НӨАТ)"
                                            etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                                        if last_avlaga.barimt_une is not None and Decimal(last_avlaga.barimt_une) > 0:
                                            res_bill_detail_list_item = etree.SubElement(res_bill_detail_list, "BillDetailListItem")
                                            etree.SubElement(res_bill_detail_list_item, "DetailID").text = "7"
                                            etree.SubElement(res_bill_detail_list_item, "Name").text = "Баримтын үнэ"
                                            etree.SubElement(res_bill_detail_list_item, "Value").text = str(round(last_avlaga.barimt_une, 2))
                                            etree.SubElement(res_bill_detail_list_item, "Description").text = "Баримтын үнэ (НӨАТ)"
                                            etree.SubElement(res_bill_detail_list_item, "IsBasicInfo").text = "0"

                            else:
                                etree.SubElement(res_list_item, "UserCode").text = cus_code
                                etree.SubElement(res_list_item, "ResponseCode").text = '3002'
                                etree.SubElement(res_list_item, "ResponseDesc").text = 'Хэрэглэгчид төлөх билл байхгүй'
                        # else:
                        #     etree.SubElement(res_list_item, "UserCode").text = cus_code
                        #     etree.SubElement(res_list_item, "ResponseCode").text = '3002'
                        #     etree.SubElement(res_list_item, "ResponseDesc").text = 'Хэрэглэгчид төлөх билл байхгүй'
                    # else:
                    #     etree.SubElement(res_list_item, "UserCode").text = cus_code
                    #     etree.SubElement(res_list_item, "ResponseCode").text = '3003'
                    #     etree.SubElement(res_list_item, "ResponseDesc").text = 'ААН төлбөр төлөх боломжгүй байна.'
                else:
                    etree.SubElement(res_list_item, "ResponseCode").text = '3001'
                    etree.SubElement(res_list_item, "ResponseDesc").text = 'Хэрэглэгчийн мэдээлэл олдсонгүй'

        elif xml_req.tag == 'GCM04':

            xml_res = etree.Element("GCM04Res")

            ref_no = xml_req.ReferenceNo.text
            txn_date = xml_req.TxnDate.text
            cus_code = xml_req.UserCode.text
            total = Decimal(xml_req.Amount.text)
            cur = xml_req.CurCode.text
            desc = xml_req.Description.text            

            if cur == 'MNT':
                if total > 0:
                    customer = Customer.objects.filter(code=cus_code).first()
                    if customer is not None:
                        pay_date = datetime.strptime(txn_date, '%Y.%m.%d %H:%M:%S')

                        his = PaymentHistory.objects.create(pay_date=pay_date, pay_total=total, customer=customer)
                        his.bank = Bank.objects.filter(code='10').first()

                        # avlaga_list = Avlaga.objects.filter(customer=customer, pay_type='0').order_by('created_date')
                        # if avlaga_list is not None:
                        #     for avlaga in avlaga_list:
                        #         ald_hemjee = Decimal(0)
                        #         days = (datetime.now() - avlaga.tulbur_date).days
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

                        his.bank_ref = ref_no
                        his.description = desc
                        his.save()

                        etree.SubElement(xml_res, "ResponseCode").text = '0'
                        etree.SubElement(xml_res, "ResponseDesc").text = 'Амжилттай'
                    else:
                        etree.SubElement(xml_res, "ResponseCode").text = '4002'
                        etree.SubElement(xml_res, "ResponseDesc").text = '/ TxnKeyField / Түлхүүр талбараар төлөх биллийн мэдээлэл олдсонгүй'
                else:
                    etree.SubElement(xml_res, "ResponseCode").text = '4003'
                    etree.SubElement(xml_res, "ResponseDesc").text = 'Гүйлгээний дүн буруу'
            else:
                etree.SubElement(xml_res, "ResponseCode").text = '4004'
                etree.SubElement(xml_res, "ResponseDesc").text = 'Гүйлгээний валют буруу'

    except etree.XMLSyntaxError:
        etree.SubElement(xml_res, "ResponseCode").text = '400'
        etree.SubElement(xml_res, "ResponseDesc").text = 'Синтаксын алдаа'    
    
    return HttpResponse(etree.tostring(xml_res, encoding="UTF-8", xml_declaration=True), content_type='text/xml')