# coding=utf-8
import datetime

from braces.views import LoginRequiredMixin
from decimal import Decimal

from django.contrib import messages
from django.shortcuts import render
from django.views import View
from apps.data.models import Customer, HasagdahHistory, PaymentHistory, PosAPI
from apps.homepage.viewz.services.posapi import PosapiMTA
from django.shortcuts import render, HttpResponse, redirect
import simplejson
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from apps.homepage.viewz.medeeleh import isValidEmail

class InvoiceAhui1(LoginRequiredMixin, View):
    template_name = "homepage/borluulalt/invoice_ahui1.html"
    permission_required = ''
    pos_api = PosapiMTA()

    def get(self, request, type, code, start_date, end_date, ehnii, before_payment, payment, bichilt, *args, **kwargs):
        result_data = self.get_customer_ahui(request, code, start_date, end_date, type, payment)

        if int(type) == 1:
            qr_data = result_data['qr_data']
            lottery = result_data['lottery']
            billId = result_data['billId']

            #TODO
        else:
            qr_data = None
            lottery = None
            billId = None

        context = {
            'customers': result_data['customer'],
            'ehnii': ehnii,
            'payment': payment,
            'before_payment': before_payment,
            'bichilt': bichilt,
            'amount': payment,
            'type': str(type),
            'qr_data': qr_data,
            'lottery': lottery,
            'billId': billId,
        }
        try:
            if result_data['customer'][0].email is not None and isValidEmail(result_data['customer'][0].email) and request.GET['email']:
                data = {"status": True}
                try:
                    htmly = get_template("homepage/borluulalt/invoice_ahui1.html")
                    context['show'] = False
                    mail = EmailMultiAlternatives('Цахилгааны төлбөр', "нэхэмжлэх",
                                                  from_email='info@smartenergy.mn',
                                                  to=[str(result_data['customer'][0].email)])
                    html_content = htmly.render(context)
                    mail.attach_alternative(html_content, "text/html")
                    mail.send()
                except Exception as ex:
                    data = {"status": False}
                return HttpResponse(simplejson.dumps(data), content_type='application/json')
        except Exception as e:
            data = {"status": str(e)}
            # return HttpResponse(simplejson.dumps(data), content_type='application/json')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        return None

    def get_customer_ahui(self, request, code, start_date, end_date, type, amount):
        year = start_date[:4]
        month = start_date[5:7]

        query = """SELECT cust.id,cust.email, cust.last_name, cust.first_name, cust.register, IFNULL(addr.address_name, '') AS address_name,
            IFNULL(bank.name, '') AS bank_name, IFNULL(bank.dans, '') AS bank_dans, cust.code AS customer_code,
            IFNULL(tohi.number, '') AS number, IFNULL(cycl.name, '') AS cycl_name, IFNULL(deds.name, '') AS deds_name,
            tohi.umnu_bichdate, tohi.odoo_bichdate, tohi.day_diff, tohi.night_diff, tohi.total_diff, tohi.day_balance_prev,
            tohi.day_balance, prta.limit, tohi.night_balance_prev, tohi.night_balance, tohi.tariff,
            ROUND(prta.low_limit_price + serg_une, 2) AS low_limit_price, ROUND(prta.high_limit_price + serg_une, 2)
            AS high_limit_price, ROUND(prta.odor_une + prta.serg_une, 2) AS odor_une,
            ROUND(prta.shono_une + prta.serg_une, 2) AS shono_une, prhi.between_days, prhi.suuri_price, prhi.barimt_une, prhi.low150_price,
            prhi.high150_price, prhi.day_price, prhi.night_price, prhi.total_price, prhi.nuat, prhi.tot_pri_suu_cha,
            prhi.total_price_nuat, avla.uilchilgeenii_tulbur, avla.tv_huraamj FROM data_customer cust
            JOIN data_avlaga avla ON cust.id = avla.customer_id AND avla.year = '""" + year + """' AND avla.month = '""" + month + """'
            JOIN data_geree gere ON cust.code = gere.customer_code AND gere.is_active = '1'
            JOIN data_cycle cycl ON gere.cycle_code = cycl.code AND cycl.is_active = '1'
            JOIN data_dedstants deds ON gere.dedstants_code = deds.code AND deds.is_active = '1'
            LEFT JOIN data_address addr ON cust.id = addr.customer_id AND addr.is_active = '1'
            JOIN data_bank bank ON gere.bank_code = bank.code AND bank.is_active = '1'
            LEFT JOIN data_tooluurhistory tohi ON cust.code = tohi.customer_code AND tohi.odoo_bichdate BETWEEN
            '""" + start_date + """ 00:00:00.000000' AND '""" + end_date + """ 23:59:59.999999'
            LEFT JOIN data_pricehistory prhi ON cust.code = prhi.customer_code AND prhi.odoo_bichdate BETWEEN
            '""" + start_date + """ 00:00:00.000000' AND '""" + end_date + """ 23:59:59.999999'
            JOIN data_pricetariff prta ON prhi.price_tariff_id = prta.id
            WHERE cust.is_active = '1' AND tohi.number = prhi.number AND cust.code = '""" + code + """'"""
        customer = Customer.objects.raw(query)

        qr_data = None
        billId = None
        lottery = None
        customer = list(customer)

        if int(type) == 1 and len(customer) > 0:
            cust = list(customer)[0]
            #self.pos_api.pos_sendData()
            return_json = self.pos_api.pos_put("", amount)
            if return_json['success']:
                qr_data = return_json['qrData']
                billId = return_json['billId']
                lottery = return_json['lottery']

                pay_his = PaymentHistory.objects.filter(customer_id=cust.id).latest('id')
                posapi = PosAPI.objects.create(pay_his_id=pay_his.id, success=return_json['success'] if return_json['success'] else 0)
                posapi.created_user_id = request.user.id
                posapi.is_active = '1'
                posapi.customer_id = cust.id
                posapi.registerNo = return_json['registerNo'] if return_json['registerNo'] else '0'
                posapi.billType = return_json['billType'] if return_json['billType'] else '0'
                posapi.cityTax = return_json['cityTax'] if return_json['cityTax'] else '0'
                posapi.vat = return_json['vat'] if return_json['vat'] else Decimal(0.00)
                posapi.invoiceId = return_json['invoiceId'] if return_json['invoiceId'] else '0'
                posapi.billId = return_json['billId'] if return_json['billId'] else '0'
                posapi.returnBillId = return_json['returnBillId'] if return_json['returnBillId'] else '0'
                posapi.posNo = return_json['posNo'] if return_json['posNo'] else '0'
                posapi.date = return_json['date'] if return_json['date'] else datetime.datetime.now()
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
            else:
                messages.warning(request, str(return_json))

        return {'customer': customer, 'qr_data': qr_data, 'billId': billId, 'lottery': lottery}


class InvoiceAan1(LoginRequiredMixin, View):
    template_name = "homepage/borluulalt/invoice_aan1.html"
    permission_required = ''

    def get(self, request, type, code, start_date, end_date, ehnii, before_payment, payment, bichilt, *args, **kwargs):
        year = start_date[:4]
        month = start_date[5:7]

        if month[0] == '0':
            month = month[1]

        hasag_q = """SELECT hahi.id, tohi.number, ROUND(tohi.guid_coef * tohi.huch_coef, 3) AS coef,
            ROUND(prta.odor_une + prta.serg_une - 0.001, 2) AS odor_une, hahi.chadal_price,
            ROUND(prta.shono_une + prta.serg_une - 0.001, 2) AS shono_une, hahi.between_days,
            ROUND(prta.orgil_une + prta.serg_une - 0.001, 2) AS orgil_une, prta.chadal_une,
            tohi.day_balance_prev, tohi.day_balance, tohi.day_diff, tohi.day_diff_coef,
            tohi.night_balance_prev, tohi.night_balance, tohi.night_diff, tohi.night_diff_coef,
            tohi.rush_balance_prev, tohi.rush_balance, tohi.rush_diff, tohi.rush_diff_coef, tohi.tariff,tohi.total_diff_coef
            FROM data_hasagdahhistory hahi JOIN data_tooluurhistory tohi ON hahi.child_tool_his = tohi.id
            JOIN data_pricetariff prta ON hahi.price_tariff_id = prta.id
            WHERE hahi.customer_code = '"""+code+"""' AND hahi.year = '"""+year+"""' AND hahi.month = '"""+month+"""'"""

        hasagdah_histories = HasagdahHistory.objects.raw(hasag_q)
        result_data = self.get_customer_aan(code, start_date, end_date, year, month)
        if len(list(hasagdah_histories)) == 0:
            context = {
                'customers': self.get_customer_aan(code, start_date, end_date, year, month),
                'ehnii': ehnii,
                'payment': payment,
                'before_payment': before_payment,
                'bichilt': bichilt,
                'amount': payment,
                'type': str(type)
            }
            try:
                if result_data['customer'][0].email is not None and isValidEmail(result_data['customer'][0].email) and request.GET['email']:
                    data = {"status": True}
                    try:
                        htmly = get_template("homepage/borluulalt/invoice_aan1.html")
                        context['show'] = False
                        mail = EmailMultiAlternatives('Цахилгааны төлбөр', "нэхэмжлэх", from_email='info@smartenergy.mn',
                                                      to=[result_data['customer'][0].email])
                        html_content = htmly.render(context)
                        mail.attach_alternative(html_content, "text/html")
                        mail.send()
                    except Exception:
                        data = {"status": False}
                    return HttpResponse(simplejson.dumps(data), content_type='application/json')
            except Exception:
                error = True
            return render(request, "homepage/borluulalt/invoice_aan1.html", context)
        else:
            context = {
                'customers': self.get_customer_aan(code, start_date, end_date, year, month),
                'hasagdah_histories': hasagdah_histories,
                'ehnii': ehnii,
                'payment': payment,
                'before_payment': before_payment,
                'bichilt': bichilt,
                'amount': payment,
                'type': str(type)
            }
            try:
                if result_data['customer'][0].email is not None and isValidEmail(result_data['customer'][0].email) and request.GET['email']:
                    data = {"status": True}
                    try:
                        htmly = get_template("homepage/borluulalt/invoice_hasagdah1.html")
                        context['show'] = False
                        mail = EmailMultiAlternatives('Цахилгааны төлбөр', "нэхэмжлэх",
                                                      from_email='info@smartenergy.mn',
                                                      to=[result_data['customer'][0].email])
                        html_content = htmly.render(context)
                        mail.attach_alternative(html_content, "text/html")
                        mail.send()
                    except Exception:
                        data = {"status": False}
                    return HttpResponse(simplejson.dumps(data), content_type='application/json')
            except Exception:
                error = True
            return render(request, "homepage/borluulalt/invoice_hasagdah1.html", context)

    def post(self, request, *args, **kwargs):
        return None

    def get_customer_aan(self, code, start_date, end_date, year, month):
        query = """SELECT cust.id,cust.email, cust.last_name, cust.first_name, cust.register, IFNULL(addr.address_name, '') AS address_name,
            IFNULL(bank.name, '') AS bank_name, IFNULL(bank.dans, '') AS bank_dans, cust.code AS customer_code, cust.customer_type,
            IFNULL(cycl.name, '') AS cycl_name, IFNULL(deds.name, '') AS deds_name, prhi.price_tariff_id, avla.uilchilgeenii_tulbur,
            tohi.umnu_bichdate, tohi.odoo_bichdate, tohi.year, tohi.month, SUM(prhi.nuat) AS nuat, prhi.price_tariff_id,
            SUM(tohi.total_diff) AS total_diff, SUM(tohi.total_diff_coef) AS total_diff_coef, SUM(prhi.chadal_price) AS chadal_price,
            SUM(prhi.total_price) AS total_price, SUM(prhi.tot_pri_suu_cha) AS tot_pri_suu_cha, prhi.barimt_une,
            SUM(prhi.total_price_nuat) AS total_price_nuat,
            IFNULL((SELECT SUM(hahi.day_price + hahi.night_price + hahi.rush_price) FROM data_hasagdahhistory hahi
            WHERE hahi.year = '"""+year+"""' AND hahi.month = '"""+month+"""' AND cust.code = hahi.customer_code), 0.00) AS hasagdah,
            IFNULL((SELECT SUM(hahi.chadal_price) FROM data_hasagdahhistory hahi
            WHERE hahi.year = '"""+year+"""' AND hahi.month = '"""+month+"""' AND cust.code = hahi.customer_code), 0.00) AS hasagdah_chadal
            FROM data_customer cust
            JOIN data_avlaga avla ON cust.id = avla.customer_id AND avla.year = '""" + year + """' AND avla.month = '""" + month + """'
            JOIN data_geree gere ON cust.code = gere.customer_code AND gere.is_active = '1'
            JOIN data_cycle cycl ON gere.cycle_code = cycl.code AND cycl.is_active = '1'
            LEFT JOIN data_dedstants deds ON gere.dedstants_code = deds.code AND deds.is_active = '1'
            LEFT JOIN data_address addr ON cust.id = addr.customer_id AND addr.is_active = '1'
            JOIN data_bank bank ON gere.bank_code = bank.code AND bank.is_active = '1'
            LEFT JOIN data_tooluurhistory tohi ON cust.code = tohi.customer_code AND tohi.odoo_bichdate BETWEEN
            '""" + start_date + """ 00:00:00.000000' AND '""" + end_date + """ 23:59:59.999999'
            LEFT JOIN data_pricehistory prhi ON cust.code = prhi.customer_code AND prhi.odoo_bichdate BETWEEN
            '""" + start_date + """ 00:00:00.000000' AND '""" + end_date + """ 23:59:59.999999'
            WHERE cust.is_active = '1' AND tohi.customer_code = prhi.customer_code AND tohi.number = prhi.number AND cust.code = '""" + code +"""'"""
        customers = Customer.objects.raw(query)
        return customers