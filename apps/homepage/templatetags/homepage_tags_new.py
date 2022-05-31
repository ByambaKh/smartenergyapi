from calendar import monthrange

from django import template
from django.core.exceptions import ObjectDoesNotExist

from apps.data.models import TooluurCustomer, PriceTariff, TooluurHistory, HasagdahHistory, CustomerUilchilgeeTulbur, \
    NiitiinHistory

register = template.Library()


@register.simple_tag
def flow_info(flow_id):
    try:
        if int(flow_id) > 0:
            tooluur_customer = TooluurCustomer.objects.filter(id=flow_id).first()
            return tooluur_customer
        else:
            return None
    except Exception as e:
        return None


@register.simple_tag
def make_float(arg1):
    if arg1:
        arg1 = float(arg1)
    else:
        arg1 = 0.0
    return round(arg1, 2)


@register.simple_tag
def divide(arg1, arg2):
    if arg1:
        arg1 = round(float(arg1), 2)
    else:
        arg1 = 0
    if arg2:
        arg2 = round(float(arg2), 2)
    else:
        arg2 = 0
    if float(arg1) == 0:
        return 0
    return round(arg1 / arg2, 2)


@register.simple_tag
def multiply(arg1, arg2):
    if arg1:
        arg1 = round(float(arg1), 2)
    else:
        arg1 = 0
    if arg2:
        arg2 = round(float(arg2), 2)
    else:
        arg2 = 0
    return round(arg1 * arg2, 2)


@register.simple_tag
def multiply_coef(arg1, arg2):
    if arg1:
        arg1 = round(float(arg1), 2)
    else:
        arg1 = 0
    if arg2:
        arg2 = round(float(arg2), 3)
    else:
        arg2 = 0
    return round(arg1 * arg2, 2)


@register.simple_tag
def append(arg1, arg2):
    if arg1:
        arg1 = round(float(arg1), 2)
    else:
        arg1 = 0.0
    if arg2:
        arg2 = round(float(arg2), 2)
    else:
        arg2 = 0.0
    return round(arg1 + arg2, 2)


@register.simple_tag
def append3(arg1, arg2, arg3):
    if arg1:
        arg1 = round(float(arg1), 2)
    else:
        arg1 = 0.0
    if arg2:
        arg2 = round(float(arg2), 2)
    else:
        arg2 = 0.0
    if arg3:
        arg3 = round(float(arg3), 2)
    else:
        arg3 = 0.0

    arg = round(round(arg1 + arg2, 2) + arg3, 2)
    return arg


@register.simple_tag
def reduce(arg1, arg2):
    if arg1:
        arg1 = round(float(arg1), 2)
    else:
        arg1 = 0.0
    if arg2:
        arg2 = round(float(arg2), 2)
    else:
        arg2 = 0.0
    return round(arg1 - arg2, 2)


@register.simple_tag
def return_same(arg1):
    return arg1


@register.simple_tag
def nuat(id, arg1):
    try:
        nuat = PriceTariff.objects.filter(id=id).first()
        if nuat is not None:
            nuat1 = round(float(arg1) * float(nuat.nuat_huvi), 2)
            nuat2 = round(nuat1 / 100, 2)
            return nuat2
        else:
            return 0
    except ObjectDoesNotExist:
        return 0


@register.simple_tag
def reduce_nuat(arg1):
    try:
        nuat = round(float(arg1) / 1.1, 2)
        nuat2 = round(float(nuat) * 0.1, 2)
        return nuat2
    except ObjectDoesNotExist:
        return 0


@register.simple_tag
def without_nuat(arg1):
    try:
        nuat = round(float(arg1) / 1.1, 2)
        return nuat
    except ObjectDoesNotExist:
        return 0


hasagdah_prices = []
@register.simple_tag
def set_hasagdah_prices(price):
    if price is None or price == '':
        price = 0
    hasagdah_prices.append(float(price))
    return ''


@register.simple_tag
def get_hasagdah_prices():
    price = 0
    for hasagdah_price in hasagdah_prices:
        price = round(hasagdah_price + price, 2)
    return float(price)

@register.simple_tag
def totalhasagdah(hasagdah_histories):
    price = 0
    try:
        for hasagdah in hasagdah_histories:
            price = round(hasagdah.day_diff_coef + hasagdah.night_diff_coef + price, 2)
        return float(price)
    except Exception:
        return 0

@register.simple_tag
def hasagdah(hasagdah):

    try:

        price = round(hasagdah.day_diff_coef + hasagdah.night_diff_coef, 2)
        return float(price)
    except Exception:
        return 0

@register.simple_tag
def del_hasagdah_prices():
    hasagdah_prices[:] = []
    return ''


@register.simple_tag
def aan_tooluurs(code, year, month):
    if code is not None and year is not None and month is not None:
        qry = """SELECT tohi.id, tohi.tariff, tohi.number,tl.name, tohi.day_balance_prev, tohi.day_balance, ROUND(tohi.guid_coef * tohi.huch_coef, 3) AS coef,
            tohi.night_balance_prev, tohi.night_balance, tohi.rush_balance_prev, tohi.rush_balance, prhi.day_price, prhi.night_price, prhi.rush_price,
            tohi.day_diff, tohi.day_diff_coef, tohi.night_diff, tohi.night_diff_coef, tohi.rush_diff, tohi.rush_diff_coef, tohi.total_diff, tohi.total_diff_coef,
            prhi.total_price, prhi.chadal_price, prta.chadal_une AS chadal_une, prhi.barimt_une, prhi.between_days, prhi.kosp,
            ROUND(prta.odor_une + prta.serg_une, 2) AS odor_une, ROUND(prta.shono_une + prta.serg_une, 2) AS shono_une,
            ROUND(prta.orgil_une + prta.serg_une, 2) AS orgil_une FROM data_tooluurhistory tohi
            JOIN data_pricehistory prhi ON tohi.customer_code = prhi.customer_code
            AND tohi.number = prhi.number AND prhi.year = '""" + year + """' AND prhi.month = '""" + month + """'
            JOIN data_pricetariff prta ON prhi.price_tariff_id = prta.id AND prta.is_active = '1'
            JOIN data_tooluur tl ON tohi.number = tl.number and tl.is_active = '1'
            WHERE tohi.year = '""" + year + """' AND tohi.month = '""" + month + """' AND tohi.customer_code = '""" + code + """'"""

        try:
            tooluurs = TooluurHistory.objects.raw(qry)
        except ObjectDoesNotExist:
            tooluurs = None
    else:
        tooluurs = None
    return tooluurs


@register.simple_tag
def hasagdah_tooluurs(code, year, month):
    qry = """"""

    try:
        tooluurs = HasagdahHistory.objects.raw(qry)
    except ObjectDoesNotExist:
        tooluurs = None

    return tooluurs


@register.simple_tag
def get_tulburt_uilchilgee(code, bich_date):
    if code is not None and bich_date is not None:
        year = str(bich_date)[:4]
        month = str(bich_date)[5:7]
        last_day = get_last_day(year, month)
        start_date = year + '-' + month + '-' + '01 00:00:00.000000'
        end_date = year + '-' + month + '-' + last_day + ' 23:59:59.999999'

        try:
            qry = """SELECT cuit.id, tuil.name, cuit.payment FROM data_customeruilchilgeetulbur cuit
                JOIN data_customer cust ON cuit.customer_id = cust.id
                JOIN data_tulburtuilchilgee tuil ON cuit.uilchilgee_id = tuil.id
                WHERE cuit.is_active = '1' AND cust.code = '""" + str(code) + """' AND
                cuit.created_date BETWEEN '""" + start_date + """' AND '""" + end_date + """'"""
            uilchilgee_tulburs = CustomerUilchilgeeTulbur.objects.raw(qry)
        except ObjectDoesNotExist:
            uilchilgee_tulburs = None
    else:
        uilchilgee_tulburs = None
    return uilchilgee_tulburs


@register.simple_tag
def get_niitiin(code, bich_date):
    if code is not None and bich_date is not None:
        year = str(bich_date)[:4]
        month = str(bich_date)[5:7]
        if month[0] == '0':
            month = month[1]

        try:
            qry = """SELECT niit.id, niit.ten_zuruu, niit.ten_price, niit.light_zuruu, niit.light_price,
                ROUND(prta.odor_une + prta.serg_une, 2) AS odor_une, prta.id AS price_id FROM data_niitiinhistory niit
                JOIN data_customer cust ON niit.customer_code = cust.code AND cust.is_active = '1'
                JOIN data_pricetariff prta ON niit.price_tariff_id = prta.id
                WHERE niit.is_active = '1' AND cust.code = '"""+code+"""' AND niit.year = '"""+year+"""' AND niit.month = '"""+month+"""'"""
            ten_light = NiitiinHistory.objects.raw(qry)
            if len(list(ten_light)) > 0:
                ten_light = list(ten_light)[0]
        except ObjectDoesNotExist:
            ten_light = None
    else:
        ten_light = None
    return ten_light


def get_last_day(the_year, the_month):
    month_last_day = str(monthrange(int(the_year), int(the_month))).split(',')
    month_last_day = str(month_last_day[1].replace(' ', '').replace(')', ''))
    return month_last_day


@register.simple_tag
def get_aan_barimt_une():
    try:
        aan_barimt_une = PriceTariff.objects.filter(une_type=0)[:1].get()
        return float(aan_barimt_une.barimt_une if aan_barimt_une.barimt_une else 0)
    except ObjectDoesNotExist:
        return 0.0