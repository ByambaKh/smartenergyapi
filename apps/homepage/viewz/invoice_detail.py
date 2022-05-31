import datetime
import operator

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import View

from apps.data.models import Customer, TooluurCustomer, PaymentHistory, CustomerUilchilgeeTulbur, Avlaga, PriceTariff, \
    HasagdahTooluur


class InvoiceDetailAhui(LoginRequiredMixin, View):
    template_name = "homepage/borluulalt/invoice_detail_ahui.html"
    permission_required = ''

    def get(self, request, code, start_date, end_date, ehnii, *args, **kwargs):
        temp_start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

        ehnii_uld = 0
        if temp_start_date < datetime.datetime.strptime('2017-09-01', '%Y-%m-%d'):
            start_date = '2017-09-01'
            avlaga = Avlaga.objects.filter(customer__code=code, year=2017, month=8).first()
            if avlaga is not None:
                ehnii_uld = round(float(avlaga.heregleenii_tulbur + avlaga.uilchilgeenii_tulbur + avlaga.barimt_une), 2)
        else:
            ehnii_uld = ehnii

        start_date += ' 00:00:00.000000'
        end_date += ' 23:59:59.999999'

        all_datas = {
            'dates': [],
            'types': [],
            'datas': [],
            'barimt': []
        }

        try:
            qry = """SELECT cust.id, cust.code, cust.first_name, cust.last_name, cust.register, addr.address_name,
                bank.name AS bank_name, bank.dans AS bank_dans, cycl.name AS cycl_name, deds.name AS deds_name FROM data_customer cust
                LEFT JOIN data_address addr ON addr.customer_id = cust.id JOIN data_geree gere ON cust.code = gere.customer_code
                LEFT JOIN data_dedstants deds ON gere.dedstants_code = deds.code LEFT JOIN data_bank bank ON gere.bank_code = bank.code
                LEFT JOIN data_cycle cycl ON gere.cycle_code = cycl.code WHERE cust.code = '"""+code+"""'"""
            customer = Customer.objects.raw(qry)
        except ObjectDoesNotExist:
            customer = None

        try:
            bichs_qry = """SELECT tocu.id, bich.id AS bich_id, tool.number, tool.tariff, bich.bichilt_date, bich.total_diff AS total_diff, IFNULL(guid.multiply_coef, 1.0) AS guid, IFNULL(huch.multiply_coef, 1.0) AS huch,
                IFNULL(umnu.day_balance, tool.balance_value) AS umnu_day, IFNULL(umnu.night_balance, tool.balance_value_night) umnu_night,
                IFNULL(umnu.rush_balance, tool.balance_value_rush) AS umnu_rush, IFNULL(bich.day_balance, umnu.day_balance) AS bich_day,
                IFNULL(bich.night_balance, umnu.night_balance) bich_night, IFNULL(bich.rush_balance, umnu.rush_balance) AS bich_rush FROM data_tooluurcustomer tocu
                JOIN data_customer cust ON tocu.customer_id = cust.id JOIN data_tooluur tool ON tocu.tooluur_id = tool.id
                LEFT JOIN data_transformator guid ON tocu.guidliin_trans_id = guid.id LEFT JOIN data_transformator huch ON tocu.huchdeliin_trans_id = huch.id
                LEFT JOIN data_bichilt bich ON tocu.id = bich.tooluur_id LEFT JOIN data_bichilt umnu ON bich.prev_bichilt_id = umnu.id
                WHERE cust.code = '"""+code+"""' AND bich.bichilt_date >= '"""+start_date+"""' AND bich.bichilt_date <= '"""+end_date+"""' ORDER BY bich.bichilt_date"""
            bichilts = TooluurCustomer.objects.raw(bichs_qry)
            barimt_une = PriceTariff.objects.filter(une_type=1)[:1].get().barimt_une
            if bichilts is not None:
                s_start_date = ''
                count = 0
                for bichilt in bichilts:
                    all_datas['dates'].append(str(bichilt.bichilt_date)[:10])
                    all_datas['types'].append('0')
                    all_datas['datas'].append(bichilt)

                    if s_start_date != str(bichilt.bichilt_date)[:10]:
                        all_datas['barimt'].append(str(barimt_une))
                        count = 0
                    else:
                        all_datas['barimt'].append('0.00')

                    if count == 0:
                        s_start_date = str(bichilt.bichilt_date)[:10]
                    count += 1
        except ObjectDoesNotExist:
            bichilts = None

        try:
            pahi_qry = """SELECT pahi.id, pahi.pay_date, bank.name AS bank_name, bank.dans AS bank_dans, pahi.pay_total FROM data_paymenthistory pahi
                LEFT JOIN data_customer cust ON pahi.customer_id = cust.id LEFT JOIN data_bank bank ON pahi.bank_id = bank.id
                WHERE cust.code = '"""+code+"""' AND pahi.is_active = '1' AND pahi.pay_date >= '"""+start_date+"""' AND pahi.pay_date <= '"""+end_date+"""' ORDER BY pahi.pay_date"""
            payments = PaymentHistory.objects.raw(pahi_qry)
            if payments is not None:
                for payment in payments:
                    all_datas['dates'].append(str(payment.pay_date)[:10])
                    all_datas['types'].append('1')
                    all_datas['datas'].append(payment)
                    all_datas['barimt'].append('')
        except ObjectDoesNotExist:
            payments = None

        try:
            if temp_start_date < datetime.datetime.strptime('2017-10-01', '%Y-%m-%d'):
                avlaga = Avlaga.objects.filter(customer__code=code, year=2017, month=9).first()
                if avlaga is not None:
                    uilchilgeenii_tulbur = round(float(avlaga.uilchilgeenii_tulbur), 2)
                    if uilchilgeenii_tulbur > 0:
                        all_datas['dates'].append(str('2017-09-25'))
                        all_datas['types'].append('2')
                        all_datas['datas'].append({'payment': uilchilgeenii_tulbur})
                        all_datas['barimt'].append('')

            uil_qry = """SELECT cuil.id, cuil.uil_date, tuil.name AS uil_name, cuil.payment FROM data_customeruilchilgeetulbur cuil
                LEFT JOIN data_customer cust ON cuil.customer_id = cust.id JOIN data_tulburtuilchilgee tuil ON cuil.uilchilgee_id = tuil.id
                WHERE cuil.is_active = '1' AND cust.code = '"""+code+"""' AND cuil.uil_date >= '"""+start_date+"""' AND cuil.uil_date <= '"""+end_date+"""' ORDER BY cuil.uil_date"""
            uilchigees = CustomerUilchilgeeTulbur.objects.raw(uil_qry)
            if uilchigees is not None:
                for uilchigee in uilchigees:
                    all_datas['dates'].append(str(uilchigee.uil_date)[:10])
                    all_datas['types'].append('2')
                    all_datas['datas'].append(uilchigee)
                    all_datas['barimt'].append('')
        except ObjectDoesNotExist:
            uilchigees = None

        if len(all_datas['dates']) > 1:
            all_datas['dates'], all_datas['types'], all_datas['datas'], all_datas['barimt'] = zip(*sorted(zip(all_datas['dates'], all_datas['types'], all_datas['datas'], all_datas['barimt']), key=operator.itemgetter(0)))

        context = {
            'customer': None if customer is None else customer[0],
            'start_date': start_date[:10],
            'end_date': end_date[:10],
            'ehnii': ehnii_uld,
            'all_datas': zip(all_datas['dates'], all_datas['types'], all_datas['datas'], all_datas['barimt'])
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, None)


class InvoiceDetailAan(LoginRequiredMixin, View):
    template_name = "homepage/borluulalt/invoice_detail_aan.html"
    permission_required = ''

    def get(self, request, code, start_date, end_date, ehnii, *args, **kwargs):
        temp_start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

        ehnii_uld = 0
        if temp_start_date < datetime.datetime.strptime('2017-08-01', '%Y-%m-%d'):
            start_date = '2017-08-01'
            avlaga = Avlaga.objects.filter(customer__code=code, year=2017, month=8).first()
            if avlaga is not None:
                ehnii_uld = round(float(avlaga.heregleenii_tulbur + avlaga.uilchilgeenii_tulbur + avlaga.barimt_une), 2)
        else:
            ehnii_uld = ehnii

        start_date += ' 00:00:00.000000'
        end_date += ' 23:59:59.999999'

        all_datas = {
            'dates': [],
            'types': [],
            'datas': []
        }

        try:
            qry = """SELECT cust.id, cust.code, cust.first_name, cust.last_name, cust.register, cust.customer_type, addr.address_name,
                bank.name AS bank_name, bank.dans AS bank_dans, cycl.name AS cycl_name, deds.name AS deds_name FROM data_customer cust
                LEFT JOIN data_address addr ON addr.customer_id = cust.id JOIN data_geree gere ON cust.code = gere.customer_code
                LEFT JOIN data_dedstants deds ON gere.dedstants_code = deds.code LEFT JOIN data_bank bank ON gere.bank_code = bank.code
                LEFT JOIN data_cycle cycl ON gere.cycle_code = cycl.code WHERE cust.code = '"""+code+"""'"""
            customer = Customer.objects.raw(qry)
        except ObjectDoesNotExist:
            customer = None

        try:
            bichs_qry = """SELECT bich.id, bich.bichilt_date, bich.chadal_price FROM data_bichilt bich
                JOIN data_tooluurcustomer tocu ON bich.tooluur_id = tocu.id JOIN data_customer cust ON tocu.customer_id = cust.id
                WHERE cust.code = '"""+code+"""' AND bich.bichilt_date >= '"""+start_date+"""'
                AND bich.bichilt_date <= '"""+end_date+"""' GROUP BY bich.bichilt_date ORDER BY bich.bichilt_date"""
            bichilts = TooluurCustomer.objects.raw(bichs_qry)
            if bichilts is not None:
                for bichilt in bichilts:
                    all_datas['dates'].append(str(bichilt.bichilt_date)[:10])
                    all_datas['types'].append('0')
                    all_datas['datas'].append(bichilt)
        except ObjectDoesNotExist:
            bichilts = None

        try:
            if temp_start_date < datetime.datetime.strptime('2017-10-01', '%Y-%m-%d'):
                avlaga = Avlaga.objects.filter(customer__code=code, year=2017, month=9).first()
                if avlaga is not None:
                    uilchilgeenii_tulbur = round(float(avlaga.uilchilgeenii_tulbur), 2)
                    if uilchilgeenii_tulbur > 0:
                        all_datas['dates'].append(str('2017-09-25'))
                        all_datas['types'].append('2')
                        all_datas['datas'].append({'payment': uilchilgeenii_tulbur})

            uil_qry = """SELECT cuil.id, cuil.uil_date, tuil.name AS uil_name, cuil.payment FROM data_customeruilchilgeetulbur cuil
                LEFT JOIN data_customer cust ON cuil.customer_id = cust.id JOIN data_tulburtuilchilgee tuil ON cuil.uilchilgee_id = tuil.id
                WHERE cuil.is_active = '1' AND cust.code = '"""+code+"""' AND cuil.uil_date >= '"""+start_date+"""' AND cuil.uil_date <= '"""+end_date+"""' ORDER BY cuil.uil_date"""
            uilchilgees = CustomerUilchilgeeTulbur.objects.raw(uil_qry)
            if uilchilgees is not None:
                for uilchilgee in uilchilgees:
                    all_datas['dates'].append(str(uilchilgee.uil_date)[:10])
                    all_datas['types'].append('2')
                    all_datas['datas'].append(uilchilgee)
        except ObjectDoesNotExist:
            uilchilgees = None

        try:
            pahi_qry = """SELECT pahi.id, pahi.pay_date, bank.name AS bank_name, bank.dans AS bank_dans, pahi.pay_total FROM data_paymenthistory pahi
                LEFT JOIN data_customer cust ON pahi.customer_id = cust.id LEFT JOIN data_bank bank ON pahi.bank_id = bank.id
                WHERE cust.code = '"""+code+"""' AND pahi.is_active = '1' AND pahi.pay_date >= '"""+start_date+"""' AND pahi.pay_date <= '"""+end_date+"""' ORDER BY pahi.pay_date"""
            payments = PaymentHistory.objects.raw(pahi_qry)
            if payments is not None:
                for payment in payments:
                    all_datas['dates'].append(str(payment.pay_date)[:10])
                    all_datas['types'].append('1')
                    all_datas['datas'].append(payment)
        except ObjectDoesNotExist:
            payments = None

        if len(all_datas['dates']) > 1:
            all_datas['dates'], all_datas['types'], all_datas['datas'] = zip(*sorted(zip(all_datas['dates'], all_datas['types'], all_datas['datas']), key=operator.itemgetter(0)))

        try:
            hasagdah_q = "SELECT hasa.id, hasa.child_tool_cus_id FROM data_hasagdahtooluur hasa JOIN data_tooluurcustomer tocu ON" \
                         " tocu.id = hasa.head_tool_cus_id WHERE tocu.customer_code = '" + str(code) + "'"
            hasagdahTooluurs = list(HasagdahTooluur.objects.raw(hasagdah_q))
        except ObjectDoesNotExist:
            hasagdahTooluurs = []

        if len(hasagdahTooluurs) == 0:
            context = {
                'customer': None if customer is None else customer[0],
                'start_date': start_date[:10],
                'end_date': end_date[:10],
                'ehnii': ehnii_uld,
                'all_datas': zip(all_datas['dates'], all_datas['types'], all_datas['datas'])
            }
            return render(request, self.template_name, context)
        else:
            context = {
                'customer': None if customer is None else customer[0],
                'start_date': start_date[:10],
                'end_date': end_date[:10],
                'ehnii': ehnii_uld,
                'all_datas': zip(all_datas['dates'], all_datas['types'], all_datas['datas'])
            }
            return render(request, "homepage/borluulalt/invoice_detail_hasagdah.html", context)

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, None)