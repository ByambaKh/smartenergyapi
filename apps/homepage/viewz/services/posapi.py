# coding=utf-8
import json
import ctypes
import platform
from braces.views import LoginRequiredMixin
from decimal import Decimal
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


if 'Windows' in platform.system():
    PosAPI = ctypes.cdll.LoadLibrary('./posapi/PosAPI.dll')
else:
    PosAPI = ctypes.cdll.LoadLibrary('/usr/lib/x86_64-linux-gnu/libPosAPI.so')


customerNo = '00000038' # Test customer id
districtCode = '23' # Duureg id /Khan-Uul/
unitPrice = '98.40'# 1 kVt tsahilgaanii une


@method_decorator(csrf_exempt, name='dispatch')
class PosapiMTA(LoginRequiredMixin):
    today = datetime.now()
    minus_month = today + relativedelta(months=-1)

    def pos_init(self):
        check_api = self.pos_checkApi()
        if check_api['network']['success']:
            if check_api['database']['success']:
                if check_api['config']['success']:
                    return True
                else:
                    if self.pos_sendData()['success']:
                        return True
                    else:
                        return False
        elif check_api['errorCode'] == '100':
            if self.pos_sendData()['success']:
                return True
            else:
                return False
        return False

    def pos_checkApi(self):
        checkApi = PosAPI.checkApi
        if 'Windows' in platform.system():
            checkApi.restype = ctypes.c_wchar_p
            return json.loads(checkApi())
        else:
            checkApi.restype = ctypes.c_char_p
            result = str(checkApi(), 'utf-8')
            return json.loads(result)

    def pos_sendData(self):
        sendData = PosAPI.sendData
        if 'Windows' in platform.system():
            sendData.restype = ctypes.c_wchar_p
            return json.loads(sendData())
        else:
            sendData.restype = ctypes.c_char_p
            result = str(sendData(), 'utf-8')
            return json.loads(result)

    def pos_getInformation(self):
        getInformation = PosAPI.getInformation
        if 'Windows' in platform.system():
            getInformation.restype = ctypes.c_wchar_p
            return json.loads(getInformation())
        else:
            getInformation.restype = ctypes.c_char_p
            result = str(getInformation(), 'utf-8')
            return json.loads(result)

    def pos_put(self, customerNo, amount):
        put = PosAPI.put

        if 'Windows' in platform.system():
            put.restype = ctypes.c_wchar_p
            result_put = put(self.make_put(customerNo, amount))
            return json.loads(result_put)
        else:
            put.restype = ctypes.c_char_p
            put.argtypes = [ctypes.c_char_p]
            c = ctypes.create_string_buffer((self.make_put(customerNo, amount)).encode())
            result = put(c)
            parse_str = str(result, 'utf-8')
            return json.loads(parse_str)

    def pos_put_aan(self, customerNo, amount):
        put = PosAPI.put

        if len(str(customerNo)) >= 7:
            if 'Windows' in platform.system():
                put.restype = ctypes.c_wchar_p
                result_put = put(self.make_put_aan(customerNo, amount))
                return json.loads(result_put)
            else:
                put.restype = ctypes.c_char_p
                put.argtypes = [ctypes.c_char_p]
                c = ctypes.create_string_buffer((self.make_put_aan(customerNo, amount)).encode())
                result = put(c)
                parse_str = str(result, 'utf-8')
                return json.loads(parse_str)

    def make_put(self, customerNo, amount):
        amount = float(amount)
        if customerNo != "":
            if len(str(customerNo)) < 7:
                customerNo = "1000000"
        print("customerNo : " + str(customerNo))
        today = datetime.now()

        put_params = "{\"billIdSuffix\": \"\", \"posNo\": \"0001\", \"districtCode\": \"23\", \"cashAmount\": \"0.00\", " \
            "\"vat\": \"" + str("{:.2f}".format((amount * 10) / 110)) + "\", \"invoiceId\": \"\"," \
            "\"reportMonth\": \"\", \"customerNo\": \"" + str(customerNo) + "\", \"billType\": \"\", \"stocks\": [{\"code\": \"6911\", " \
            "\"totalAmount\": \"" + str("{:.2f}".format(amount)) + "\", \"measureUnit\": \"кВт\", \"name\": \"Цахилгаан\", \"qty\": \"1.00\", " \
            "\"cityTax\": \"0.00\", \"vat\": \"" + str("{:.2f}".format((amount * 10) / 110)) + "\", \"barcode\": \"6911\", " \
            "\"unitPrice\": \"" + str("{:.2f}".format(amount - (amount * 10) / 110)) + "\"}], \"returnBillId\": \"\", \"taxType\": \"\", " \
            "\"amount\": \"" + str("{:.2f}".format(amount)) + "\", \"branchNo\": \"001\", " \
            "\"nonCashAmount\": \"" + str("{:.2f}".format(amount)) + "\", \"cityTax\": \"0.00\"}"
        return put_params

    def make_put_aan(self, customerNo, amount):
        put_params = "{\"billIdSuffix\": \"\", \"posNo\": \"0001\", \"districtCode\": \"23\", \"cashAmount\": \"0.00\", " \
            "\"vat\": \"" + str("{:.2f}".format((amount * 10) / 110)) + "\", \"invoiceId\": \"\"," \
            "\"reportMonth\": \"\", \"customerNo\": \"" + str(customerNo) + "\", \"billType\": \"3\", \"stocks\": [{\"code\": \"6911\", " \
            "\"totalAmount\": \"" + str("{:.2f}".format(amount)) + "\", \"measureUnit\": \"кВт\", \"name\": \"Цахилгаан\", \"qty\": \"1.00\", " \
            "\"cityTax\": \"0.00\", \"vat\": \"" + str("{:.2f}".format((amount * 10) / 110)) + "\", \"barcode\": \"6911\", " \
            "\"unitPrice\": \"" + str("{:.2f}".format(amount - (amount * 10) / 110)) + "\"}], \"returnBillId\": \"\", \"taxType\": \"\", " \
            "\"amount\": \"" + str("{:.2f}".format(amount)) + "\", \"branchNo\": \"001\", " \
            "\"nonCashAmount\": \"" + str("{:.2f}".format(amount)) + "\", \"cityTax\": \"0.00\"}"
        return put_params

    def return_bill(self, bill_id, date):
        returnBill = PosAPI.returnBill

        date = datetime.strftime(date, "%Y-%m-%d %H:%M:%S")
        rb_params = "{\"returnBillId\": \"" + str(bill_id) + "\", \"date\": \"" + str(date) + "\"}"

        if 'Windows' in platform.system():
            returnBill.restype = ctypes.c_wchar_p
            result_put = returnBill(rb_params)
            return json.loads(result_put)
        else:
            returnBill.restype = ctypes.c_char_p
            returnBill.argtypes = [ctypes.c_char_p]
            c = ctypes.create_string_buffer(rb_params.encode())
            result = returnBill(c)
            parse_str = str(result, 'utf-8')
            return json.loads(parse_str)

    def pos_put_group(self, results):
        print("IN pos_put_group FUNCTION")

        no_registers = []
        data_results = []
        put = PosAPI.put
        counter = 0

        print("results_len : " + str(len(results)))
        for result in results:
            print("customer_angilal : " + str(result.customer_angilal))
            if result.customer_angilal == '1': # butsaaj 0 bolgoh
                customerNo = "5228697" # str(result.register)
                balance = result.balance
                if (len(customerNo) == 7 or len(customerNo) == 10) and (balance > Decimal(0.00)):
                    if 'Windows' in platform.system():
                        if self.pos_init():
                            try:
                                put.restype = ctypes.c_wchar_p
                                result_put = put(self.make_put_group(result, customerNo))
                                print(json.loads(result_put))
                                res = json.loads(result_put)
                                if res['success']:
                                    data_results.append(res['billId'])
                            except Exception as e:
                                print("SEND PUT MESSAGE : " + str(e))
                    else:
                        print("IN Linux FUNCTION")
                        print("customerNo : " + str(customerNo))
                        print("balance : " + str(float(result.balance if result.balance else 0.0)))
                        print("vat : " + str("{:.2f}".format((100 * 10) / 110)))
                        print("unitPrice : " + str("{:.2f}".format(100 - (100 * 10) / 110)))

                        if self.pos_init():
                            try:
                                put.restype = ctypes.c_char_p
                                put.argtypes = [ctypes.c_char_p]
                                c = ctypes.create_string_buffer((self.make_put_group(result, customerNo)).encode())
                                result_put = put(c)
                                parse_str = str(result_put, 'utf-8')
                                print(json.loads(parse_str))
                                res = json.loads(parse_str)
                                if res['success']:
                                    data_results.append(res['billId'])
                            except Exception as e:
                                print("SEND PUT MESSAGE : " + str(e))
                else:
                    no_registers.append(result.code)
                    print("ilgeegdeegui aan : " + str(no_registers))

            counter = counter + 1
            if counter == 1:
                return {'data_results': data_results, 'no_registers': no_registers}
        return {'data_results': data_results, 'no_registers': no_registers}

    def make_put_group(self, result, customerNo):
        amount = float(result.balance if result.balance else 0.0)

        put_params = "{\"billIdSuffix\": \"\", \"posNo\": \"0001\", \"districtCode\": \"23\", \"cashAmount\": \"0.00\", " \
            "\"vat\": \"" + str("{:.2f}".format((100 * 10) / 110)) + "\", \"invoiceId\": \"\"," \
            "\"reportMonth\": \"\", \"customerNo\": \"" + customerNo + "\", \"billType\": \"3\", \"stocks\": [{\"code\": \"6911\", " \
            "\"totalAmount\": \"" + str("{:.2f}".format(100)) + "\", \"measureUnit\": \"кВт\", \"name\": \"Цахилгаан\", \"qty\": \"1.00\", " \
            "\"cityTax\": \"0.00\", \"vat\": \"" + str("{:.2f}".format((100 * 10) / 110)) + "\", \"barcode\": \"6911\", " \
            "\"unitPrice\": \"" + str("{:.2f}".format(100 - (100 * 10) / 110)) + "\"}], \"returnBillId\": \"\", \"taxType\": \"\", " \
            "\"amount\": \"" + str("{:.2f}".format(100)) + "\", \"branchNo\": \"001\", " \
            "\"nonCashAmount\": \"" + str("{:.2f}".format(100)) + "\", \"cityTax\": \"0.00\"}"

        return put_params