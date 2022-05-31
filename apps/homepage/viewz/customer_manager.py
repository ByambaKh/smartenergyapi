# coding=utf-8
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist

from mcsi.utils import *
from apps.extra import *

class CustomerManager():
    def create_customer_bank(self,bank_id,bank_code,user_code):
        response = {}
        try:
            bank_customers = CustomerHasBank.objects.filter(bank_code=bank_code,bank_id=bank_id,customer_id=user_code).first()
            bank= DataBank.objects.filter(id=bank_id).first()
            print(bank_customers,'bank_customers')
            if bank_customers is None:
                if bank is not None:
                    cur_date = datetime.datetime.now()      
                    new_bank = CustomerHasBank.objects.create(created_date=cur_date, updated_date=cur_date, bank_code=bank_code,bank_id=bank_id,customer_id=user_code)
                    new_bank.save()
                    response["code"] = 200
                    response["message"] = "Амжилттай үүслээ."
                    response["data"] = new_bank
                else:
                    response["code"] = 400
                    response["message"] = "Буруу код илгээсэн байна."   
            else:
                response["code"] = 400
                response["message"] = "Аль хэдийн үүссэн байна."

        except Geree.DoesNotExist:
            response["code"] = 400
            response["message"] = "Алдаа гарлаа."
        return response
        
    def remove_customer_bank(self,bank_id,bank_code,user_code):
        response = {}
        try:
            bank_customers = CustomerHasBank.objects.filter(bank_code=bank_code,bank_id=bank_id,customer_id=user_code).first()
            bank= DataBank.objects.filter(code=bank_code,id=bank_id).first()
            print(bank_customers,'bank_customers')
            if bank_customers is not None:
                if bank is not None:
                    selected_bank = CustomerHasBank.objects.get(bank_code=bank_code,bank_id=bank_id,customer_id=user_code)
                    selected_bank.delete()
                    response["code"] = 200
                    response["message"] = "Амжилттай устлаа."
                else:
                    response["code"] = 400
                    response["message"] = "Буруу код илгээсэн байна."   
            else:
                response["code"] = 400
                response["message"] = "Уг хэрэглэгчийн мэдээлэл байхгүй байна."

        except Geree.DoesNotExist:
            response["code"] = 400
            response["message"] = "Алдаа гарлаа."
        return response
