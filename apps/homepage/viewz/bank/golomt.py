# coding=utf-8
from django.core.exceptions import ObjectDoesNotExist
from lxml import objectify, etree
from apps.data.models import *
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import requests
@csrf_exempt
def check_billing(request):
    xml_res = etree.Element("string")
    res_list = etree.SubElement(xml_res, "Response")
    res_msg = etree.SubElement(res_list, "ResponseMessage")

    if request.GET['CustomerCode'] is not None:
        cus_code = str(request.GET['CustomerCode'])
    else:
        cus_code = '0'
        etree.SubElement(res_msg, "ResCode").text = '400'
        etree.SubElement(res_msg, "ResDesc").text = 'Хэрэглэгчийн мэдээлэл олдсонгүй'

    tc = TooluurCustomer.objects.filter(customer_code=cus_code, is_active="1")

    if tc is not None:
        cus = Customer.objects.filter(code=cus_code, is_active='1').first()
        balance_type = 'balance'
        now = datetime.now()
        today = str(now)
        year = today[:4]
        now_year = today[:4]
        month = today[5:7]
        day = today[8:10]
        now_month = today[5:7]
        balance = 0
        last_avlaga = None

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
            if balance_type == 'balance':
                ehnii_balance = Final_Balance.objects.filter(customer_id=cus.id, year=year, month=month).first().balance
            else:
                ehnii_balance = Final_Balance.objects.filter(customer_id=cus.id, year=year, month=month).first().ehnii

            payment_history = None

            bichilt = last_avlaga = Avlaga.objects.filter(customer=cus, is_active='1').order_by('-created_date').first()
            if bichilt is not None:
                if len(month) == 1:
                    month += '0' + month
                pay_date = now_year + '-' + now_month + '-01 00:00:00.000000'

                payment_history = list(PaymentHistory.objects.raw("""SELECT cust.id, IFNULL(SUM(pahi.pay_total), 0) AS pay_total FROM data_customer cust
                            JOIN data_paymenthistory pahi ON cust.id = pahi.customer_id
                            WHERE pahi.is_active = '1' AND pahi.customer_id = """ + str(cus.id) + """ AND pahi.pay_date >= '""" + pay_date + """';"""))

                if bichilt.uilchilgeenii_tulbur is not None:
                    uilchilgeenii_tulbur = bichilt.uilchilgeenii_tulbur
                else:
                    uilchilgeenii_tulbur = Decimal(0)
                bichilt = str(bichilt.heregleenii_tulbur + uilchilgeenii_tulbur + bichilt.barimt_une)
            else:
                bichilt = 0.00

            if int(day) < 26:
                balance = round(float(ehnii_balance) - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)
            else:
                balance = round(float(ehnii_balance) + float(bichilt), 2)
                balance = round(balance - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)
        except ObjectDoesNotExist:
            etree.SubElement(res_msg, "ResCode").text = '400'
            etree.SubElement(res_msg, "ResDesc").text = 'Хэрэглэгчийн мэдээлэл олдсонгүй'

        if balance > 0:
            etree.SubElement(res_msg, "ResCode").text = '0'
            etree.SubElement(res_msg, "ResDesc").text = 'Амжилттай'

            res_info = etree.SubElement(res_list, "BillingInfo")

            etree.SubElement(res_info, "CustomerCode").text = cus_code
            etree.SubElement(res_info, "CustomerName").text = cus.first_name + ' ' + cus.last_name
            etree.SubElement(res_info, "BillMonth").text = str(last_avlaga.month) + ' сар'
            etree.SubElement(res_info, "BillAmount").text = str(balance)
        else:
            etree.SubElement(res_msg, "ResCode").text = '300'
            etree.SubElement(res_msg, "ResDesc").text = 'Хэрэглэгч дээр нэхэмжлэх үүсээгүй байна'
    else:
        etree.SubElement(res_msg, "ResCode").text = '400'
        etree.SubElement(res_msg, "ResDesc").text = 'Хэрэглэгчийн мэдээлэл олдсонгүй'

    return HttpResponse(etree.tostring(xml_res, encoding="UTF-8", xml_declaration=True), content_type='text/xml')

@csrf_exempt
def check_billing_details(request):
    xml_res = etree.Element("string")
    res_list = etree.SubElement(xml_res, "Response")
    res_msg = etree.SubElement(res_list, "ResponseMessage")

    if request.GET['CustomerCode'] is not None:
        cus_code = request.GET['CustomerCode']
    else:
        cus_code = '0'
        etree.SubElement(res_msg, "ResCode").text = '400'
        etree.SubElement(res_msg, "ResDesc").text = 'Хэрэглэгчийн мэдээлэл олдсонгүй'

    tc = TooluurCustomer.objects.filter(customer_code=cus_code, is_active="1")

    if tc is not None:
        cus = Customer.objects.filter(code=cus_code, is_active='1').first()

        balance_type = 'balance'
        now = datetime.now()
        today = str(now)
        year = cur_year = today[:4]
        month = today[5:7]
        cur_month = today[5:7]
        day = today[8:10]
        now_month = today[5:7]
        balance = ehnii = 0
        last_avlaga = last_bichilt = None

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
            if balance_type == 'balance':
                ehnii_balance = Final_Balance.objects.filter(customer_id=cus.id, year=year, month=month).first().balance
            else:
                ehnii_balance = Final_Balance.objects.filter(customer_id=cus.id, year=year, month=month).first().ehnii

            payment_history = None

            bichilt = last_avlaga = Avlaga.objects.filter(customer=cus, is_active='1').order_by('-created_date').first()
            last_bichilt = Bichilt.objects.filter(avlaga=last_avlaga).first()

            if bichilt is not None:
                if len(month) == 1:
                    month += '0' + month
                pay_date = cur_year + '-' + now_month + '-01 00:00:00.000000'

                payment_history = list(PaymentHistory.objects.raw("""SELECT cust.id, IFNULL(SUM(pahi.pay_total), 0) AS pay_total FROM data_customer cust
                    JOIN data_paymenthistory pahi ON cust.id = pahi.customer_id
                    WHERE pahi.is_active = '1' AND pahi.customer_id = """ + str(cus.id) + """ AND pahi.pay_date >= '""" + pay_date + """';"""))

                if bichilt.uilchilgeenii_tulbur is not None:
                    uilchilgeenii_tulbur = bichilt.uilchilgeenii_tulbur
                else:
                    uilchilgeenii_tulbur = Decimal(0)
                bichilt = str(bichilt.heregleenii_tulbur + uilchilgeenii_tulbur + bichilt.barimt_une)
            else:
                bichilt = 0.00
                payment = Payment.objects.filter(customer=cus).first()
                ehnii = 0.00 if payment is None else -payment.uldegdel

            if '0' == cur_month[0]:
                cur_month = cur_month[1]
            cur_month_avlaga = Avlaga.objects.filter(customer=cus, is_active='1', month=cur_month, year=cur_year).first()
            if cur_month_avlaga is None:
                ehnii = round(float(ehnii_balance) - float(bichilt), 2)
                # ehnii = round(ehnii - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)
                balance = round(float(ehnii_balance) - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)
            else:
                ehnii = float(ehnii_balance)
                balance = round(float(ehnii_balance) + float(bichilt), 2)
                balance = round(balance - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)
        except ObjectDoesNotExist:
            etree.SubElement(res_msg, "ResCode").text = '400'
            etree.SubElement(res_msg, "ResDesc").text = 'Хэрэглэгчийн мэдээлэл олдсонгүй'

        if balance > 0:
            etree.SubElement(res_msg, "ResCode").text = '0'
            etree.SubElement(res_msg, "ResDesc").text = 'Амжилттай'

            res_info = etree.SubElement(res_list, "BillingInfo")

            etree.SubElement(res_info, "Info01").text = "Эрчим Сүлжээ ХХК"
            etree.SubElement(res_info, "Info02").text = cus.first_name + ' ' + cus.last_name
            etree.SubElement(res_info, "Info03").text = cus.register
            etree.SubElement(res_info, "Info04").text = ""
            address = Address.objects.filter(customer=cus).first()
            etree.SubElement(res_info, "Info05").text = address.address_name
            etree.SubElement(res_info, "Info06").text = cus_code
            etree.SubElement(res_info, "Info07").text = last_avlaga.created_date.strftime('%Y.%m.%d')
            etree.SubElement(res_info, "Info08").text = str(last_avlaga.year) + month
            etree.SubElement(res_info, "Info09").text = str(ehnii)
            etree.SubElement(res_info, "Info10").text = str(round(balance - ehnii, 2))
            etree.SubElement(res_info, "Info11").text = str(balance)

            hereglee_price = round(float(last_bichilt.hereglee_price) + float(last_bichilt.sergeegdeh_price), 2)
            if hereglee_price > 0:
                res_bill_detail_list = etree.SubElement(res_list, "BillingDetails")

                etree.SubElement(res_bill_detail_list, "PaymentType").text = str(last_avlaga.id)
                etree.SubElement(res_bill_detail_list, "PaymentName").text = "Хэрэглээний төлбөр"
                etree.SubElement(res_bill_detail_list, "Amount").text = str(round(hereglee_price / 1.1, 2))
                etree.SubElement(res_bill_detail_list, "AmountVAT").text = str(round(hereglee_price - round(hereglee_price / 1.1, 2), 2))
                etree.SubElement(res_bill_detail_list, "BillingDate").text = last_avlaga.created_date.strftime('%Y.%m.%d')

            if cus.customer_angilal == "1" and float(last_bichilt.suuri_price) > 0:
                res_bill_detail_list = etree.SubElement(res_list, "BillingDetails")

                etree.SubElement(res_bill_detail_list, "PaymentType").text = str(last_avlaga.id)
                etree.SubElement(res_bill_detail_list, "PaymentName").text = "ЦЭХ-ний суурь үнэ"
                etree.SubElement(res_bill_detail_list, "Amount").text = str(round(float(last_bichilt.suuri_price) / 1.1, 2))
                etree.SubElement(res_bill_detail_list, "AmountVAT").text = str(round(float(last_bichilt.suuri_price) - round(float(last_bichilt.suuri_price) / 1.1, 2), 2))
                etree.SubElement(res_bill_detail_list, "BillingDate").text = last_avlaga.created_date.strftime('%Y.%m.%d')

            if cus.customer_angilal == "0" and float(last_bichilt.chadal_price) > 0 > 0:
                res_bill_detail_list = etree.SubElement(res_list, "BillingDetails")

                etree.SubElement(res_bill_detail_list, "PaymentType").text = str(last_avlaga.id)
                etree.SubElement(res_bill_detail_list, "PaymentName").text = "Чадлын төлбөр"
                etree.SubElement(res_bill_detail_list, "Amount").text = str(round(float(last_bichilt.chadal_price) / 1.1))
                etree.SubElement(res_bill_detail_list, "AmountVAT").text = str(round(float(last_bichilt.chadal_price) - round(float(last_bichilt.chadal_price) / 1.1, 2), 2))
                etree.SubElement(res_bill_detail_list, "BillingDate").text = last_avlaga.created_date.strftime('%Y.%m.%d')

            if float(last_avlaga.uilchilgeenii_tulbur) > 0:
                res_bill_detail_list = etree.SubElement(res_list, "BillingDetails")

                etree.SubElement(res_bill_detail_list, "PaymentType").text = str(last_avlaga.id)
                etree.SubElement(res_bill_detail_list, "PaymentName").text = "Төлбөрт үйлчилгээ"
                etree.SubElement(res_bill_detail_list, "Amount").text = str(round(float(last_avlaga.uilchilgeenii_tulbur) / 1.1))
                etree.SubElement(res_bill_detail_list, "AmountVAT").text = str(round(float(last_avlaga.uilchilgeenii_tulbur) - round(float(last_avlaga.uilchilgeenii_tulbur) / 1.1, 2), 2))
                etree.SubElement(res_bill_detail_list, "BillingDate").text = last_avlaga.created_date.strftime('%Y.%m.%d')

            if 0 > 0:
                res_bill_detail_list = etree.SubElement(res_list, "BillingDetails")

                etree.SubElement(res_bill_detail_list, "PaymentType").text = str(last_avlaga.id)
                etree.SubElement(res_bill_detail_list, "PaymentName").text = "Алданги"
                etree.SubElement(res_bill_detail_list, "Amount").text = "0.0"
                etree.SubElement(res_bill_detail_list, "AmountVAT").text = "0.0"
                etree.SubElement(res_bill_detail_list, "BillingDate").text = last_avlaga.created_date.strftime('%Y.%m.%d')

            if float(last_avlaga.barimt_une) > 0:
                res_bill_detail_list = etree.SubElement(res_list, "BillingDetails")

                etree.SubElement(res_bill_detail_list, "PaymentType").text = str(last_avlaga.id)
                etree.SubElement(res_bill_detail_list, "PaymentName").text = "Баримтын үнэ"
                etree.SubElement(res_bill_detail_list, "Amount").text = str(round(float(last_avlaga.barimt_une) / 1.1, 2))
                etree.SubElement(res_bill_detail_list, "AmountVAT").text = str(round(float(last_avlaga.barimt_une) - round(float(last_avlaga.barimt_une) / 1.1, 2), 2))
                etree.SubElement(res_bill_detail_list, "BillingDate").text = last_avlaga.created_date.strftime('%Y.%m.%d')
        else:
            etree.SubElement(res_msg, "ResCode").text = '300'
            etree.SubElement(res_msg, "ResDesc").text = 'Хэрэглэгч дээр нэхэмжлэх үүсээгүй байна'
    else:
        etree.SubElement(res_msg, "ResCode").text = '400'
        etree.SubElement(res_msg, "ResDesc").text = 'Хэрэглэгчийн мэдээлэл олдсонгүй'

    return HttpResponse(etree.tostring(xml_res, encoding="UTF-8", xml_declaration=True), content_type='text/xml')

@csrf_exempt
def golomt_transaction(request):

    # xml_res = etree.Element("notif")
    #
    # try:
    #     xml_req = objectify.fromstring(request.body)
    #
    #
    #     type = xml_req.transaction.type.text
    #     account = xml_req.transaction.account.text
    #     journalid = xml_req.transaction.journalid.text
    #     amount = Decimal(xml_req.transaction.amount.text)
    #     posted_date = xml_req.transaction.posteddate.text
    #     statement_date = xml_req.transaction.statementdate.text
    #     description = xml_req.transaction.description.text
    #
    #     customer = None
    #     if len(description) == 7:
    #         customer = Customer.objects.filter(code=description).first()
    #
    #     trans = GolomtTransactions.objects.create(type=type, account=account, journalid=journalid, amount=amount,
    #                                               posted_date=posted_date, statement_date=statement_date,
    #                                               description=description)
    #
    #     trans.save()
    #     etree.SubElement(xml_res, "transaction").text = journalid
    #
    # except etree.XMLSyntaxError:
    #     print('Syntax error')

    xml = request.body
    headers = {'Content-Type': 'application/xml'}
    r = requests.post('http://127.0.0.1:8080/home/golomt_transaction', data=xml, headers=headers, verify=False)

    return HttpResponse(r, content_type='text/xml')

    # return HttpResponse(etree.tostring(xml_res, encoding="UTF-8", xml_declaration=True), content_type='text/xml')

@csrf_exempt
def khan_transaction(request):

    # xml_res = etree.Element("txns")
    #
    # try:
    #     xml_req = objectify.fromstring(request.body)
    #
    #
    #     type = xml_req.txn.type.text
    #     account = xml_req.txn.acct.text
    #     journalid = xml_req.txn.jrnl.text
    #     amount = Decimal(xml_req.txn.amt.text)
    #     posted_date = xml_req.txn.date.text
    #     statement_date = xml_req.txn.date.text
    #     description = xml_req.txn.desc.text
    #
    #     customer = None
    #     if len(description) == 7:
    #         customer = Customer.objects.filter(code=description).first()
    #
    #     trans = GolomtTransactions.objects.create(type=type, account=account, journalid=journalid, amount=amount,
    #                                               posted_date=posted_date, statement_date=statement_date,
    #                                               description=description)
    #
    #     trans.save()
    #     etree.SubElement(xml_res, "transaction").text = journalid
    #
    # except etree.XMLSyntaxError:
    #     print('Syntax error')
    xml = request.body
    headers = {'Content-Type': 'application/xml'}
    r = requests.post('http://127.0.0.1:8080/home/khan_request', data=xml, headers=headers, verify=False)

    return HttpResponse(r)
