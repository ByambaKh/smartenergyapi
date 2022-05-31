import json
import logging
import re
import requests
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.views import View
from apps.data.models import Avlaga, MedeelehZagvar, TooluurCustomer, Aimag, Cycle
from django.shortcuts import render, HttpResponse, redirect
import simplejson


class Warning(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_medeelehzagvar'
    template_name = 'homepage/medeeleh/medeeleh.html'
    menu = '11'
    sub = '1'

    def get(self, request, type, *args, **kwargs):
        aimags = None
        cycle = Cycle.objects.filter(is_active='1')

        if '0' == str(type):
            aimags = Aimag.objects.filter(is_active="1")

        data = {
            'aimags': aimags,
            'menu': self.menu,
            'sub': self.sub,
            "cycle": cycle,
        }
        return render(request, self.template_name, data)

    def post(self, request, type, *args, **kwargs):
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        balance_type = 'balance'

        year = start_date[:4]
        month = start_date[5:7]
        day = start_date[8:10]

        if '0' == month[0]:
            month = month[1]
        if '1' == month:
            year = str(int(year) - 1)
            month = '12'
        elif '8' == month and year == '2017':
            balance_type = 'ehnii'
        else:
            month = str(int(month) - 1)

        if '0' == day[0]:
            day = day[1]

        if '1' == str(type):
            first_name = request.POST['customer_name']
            code = request.POST['customer_code']
            cycle = request.POST['select_cycle']
            address = request.POST['address']
            customer_angilal = request.POST['customer_angilal']

            if int(day) == 1:
                qry = """SELECT tocu.id, cust.code, cust.register, cust.phone, cust.last_name, cust.first_name, cust.customer_angilal, addr.address_name, addr.toot, addr.building_number, cust.email,
                            IFNULL((SELECT fiba.""" + balance_type + """ FROM data_final_balance fiba WHERE fiba.year = '""" + year + """' AND fiba.month = '""" + month + """' AND tocu.customer_id = fiba.customer_id), 0) AS ehnii,
                            IFNULL((SELECT SUM(avbi.heregleenii_tulbur + avbi.uilchilgeenii_tulbur + avbi.tv_huraamj + IFNULL(avbi.light, 0.00) + IFNULL(avbi.ten, 0.00) + avbi.barimt_une) FROM data_avlaga avbi WHERE avbi.created_date >= '""" + start_date + """ 00:00:00.000000'
                            AND avbi.created_date <= '""" + end_date + """ 23:59:59.999999' AND avbi.is_active = '1' AND tocu.customer_id = avbi.customer_id), 0) AS bichilt,
                            IFNULL((SELECT SUM(pahi.pay_total) FROM data_paymenthistory pahi WHERE pahi.is_active = '1' AND pahi.pay_date >= '""" + start_date + """ 00:00:00.000000' AND pahi.pay_date <= '""" + end_date + """ 23:59:59.999999'
                            AND pahi.is_active = '1' AND tocu.customer_id = pahi.customer_id), 0) AS payment,
                            (SELECT COUNT(tc.id) FROM data_tooluurcustomer tc WHERE tc.customer_id = cust.id) AS tool_count
                            , count( distinct a.id ) avlaga_count
                            , h.head_tool_cus_id
                            , a.id avlaga_id
                            FROM data_tooluurcustomer tocu 
                            JOIN data_customer cust ON tocu.customer_id = cust.id
                            left join data_avlaga a on cust.id = a.customer_id
                            and a.created_date between '""" + start_date + """ 00:00:00.000000' AND '""" + end_date + """ 23:59:59.999999'
                            LEFT JOIN data_address addr ON cust.id = addr.customer_id
                            LEFT JOIN data_geree geree ON cust.code = geree.customer_code
                            left join data_hasagdahtooluur h on tocu.id = h.head_tool_cus_id
                            WHERE tocu.is_active = '1' AND tocu.customer_angilal = '1'"""
            else:
                if len(month) == 0:
                    month = '0' + month
                sub_start_date = year + '-' + month + '-01'
                qry = """SELECT tocu.id, cust.code, cust.register, cust.phone, cust.last_name, cust.first_name, cust.customer_angilal, addr.address_name, addr.toot, addr.building_number, cust.email,
                            (IFNULL((SELECT fiba.""" + balance_type + """ FROM data_final_balance fiba WHERE fiba.year = '""" + year + """' AND fiba.month = '""" + month + """' AND tocu.customer_id = fiba.customer_id), 0) - 
                            IFNULL((SELECT SUM(pahi.pay_total) FROM data_paymenthistory pahi WHERE pahi.is_active = '1' AND pahi.pay_date >= '""" + sub_start_date + """ 00:00:00.000000' AND pahi.pay_date <= '""" + start_date + """" 23:59:59.999999'
                            AND pahi.is_active = '1' AND tocu.customer_id = pahi.customer_id), 0)) AS ehnii,
                            IFNULL((SELECT SUM(avbi.heregleenii_tulbur + avbi.uilchilgeenii_tulbur + avbi.tv_huraamj + IFNULL(avbi.light, 0.00) + IFNULL(avbi.ten, 0.00) + avbi.barimt_une) FROM data_avlaga avbi WHERE avbi.created_date >= '""" + start_date + """" 00:00:00.000000'
                            AND avbi.created_date <= '""" + end_date + """ 23:59:59.999999' AND avbi.is_active = '1' AND tocu.customer_id = avbi.customer_id), 0) AS bichilt,
                            IFNULL((SELECT SUM(pahi.pay_total) FROM data_paymenthistory pahi WHERE pahi.is_active = '1' AND pahi.is_active = '1' AND pahi.pay_date >= '""" + start_date + """" 00:00:00.000000' AND pahi.pay_date <= '""" + end_date + """ 23:59:59.999999'
                            AND pahi.is_active = '1' AND tocu.customer_id = pahi.customer_id), 0) AS payment,
                            (SELECT COUNT(tc.id) FROM data_tooluurcustomer tc WHERE tc.customer_id = cust.id) AS tool_count
                            , count( distinct a.id ) avlaga_count
                            , h.head_tool_cus_id
                            , a.id avlaga_id
                            FROM data_tooluurcustomer tocu 
                            JOIN data_customer cust ON tocu.customer_id = cust.id
                            left join data_avlaga a on cust.id = a.customer_id
                            and a.created_date between '""" + start_date + """ 00:00:00.000000' AND '""" + end_date + """ 23:59:59.999999'
                            LEFT JOIN data_address addr ON cust.id = addr.customer_id
                            LEFT JOIN data_geree geree ON cust.code = geree.customer_code
                            left join data_hasagdahtooluur h on tocu.id = h.head_tool_cus_id
                            WHERE tocu.is_active = '1' AND tocu.customer_angilal = '1'"""

            if first_name != '':
                qry = qry + " AND cust.first_name LIKE '%%" + first_name + "%%'"
            if code != '':
                qry = qry + " AND cust.code = '" + code + "'"
            if cycle != '':
                qry = qry + " AND geree.cycle_code = '" + cycle + "'"
            if address != '':
                qry = qry + " AND addr.address_name LIKE '%%" + address + "%%'"
            if customer_angilal != '':
                qry = qry + " AND cust.customer_angilal = '" + customer_angilal + "'"
            qry = qry + " GROUP BY tocu.customer_id ORDER BY cust.code;"

            search_q = { 'customer_name': first_name, 'customer_code': code, 'start_date': start_date, 'filter':filter , 'end_date': end_date, 'address': address, 'customer_angilal': customer_angilal, 'cycle':cycle }
        elif '2' == str(type):
            aimag = request.POST['aimag']
            duureg = request.POST['duureg']
            khoroo = request.POST['khoroo']
            hothon = request.POST['hothon']
            egnee = request.POST.get('egnee', '')
            bair = request.POST.get('bair', '')

            if int(day) == 1:
                qry = """SELECT tocu.id, cust.code, cust.register, cust.phone, cust.last_name, cust.first_name, cust.customer_angilal, addr.address_name, addr.toot, addr.hothon_code, addr.building_number, cust.email,
                            IFNULL((SELECT fiba.""" + balance_type + """ FROM data_final_balance fiba WHERE fiba.year = '""" + year + """' AND fiba.month = '""" + month + """' AND tocu.customer_id = fiba.customer_id), 0) AS ehnii,
                            IFNULL((SELECT SUM(avbi.heregleenii_tulbur + avbi.uilchilgeenii_tulbur + avbi.tv_huraamj + IFNULL(avbi.light, 0.00) + IFNULL(avbi.ten, 0.00) + avbi.barimt_une) FROM data_avlaga avbi WHERE avbi.created_date >= '""" + start_date + """ 00:00:00.000000'
                            AND avbi.created_date <= '""" + end_date + """ 23:59:59.999999' AND avbi.is_active = '1' AND tocu.customer_id = avbi.customer_id), 0) AS bichilt,
                            IFNULL((SELECT SUM(pahi.pay_total) FROM data_paymenthistory pahi WHERE pahi.is_active = '1' AND pahi.pay_date >= '""" + start_date + """ 00:00:00.000000' AND pahi.pay_date <= '""" + end_date + """ 23:59:59.999999'
                            AND pahi.is_active = '1' AND tocu.customer_id = pahi.customer_id), 0) AS payment,
                            (SELECT COUNT(tc.id) FROM data_tooluurcustomer tc WHERE tc.customer_id = cust.id) AS tool_count
                            , count( distinct a.id ) avlaga_count
                            , h.head_tool_cus_id
                            , a.id avlaga_id
                            FROM data_tooluurcustomer tocu 
                            JOIN data_customer cust ON tocu.customer_id = cust.id
                            left join data_avlaga a on cust.id = a.customer_id
                            and a.created_date between '""" + start_date + """ 00:00:00.000000' AND '""" + end_date + """ 23:59:59.999999'
                            LEFT JOIN data_address addr ON cust.id = addr.customer_id
                            left join data_hasagdahtooluur h on tocu.id = h.head_tool_cus_id
                            WHERE tocu.is_active = '1' AND tocu.customer_angilal = '1'"""
            else:
                if len(month) == 0:
                    month = '0' + month
                sub_start_date = year + '-' + month + '-01'
                qry = """SELECT tocu.id, cust.code, cust.register, cust.phone, cust.last_name, cust.first_name, cust.customer_angilal, addr.address_name, addr.toot, addr.hothon_code, addr.building_number, cust.email,
                            (IFNULL((SELECT fiba.""" + balance_type + """ FROM data_final_balance fiba WHERE fiba.year = '""" + year + """' AND fiba.month = '""" + month + """' AND tocu.customer_id = fiba.customer_id), 0) - 
                            IFNULL((SELECT SUM(pahi.pay_total) FROM data_paymenthistory pahi WHERE pahi.is_active = '1' AND pahi.pay_date >= '""" + sub_start_date + """ 00:00:00.000000' AND pahi.pay_date <= '""" + start_date + """" 23:59:59.999999'
                            AND pahi.is_active = '1' AND tocu.customer_id = pahi.customer_id), 0)) AS ehnii,
                            IFNULL((SELECT SUM(avbi.heregleenii_tulbur + avbi.uilchilgeenii_tulbur + avbi.tv_huraamj + IFNULL(avbi.light, 0.00) + IFNULL(avbi.ten, 0.00) + avbi.barimt_une) FROM data_avlaga avbi WHERE avbi.created_date >= '""" + start_date + """" 00:00:00.000000'
                            AND avbi.created_date <= '""" + end_date + """ 23:59:59.999999' AND avbi.is_active = '1' AND tocu.customer_id = avbi.customer_id), 0) AS bichilt,
                            IFNULL((SELECT SUM(pahi.pay_total) FROM data_paymenthistory pahi WHERE pahi.is_active = '1' AND pahi.is_active = '1' AND pahi.pay_date >= '""" + start_date + """" 00:00:00.000000' AND pahi.pay_date <= '""" + end_date + """ 23:59:59.999999'
                            AND pahi.is_active = '1' AND tocu.customer_id = pahi.customer_id), 0) AS payment,
                            (SELECT COUNT(tc.id) FROM data_tooluurcustomer tc WHERE tc.customer_id = cust.id) AS tool_count
                            , count( distinct a.id ) avlaga_count
                            , h.head_tool_cus_id
                            , a.id avlaga_id
                            FROM data_tooluurcustomer tocu 
                            JOIN data_customer cust ON tocu.customer_id = cust.id
                            left join data_avlaga a on cust.id = a.customer_id
                            and a.created_date between '""" + start_date + """ 00:00:00.000000' AND '""" + end_date + """ 23:59:59.999999'
                            LEFT JOIN data_address addr ON cust.id = addr.customer_id
                            left join data_hasagdahtooluur h on tocu.id = h.head_tool_cus_id
                            WHERE tocu.is_active = '1' AND tocu.customer_angilal = '1'"""

            if hothon != '':
                qry = qry + " AND addr.hothon_code = '" + hothon + "'"
            if egnee != '':
                qry = qry + " AND addr.block_code = '" + egnee + "'"
            if bair != '':
                qry = qry + " AND addr.building_number = '" + bair + "'"
            qry = qry + " GROUP BY tocu.customer_id ORDER BY cust.code;"

            search_q = { 'start_date': start_date, 'end_date': end_date}
        else:
            return redirect('/home/medeeleh/0/')

        try:
            sms_designs = MedeelehZagvar.objects.filter(type=0).filter(is_active=1)
            email_designs = MedeelehZagvar.objects.filter(type=1).filter(is_active=1)
            print_designs = MedeelehZagvar.objects.filter(type=2).filter(is_active=1)
        except ObjectDoesNotExist as e:
            sms_designs = None
            email_designs = None
            print_designs = None
            logging.error('"MedeelehZagvar" model has no object: %s', e)

        aimags = Aimag.objects.filter(is_active="1")
        cycle = Cycle.objects.filter(is_active='1')

        try:
            huvi_avlagas_ = TooluurCustomer.objects.raw(qry)
        except ObjectDoesNotExist as e:
            huvi_avlagas_ = None
            logging.error('"Avlaga" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'sub': self.sub,
            'huvi_avlagas': huvi_avlagas_,
            'sms_designs': sms_designs,
            'email_designs': email_designs,
            'print_designs': print_designs,
            'aimags': aimags,
            "cycle": cycle,
            'search_q': search_q
        }
        return render(request, self.template_name, data)


def prepareText(request, ids, design_id, type):
    avlaga_ids = []
    texts = []
    phones = []
    emails = []

    try:
        design = MedeelehZagvar.objects.get(id=design_id)
        for id in ids:
            try:
                q = """
                    select a.*
                    , c.code
                    , c.first_name
                    , c.last_name
                    , c.phone
                    , c.email
                    , ad.address_name
                    , ad.toot
                    from data_avlaga a
                    join data_customer c on a.customer_id = c.id
                    left join data_address ad on c.id = ad.customer_id
                    where a.id = """ + str(id)

                huvi_avlaga = Avlaga.objects.raw(q)[0]
                if huvi_avlaga.phone is not None and type == 0:
                    if len(huvi_avlaga.phone) > 7:
                        text = design.text.replace('{{code}}', huvi_avlaga.code)
                        text = text.replace('{{toot}}', huvi_avlaga.toot if huvi_avlaga.toot is not None else '')
                        text = text.replace('{{tulbur}}', str(int(huvi_avlaga.heregleenii_tulbur) + int(huvi_avlaga.uilchilgeenii_tulbur) + int(huvi_avlaga.barimt_une)))
                        texts.append(text)
                        avlaga_ids.append(huvi_avlaga.id)
                        phones.append(str(huvi_avlaga.phone)[:8])
                if huvi_avlaga.customer.email is not None and type == 1:
                    if len(huvi_avlaga.customer.email) > 5 and '@' in huvi_avlaga.customer.email:
                        text = design.text.replace('{{code}}', huvi_avlaga.code)
                        text = text.replace('{{toot}}', huvi_avlaga.toot if huvi_avlaga.toot is not None else '')
                        text = text.replace('{{tulbur}}', str(int(huvi_avlaga.heregleenii_tulbur) + int(huvi_avlaga.uilchilgeenii_tulbur) + int(huvi_avlaga.barimt_une)))
                        text = text.replace('{{first_name}}', huvi_avlaga.first_name)
                        text = text.replace('{{last_name}}', huvi_avlaga.last_name)
                        text = text.replace('{{address}}', huvi_avlaga.address_name if huvi_avlaga.address_name is not None else '')
                        texts.append(text)
                        avlaga_ids.append(huvi_avlaga.id)
                        emails.append(huvi_avlaga.email)
                if type == 2:
                    text = design.text.replace('{{code}}', huvi_avlaga.customer.code)
                    text = text.replace('{{toot}}', huvi_avlaga.toot if huvi_avlaga.toot is not None else '')
                    text = text.replace('{{tulbur}}', str(int(huvi_avlaga.heregleenii_tulbur) + int(huvi_avlaga.uilchilgeenii_tulbur) + int(huvi_avlaga.barimt_une)))
                    text = text.replace('{{first_name}}', huvi_avlaga.customer.first_name)
                    text = text.replace('{{last_name}}', huvi_avlaga.customer.last_name)
                    text = text.replace('{{address}}', huvi_avlaga.address_name if huvi_avlaga.address_name is not None else '')
                    texts.append(text)
                    avlaga_ids.append(huvi_avlaga.id)
            except ObjectDoesNotExist:
                messages.error(request, 'Алдаа гарлаа, та дахин оролдоно уу!')

        if type == 0:
            return phones, texts, avlaga_ids
        if type == 1:
            return emails, texts, avlaga_ids
        if type == 2:
            return texts, avlaga_ids
    except ObjectDoesNotExist:
        messages.error(request, 'Алдаа гарлаа, та дахин оролдоно уу!')
        return redirect('/home/medeeleh/0/')


class WarningSms(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_medeelehzagvar'
    template_name = 'homepage/medeeleh/medeeleh_sms.html'
    menu = '11'
    sub = '1'

    def get(self, request, *args, **kwargs):
        return redirect('/home/medeeleh/0/')

    def post(self, request, *args, **kwargs):
        sms_datas = request.POST['sms_datas']
        design_id = request.POST['sms_design_id']
        limit = request.POST['sms_limit']
        if limit == '':
            limit = '0'

        if design_id == '':
            messages.error(request, 'Загвар сонгоогүй байна!')
            return redirect('/home/medeeleh/0/')

        sms_datas = sms_datas.replace("'", '"')
        sms_datas = json.loads(sms_datas)

        design = MedeelehZagvar.objects.get(id=design_id)

        texts = []
        phones = []
        for sms_data in sms_datas:
            if float(sms_data['tulbur']) >= float(limit):
                if len(sms_data['phone']) > 7:
                    phones.append(sms_data['phone'][:8])
                    text = design.text.replace('{{code}}', str(sms_data['code']))
                    text = text.replace('{{toot}}', str(sms_data['toot']))
                    text = text.replace('{{tulbur}}', str(int(sms_data['tulbur'])))
                    text = text.replace('{{bichilt}}', str(int(sms_data['bichilt'])))
                    texts.append(text)

        data = {
            'menu': self.menu,
            'sub': self.sub,
            'sms_texts': zip(phones, texts),
            'data_texts': zip(phones, texts),
            'sms_design_id': design_id,
        }
        return render(request, self.template_name, data)


class WarningSmsSend(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_medeelehzagvar'
    template_name = 'homepage/medeeleh/medeeleh_sms.html'
    menu = '11'
    sub = '1'

    def get(self, request, *args, **kwargs):
        return redirect('/home/medeeleh/0/')

    def post(self, request, *args, **kwargs):
        # phones = request.POST.getlist('phones')
        # sms_texts = request.POST.getlist('sms_texts')

        phone = request.POST.get('sms')
        text = request.POST.get('text')
        status = False

        try:
            # if len(phones) == len(sms_texts):
            #     s_phones = []
            #     e_phones = []
            #     for i in range(0, len(phones)):
            #         r = None
            #         if str(phones[i])[:2] == '96' or str(phones[i])[:2] == '90' or str(phones[i])[:2] == '91':
            #             r = requests.get('http://sms.skytel.mn/skysms/pushsms.php?src=132888&id=100348&dest=' + str(phones[i]) + '&text=' + str(sms_texts[i]))
            #             print('SKYTEL : ' + str(r.status_code) + ' :: ' + str(r.text), flush=True)
            #             if str(r.text) != 'OK':
            #                 messages.warning(request, 'SKYTEL: ' + str(r.status_code) + ', ' + str(r.text))
            #         elif str(phones[i])[:2] == '99' or str(phones[i])[:2] == '95' or str(phones[i])[:2] == '94' or str(phones[i])[:2] == '85' \
            #                 or str(phones[i])[:2] == '80' or str(phones[i])[:2] == '86' or str(phones[i])[:2] == '88' or str(phones[i])[:2] == '89'\
            #                 or str(phones[i])[:2] == '98' or str(phones[i])[:2] == '93' or str(phones[i])[:2] == '97' or str(phones[i])[:2] == '83':
            #             r = requests.get('http://27.123.214.168/smsmt/mt?servicename=smartenergy&username=smartenergy&from=132888&to='+str(phones[i])+'&msg='+str(sms_texts[i]))
            #             print('MOBICOM : ' + str(r.status_code) + ' :: ' + str(r.text), flush=True)
            #             #messages.warning(request, 'MOBICOM: ' + str(r.status_code) + ', ' + str(r.text))
            #
            #         if r is not None:
            #             if r.status_code == 200:
            #                 s_phones.append({'phone': str(phones[i]), 'text': str(sms_texts[i])})
            #             else:
            #                 e_phones.append({'phone': str(phones[i]), 'text': str(sms_texts[i])})
            #         else:
            #             e_phones.append({'phone': str(phones[i]), 'text': str(sms_texts[i])})
                # messages.success(request, 'SMS амжилттай илгээгдлээ!')
            # else:
            #     messages.success(request, 'SMS илгээх үед алдаа гарлаа!')
            r = None
            if str(phone)[:2] == '96' or str(phone)[:2] == '90' or str(phone)[:2] == '91':
                r = requests.get('http://sms.skytel.mn/skysms/pushsms.php?src=132888&id=100348&dest=' + str(phone) + '&text=' + str(text))


            elif str(phone)[:2] == '99' or str(phone)[:2] == '95' or str(phone)[:2] == '94' or str(phone)[:2] == '85' \
                or str(phone)[:2] == '80' or str(phone)[:2] == '86' or str(phone)[:2] == '88' or str(phone)[:2] == '89'\
                or str(phone)[:2] == '98' or str(phone)[:2] == '93' or str(phone)[:2] == '97' or str(phone)[:2] == '83':
                r = requests.get('http://27.123.214.168/smsmt/mt?servicename=smartenergy&username=smartenergy&from=132888&to='+str(phone)+'&msg='+str(text))
                        #print('MOBICOM : ' + str(r.status_code) + ' :: ' + str(r.text), flush=True)
            if r is not None:
                print(r)
                if r.status_code == 200:
                    status = True
        except Exception as e:
            print(e)
            status = False
            #messages.success(request, 'SMS илгээх үед алдаа гарлаа! : %s', e)
        data = {"status": status}
        return HttpResponse(simplejson.dumps(data), content_type='application/json')
        #return redirect('/home/medeeleh/0/')


class WarningEmail(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_medeelehzagvar'
    template_name = 'homepage/medeeleh/medeeleh_email.html'
    menu = '11'
    sub = '1'

    def get(self, request, *args, **kwargs):
        return redirect('/home/medeeleh/0/')

    def post(self, request, *args, **kwargs):
        email_datas = request.POST['email_datas']
        design_id = request.POST['email_design_id']
        limit = request.POST['email_limit']
        if limit == '':
            limit = '0'

        if design_id == '':
            messages.error(request, 'Загвар сонгоогүй байна!')
            return redirect('/home/medeeleh/0/')

        email_datas = email_datas.replace("'", '"')
        email_datas = json.loads(email_datas)

        design = MedeelehZagvar.objects.get(id=design_id)

        texts = []
        emails = []
        for email_data in email_datas:
            if float(email_data['tulbur']) >= float(limit):
                if '@' in email_data['email'] and len(email_data['email']) > 5:
                    emails.append(email_data['email'])
                    text = design.text.replace('{{last_name}}', str(email_data['last_name']))
                    text = text.replace('{{first_name}}', str(email_data['first_name']))
                    text = text.replace('{{address}}', str(email_data['address']))
                    text = text.replace('{{code}}', str(email_data['code']))
                    text = text.replace('{{toot}}', str(email_data['toot']))
                    text = text.replace('{{tulbur}}', str(email_data['tulbur']))
                    texts.append(text)
        data = {
            'menu': self.menu,
            'sub': self.sub,
            'email_texts': zip(emails, texts),
            'show_texts': zip(emails, texts),
            'email_design_id': design_id,
        }
        return render(request, self.template_name, data)


class WarningEmailSend(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_medeelehzagvar'
    template_name = 'homepage/medeeleh/medeeleh_email.html'
    menu = '11'
    sub = '1'

    def get(self, request, *args, **kwargs):
        return redirect('/home/medeeleh/0/')

    def post(self, request, *args, **kwargs):
        emails = request.POST.getlist('emails')
        email_texts = request.POST.getlist('email_texts')

        for email, text in zip(emails, email_texts):
            try:
                mail = EmailMultiAlternatives('Цахилгааны төлбөр', text, from_email='info@smartenergy.mn', to=[email])
                mail.attach_alternative(text, "text/html")
                mail.send()
            except Exception as e:
                # messages.error(request, 'Имэйл илгээхэд алдаа гарлаа!')
                messages.error(request, str(e))
                return redirect('/home/medeeleh/0/')

        messages.success(request, 'Имэйл амжилттай илгээгдлээ!')
        return redirect('/home/medeeleh/0/')


class WarningPrint(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_medeelehzagvar'
    template_name = 'homepage/medeeleh/medeeleh_print.html'
    menu = '11'
    sub = '1'

    def get(self, request, *args, **kwargs):
        return redirect('/home/medeeleh/0/')

    def post(self, request, *args, **kwargs):
        print_datas = request.POST['print_datas']
        design_id = request.POST['print_design_id']
        limit = request.POST['limit']
        if limit == '':
            limit = '0'

        if design_id == '':
            messages.error(request, 'Загвар сонгоогүй байна!')
            return redirect('/home/medeeleh/0/')

        print_datas = print_datas.replace("'", '"')
        print_datas = json.loads(print_datas)

        texts = []
        design = MedeelehZagvar.objects.get(id=design_id)
        for print_data in print_datas:
            if float(print_data['tulbur']) >= float(limit):
                text = design.text.replace('{{last_name}}', str(print_data['last_name']))
                text = text.replace('{{first_name}}', str(print_data['first_name']))
                text = text.replace('{{address}}', str(print_data['address']))
                text = text.replace('{{code}}', str(print_data['code']))
                text = text.replace('{{toot}}', str(print_data['toot']))
                text = text.replace('{{bair}}', str(print_data['building_number']))
                text = text.replace('{{tulbur}}', str(print_data['tulbur']))
                texts.append(text)

        data = {
            'menu': self.menu,
            'sub': self.sub,
            'print_texts': texts,
            'print_design_id': design_id,
        }
        return render(request, self.template_name, data)


class WarningPrintHevleh(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_medeelehzagvar'
    template_name = 'homepage/medeeleh/medeeleh_print.html'
    menu = '11'
    sub = '1'

    def get(self, request, *args, **kwargs):
        return redirect('/home/medeeleh/0/')

    def post(self, request, *args, **kwargs):
        ids = request.POST.getlist('avlaga_id')
        design_id = request.POST['print_design_id']

        texts, avlaga_ids = prepareText(request, ids, design_id, 2)

        if 'pdf' in request.POST:
            counter = 0

            for text in texts:
                input_filename = 'media/hehemjlel' + str(counter) + '.html'
                output_filename = 'media/hehemjlel' + str(counter) + '.pdf'

                html_file = open(input_filename, 'w')
                html_file.write("""<html><head><title>Нэхэмжлэл</title></head><body>""" + str.encode(text, 'utf-8') + """</body></html>""")
                html_file.close()

                counter += 1

        return redirect('/home/medeeleh/0/')


class WarningDesign(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_medeelehzagvar'
    template_name = 'homepage/medeeleh/medeeleh_zagvar.html'
    menu = '11'
    sub = '2'

    def get(self, request, activeTab, *args, **kwargs):
        try:
            smsMedeelehs = MedeelehZagvar.objects.filter(type='0').order_by('-created_date')
            emailMedeelehs = MedeelehZagvar.objects.filter(type='1').order_by('-created_date')
            printMedeelehs = MedeelehZagvar.objects.filter(type='2').order_by('-created_date')
        except ObjectDoesNotExist as e:
            smsMedeelehs = None
            emailMedeelehs = None
            printMedeelehs = None
            logging.error('"MedeelehZagvar" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'sub': self.sub,
            'activeTab': activeTab,
            'sms_action': '/home/medeeleh/zagvar/1/',
            'email_action': '/home/medeeleh/zagvar/2/',
            'print_action': '/home/medeeleh/zagvar/3/',
            'smsMedeelehs': smsMedeelehs,
            'emailMedeelehs': emailMedeelehs,
            'ptintMedeelehs': printMedeelehs,
        }
        return render(request, self.template_name, data)

    def post(self, request, activeTab, *args, **kwargs):
        if activeTab == '1':
            try:
                mz = MedeelehZagvar(name=request.POST['sms_name'], type='0', text=request.POST['sms_text'], is_active=request.POST['sms_is_active'], created_user_id=request.user.id)
                mz.save()
                messages.success(request, 'SMS загвар амжилттай хадгалагдлаа!')
            except Exception as e:
                messages.error(request, 'SMS загвар хадгалахад алдаа гарлаа!')
                logging.error('%s', e)

        if activeTab == '2':
            try:
                mz = MedeelehZagvar(name=request.POST['email_name'], type='1', text=request.POST['email_text'], is_active=request.POST['email_is_active'], created_user_id=request.user.id)
                mz.save()
                messages.success(request, 'Имэйл загвар амжилттай хадгалагдлаа!')
            except Exception as e:
                messages.error(request, 'Имэйл загвар хадгалахад алдаа гарлаа!')
                logging.error('%s', e)

        if activeTab == '3':
            try:
                mz = MedeelehZagvar(name=request.POST['print_name'], type='2', text=request.POST['print_text'], is_active=request.POST['print_is_active'], created_user_id=request.user.id)
                mz.save()
                messages.success(request, 'Хэвлэх загвар амжилттай хадгалагдлаа!')
            except Exception as e:
                messages.error(request, 'Хэвлэх загвар хадгалахад алдаа гарлаа!')
                logging.error('%s', e)

        return redirect('/home/medeeleh/zagvar/' + activeTab + '/')


class WarningDesignEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_medeelehzagvar'
    template_name = 'homepage/medeeleh/medeeleh_zagvar.html'
    menu = '11'
    sub = '2'

    def get(self, request, activeTab, id, *args, **kwargs):
        smsMedeel = None
        emailMedeel = None
        printMedeel = None

        if activeTab == '1':
            try:
                smsMedeel = MedeelehZagvar.objects.get(id=id)
            except ObjectDoesNotExist as e:
                smsMedeel = None
                logging.error('"MedeelehZagvar" model has no object: %s', e)

        if activeTab == '2':
            try:
                emailMedeel = MedeelehZagvar.objects.get(id=id)
            except ObjectDoesNotExist as e:
                emailMedeel = None
                logging.error('"MedeelehZagvar" model has no object: %s', e)

        if activeTab == '3':
            try:
                printMedeel = MedeelehZagvar.objects.get(id=id)
            except ObjectDoesNotExist as e:
                printMedeel = None
                logging.error('"MedeelehZagvar" model has no object: %s', e)

        try:
            smsMedeelehs = MedeelehZagvar.objects.filter(type='0').order_by('-created_date')
            emailMedeelehs = MedeelehZagvar.objects.filter(type='1').order_by('-created_date')
            printMedeelehs = MedeelehZagvar.objects.filter(type='2').order_by('-created_date')
        except ObjectDoesNotExist as e:
            smsMedeelehs = None
            emailMedeelehs = None
            printMedeelehs = None
            logging.error('"MedeelehZagvar" model has no object: %s', e)

        data = {
            'menu': self.menu,
            'sub': self.sub,
            'activeTab': activeTab,
            'sms_action': '/home/medeeleh/zagvar/edit/1/' + id + '/',
            'email_action': '/home/medeeleh/zagvar/edit/2/' + id + '/',
            'print_action': '/home/medeeleh/zagvar/edit/3/' + id + '/',
            'smsMedeel': smsMedeel,
            'emailMedeel': emailMedeel,
            'printMedeel': printMedeel,
            'smsMedeelehs': smsMedeelehs,
            'emailMedeelehs': emailMedeelehs,
            'ptintMedeelehs': printMedeelehs,
        }
        return render(request, self.template_name, data)

    def post(self, request, activeTab, id, *args, **kwargs):
        if activeTab == '1':
            try:
                smsMedeel = MedeelehZagvar.objects.get(id=id)
                smsMedeel.name = request.POST['sms_name']
                smsMedeel.type = '0'
                smsMedeel.text = request.POST['sms_text']
                smsMedeel.is_active = request.POST['sms_is_active']
                smsMedeel.save()
                messages.success(request, 'SMS загвар амжилттай засварлагдлаа!')
            except Exception as e:
                messages.error(request, 'SMS загвар засварлахад алдаа гарлаа!')
                logging.error('%s', e)

        if activeTab == '2':
            try:
                emailMedeel = MedeelehZagvar.objects.get(id=id)
                emailMedeel.name = request.POST['email_name']
                emailMedeel.type = '1'
                emailMedeel.text = request.POST['email_text']
                emailMedeel.is_active = request.POST['email_is_active']
                emailMedeel.save()
                messages.success(request, 'Имэйл загвар амжилттай засварлагдлаа!')
            except Exception as e:
                messages.error(request, 'Имэйл загвар засварлахад алдаа гарлаа!')
                logging.error('%s', e)

        if activeTab == '3':
            try:
                printMedeel = MedeelehZagvar.objects.get(id=id)
                printMedeel.name = request.POST['print_name']
                printMedeel.type = '2'
                printMedeel.text = request.POST['print_text']
                printMedeel.is_active = request.POST['print_is_active']
                printMedeel.save()
                messages.success(request, 'Хэвлэх загвар амжилттай засварлагдлаа!')
            except Exception as e:
                messages.error(request, 'Хэвлэх загвар засварлахад алдаа гарлаа!')
                logging.error('%s', e)

        return redirect('/home/medeeleh/zagvar/' + activeTab + '/')


class WarningDesignDelete(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_medeelehzagvar'
    template_name = 'homepage/medeeleh/medeeleh_zagvar.html'
    menu = '11'
    sub = '2'

    def get(self, request, activeTab, id, *args, **kwargs):
        tabName = ''

        if activeTab == '1':
            tabName = 'SMS'
        elif activeTab == '2':
            tabName = 'Имэйл'
        elif activeTab == '3':
            tabName = 'Хэвлэх'

        try:
            sepmedeel = MedeelehZagvar.objects.get(id=id)
            sepmedeel.delete()
            messages.success(request, tabName + ' загвар амжилттай устгагдлаа!')
        except ObjectDoesNotExist as e:
            messages.error(request, tabName + ' загвар устахад алдаа гарлаа!')
            logging.error('"MedeelehZagvar" model has no object: %s', e)

        return redirect('/home/medeeleh/zagvar/' + activeTab + '/')

    def post(self, request, activeTab, id, *args, **kwargs):
        return redirect('/home/medeeleh/zagvar/' + activeTab + '/')


def isValidEmail(email):
    if len(email) > 7:
        if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email):
            return True
        return False