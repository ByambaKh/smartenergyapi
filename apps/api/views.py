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
import simplejson
import json



class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


@api_view(['GET'])
def customer_list(request):
    if request.method == 'GET':
        q = "SELECT cu.id, cu.first_name, cu.last_name, cu.code, ad.address_name FROM data_customer as cu " \
            "LEFT JOIN data_address as ad ON cu.id=ad.customer_id"
        snippets = Customer.objects.raw(q)
        serializer = CustomerSerializer(snippets, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def check_staff_available(request):
    data = {"success": 1, "user_id": request.user.id}
    return Response(data)


@api_view(['GET'])
def get_balance_list(request):
    # (SELECT  AVG(bi.rush_diff) FROM data_bichilt bi INNER JOIN data_tooluurcustomer AS to_cu ON bi.tooluur_id = to_cu.id WHERE to_cu.tooluur_id = tocu.tooluur_id ORDER BY month , year DESC LIMIT 3) AS rush_average
    q = "SELECT tocu.id, tocu.tooluur_id, bi.day_balance, bi.night_balance, bi.rush_balance, bi.id as last_bichilt_id, bi.month, bi.year, bi.day_diff, bi.night_diff, bi.rush_diff  " \
        "FROM data_tooluurcustomer AS tocu" \
        "   INNER JOIN " \
        "data_bichilt AS bi ON (bi.tooluur_id = tocu.id)" \
        "   LEFT OUTER JOIN " \
        "data_bichilt AS bi2 ON (tocu.id = bi2.tooluur_id AND bi.id < bi2.id) " \
        "WHERE " \
        "bi2.id IS NULL;"
    print(q)
    snippets = Bichilt.objects.raw(q)
    serializer = ZaaltSerializer(snippets, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_tooluur_list(request):
    q = "SELECT to_cu.id, too.id, to_cu.customer_code, too.name as tooluur_name, too.number as tooluur_number, too.tariff, too.balance_value as init_day, too.balance_value_night as init_night, too.balance_value_rush as init_rush, to_cu.customer_angilal, to_cu.dedstants_id, to_cu.bair_id" \
        " FROM data_tooluurcustomer as to_cu " \
        "INNER JOIN data_tooluur as too ON too.id = to_cu.tooluur_id WHERE to_cu.is_active='1';"
    print(q)
    snippets = TooluurCustomer.objects.raw(q)
    serializer = TooluurSerializer(snippets, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def taslalt_hiih_list(request):
    if request.method == 'GET':
        q = "SELECT dt.id as id, dt.code as code, dt.last_name as lastName, dt.first_name as firstName" \
            " FROM data_taslaltzalgalt dt LEFT JOIN data_aimag da ON dt.aimag_code = da.code AND da.is_active = '1' " \
            " LEFT JOIN data_duureg dd ON dt.duureg_code = dd.code AND dd.is_active = '1' " \
            " LEFT JOIN data_horoo dh ON dt.horoo_code = dh.code AND dh.is_active = '1' " \
            " LEFT JOIN data_hothon dhh ON dt.hothon_code = dhh.code AND dhh.is_active = '1' " \
            " LEFT JOIN data_block db ON dt.block_code = db.code AND db.is_active = '1' WHERE dt.status = '1';"
        snippets = TaslaltZalgalt.objects.raw(q)
        serializer = TaslaltZalgaltSerializer(snippets, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def get_payservice_list(request):
    q = 'SELECT id, name, payment, angilal, is_active FROM data_tulburtuilchilgee WHERE is_active="1";'
    q_result = TulburtUilchilgee.objects.raw(q)
    serializers = PayServiceSerializer(q_result, many=True)
    return Response(serializers.data)


@api_view(['GET'])
def get_dedstants_list(request):
    q_result = DedStants.objects.filter(is_active="1")
    serializers = DedstantsSerializer(q_result, many=True)
    return Response(serializers.data)


@api_view(['GET'])
def get_bair_list(request):
    q_result = Bair.objects.filter(is_active="1")
    serializers = BairSerializer(q_result, many=True)
    return Response(serializers.data)


@api_view(['POST'])
def post_pay_service(request):
    bich_man = BichiltManager()
    serializer = CustomerPayServiceSerializer(data=request.data)
    print(request.data)
    error = {'error': ''}
    if serializer.is_valid():
        uil_date = datetime.datetime.strptime(
            serializer.data['uil_date'], '%Y-%m-%dT%H:%M:%S')
        try:
            customer = Customer.objects.get(
                code=serializer.data['customer_id'])
            try:
                monter = User.objects.get(id=int(serializer.data['monter_id']))
                try:
                    tooluur = Tooluur.objects.get(
                        id=int(serializer.data['tooluur_id']))
                    try:
                        uilchilgee = TulburtUilchilgee.objects.get(
                            id=int(serializer.data['uilchilgee_id']))
                        u = CustomerUilchilgeeTulbur.objects.create(tooluur=tooluur,
                                                                    customer=customer,
                                                                    monter=monter,
                                                                    created_user_id=int(
                                                                        serializer.data['monter_id']),
                                                                    uilchilgee=uilchilgee,
                                                                    uil_date=uil_date)
                        u.payment = Decimal(serializer.data['payment'])
                        if '0' == serializer.data['month'][0]:
                            t_month = serializer.data['month'][1]
                        else:
                            t_month = serializer.data['month']
                        u.month = t_month
                        u.year = serializer.data['year']
                        a = None
                        tc = TooluurCustomer.objects.get(
                            tooluur=u.tooluur, customer_code=u.customer.code)
                        if (tc != None):
                            tulbur_date = getPayDate(
                                tc, int(u.year), int(u.month))
                            cur_date = datetime.datetime.now()
                            avlaga_date = datetime.datetime.now()

                            if tc.customer.customer_angilal == '0':
                                prices = PriceTariff.objects.filter(une_type=0)[
                                    :1].get()
                            else:
                                prices = PriceTariff.objects.filter(une_type=1)[
                                    :1].get()

                            if int(cur_date.day) < 25 and int(cur_date.month) < 12:
                                avlaga_date = uil_date
                            elif int(cur_date.day) > 25 and int(cur_date.month) < 12:
                                avlaga_date = datetime.datetime.strptime(
                                    str(uil_date.year) + '-' + str(int(uil_date.month) + 1) + '-10', '%Y-%m-%d')
                            elif int(cur_date.day) > 25 and int(cur_date.month) > 12:
                                avlaga_date = datetime.datetime.strptime(
                                    str(int(uil_date.year) + 1) + '-01-10', '%Y-%m-%d')
                            try:
                                a = Avlaga.objects.get(
                                    customer=tc.customer, year=avlaga_date.year, month=avlaga_date.month)
                            except Avlaga.DoesNotExist:
                                a = None
                            if (a != None):
                                a.uilchilgeenii_tulbur = Decimal(
                                    a.uilchilgeenii_tulbur if a.uilchilgeenii_tulbur else 0.00) + Decimal(u.payment)
                                a.pay_uld = Decimal(
                                    a.pay_uld) + Decimal(a.uilchilgeenii_tulbur if a.uilchilgeenii_tulbur else 0.00)
                            else:
                                a = Avlaga.objects.create(created_user_id=request.user.id, year=avlaga_date.year,
                                                          month=avlaga_date.month, customer=tc.customer, tulbur_date=tulbur_date)
                                a.uilchilgeenii_tulbur = Decimal(u.payment)
                                a.pay_uld = Decimal(
                                    u.payment) + Decimal(bich_man.add_nuat_price(prices.barimt_une))
                            a.barimt_une = Decimal(
                                bich_man.add_nuat_price(prices.barimt_une))
                            a.save()
                        u.avlaga = a
                        u.save()
                        return Response({'status': 'OK'})
                    except TulburtUilchilgee.DoesNotExist:
                        error['error'] = "Not found UILCHILGEE_ID."
                except Tooluur.DoesNotExist:
                    error['error'] = "Not found TOOLUUR_ID."
            except User.DoesNotExist:
                error['error'] = "Not found MONTER_ID."
        except Customer.DoesNotExist:
            error['error'] = "Not found CUSTOMER_ID."
        print(error)
        return Response(error, status=status.HTTP_400_BAD_REQUEST)
    else:
        error['error'] = serializer.errors
        print(serializer.errors)
    return Response(error, status=status.HTTP_400_BAD_REQUEST)


class AddZaaltView(APIView):
    NUAT = 0.1
    POWER_TIME_BY_USER = 12
    POWER_TIME_BY_ORG = 5

    def post(self, request, format=None):

        #result = request.data
        # print(result['id'])
        # handle1=open('file.txt','r+')
        # handle1.write(json.dumps(result))
        # handle1.close()
        serializer = CustomerZaaltSerializer(data=request.data)
        if serializer.is_valid():

            day = serializer.data['day_balance']
            night = serializer.data['night_balance']
            rush = serializer.data['rush_balance']
            tooluur_number = serializer.data['tooluur_number']
            customer_id = serializer.data['customer_id']
            employee_id = serializer.data['employee_id']
            bichilt_date = serializer.data['bichilt_date']
            customer_angilal = serializer.data['customer_angilal']
            is_problem = serializer.data['is_problem']
            zadgai_bichilt = "0"
            description = ""

            if is_problem == '':
                is_problem = "0"
            if night == '':
                night = "0"
            if rush == '':
                rush = "0"

            b_date = datetime.datetime.strptime(
                bichilt_date, '%Y-%m-%dT%H:%M:%S')
            response = BichiltManager().create_bichilt(customer_angilal, tooluur_number, customer_id,
                                                       b_date, zadgai_bichilt, day, night, rush, description, employee_id, is_problem)
            if response["code"] == 400:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({'status': 'OK'})
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NominPos(APIView):

    def get(self, request):

        rq = request.GET
        user_code = rq.get('cusnum', '')
        balance_type = 'balance'
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
        cdatas = []
        if user_code != '':
            try:
                users = Customer.objects.filter(code=user_code, is_active='1')

                if len(users) == 0 or users is None:
                    users = Customer.objects.filter(
                        phone=user_code, is_active='1')
                if users is not None and len(users) > 0:
                    userdatas = []

                    for user in users:
                        print(user.id)
                        # cdatas.append(user.id)
                        ehnii_balance = Final_Balance.objects.filter(customer_id=user.id, year=year,
                                                                     month=month).first().balance
                        print(ehnii_balance)
                        # address = Address.objects.filter(customer=user, is_active='1').first()

                        payment_history = None
                        bichilt_data = []
                        bichilt = Avlaga.objects.filter(
                            customer=user, is_active='1').order_by('-created_date').first()
                        uilchilgeenii_tulbur = 0
                        start_date = ''
                        end_date = ''
                        barimt_une = 0
                        udur = 0
                        shunu = 0
                        if bichilt is not None:
                            tariff = PriceTariff.objects.get(
                                une_type='1', is_active='1')
                            udur = tariff.odor_une + tariff.serg_une
                            shunu = tariff.shono_une + tariff.serg_une
                            barimt_une = bichilt.barimt_une
                            bichilts = Bichilt.objects.filter(is_active='1', tooluur__customer_id=bichilt.customer_id,
                                                              year=bichilt.year, month=bichilt.month)
                            for bichilt1 in bichilts:
                                end_date = str(bichilt1.bichilt_date.year) + '-' + str(
                                    bichilt1.bichilt_date.month) + '-' + str(bichilt1.bichilt_date.day)
                                bichilt2 = Bichilt.objects.filter(
                                    is_active='1', id=bichilt1.prev_bichilt_id).first()
                                start_date = str(bichilt2.bichilt_date.year) + '-' + str(
                                    bichilt2.bichilt_date.month) + '-' + str(
                                    bichilt2.bichilt_date.day)
                                bichilt_data.append(
                                    {'code': bichilt1.tooluur.tooluur.number, 'dayfirst': str(bichilt2.day_balance),
                                     'daylast': str(bichilt1.day_balance), 'day_usage': str(bichilt1.day_diff),
                                     'nightfirst': str(bichilt2.night_balance),
                                     'nightlast': str(bichilt1.night_balance), 'night_usage': str(bichilt1.night_diff)})
                            # if len(month) == 1:
                            #     month += '0' + month
                            pay_date = cur_year + '-' + now_month + '-01 00:00:00.000000'

                            payment_history = list(PaymentHistory.objects.raw("""SELECT cust.id, IFNULL(SUM(pahi.pay_total), 0) AS pay_total FROM data_customer cust
                                            JOIN data_paymenthistory pahi ON cust.id = pahi.customer_id
                                            WHERE pahi.is_active = '1' AND pahi.customer_id = """ + str(
                                user.id) + """ AND pahi.pay_date >= '""" + pay_date + """';"""))

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
                            ehnii = 0.00 if payment is None else -payment.uldegdel

                        if '0' == cur_month[0]:
                            cur_month = cur_month[1]
                        cur_month_avlaga = Avlaga.objects.filter(customer=user, is_active='1', month=cur_month,
                                                                 year=cur_year).first()
                        if cur_month_avlaga is None:
                            ehnii = round(float(ehnii_balance) -
                                          float(bichilt_tulbur), 2)
                            #ehnii = round(ehnii - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)
                            balance = round(
                                float(ehnii_balance) - float(
                                    0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)

                        else:
                            ehnii = float(ehnii_balance)
                            balance = round(
                                float(ehnii_balance) + float(bichilt_tulbur), 2)
                            balance = round(
                                balance - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)

                        vat = int(balance) / 11
                        data = {

                            'cusnum': user.code,
                            'cusname': user.first_name,
                            'startdate': start_date,
                            'enddate': end_date,
                            'info': bichilt_data,
                            'base_tariff': '2000',
                            'tv': bichilt.tv_huraamj,
                            'bichilt': str(int(float(bichilt_tulbur))),
                            'servicefee': uilchilgeenii_tulbur,
                            'vat': round(vat, 2),
                            'totalpayment': str(int(balance)),
                            'rest': str(int(float(ehnii_balance))),
                            'undueloss': 0,
                            'receiptfee': barimt_une,
                            'daytariff': udur,
                            'nighttariff': shunu
                        }
                        userdatas.append(data)
                    if len(userdatas) == 1:
                        data_last = {
                            'errMsg': 'success',
                            'success': 1,
                            'data': userdatas[0]
                        }

                    else:
                        codes = "Энэ утасны дугаар дээр олон хэрэглэгч бүртгэлтэй байна. "
                        for u in userdatas:
                            codes += u["cusnum"]
                            codes += ", "
                        data_last = {
                            'errMsg': codes,
                            'success': 0,
                            'data': userdatas
                        }

                    return HttpResponse(simplejson.dumps(data_last), content_type='application/json')

                else:
                    multi_dict = rq
                    dataa = []
                    # for key in multi_dict:
                    #     dataa.append({"key": key, "value":multi_dict[key]})

                    data_last = {
                        'errMsg': 'Харилцагчийн код олдсонгүй.',
                        'success': 0,
                        'data': dataa
                    }
            except Exception:
                data_last = {
                    'errMsg': 'Харилцагчийн код олдсонгүй',
                    'success': 0,
                    'data': cdatas
                }

        else:
            multi_dict = rq
            dataa = []
            # for key in multi_dict:
            #     dataa.append({"key": key, "value":multi_dict[key]})

            data_last = {
                'errMsg': 'Харилцагчийн код илгээгээгүй байна.',
                'success': 0,
                'data': dataa
            }
        return HttpResponse(simplejson.dumps(data_last), content_type='application/json')

    def post(self, request):
        rq = request.data
        user_code = rq.get('cusnum', '')
        balance_type = 'balance'
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
        cdatas = []
        if user_code != '':
            try:
                users = Customer.objects.filter(code=user_code, is_active='1')
                if len(users) == 0 or users is None:
                    users = Customer.objects.filter(
                        phone=user_code, is_active='1')
                if users is not None and len(users) > 0:
                    userdatas = []
                    for user in users:
                        # cdatas.append(user.id)
                        ehnii_balance = Final_Balance.objects.filter(
                            customer_id=user.id, year=year, month=month).first().balance
                        # address = Address.objects.filter(customer=user, is_active='1').first()

                        payment_history = None
                        bichilt_data = []
                        bichilt = Avlaga.objects.filter(
                            customer=user, is_active='1').order_by('-created_date').first()
                        uilchilgeenii_tulbur = 0
                        start_date = ''
                        end_date = ''
                        barimt_une = 0
                        udur = 0
                        shunu = 0
                        if bichilt is not None:
                            tariff = PriceTariff.objects.get(
                                une_type='1', is_active='1')
                            udur = tariff.odor_une + tariff.serg_une
                            shunu = tariff.shono_une + tariff.serg_une
                            barimt_une = bichilt.barimt_une
                            bichilts = Bichilt.objects.filter(is_active='1', tooluur__customer_id=bichilt.customer_id,
                                                              year=bichilt.year, month=bichilt.month)
                            for bichilt1 in bichilts:
                                end_date = str(bichilt1.bichilt_date.year) + '-' + str(
                                    bichilt1.bichilt_date.month) + '-' + str(bichilt1.bichilt_date.day)
                                bichilt2 = Bichilt.objects.filter(
                                    is_active='1', id=bichilt1.prev_bichilt_id).first()
                                start_date = str(bichilt2.bichilt_date.year) + '-' + str(bichilt2.bichilt_date.month) + '-' + str(
                                    bichilt2.bichilt_date.day)
                                bichilt_data.append({'code': bichilt1.tooluur.tooluur.number, 'dayfirst': str(bichilt2.day_balance), 'daylast': str(bichilt1.day_balance), 'day_usage': str(bichilt1.day_diff),
                                                     'nightfirst': str(bichilt2.night_balance), 'nightlast': str(bichilt1.night_balance), 'night_usage': str(bichilt1.night_diff)})
                            # if len(month) == 1:
                            #     month += '0' + month
                            pay_date = cur_year + '-' + now_month + '-01 00:00:00.000000'

                            payment_history = list(PaymentHistory.objects.raw("""SELECT cust.id, IFNULL(SUM(pahi.pay_total), 0) AS pay_total FROM data_customer cust
                                    JOIN data_paymenthistory pahi ON cust.id = pahi.customer_id
                                    WHERE pahi.is_active = '1' AND pahi.customer_id = """ + str(
                                user.id) + """ AND pahi.pay_date >= '""" + pay_date + """';"""))

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
                            ehnii = 0.00 if payment is None else -payment.uldegdel

                        if '0' == cur_month[0]:
                            cur_month = cur_month[1]
                        cur_month_avlaga = Avlaga.objects.filter(customer=user, is_active='1', month=cur_month,
                                                                 year=cur_year).first()
                        if cur_month_avlaga is None:
                            ehnii = round(float(ehnii_balance) -
                                          float(bichilt_tulbur), 2)
                            # ehnii = round(ehnii - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)
                            balance = round(
                                float(ehnii_balance) - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)

                        else:
                            ehnii = float(ehnii_balance)
                            balance = round(
                                float(ehnii_balance) + float(bichilt_tulbur), 2)
                            balance = round(
                                balance - float(0 if len(payment_history) < 1 else payment_history[0].pay_total), 2)

                        vat = int(balance) / 11
                        data = {

                            'cusnum': user.code,
                            'cusname': user.first_name,
                            'startdate': start_date,
                            'enddate': end_date,
                            'info': bichilt_data,
                            'base_tariff': '2000',
                            'tv': bichilt.tv_huraamj,
                            'bichilt': str(int(float(bichilt_tulbur))),
                            'servicefee': uilchilgeenii_tulbur,
                            'vat': round(vat, 2),
                            'totalpayment': str(int(balance)),
                            'rest': str(int(float(ehnii_balance))),
                            'undueloss': 0,
                            'receiptfee': barimt_une,
                            'daytariff': udur,
                            'nighttariff': shunu
                        }
                        userdatas.append(data)
                    if len(userdatas) == 1:

                        data_last = {
                            'errMsg': 'success',
                            'success': 1,
                            'data': userdatas[0]
                        }
                    else:
                        codes = "Энэ утасны дугаар дээр олон хэрэглэгч бүртгэлтэй байна. "
                        for u in userdatas:
                            codes += u["cusnum"]
                            codes += ", "
                        data_last = {
                            'errMsg': codes,
                            'success': 0,
                            'data': userdatas
                        }

                    return HttpResponse(simplejson.dumps(data_last), content_type='application/json')

                else:
                    multi_dict = rq
                    dataa = []
                    # for key in multi_dict:
                    #     dataa.append({"key": key, "value":multi_dict[key]})

                    data_last = {
                        'errMsg': 'Харилцагчийн код олдсонгүй.',
                        'success': 0,
                        'data': dataa
                    }
            except Exception:
                data_last = {
                    'errMsg': 'Харилцагчийн код олдсонгүй',
                    'success': 0,
                    'data': cdatas
                }

        else:
            multi_dict = rq
            dataa = []
            # for key in multi_dict:
            #     dataa.append({"key": key, "value":multi_dict[key]})

            data_last = {
                'errMsg': 'Харилцагчийн код илгээгээгүй байна.',
                'success': 0,
                'data': dataa
            }
        return HttpResponse(simplejson.dumps(data_last), content_type='application/json')


class NominPosPayment(APIView):

    def post(self, request, format=None):
        user_code = ''
        total_payment = 0.00
        status = 0
        message = 'Алдаа'
        today = datetime.datetime.now()
        bank_code = ''
        error = ''
        rq = ''
        try:
            rq = request.data
            serializer = PosPaymentSerializer(data=request.data)
            if serializer.is_valid():
                user_code = serializer.data['cusnum']
                total_payment = serializer.data['totalpayment']
                try:
                    total = float(total_payment)
                except Exception:
                    total = 0.00

                customer = Customer.objects.filter(code=user_code).first()
                if customer is not None:
                    last_date = str(today)[:10]
                    pay_date = datetime.datetime.strptime(
                        last_date + ' 00:00', '%Y-%m-%d %H:%M')

                    his = PaymentHistory.objects.create(
                        pay_date=pay_date, pay_total=total, customer=customer)
                    bank = Bank.objects.filter(code=7).first()
                    if bank is not None:
                        bank_code = bank.code
                        his.bank = bank
                    his.created_user_id = 1
                    his.save()
                    message = 'success'
                    status = 1

                else:
                    message = 'Хэрэглэгч олдсонгүй'

            else:
                message = 'Алдаатай утга дамжуулсан'
        except Exception as ex:
            error = str(ex)
            message = 'Алдаа гарлаа: ' + str(ex)
        finally:
            data = {'errMsg': message, 'success': status}
            log = ServiceLog.objects.create(invoice_no=user_code, request=rq, response=data, type='nominPosPayment',
                                            request_date=today, response_date=datetime.datetime.now(), status=status, bank_type=bank_code, error=error)
            log.save()
        return HttpResponse(simplejson.dumps(data), content_type='application/json')

    def get(self, request, format=None):
        rq = request.GET
        user_code = rq.get('cusnum', '')
        total_payment = rq.get('totalpayment', '')
        try:
            total = float(total_payment)
        except Exception:
            total = 0.00
        balance_type = 'balance'

        customer = Customer.objects.filter(code=user_code).first()

        if customer is not None:
            today = datetime.datetime.now()
            minus1_month = today + relativedelta(months=-1)
            last_date = str(today)[:10]

            today_year = last_date[:4]
            today_month = last_date[5:7]

            pay_date = datetime.datetime.strptime(
                last_date + ' 00:00', '%Y-%m-%d %H:%M')

            his = PaymentHistory.objects.create(
                pay_date=pay_date, pay_total=total, customer=customer)
            bank = Bank.objects.filter(code=7).first()

            his.bank = bank
            his.created_user_id = 1
            his.save()

        data = {'errMsg': 'success', 'success': 1}
        return HttpResponse(simplejson.dumps(data), content_type='application/json')


class NominPosPaymentOldVersion(APIView):

    def post(self, request, format=None):
        rq = request.data
        user_code = rq.get('cusnum', '')
        total_payment = rq.get('totalpayment', '')
        try:
            total = float(total_payment)
        except Exception:
            total = 0.00
        balance_type = 'balance'

        customer = Customer.objects.filter(code=user_code).first()

        if customer is not None:
            today = datetime.datetime.now()
            minus1_month = today + relativedelta(months=-1)
            last_date = str(today)[:10]

            today_year = last_date[:4]
            today_month = last_date[5:7]

            pay_date = datetime.datetime.strptime(
                last_date + ' 00:00', '%Y-%m-%d %H:%M')

            his = PaymentHistory.objects.create(
                pay_date=pay_date, pay_total=total, customer=customer)
            bank = Bank.objects.filter(code=7).first()

            his.bank = bank
            his.created_user_id = 1
            his.save()

        data = {'errMsg': 'success', 'success': 1}
        return HttpResponse(simplejson.dumps(data), content_type='application/json')

    def get(self, request, format=None):
        rq = request.GET
        user_code = rq.get('cusnum', '')
        total_payment = rq.get('totalpayment', '')
        try:
            total = float(total_payment)
        except Exception:
            total = 0.00
        balance_type = 'balance'

        customer = Customer.objects.filter(code=user_code).first()

        if customer is not None:
            today = datetime.datetime.now()
            minus1_month = today + relativedelta(months=-1)
            last_date = str(today)[:10]

            today_year = last_date[:4]
            today_month = last_date[5:7]

            pay_date = datetime.datetime.strptime(
                last_date + ' 00:00', '%Y-%m-%d %H:%M')

            his = PaymentHistory.objects.create(
                pay_date=pay_date, pay_total=total, customer=customer)
            bank = Bank.objects.filter(code=7).first()

            his.bank = bank
            his.created_user_id = 1
            his.save()

        data = {'errMsg': 'success', 'success': 1}
        return HttpResponse(simplejson.dumps(data), content_type='application/json')
