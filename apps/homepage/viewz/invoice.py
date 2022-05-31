# coding=utf-8
from datetime import datetime
from decimal import Decimal

from braces.views import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import View

from apps.data.models import PaymentHistory, PosAPI, TooluurCustomer, Bichilt, Customer, HasagdahTooluur
from apps.homepage.viewz.services.posapi import PosapiMTA


class InvoiceAhui(LoginRequiredMixin, View):
    template_name = "homepage/borluulalt/invoice_ahui.html"
    permission_required = ''
    pos_api = PosapiMTA()

    def get(self, request, type, code, start_date, end_date, ehnii, before_payment, payment, bichilt, *args, **kwargs):
        result_data = self.make_invoice(request, type, code, start_date, end_date, payment)

        if int(type) == 1:
            qr_data = result_data['qr_data']
            lottery = result_data['lottery']
            billId = result_data['billId']
        else:
            qr_data = None
            lottery = None
            billId = None
        avlaga_type = result_data['avlaga_type']

        if avlaga_type == '1' and ehnii == '0.00':
            ehnii = bichilt

        context = {
            'start_date': start_date,
            'end_date': end_date,
            'avlagas': result_data['avlagas'],
            'ehnii': ehnii,
            'payment': payment,
            'before_payment': before_payment,
            'bichilt': bichilt,
            'qr_data': qr_data,
            'lottery': lottery,
            'billId': billId,
            'amount': payment,
            'type': str(type),
            'avlaga_type': avlaga_type
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        return None

    def make_invoice(self, request, type, code, start_date, end_date, amount):
        start_date += ' 00:00:00.000000'
        end_date += ' 23:59:59.999999'
        avlaga_type = '0'
        try:
            qry = """SELECT tocu.id, odoo.id AS bich_id, cust.first_name, cust.last_name, cust.register, cust.customer_angilal, addr.address_name, bank.name AS bank_name, bank.dans AS bank_dans,
                cust.code, tool.number, tool.tariff, deds.name AS deds_name, SUM(odoo.suuri_price) AS suuri_price, avla.tulbur_date, avla.uilchilgeenii_tulbur,
                umnu.bichilt_date AS umnu_bich_date, odoo.bichilt_date AS odoo_bich_date,
                IFNULL(umnu.day_balance, umum.day_balance) AS day_umnu, IFNULL(odoo.day_balance, umnu.day_balance) AS day_odoo,
                IFNULL(umnu.night_balance, umum.night_balance) AS night_umnu, IFNULL(odoo.night_balance, umnu.night_balance) AS night_odoo,
                IFNULL(umnu.rush_balance, umum.rush_balance) AS rush_umnu, IFNULL(odoo.rush_balance, umnu.rush_balance) AS rush_odoo,
                IFNULL(odoo.day_diff, umnu.day_diff) AS day_diff, IFNULL(odoo.night_diff, umnu.night_diff) AS night_diff,
                IFNULL(odoo.rush_diff, umnu.rush_diff) AS day_diff, IFNULL(odoo.total_diff, umnu.total_diff) AS total_diff
                FROM data_tooluurcustomer tocu JOIN data_customer cust ON tocu.customer_id = cust.id
                JOIN data_tooluur tool ON tocu.tooluur_id = tool.id LEFT JOIN data_bichilt odoo ON tocu.id = odoo.tooluur_id
                LEFT JOIN data_bichilt umnu ON odoo.prev_bichilt_id = umnu.id LEFT JOIN data_bichilt umum ON umnu.prev_bichilt_id = umum.id
                LEFT JOIN data_avlaga avla ON avla.id = odoo.avlaga_id LEFT JOIN data_address addr ON cust.id = addr.customer_id
                LEFT JOIN data_paymenthistory pahi ON tocu.customer_id = pahi.customer_id LEFT JOIN data_geree gere ON gere.customer_code = tocu.customer_code
                LEFT JOIN data_bank bank ON gere.bank_code = bank.code LEFT JOIN data_dedstants deds ON gere.dedstants_code = deds.code
                WHERE avla.created_date BETWEEN '"""+start_date+"""' AND '"""+end_date+"""' AND cust.code = '"""+code+"""' GROUP BY tocu.id;"""

            avlagas = TooluurCustomer.objects.raw(qry)

            if len(list(avlagas)) == 0:
                qry = """SELECT tocu.id, cust.first_name, cust.last_name, cust.register, cust.customer_angilal, addr.address_name,
                    bank.name AS bank_name, bank.dans AS bank_dans, cust.code, tool.number, tool.tariff, deds.name AS deds_name
                    FROM data_tooluurcustomer tocu JOIN data_customer cust ON tocu.customer_id = cust.id
                    JOIN data_tooluur tool ON tocu.tooluur_id = tool.id LEFT JOIN data_bichilt odoo ON tocu.id = odoo.tooluur_id
                    LEFT JOIN data_address addr ON cust.id = addr.customer_id LEFT JOIN data_geree gere ON gere.customer_code = tocu.customer_code
                    LEFT JOIN data_bank bank ON gere.bank_code = bank.code LEFT JOIN data_dedstants deds ON gere.dedstants_code = deds.code
                    WHERE cust.code = '"""+code+"""' GROUP BY tocu.id;"""
                avlagas = TooluurCustomer.objects.raw(qry)
                avlaga_type = '1'
        except ObjectDoesNotExist:
            avlagas = None

        qr_data = None
        lottery = None
        billId = None

        try:
            customer = Customer.objects.filter(code=str(code), customer_angilal='1', is_active='1').first()
        except Exception as e:
            print("Exception : %s" % e)
            customer = None

        if int(type) == 1 and customer is not None:
            not_ebarimt = [1910004, 1910009, 1911292, 1910611, 1910618, 1914052, 1914062, 1911002]

            if int(customer.code) not in not_ebarimt:
                # if self.pos_api.pos_init():
                return_json = self.pos_api.pos_put("", amount)

                qr_data = None
                billId = None
                lottery = None

                if return_json['success']:
                    qr_data = return_json['qrData']
                    billId = return_json['billId']
                    lottery = return_json['lottery']

                    pay_his = PaymentHistory.objects.filter(customer=customer).latest('id')
                    posapi = PosAPI.objects.create(pay_his_id=pay_his.id, success=return_json['success'] if return_json['success'] else 0)
                    posapi.created_user_id = request.user.id
                    posapi.is_active = '1'
                    posapi.customer = customer
                    posapi.registerNo = return_json['registerNo'] if return_json['registerNo'] else '0'
                    posapi.billType = return_json['billType'] if return_json['billType'] else '0'
                    posapi.cityTax = return_json['cityTax'] if return_json['cityTax'] else '0'
                    posapi.vat = return_json['vat'] if return_json['vat'] else Decimal(0.00)
                    posapi.invoiceId = return_json['invoiceId'] if return_json['invoiceId'] else '0'
                    posapi.billId = return_json['billId'] if return_json['billId'] else '0'
                    posapi.returnBillId = return_json['returnBillId'] if return_json['returnBillId'] else '0'
                    posapi.posNo = return_json['posNo'] if return_json['posNo'] else '0'
                    posapi.date = return_json['date'] if return_json['date'] else datetime.now()
                    posapi.cashAmount = return_json['cashAmount'] if return_json['cashAmount'] else Decimal(0.00)
                    posapi.merchantId = return_json['merchantId'] if return_json['merchantId'] else '0'
                    posapi.districtCode = return_json['districtCode'] if return_json['districtCode'] else '0'
                    posapi.branchNo = return_json['branchNo'] if return_json['branchNo'] else '0'
                    posapi.nonCashAmount = return_json['nonCashAmount'] if return_json['nonCashAmount'] else Decimal(0.00)
                    posapi.taxType = return_json['taxType'] if return_json['taxType'] else '0'
                    posapi.macAddress = return_json['macAddress'] if return_json['macAddress'] else '0'
                    posapi.amount = return_json['amount'] if return_json['amount'] else Decimal(0.00)
                    posapi.billIdSuffix = return_json['billIdSuffix'] if return_json['billIdSuffix'] else '0'
                    posapi.customerNo = return_json['customerNo'] if return_json['customerNo'] else '0'
                    posapi.reportMonth = return_json['reportMonth'] if return_json['reportMonth'] else '0000-00'
                    posapi.save()
                # else:
                    # print("PosAPI-тай холбогдоход алдаа гарлаа")
        return {'avlagas': avlagas, 'avlaga_type': avlaga_type, 'qr_data': qr_data, 'billId': billId, 'lottery': lottery}


class InvoiceAan(LoginRequiredMixin, View):
    template_name = "homepage/borluulalt/invoice_aan.html"
    permission_required = ''

    def get(self, request, type, code, start_date, end_date, ehnii, before_payment, payment, bichilt, *args, **kwargs):
        start_date += ' 00:00:00.000000'
        end_date += ' 23:59:59.999999'
        try:
            hasagdah_q = "SELECT hasa.id, hasa.child_tool_cus_id FROM data_hasagdahtooluur hasa JOIN data_tooluurcustomer tocu ON" \
                         " tocu.id = hasa.head_tool_cus_id WHERE tocu.customer_code = '" + str(code) + "'"
            hasagdah = list(HasagdahTooluur.objects.raw(hasagdah_q))
        except ObjectDoesNotExist:
            hasagdah = []

        try:
            qry = """SELECT bich.id, avla.id AS avlaga_id, cust.code, bich.bichilt_date, cust.customer_type, cust.register, cust.first_name, cust.last_name, addr.address_name, avla.uilchilgeenii_tulbur
                FROM data_bichilt bich JOIN data_tooluurcustomer tocu ON bich.tooluur_id = tocu.id
                JOIN data_customer cust ON tocu.customer_id = cust.id LEFT JOIN data_avlaga avla ON bich.avlaga_id = avla.id LEFT JOIN data_address addr ON cust.id = addr.customer_id
                WHERE cust.code = '""" + code + """' AND bich.bichilt_date >= '""" + start_date + """ 00:00:00.000000' AND bich.bichilt_date <= '""" + end_date + """ 23:59:59.999999' GROUP BY bich.bichilt_date"""
            avlagas = Bichilt.objects.raw(qry)
        except ObjectDoesNotExist:
            avlagas = None

        context = {
            'code': code,
            'start_date': start_date,
            'end_date': end_date,
            'ehnii': ehnii,
            'before_payment': before_payment,
            'payment': payment,
            'bichilt': bichilt,
            'avlagas': avlagas,
            'type': str(type)
        }

        if len(hasagdah) == 0:
            return render(request, self.template_name, context)
        else:
            return render(request, "homepage/borluulalt/invoice_hasagdah.html", context)

    def post(self, request, *args, **kwargs):
        return None