# coding=utf-8
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist

from mcsi.utils import *
from apps.extra import *

class BichiltManager():
    def create_bichilt(self, type, tooluur_number, code, bichilt_date, zadgai_bichilt, day, night, rush, description, user_id, is_problem):
        tooluur_customers = TooluurCustomer.objects.filter(tooluur__number=tooluur_number, is_active='1')

        add_bichilt = None

        if len(tooluur_customers) > 1:
            for tooluur_customer in tooluur_customers:
                if tooluur_customer.dedstants is not None:
                    add_bichilt = self.add_bichilt(tooluur_customer, "0", bichilt_date, zadgai_bichilt, day, night, rush, description, user_id, is_problem)
                if tooluur_customer.customer is not None:
                    add_bichilt = self.add_bichilt(tooluur_customer, "1", bichilt_date, zadgai_bichilt, day, night, rush, description, user_id, is_problem)
                if tooluur_customer.bair is not None:
                    add_bichilt = self.add_bichilt(tooluur_customer, "2", bichilt_date, zadgai_bichilt, day, night, rush, description, user_id, is_problem)
        else:
            add_bichilt = self.add_bichilt(tooluur_customers.first(), type, bichilt_date, zadgai_bichilt, day, night, rush, description, user_id, is_problem)

        return add_bichilt

    def add_bichilt(self, tooluur_customer, type, bichilt_date, zadgai_bichilt, day, night, rush, description, user_id, is_problem):
        response = {}

        total_day_zoruu = 0
        total_night_zoruu = 0
        total_rush_zoruu = 0
        total_zoruu = 0
        tariff = None

        if tooluur_customer is not None:
            bichilt_list = tooluur_customer.bichilt_set.all().order_by('-bichilt_date')
            
            if type == "1":
                try:
                    geree = Geree.objects.get(customer_code=tooluur_customer.customer_code)
                except Geree.DoesNotExist:
                    response["code"] = 400
                    response["description"] = "Алдаа гарлаа. Гэрээний мэдээлэл олдсонгүй."
                    return response
                try:
                    tariff = PriceTariff.objects.get(bus_type=geree.bus_type, une_type=tooluur_customer.customer.customer_angilal)
                except PriceTariff.DoesNotExist:
                    response["code"] = 400
                    response["description"] = "Алдаа гарлаа. Тарифийн мэдээлэл олдсонгүй."
                    return response
            
            if len(bichilt_list) > 0:
                bichilt = bichilt_list[0]
                prev_id = str(bichilt.id)
                if bichilt.day_balance == None:
                    prev_day_balance = 0
                else:
                    prev_day_balance = float(bichilt.day_balance)
                if bichilt.night_balance == None:
                    prev_night_balance = 0
                else:
                    prev_night_balance = float(bichilt.night_balance)
                if bichilt.rush_balance == None:
                    prev_rush_balance = 0
                else:
                    prev_rush_balance = float(bichilt.rush_balance)
                if zadgai_bichilt == "0":
                    total_night_zoruu = float(night) - prev_night_balance
                    if total_night_zoruu < 0:
                        total_night_zoruu = 0
                        night = prev_night_balance
                    total_day_zoruu = float(day) - prev_day_balance
                    if total_day_zoruu < 0:
                        total_day_zoruu = 0
                        day = prev_day_balance
                    total_rush_zoruu = float(rush) - prev_rush_balance
                    if total_rush_zoruu < 0:
                        total_rush_zoruu = 0
                        rush = prev_rush_balance
                    total_zoruu = total_day_zoruu + total_night_zoruu + total_rush_zoruu
                else:
                    day = prev_day_balance
                    night = prev_night_balance
                    rush = prev_rush_balance
                start_date = bichilt.bichilt_date
            else:
                prev_id = "0"
                if zadgai_bichilt == "0":
                    total_zoruu = 0
                    total_day_zoruu = float(day) - float(tooluur_customer.tooluur.balance_value)
                    if total_day_zoruu > 0:
                        total_zoruu = total_day_zoruu
                    if tooluur_customer.tooluur.balance_value_night is not None and tooluur_customer.tooluur.balance_value_night != '':
                        total_night_zoruu = float(night) - float(tooluur_customer.tooluur.balance_value_night)
                        if total_night_zoruu < 0:
                            total_night_zoruu = 0
                            night = float(tooluur_customer.tooluur.balance_value_night)
                        else:
                            total_zoruu = total_zoruu + total_night_zoruu
                    else:
                        total_night_zoruu = 0
                    if tooluur_customer.tooluur.balance_value_rush is not None and tooluur_customer.tooluur.balance_value_rush != '':
                        total_rush_zoruu = float(rush) - float(tooluur_customer.tooluur.balance_value_rush)
                        if total_rush_zoruu < 0:
                            total_rush_zoruu = 0
                            rush = float(tooluur_customer.tooluur.balance_value_rush)
                        else:
                            total_zoruu = total_zoruu + total_rush_zoruu
                    else:
                        total_rush_zoruu = 0
                else:
                    day = float(tooluur_customer.tooluur.balance_value if tooluur_customer.tooluur.balance_value else 0.00)
                    night = float(tooluur_customer.tooluur.balance_value_night if tooluur_customer.tooluur.balance_value_night else 0.00)
                    rush = float(tooluur_customer.tooluur.balance_value_rush if tooluur_customer.tooluur.balance_value_rush else 0.00)
                start_date = bichilt_date + relativedelta(months=-1)

            b_date = bichilt_date.date()
            bichilt_date = datetime.datetime.strftime(bichilt_date, '%Y-%m-%d 00:00:00')
            bichilt_date = datetime.datetime.strptime(bichilt_date, '%Y-%m-%d %H:%M:%S')
            new_bichilt = Bichilt.objects.create(tooluur=tooluur_customer, bichilt_date=bichilt_date, prev_bichilt_id=prev_id)
            new_bichilt.year = b_date.year
            new_bichilt.month = b_date.month
            new_bichilt.user_type = str(type)
            new_bichilt.day_balance = day
            new_bichilt.night_balance = night
            new_bichilt.rush_balance = rush
            new_bichilt.is_problem = is_problem
            if zadgai_bichilt == "0":
                new_bichilt.day_diff = str(round(total_day_zoruu, 9))
                new_bichilt.night_diff = str(round(total_night_zoruu, 9))
                new_bichilt.rush_diff = str(round(total_rush_zoruu, 9))
                new_bichilt.total_diff = str(round(total_zoruu, 9))
                if type == "1":
                    self.calculate_price(total_day_zoruu, total_night_zoruu, total_rush_zoruu, tariff, start_date, b_date, new_bichilt, tooluur_customer)
            else:
                if type == "1":
                    new_bichilt.is_zadgai = zadgai_bichilt
                    new_bichilt.description = description
            new_bichilt.created_user_id = user_id
            new_bichilt.save()
            response["code"] = 200
            return response
        else:
            response["code"] = 400
            response["description"] = "Алдаа гарлаа. Тоолууртай холбогдсон хэрэглэгч(дэд станц, байр) олдсонгүй."
            return response

    def edit_bichilt(self, type, selected_bichilt, bichilt_date, zadgai_bichilt, day, night, rush, description, user_id, is_problem):
        response = {}

        total_day_zoruu = 0
        total_night_zoruu = 0
        total_rush_zoruu = 0
        total_zoruu = 0
        tariff = None
        customer_angilal = selected_bichilt.tooluur.customer_angilal

        if type == "1":
            try:
                geree = Geree.objects.get(customer_code=selected_bichilt.tooluur.customer.code)
            except Geree.DoesNotExist:
                response["code"] = 400
                response["description"] = "Алдаа гарлаа. Гэрээний мэдээлэл олдсонгүй."
                return response
            try:
                tariff = PriceTariff.objects.get(bus_type=geree.bus_type, une_type=customer_angilal)
            except PriceTariff.DoesNotExist:
                response["code"] = 400
                response["description"] = "Алдаа гарлаа. Тарифийн мэдээлэл олдсонгүй."
                return response

        if selected_bichilt.prev_bichilt_id != "0" and selected_bichilt.prev_bichilt_id != None:
            bichilt = Bichilt.objects.get(id=selected_bichilt.prev_bichilt_id)
            if bichilt.day_balance == None:
                prev_day_balance = 0
            else:
                prev_day_balance = float(bichilt.day_balance)
            if bichilt.night_balance == None:
                prev_night_balance = 0
            else:
                prev_night_balance = float(bichilt.night_balance)
            if bichilt.rush_balance == None:
                prev_rush_balance = 0
            else:
                prev_rush_balance = float(bichilt.rush_balance)
            if zadgai_bichilt == "0":
                total_night_zoruu = float(night) - prev_night_balance
                if total_night_zoruu < 0:
                    total_night_zoruu = 0
                    night = prev_night_balance
                total_day_zoruu = float(day) - prev_day_balance
                if total_day_zoruu < 0:
                    total_day_zoruu = 0
                    day = prev_day_balance
                total_rush_zoruu = float(rush) - prev_rush_balance
                if total_rush_zoruu < 0:
                    total_rush_zoruu = 0
                    rush = prev_rush_balance
                total_zoruu = total_day_zoruu + total_night_zoruu + total_rush_zoruu
            else:
                day = prev_day_balance
                night = prev_night_balance
                rush = prev_rush_balance
            start_date = bichilt.bichilt_date
        else:
            if zadgai_bichilt == "0":
                total_zoruu = 0
                total_day_zoruu = float(day) - float(selected_bichilt.tooluur.tooluur.balance_value)
                if total_day_zoruu > 0:
                    total_zoruu = total_day_zoruu
                if selected_bichilt.tooluur.tooluur.balance_value_night != '':
                    total_night_zoruu = float(night) - float(selected_bichilt.tooluur.tooluur.balance_value_night)
                    if total_night_zoruu < 0:
                        total_night_zoruu = 0
                        night = float(selected_bichilt.tooluur.tooluur.balance_value_night)
                    else:
                        total_zoruu = total_zoruu + total_night_zoruu
                else:
                    total_night_zoruu = 0
                if selected_bichilt.tooluur.tooluur.balance_value_rush != '':
                    total_rush_zoruu = float(rush) - float(selected_bichilt.tooluur.tooluur.balance_value_rush)
                    if total_rush_zoruu < 0:
                        total_rush_zoruu = 0
                        rush = float(selected_bichilt.tooluur.tooluur.balance_value_rush)
                    else:
                        total_zoruu = total_zoruu + total_rush_zoruu
                else:
                    total_rush_zoruu = 0
            else:
                day = float(selected_bichilt.tooluur.tooluur.balance_value)
                night = float(selected_bichilt.tooluur.tooluur.balance_value_night)
                rush = float(selected_bichilt.tooluur.tooluur.balance_value_rush)
            start_date = bichilt_date + relativedelta(months=-1)

        selected_bichilt.bichilt_date = bichilt_date
        selected_bichilt.day_balance = day
        selected_bichilt.night_balance = night
        selected_bichilt.rush_balance = rush
        selected_bichilt.is_zadgai = zadgai_bichilt
        selected_bichilt.is_problem = is_problem
        selected_bichilt.description = description
        selected_bichilt.day_diff = str(round(total_day_zoruu, 9))
        selected_bichilt.night_diff = str(round(total_night_zoruu, 9))
        selected_bichilt.rush_diff = str(round(total_rush_zoruu, 9))
        selected_bichilt.total_diff = str(round(total_zoruu, 9))
        if zadgai_bichilt == "0" and type == 1:
            self.calculate_price(total_day_zoruu, total_night_zoruu, total_rush_zoruu, tariff, start_date,
                                 bichilt_date.date(), selected_bichilt, selected_bichilt.tooluur)

        selected_bichilt.created_user_id = user_id
        selected_bichilt.year = bichilt_date.date().year
        selected_bichilt.month = bichilt_date.date().month
        selected_bichilt.save()
        response["code"] = 200
        return response

    def calculate_price(self, day, night, rush, tariff, start_date, end_date, new_bichilt, tooluur_customer):
        day = round(float(day), 3)
        night = round(float(night), 3)
        rush = round(float(rush), 3)

        day_price = round(float(tariff.odor_une) + float(tariff.serg_une), 2)
        night_price = round(float(tariff.shono_une) + float(tariff.serg_une), 2)
        rush_price = round(float(tariff.orgil_une) + float(tariff.serg_une), 2)
        low_limit_price = round(float(tariff.low_limit_price) + float(tariff.serg_une), 2)
        high_limit_price = round(float(tariff.high_limit_price) + float(tariff.serg_une), 2)
        chadal_price = float(tariff.chadal_une)
        suuri_une = float(tariff.suuri_une)
        customer_angilal = tooluur_customer.customer.customer_angilal

        total_diff = round(day + night + rush, 2)
        if total_diff > 0:
            coef = 1
            if customer_angilal == "1":
                if tooluur_customer.tooluur.tariff == "0":
                    if day <= float(tariff.limit):
                        hereglee_price1 = round(day * low_limit_price, 2)
                        hereglee_price = self.add_nuat_price(hereglee_price1)
                    else:
                        first_hereglee_price = round(float(tariff.limit) * low_limit_price, 2)
                        second_hereglee_price1 = round(day - float(tariff.limit), 2)
                        second_hereglee_price = round(second_hereglee_price1 * high_limit_price, 2)
                        hereglee_price1 = round(first_hereglee_price + second_hereglee_price, 2)
                        hereglee_price = self.add_nuat_price(hereglee_price1)
                else:
                    hereglee_price_day = round(day * day_price, 2)
                    hereglee_price_night = round(night * night_price, 2)
                    hereglee_price1 = round(hereglee_price_day + hereglee_price_night, 2)
                    hereglee_price = self.add_nuat_price(hereglee_price1)
            else:
                amp_coff = huch_coff = 1
                if tooluur_customer.guidliin_trans != None and tooluur_customer.guidliin_trans != '':
                    amp_coff = round(float(tooluur_customer.guidliin_trans.multiply_coef), 3)
                if tooluur_customer.huchdeliin_trans != None and tooluur_customer.huchdeliin_trans != '':
                    huch_coff = round(float(tooluur_customer.huchdeliin_trans.multiply_coef), 3)
                coef = round(amp_coff * huch_coff, 3)
                day_total_price1 = round(day * coef, 2)
                day_total_price = round(day_total_price1 * day_price, 2)
                night_total_price1 = round(night * coef, 2)
                night_total_price = round(night_total_price1 * night_price, 2)
                rush_total_price1 = round(rush * coef, 2)
                rush_total_price = round(rush_total_price1 * rush_price, 2)
                hereglee_price1 = round(day_total_price + night_total_price, 2)
                hereglee_price2 = round(hereglee_price1 + rush_total_price, 2)
                hereglee_price = self.add_nuat_price(hereglee_price2)
            new_bichilt.hereglee_price = str(round(hereglee_price, 2))
            new_bichilt.sergeegdeh_price = 0.00

            if customer_angilal == "0":
                diff = 1
                power_time = 1
                if tooluur_customer.tooluur.tariff == "0":
                    diff = round(day * coef, 2)
                    power_time = 12
                elif tooluur_customer.tooluur.tariff == "1":
                    diff = round((day + night) * coef, 2)
                    power_time = 12
                elif tooluur_customer.tooluur.tariff == "2":
                    diff = round(rush * coef, 2)
                try:
                    number_of_days = get_number_of_days(start_date, end_date)
                    if number_of_days <= 27:
                        chadal_price = round(chadal_price / 30, 2)
                        chadal_price = round(chadal_price * number_of_days, 2)
                    chadal1 = round(diff / number_of_days, 2)
                    chadal2 = round(chadal1 / power_time, 2)
                    chadal3 = round(chadal2 * chadal_price, 2)
                    chadal = self.add_nuat_price(chadal3)
                except ZeroDivisionError:
                    chadal = 0.00
                if tooluur_customer.customer.customer_type == "0":
                    chadal = 0.00
                suuri_une = 0.00
            else:
                chadal = 0.00
                suuri_une = self.add_nuat_price(suuri_une)

            new_bichilt.chadal_price = chadal
            new_bichilt.suuri_price = suuri_une

            total_price1 = round(hereglee_price + suuri_une, 2)
            total_price = round(total_price1 + chadal, 2)
            new_bichilt.total_price = total_price
            return total_price

        new_bichilt.sergeegdeh_price = 0.00
        new_bichilt.chadal_price = 0.00
        new_bichilt.suuri_price = 0.00
        new_bichilt.total_price = 0.00
        return 0.00

    def add_nuat_price(self, total_price):
        total_price = round(float(total_price), 2)
        try:
            nuat = PriceTariff.objects.filter(une_type=1)[:1].get()
            nuat_huvi = float(nuat.nuat_huvi if nuat.nuat_huvi else 10.0)
        except ObjectDoesNotExist:
            nuat = PriceTariff.objects.filter(une_type=0)[:1].get()
            nuat_huvi = float(nuat.nuat_huvi if nuat.nuat_huvi else 10.0)

        total_price = round(round(total_price * nuat_huvi, 2) / 100, 2) + total_price
        return round(total_price, 2)