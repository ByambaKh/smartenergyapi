from rest_framework import viewsets
from apps.api.serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime
from rest_framework import status
from mcsi.utils import *
from apps.extra import *
from rest_framework.views import APIView
from apps.homepage.viewz.bichilt_manager import *
from django.shortcuts import render, HttpResponse, redirect
# from basicauth.decorators import basic_auth_required

import simplejson
import json


@api_view(['POST'])
# @basic_auth_required(
#     target_test=lambda request: not request.user.is_authenticated
# )
def getUserElectricityInfo(request):
    data = {}
    status = 0
    invoice_no = ''
    error = ''
    try:
        now = datetime.datetime.now()
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
        else:
            month = str(int(month) - 1)
        serializer = PosSerializer(data=request.data)
        if serializer.is_valid():
            user_code = serializer.data['customerCode']
            bankCode = serializer.data['bankCode']
            bankInfo = DataBank.objects.filter(code=bankCode).first()
            if bankInfo is not None:
                user = Customer.objects.filter(
                    code=user_code, is_active='1').first()
                if user is not None:
                    final_Balance = Final_Balance.objects.filter(
                        customer_id=user.id, year=year, month=month).first()
                    if final_Balance is not None:
                        ehnii_balance = final_Balance.balance
                        payment_history = None
                        bichilt_data = []
                        bichilt = Avlaga.objects.filter(
                            customer=user, is_active='1').order_by('-created_date').first()
                        uilchilgeenii_tulbur = 0
                        start_date = ''
                        end_date = ''
                        barimt_une = 0
                        suuri_price = 0
                        undueLoss = 0
                        customerType = "Өрх"
                        if int(user.customer_angilal) == 0:
                            customerType = "Байгууллага"
                        if bichilt is not None:
                            tariff = PriceTariff.objects.get(
                                une_type='1', is_active='1')
                            barimt_une = bichilt.barimt_une
                            bichilts = Bichilt.objects.filter(
                                is_active='1', tooluur__customer_id=bichilt.customer_id, year=bichilt.year, month=bichilt.month)
                            for bichilt1 in bichilts:
                                end_date = str(bichilt1.bichilt_date.year) + '-' + str(
                                    bichilt1.bichilt_date.month) + '-' + str(bichilt1.bichilt_date.day)
                                bichilt2 = Bichilt.objects.filter(
                                    is_active='1', id=bichilt1.prev_bichilt_id).first()
                                start_date = str(bichilt2.bichilt_date.year) + '-' + str(
                                    bichilt2.bichilt_date.month) + '-' + str(bichilt2.bichilt_date.day)
                                bichilt_data.append(
                                    {
                                        'basePrice': str(bichilt1.suuri_price),
                                        'tooluurCode': str(bichilt1.tooluur.tooluur.number),
                                        'dayFirst': str(bichilt2.day_balance),
                                        'dayLast': str(bichilt1.day_balance),
                                        'dayUsage': str(bichilt1.day_diff),
                                        'nightFirst': str(bichilt2.night_balance),
                                        'nightLast': str(bichilt1.night_balance),
                                        'nightUsage': str(bichilt1.night_diff),
                                        'zadgaiUsage': str(bichilt1.zadgai_diff),
                                        'lightFirst': str(bichilt2.light_balance),
                                        'lightLast': str(bichilt1.light_balance),
                                        'staticLightUsage': str(bichilt1.static_light)
                                    }
                                )
                            pay_date = cur_year + '-' + now_month + '-01 00:00:00.000000'
                            payment_history = list(PaymentHistory.objects.raw("""SELECT cus.id, IFNULL(SUM(pahi.pay_total), 0) AS pay_total 
                                FROM data_customer cus
                                JOIN data_paymenthistory pahi ON cus.id = pahi.customer_id
                                WHERE pahi.is_active = '1' AND pahi.customer_id = """ + str(user.id) + """ AND pahi.pay_date >= '""" + pay_date + """';"""))
                            if bichilt.uilchilgeenii_tulbur is not None:
                                uilchilgeenii_tulbur = bichilt.uilchilgeenii_tulbur
                            else:
                                uilchilgeenii_tulbur = Decimal(0)
                            if bichilt.is_discount == '1':
                                bichilt_tulbur = str(
                                    bichilt.payment_gap + uilchilgeenii_tulbur + bichilt.barimt_une + bichilt.tv_huraamj)
                            else:
                                bichilt_tulbur = str(
                                    bichilt.heregleenii_tulbur + uilchilgeenii_tulbur + bichilt.barimt_une + bichilt.tv_huraamj)
                        else:
                            bichilt_tulbur = 0.00
                            payment = Payment.objects.filter(
                                customer=user).first()
                        if '0' == cur_month[0]:
                            cur_month = cur_month[1]
                        cur_month_avlaga = Avlaga.objects.filter(
                            customer=user, is_active='1', month=cur_month, year=cur_year).first()
                        if cur_month_avlaga is None:
                            balance = round(float(
                                ehnii_balance) - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)
                        else:
                            balance = round(
                                float(ehnii_balance) + float(bichilt_tulbur), 2)
                            balance = round(
                                balance - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)
                        vat = int(balance) / 11

                        customerPayment = PaymentOrder.objects.filter(
                            customer_id=user.id, is_active=1).first()
                        if customerPayment is not None:
                            customerPayment.is_active = 0
                            customerPayment.save()
                        payment = PaymentOrder.objects.create(
                            payment_amount=balance, customer_id=user.id, created_date=now, is_active=1)
                        invoice_no = payment.invoice_no
                        if bichilt.aldangi_date > datetime.datetime.now():
                            undueLoss = ((float(bichilt_tulbur) * float(bichilt.ald_huvi)) / 100) * diff_dates(
                                bichilt.aldangi_date.date(), datetime.datetime.now().date())

                        # if bankCode==1:  #TODO bankCode yalgaatai avahaar bolvol
                        if int(user.customer_angilal) == 1:
                            data = {
                                'customerType': customerType,
                                'customerCode': user.code,
                                'customerName': user.first_name,
                                'startDate': start_date,
                                'endDate': end_date,
                                'detail': str(bichilt_data),
                                'tv': bichilt.tv_huraamj,
                                'bichilt': str(int(float(bichilt_tulbur))),
                                'serviceFee': uilchilgeenii_tulbur,
                                'vat': round(vat, 2),
                                'totalPayment': str(int(balance)),
                                'rest': str(int(float(ehnii_balance))),
                                # 'unduePercent': bichilt.ald_huvi,
                                # 'undueDateDiff': str(diff_dates(bichilt.aldangi_date.date(), datetime.datetime.now().date())),
                                # 'undueLoss': undueLoss,
                                'unduePercent': 0,
                                'undueDateDiff': str(diff_dates(bichilt.aldangi_date.date(), datetime.datetime.now().date())),
                                'undueLoss': 0,
                                'receiptFee': barimt_une,
                                'expiredDate': str(today[0:10]+' 23:59:59'),
                                'invoiceNo': str(invoice_no)
                            }
                        else:
                            data = {
                                'customerType': customerType,
                                'customerCode': user.code,
                                'customerName': user.first_name,
                                'startDate': start_date,
                                'endDate': end_date,
                                'detail': str(bichilt_data),
                                'bichilt': str(int(float(bichilt_tulbur))),
                                'serviceFee': uilchilgeenii_tulbur,
                                'vat': round(vat, 2),
                                'totalPayment': str(int(balance)),
                                'rest': str(int(float(ehnii_balance))),
                                # 'unduePercent': bichilt.ald_huvi,
                                # 'undueDateDiff': str(diff_dates(bichilt.aldangi_date.date(), datetime.datetime.now().date())),
                                # 'undueLoss': undueLoss,
                                'unduePercent': 0,
                                'undueDateDiff': str(diff_dates(bichilt.aldangi_date.date(), datetime.datetime.now().date())),
                                'undueLoss': 0,
                                'receiptFee': barimt_une,
                                'expiredDate': str(today[0:10]+' 23:59:59'),
                                'invoiceNo': str(invoice_no)
                            }
                        status = 1
                        message = 'Амжилттай'
                    else:
                        message = 'Харилцагчийн эхний үлдэгдэл олдсонгүй.'
                else:
                    message = 'Харилцагчийн код олдсонгүй.'
            else:
                message = 'Банкны код олдсонгүй.'
        else:
            message = 'Мэдээлэл дутуу илгээгдсэн байна.'
    except Exception as ex:
        status = 0
        error = str(ex)
        message = 'Алдаа гарлаа: ' + error
        data = ''
    finally:
        data_last = {
            'status': status,
            'message': message,
            'data': data
        }
        log = ServiceLog.objects.create(invoice_no=invoice_no, request=request.data, response=data_last, type='getUserElectricityInfo',
                                        request_date=today, response_date=datetime.datetime.now(), status=status, bank_type='', error=error)
        log.save()
        return HttpResponse(simplejson.dumps(data_last), content_type='application/json')


@api_view(['POST'])
# @basic_auth_required(
#     target_test=lambda request: not request.user.is_authenticated
# )
def putUserElectricityInfo(request):
    try:
        today = datetime.datetime.now()
        rq = request.data
        status = 0
        error = ''
        message = 'Харилцагчийн код буруу байна'
        data = {'message': message, 'status': status}

        user_code = rq.get('customerCode', '')
        total_payment = rq.get('totalPayment', '')
        bankCode = rq.get('bankCode', '')
        invoice = rq.get('invoiceNo', '')
        order_no = rq.get('orderNo', '')
        total = float(total_payment)
        customer = Customer.objects.filter(
            code=user_code, is_active='1').first()

        if customer is None:
            message = 'Харилцагчийн код буруу байна'
        else:
            if total < 0:
                message = 'Төлбөрийн дүн хасах дамжуулах боломжгүй'
            else:
                if len(order_no) < 1:
                    message = 'orderNo дамжуулах шаардлагатай'
                else:
                    bank = Bank.objects.filter(
                        code=bankCode, is_active='1').first()
                    if bank is None:
                        message = 'Банк төрөл буруу дамжуулсан'
                    else:
                        payment = PaymentOrder.objects.filter(
                            invoice_no=invoice, is_active=1).first()
                        if payment is None:
                            message = 'invoiceNo идэвхитэй олдсонгүй'
                        else:
                            minus1_month = today + relativedelta(months=-1)
                            last_date = str(today)[:10]
                            today_year = last_date[:4]
                            today_month = last_date[5:7]

                            pay_date = datetime.datetime.strptime(
                                last_date + ' 00:00', '%Y-%m-%d %H:%M')
                            his = PaymentHistory.objects.create(
                                pay_date=pay_date, pay_total=total, customer=customer)

                            payment.order_no = order_no
                            payment.paid_amount = total_payment
                            payment.is_active = 0
                            payment.save()
                            his.bank = bank
                            his.created_user_id = bank.id
                            his.save()
                            status = 1
                            message = 'Амжилттай'
    except Exception as ex:
        print(str(ex))
        error = str(ex)
        message = 'Алдаа гарлаа: ' + str(ex)
    finally:
        data = {'message': message, 'status': status}
        log = ServiceLog.objects.create(invoice_no=invoice, request=rq, response=data, type='putUserElectricityInfo',
                                        request_date=today, response_date=datetime.datetime.now(), status=status, bank_type=bankCode, error=error)
        log.save()
    return HttpResponse(simplejson.dumps(data), content_type='application/json')


def diff_dates(date1, date2):
    return abs(date2-date1).days
