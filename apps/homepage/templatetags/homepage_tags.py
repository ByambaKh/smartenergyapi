from dateutil.relativedelta import relativedelta
from django import template
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from apps.data.models import ZaavarchilgaaUsers, DedStants, Shugam, Avlaga, PriceTariff, Bichilt, TooluurCustomer, \
    HasagdahTooluur, CustomerUilchilgeeTulbur, Address
from apps.homepage.viewz.bichilt_manager import BichiltManager
import datetime
register = template.Library()


@register.simple_tag
def get_position(id):
    try:
        user = User.objects.get(id=id)
        group = Group.objects.get(user=user)
        position = user.groups.get(id=group.id)
    except ObjectDoesNotExist:
        position = None

    return position.name if position else ''


@register.simple_tag
def get_position_id(id):
    try:
        user = User.objects.get(id=id)
        group = Group.objects.get(user=user)
    except ObjectDoesNotExist:
        group = None

    return int(group.id) if group else 0


@register.simple_tag
def get_first_last_name(id):
    try:
        user_name = ''
        if str(id) != '':
            id = int(id)
            user = User.objects.filter(id=id).first()
            user_name = user.last_name + ' ' + user.first_name
    except ObjectDoesNotExist:
        user_name = ''

    return user_name


@register.simple_tag
def get_address(id):
    result = ''
    if id:
        address = Address.objects.filter(customer_id=int(id)).order_by('-created_date').first()
        if address is not None:
            result = address.address_name
    return result

# @register.simple_tag
# def get_code_by_pahi(pahi_id):
#     try:
#         cust_code = str(PaymentHistory.objects.filter(id=pahi_id).first().customer.code)
#     except ObjectDoesNotExist:
#         cust_code = ''
#
#     return cust_code


@register.simple_tag
def get_zaavar_taniltssan_eseh(ashiglalt_zaavar_id, user_id):
    try:
        zaavarchilgaa_user = ZaavarchilgaaUsers.objects.get(ashiglalt_zaavar_id=ashiglalt_zaavar_id, user_id=user_id)
    except ObjectDoesNotExist:
        zaavarchilgaa_user = None

    return zaavarchilgaa_user.taniltssan_eseh if zaavarchilgaa_user else 0


@register.simple_tag
def all_zaavar_taniltssan_eseh(ashiglalt_zaavar_id):
    taniltssan_eseh = 0
    try:
        taniltssan_count = 0
        zaavarchilgaa_users = ZaavarchilgaaUsers.objects.filter(ashiglalt_zaavar_id=ashiglalt_zaavar_id)
        for zaavarchilgaa_user in zaavarchilgaa_users:
            taniltssan_count += int(zaavarchilgaa_user.taniltssan_eseh)
        if zaavarchilgaa_users.count() == taniltssan_count:
            taniltssan_eseh = 1
    except ObjectDoesNotExist:
        zaavarchilgaa_user = None
    return taniltssan_eseh


@register.simple_tag
def get_current_season():
    month = datetime.datetime.today().strftime("%m")

    if int(month) >= 1 and int(month) <= 3:
        return 1
    if int(month) >= 4 and int(month) <= 6:
        return 2
    if int(month) >= 7 and int(month) <= 9:
        return 3
    if int(month) >= 10 and int(month) <= 12:
        return 4


@register.simple_tag
def get_dedstants_name(id):
    try:
        ded_stants = DedStants.objects.get(id=id)
        return ded_stants.name
    except ObjectDoesNotExist:
        return ''


@register.simple_tag
def divide(arg1, arg2):
    if float(arg1) == 0 or float(arg2) == 0:
        return 0
    if arg1:
        arg1 = round(float(arg1), 2)
    else:
        arg1 = 0
    if arg2:
        arg2 = round(float(arg2), 2)
    else:
        arg2 = 0
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
def make_float(arg1):
    if arg1:
        arg1 = float(arg1)
    else:
        arg1 = 0.0
    return round(arg1, 2)

@register.simple_tag
def make_int(arg1):
    if arg1:
        arg1 = int(arg1)
    else:
        arg1 = 0
    return round(arg1, 2)

@register.simple_tag
def make_str(arg1):
    if arg1:
        arg1 = str(arg1)
    else:
        arg1 = ''
    return arg1

@register.simple_tag
def date_str(arg1):
    if arg1:
        arg1 = str(arg1)[:10]
    else:
        arg1 = ''
    return arg1

@register.simple_tag
def return_same(arg1):
    return arg1

@register.simple_tag
def item_by_index(list, i):
    return list[int(i-1)]

@register.simple_tag
def get_shugam_by_ded(id):
    try:
        return Shugam.objects.filter(is_active='1').filter(ded_stants_id=id)
    except ObjectDoesNotExist:
        return None

ann_detail_dates = []
@register.simple_tag
def set_aan_detail_date(date):
    is_have = False

    if date is not None and date != '':
        if len(ann_detail_dates) > 0:
            for ann_detail_date in ann_detail_dates:
                if ann_detail_date == date[:4] + date[5:7]:
                    is_have = False
                else:
                    is_have = True

        if not is_have:
            ann_detail_dates.append(date[:4] + date[5:7])
    return ''

@register.simple_tag
def get_aan_detail_date():
    if len(ann_detail_dates) >= 2:
        return '1'
    else:
        return '0'

@register.simple_tag
def del_aan_detail_date():
    ann_detail_dates[:] = []
    return ''

each_tool_prices = []
@register.simple_tag
def each_tool_price(price):
    if price is None or price == '':
        price = 0
    each_tool_prices.append(round(float(price), 2))
    return ''

@register.simple_tag
def get_all_tool_price():
    price = 0
    for each_tool_price in each_tool_prices:
        price += each_tool_price
    each_tool_prices[:] = []
    return round(price, 2)

print_datas = []
@register.simple_tag
def set_print_datas(last_name, first_name, address, code, toot, tulbur, bichilt, building_number, phone, email):
    temp_dic = {'last_name': last_name if last_name is not None else '',
                'first_name': first_name,
                'address': address if address is not None else '',
                'code': code,
                'toot': toot if toot is not None else '',
                'tulbur': tulbur,
                'bichilt': float(bichilt),
                'building_number': building_number if building_number is not None else '',
                'phone': phone if phone is not None else '',
                'email': email if email is not None else ''}
    print_datas.append(temp_dic)
    return ''

@register.simple_tag
def get_print_datas():
    return print_datas

@register.simple_tag
def del_print_datas():
    print_datas[:] = []
    return ''

each_tool_diffs = []
@register.simple_tag
def each_tool_diff(diff):
    if diff is None or diff == '':
        diff = 0.0
    each_tool_diffs.append(round(float(diff), 2))
    return ''

@register.simple_tag
def get_all_tool_diff():
    diff = 0
    for each_tool_diff in each_tool_diffs:
        diff = diff + each_tool_diff
    each_tool_diffs[:] = []
    return round(diff, 2)

each_tool_kvts = []
@register.simple_tag
def each_tool_kvt(diff):
    if diff is None or diff == '':
        diff = 0.0
    each_tool_kvts.append(round(float(diff), 2))
    return ''

@register.simple_tag
def get_all_tool_kvt():
    diff = 0
    for each_tool_kvt in each_tool_kvts:
        diff = diff + each_tool_kvt
    each_tool_kvts[:] = []
    return round(diff, 2)

each_tool_chad_prices = []
@register.simple_tag
def each_tool_chad_price(price):
    if price is None or price == '':
        price = 0
    each_tool_chad_prices.append(round(float(price), 2))
    return ''

@register.simple_tag
def get_all_tool_chad_price():
    price = 0
    for each_tool_chad_price in each_tool_chad_prices:
        price = price + each_tool_chad_price
    each_tool_chad_prices[:] = []
    return round(price, 2)

each_rush_tool_diffs = []
@register.simple_tag
def each_rush_tool_diff(diff):
    if diff is None or diff == '':
        diff = 0.0
    each_rush_tool_diffs.append(round(float(diff), 2))
    return ''

@register.simple_tag
def get_all_rush_tool_diff():
    diff = 0
    for each_rush_tool_diff in each_rush_tool_diffs:
        diff += each_rush_tool_diff
    each_rush_tool_diffs[:] = []
    return round(diff, 2)

each_ch_rush_tool_diffs = []
@register.simple_tag
def each_ch_rush_tool_diff(diff):
    if diff is None or diff == '':
        diff = 0.0
    each_ch_rush_tool_diffs.append(round(float(diff), 2))
    return ''

@register.simple_tag
def get_all_ch_rush_tool_diff():
    diff = 0
    for each_ch_rush_tool_diff in each_ch_rush_tool_diffs:
        diff += each_ch_rush_tool_diff
    each_ch_rush_tool_diffs[:] = []
    return round(diff, 2)


b_tool_num = []
b_tool_zaalt = []
@register.simple_tag
def set_before_tooluurs(number, day_odoo, day_umnu, coef):
    b_tool_num.append(str(number))
    b_tool_zaalt.append(round(round((float(day_odoo) - float(day_umnu)), 2) * round(float(coef), 3)))
    return ''

@register.simple_tag
def get_before_tooluurs(number):
    if len(b_tool_num) > 0:
        i = b_tool_num.index(str(number)) if number in b_tool_num else 0
        return float(b_tool_zaalt[i])
    return ''

@register.simple_tag
def del_before_tooluurs():
    b_tool_num[:] = []
    b_tool_zaalt[:] = []
    return ''

b_ch_tool_num = []
b_ch_tool_zaalt = []
@register.simple_tag
def set_before_child_tooluurs(number, day_odoo, day_umnu, coef):
    if day_odoo != '' and day_umnu != '' and day_odoo is not None and day_umnu is not None:
        b_ch_tool_num.append(str(number))
        b_ch_tool_zaalt.append(round(round((float(day_odoo) - float(day_umnu)), 2) * round(float(coef), 2)))
    return ''

@register.simple_tag
def get_before_child_tooluurs(number):
    if len(b_tool_num) > 0:
        i = b_ch_tool_num.index(str(number)) if str(number) in b_ch_tool_num else None
        return float(b_ch_tool_zaalt[i]) if i is not None else 0
    return ''

@register.simple_tag
def del_before_tooluurs():
    b_tool_num[:] = []
    b_tool_zaalt[:] = []
    return ''

@register.simple_tag
def del_before_child_tooluurs():
    b_ch_tool_num[:] = []
    b_ch_tool_zaalt[:] = []
    return ''

bef_bich_date = []
@register.simple_tag
def set_bef_bich_date(b_date):
    bef_bich_date.append(str(b_date)[:10])
    return ''

@register.simple_tag
def get_bef_bich_date():
    if len(bef_bich_date) > 1:
        return bef_bich_date[0]
    return ''

@register.simple_tag
def del_bef_bich_date():
    bef_bich_date[:] = []
    return ''

bichilt_prices = []
@register.simple_tag
def set_bichilt_prices(price):
    if price is None or price == '':
        price = 0
    bichilt_prices.append(round(float(price), 2))
    return ''

@register.simple_tag
def get_bichilt_prices():
    price = 0
    for bichilt_price in bichilt_prices:
        price += bichilt_price
    bichilt_prices[:] = []
    return round(price, 2)

uilchilgee_prices = []
@register.simple_tag
def set_uilchilgee_prices(price):
    if price is None or price == '':
        price = 0
    uilchilgee_prices.append(round(float(price), 2))
    return ''

@register.simple_tag
def get_uilchilgee_prices():
    price = 0
    for uilchilgee_price in uilchilgee_prices:
        price += uilchilgee_price
    uilchilgee_prices[:] = []
    return round(price, 2)

orlogo_prices = []
@register.simple_tag
def set_orlogo_prices(price):
    if price is None or price == '':
        price = 0
    orlogo_prices.append(round(float(price), 2))
    return ''

@register.simple_tag
def get_orlogo_prices():
    price = 0
    for orlogo_price in orlogo_prices:
        price += orlogo_price
    orlogo_prices[:] = []
    return round(price, 2)

total_diff = []
@register.simple_tag
def set_total_diff(diff):
    if diff is None or diff == '':
        diff = 0
    total_diff.append(float(diff))
    return ''

@register.simple_tag
def get_total_diff():
    t_diff = 0
    for total in total_diff:
        t_diff += total
    return float(t_diff)

@register.simple_tag
def del_total_diff():
    total_diff[:] = []
    return ''

tulburts = []
@register.simple_tag
def set_tulburt_une(une):
    if une is None or une == '':
        une = 0
    tulburts.append(float(une))
    return ''

@register.simple_tag
def get_tulburt_une():
    t_une = 0
    for tulburt in tulburts:
        t_une += tulburt
    return float(t_une)

@register.simple_tag
def del_tulburt_une():
    tulburts[:] = []
    return ''

@register.simple_tag
def minus_1months(today):
    minus_month = today + relativedelta(months=-1)
    return str(minus_month)[:8] + '01'

@register.simple_tag
def get_2days_diff(start_date, end_date):
    if str(end_date)[:10] == '2017-08-25':
        if get_bef_bich_date() == '2017-07-25':
            return 31
        if get_bef_bich_date() == '2017-07-26':
            return 30

    if end_date != '' and end_date is not None:
        if start_date is None:
            start_date = end_date + relativedelta(months=-1)
            start_date = start_date.date()
            # start_date = parse_date('2017-08-25')
            end_date = end_date.date()
        diff_days = abs(end_date - start_date).days

        return diff_days
    else:
        return 1

@register.simple_tag
def get_day_balances(customer_code, start_date, end_date):
    aan_balances = {}
    day_total_balance = 0
    day_total_kvt = 0
    day_total = 0
    day_total_serg = 0

    qry = "SELECT avla.id, tool.tariff, tool.number, tran.multiply_coef, IFNULL(day_prev.day_balance, tool.balance_value) AS day_umnu, day_now.day_balance AS day_odoo," \
          " ABS(day_now.day_balance - IFNULL(day_prev.day_balance, tool.balance_value)) AS zuruu FROM data_avlaga avla" \
          " JOIN data_bichilt day_now ON avla.id=day_now.avlaga_id" \
          " LEFT JOIN data_bichilt day_prev ON day_now.prev_bichilt_id=day_prev.id" \
          " JOIN data_tooluurcustomer tocu ON avla.customer_id=tocu.customer_id" \
          " JOIN data_tooluur tool ON tocu.tooluur_id=tool.id" \
          " JOIN data_transformator tran ON tocu.guidliin_trans_id=tran.id" \
          " WHERE avla.is_active='1' AND tocu.is_active='1' AND tool.is_active='1' AND" \
          " tocu.customer_code='"+customer_code+"' AND avla.created_date>='"+start_date+"' AND avla.created_date<='"+end_date+"'"
    try:
        day_balances = Bichilt.objects.raw(qry)
        for day_balance in day_balances:
            day_total_balance += round(float(day_balance.zuruu), 2)
            day_total_kvt += round(float(day_balance.zuruu) * float(day_balance.multiply_coef), 2)
            day_total += round(float(day_balance.zuruu) * float(day_balance.multiply_coef) * get_aan_udur_une(), 2)
            day_total_serg += round(float(day_balance.zuruu) * get_aan_serg_une(), 2)
    except ObjectDoesNotExist:
        day_balances = None

    aan_balances['day_balances'] = day_balances
    aan_balances['day_total_balance'] = day_total_balance
    aan_balances['day_total_kvt'] = day_total_kvt
    aan_balances['day_total'] = day_total
    aan_balances['day_total_serg'] = day_total_serg
    return aan_balances

@register.simple_tag
def get_barimt(customer_code, start_date, end_date):
    qry = """SELECT avla.id, cust.code, cust.first_name, cust.last_name, cust.register, tool.number, tool.tariff, addr.address_name,
        IFNULL(day_umnu.day_balance, tool.balance_value) AS day_umnu, day_odoo.day_balance AS day_odoo, IFNULL(night_odoo.night_balance, tool.balance_value) AS night_odoo, deds.name AS ded_stants_name,
        night_umnu.night_balance AS night_umnu, cust.customer_angilal FROM data_avlaga avla
        JOIN data_tooluurcustomer tocu ON avla.customer_id=tocu.customer_id
        JOIN data_customer cust ON tocu.customer_id=cust.id
        JOIN data_tooluur tool ON tocu.tooluur_id=tool.id
        JOIN data_address addr ON cust.id=addr.customer_id
        JOIN data_bichilt day_odoo ON avla.id=day_odoo.avlaga_id
        LEFT JOIN data_bichilt day_umnu ON day_odoo.prev_bichilt_id=day_umnu.id
        JOIN data_bichilt night_odoo ON avla.id=night_odoo.avlaga_id
        LEFT JOIN data_bichilt night_umnu ON night_odoo.prev_bichilt_id=night_umnu.id
        LEFT JOIN data_dedstants deds ON tocu.dedstants_id=deds.id
        WHERE avla.is_active='1' AND cust.is_active='1' AND (avla.created_date BETWEEN '"""+start_date+"""' AND '"""+end_date+"""') AND cust.code='"""+customer_code+"""'"""

    try:
        avlaga_barimt = Avlaga.objects.raw(qry)
    except ObjectDoesNotExist:
        avlaga_barimt = None
    return avlaga_barimt

@register.simple_tag
def check_next_barimt(customer_code, start_date, end_date):
    barimts = list(get_barimt(customer_code, start_date, end_date))
    if len(barimts) > 1:
        return True
    else:
        return False

@register.simple_tag
def get_total_balance(customer_code, start_date, end_date):
    total_balance = 0
    barimts = get_barimt(customer_code, start_date, end_date)
    if barimts:
        for barimt in barimts:
            result1 = round(float(barimt.day_odoo if barimt.day_odoo else 0), 2) - round(float(barimt.day_umnu if barimt.day_umnu else 0), 2)
            result2 = round(float(barimt.night_odoo if barimt.night_odoo else 0), 2) - round(float(barimt.night_umnu if barimt.night_umnu else 0), 2)
            total_balance += result1 + result2
        return round(total_balance, 2)
    else:
        return 0

@register.simple_tag
def get_ahuin_udur_une():
    try:
        ahuin_udur_une = PriceTariff.objects.filter(une_type=1)[:1].get()
        total_ahuin_udur_une = float(ahuin_udur_une.low_limit_price if ahuin_udur_une.low_limit_price else 0) + float(ahuin_udur_une.serg_une if ahuin_udur_une.serg_une else 0)
        return round(total_ahuin_udur_une, 2)
    except ObjectDoesNotExist:
        return 0.0

@register.simple_tag
def get_ahuin_udur_une_tariff2():
    try:
        ahuin_udur_une = PriceTariff.objects.filter(une_type=1)[:1].get()
        total_ahuin_udur_une_tariff2 = float(ahuin_udur_une.odor_une if ahuin_udur_une.odor_une else 0) + float(ahuin_udur_une.serg_une if ahuin_udur_une.serg_une else 0)
        return round(total_ahuin_udur_une_tariff2, 2)
    except ObjectDoesNotExist:
        return 0.0

@register.simple_tag
def get_ahuin_udur_une_high():
    try:
        ahuin_udur_une = PriceTariff.objects.filter(une_type=1)[:1].get()
        total_ahuin_udur_une_high = float(ahuin_udur_une.high_limit_price if ahuin_udur_une.high_limit_price else 0) + float(ahuin_udur_une.serg_une if ahuin_udur_une.serg_une else 0)
        return round(total_ahuin_udur_une_high, 2)
    except ObjectDoesNotExist:
        return 0.0

@register.simple_tag
def get_ahuin_shunu_une():
    try:
        ahuin_shunu_une = PriceTariff.objects.filter(une_type=1)[:1].get()
        total_ahuin_shunu_une = float(ahuin_shunu_une.shono_une if ahuin_shunu_une.shono_une else 0) + float(ahuin_shunu_une.serg_une if ahuin_shunu_une.serg_une else 0)
        return round(total_ahuin_shunu_une, 2)
    except ObjectDoesNotExist:
        return 0.0

@register.simple_tag
def get_ahuin_orgil_une():
    try:
        ahuin_orgil_une = PriceTariff.objects.filter(une_type=1)[:1].get()
        return float(ahuin_orgil_une.orgil_une if ahuin_orgil_une.orgil_une else 0)
    except ObjectDoesNotExist:
        return 0.0

@register.simple_tag
def get_ahuin_high_une():
    try:
        ahuin_high_une = PriceTariff.objects.filter(une_type=1)[:1].get()
        return float(ahuin_high_une.high_limit_price if ahuin_high_une.high_limit_price else 0)
    except ObjectDoesNotExist:
        return 0.0

@register.simple_tag
def get_ahui_serg_une():
    try:
        ahui_serg_une = PriceTariff.objects.filter(une_type=1)[:1].get()
        return float(ahui_serg_une.serg_une if ahui_serg_une.serg_une else 0)
    except ObjectDoesNotExist:
        return 0.0

@register.simple_tag
def new_ahui_suuri_une(id):
    try:
        bich = Bichilt.objects.filter(id=id).first()
        if bich is not None:
            return float(bich.suuri_price) / 1.1
        else:
            return 0.0
    except ObjectDoesNotExist:
        return 0.0

@register.simple_tag
def get_ahui_suuri_une():
    try:
        ahui_suuri_une = PriceTariff.objects.filter(une_type=1)[:1].get()
        return float(ahui_suuri_une.suuri_une if ahui_suuri_une.suuri_une else 0)
    except ObjectDoesNotExist:
        return 0.0

@register.simple_tag
def get_ahui_barimt_une():
    try:
        ahui_barimt_une = PriceTariff.objects.filter(une_type=1)[:1].get()
        return float(ahui_barimt_une.barimt_une if ahui_barimt_une.barimt_une else 0)
    except ObjectDoesNotExist:
        return 0.0

@register.simple_tag
def get_aan_udur_une():
    try:
        aan_udur_une = PriceTariff.objects.filter(une_type=0)[:1].get()
        return float(aan_udur_une.odor_une if aan_udur_une.odor_une else 0) + get_aan_serg_une()
    except ObjectDoesNotExist:
        return 0.0


@register.simple_tag
def get_aan_shunu_une():
    try:
        aan_shunu_une = PriceTariff.objects.filter(une_type=0)[:1].get()
        return float(aan_shunu_une.shono_une if aan_shunu_une.shono_une else 0) + get_aan_serg_une()
    except ObjectDoesNotExist:
        return 0.0

@register.simple_tag
def get_aan_orgil_une():
    try:
        aan_orgil_une = PriceTariff.objects.filter(une_type=0)[:1].get()
        return float(aan_orgil_une.orgil_une if aan_orgil_une.orgil_une else 0) + get_aan_serg_une()
    except ObjectDoesNotExist:
        return 0.0

@register.simple_tag
def get_aan_high_une():
    try:
        aan_high_une = PriceTariff.objects.filter(une_type=0)[:1].get()
        return float(aan_high_une.high_limit_price if aan_high_une.high_limit_price else 0)
    except ObjectDoesNotExist:
        return 0.0

@register.simple_tag
def get_aan_serg_une():
    try:
        aan_high_une = PriceTariff.objects.filter(une_type=0)[:1].get()
        return float(aan_high_une.serg_une if aan_high_une.serg_une else 0)
    except ObjectDoesNotExist:
        return 0.0

@register.simple_tag
def get_aan_chad_une(day_diff):
    if day_diff:
        day_diff = float(day_diff)

        try:
            aan_chad_une = PriceTariff.objects.filter(une_type=0)[:1].get()
            aan_chad_une = float(aan_chad_une.chadal_une if aan_chad_une.chadal_une else 0.00)
        except ObjectDoesNotExist:
            aan_chad_une = 0.00

        if int(day_diff) <= 27:
            aan_chad_une = round(round(aan_chad_une / 30, 2) * day_diff, 2)

        return aan_chad_une
    else:
        return 0.00

@register.simple_tag
def get_aan_barimt_une():
    try:
        aan_barimt_une = PriceTariff.objects.filter(une_type=0)[:1].get()
        return float(aan_barimt_une.barimt_une if aan_barimt_une.barimt_une else 0)
    except ObjectDoesNotExist:
        return 0.0


@register.simple_tag
def return_nuat(arg1):
    try:
        nuat = PriceTariff.objects.filter(une_type=0)[:1].get()
        nuat1 = round(float(arg1) * float(nuat.nuat_huvi), 2)
        nuat2 = round(nuat1 / 100, 2)
        return nuat2
    except ObjectDoesNotExist:
        return 0


@register.simple_tag
def get_ahui_ald_huvi():
    try:
        aan_barimt_une = PriceTariff.objects.filter(une_type=1)[:1].get()
        return float(aan_barimt_une.ald_huvi if aan_barimt_une.ald_huvi else 0)
    except ObjectDoesNotExist:
        return 0


@register.simple_tag
def get_aldangi(code):
    qry = "SELECT avla.id, avla.tulbur_date, avla.pay_uld, avla.ald_huvi FROM data_avlaga avla" \
          " JOIN data_customer cust ON avla.customer_id = cust.id" \
          " WHERE tulbur_date <= CURDATE() AND pay_type = '0' AND cust.code = '"+str(code)+"';"

    try:
        aldangi = Avlaga.objects.raw(qry)
        if len(aldangi) > 0:
            aldangi = aldangi[0]
    except ObjectDoesNotExist:
        aldangi = None

    bm = BichiltManager()
    ald = 0

    if aldangi is not None:
        days = (datetime.datetime.now() - aldangi.tulbur_date).days
        if days > 0:
            ald = round(float(aldangi.pay_uld), 2) / round(float(days), 2) / float(aldangi.ald_huvi)
    return bm.add_nuat_price(ald)


@register.simple_tag
def get_customer_tooluurs(code, bichilt_date):
    bichilt_date = make_str(bichilt_date)

    qry = "SELECT tocu.id, tool.number, odoo.chadal_price, tool.tariff, umnu.bichilt_date AS u_bichilt_date, odoo.bichilt_date AS o_bichilt_date, deds.name AS deds_name, bank.name AS bank_name, bank.dans AS bank_dans, cust.customer_type," \
          " IFNULL(umnu.day_balance, umum.balance_value) AS day_umnu, IFNULL(umnu.night_balance, umum.balance_value_night) AS night_umnu," \
          " IFNULL(umnu.rush_balance, umum.balance_value_rush) AS rush_umnu, IFNULL(odoo.day_balance, umnu.day_balance) AS day_odoo," \
          " IFNULL(odoo.night_balance, umnu.night_balance) AS night_odoo, IFNULL(odoo.rush_balance, umnu.rush_balance) AS rush_odoo," \
          " IFNULL(odoo.day_diff, 0.0) AS day_diff, IFNULL(odoo.night_diff, 0.0) AS night_diff, IFNULL(odoo.rush_diff, 0.0) AS rush_diff, IFNULL(odoo.total_diff, 0.0) AS total_diff," \
          " (IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) AS coef" \
          " FROM data_tooluurcustomer tocu JOIN data_tooluur tool ON tocu.tooluur_id = tool.id JOIN data_customer cust ON tocu.customer_id = cust.id" \
          " LEFT JOIN data_bichilt odoo ON tocu.id = odoo.tooluur_id LEFT JOIN data_bichilt umnu ON odoo.prev_bichilt_id = umnu.id" \
          " LEFT JOIN data_tooluur umum ON tocu.tooluur_id = umum.id LEFT JOIN data_transformator guid ON tocu.guidliin_trans_id = guid.id" \
          " LEFT JOIN data_transformator huch ON tocu.huchdeliin_trans_id = huch.id" \
          " LEFT JOIN data_geree gere ON gere.customer_code = tocu.customer_code LEFT JOIN data_dedstants deds ON deds.code = gere.dedstants_code" \
          " LEFT JOIN data_bank bank ON bank.code = gere.bank_code" \
          " WHERE odoo.bichilt_date = '"+bichilt_date+"' AND tocu.is_active = '1' AND tocu.customer_code = '"+code+"'"
    try:
        tooluurs = TooluurCustomer.objects.raw(qry)
    except ObjectDoesNotExist:
        tooluurs = None

    return tooluurs


@register.simple_tag
def get_hasagdah_tooluurs(code, bichilt_date):
    bichilt_date = make_str(bichilt_date)

    try:
        qry = """SELECT bich.id, tool.number, tool.tariff, avla.uilchilgeenii_tulbur, umnu.day_balance AS umnu_day, umnu.night_balance AS umnu_night, umnu.rush_balance AS umnu_rush,
            bich.day_balance AS odoo_day, bich.night_balance AS odoo_night, bich.rush_balance AS odoo_rush, umnu.bichilt_date AS u_bichilt_date, bich.bichilt_date AS o_bichilt_date,
            bich.day_diff AS day_diff, bich.night_diff AS night_diff, bich.rush_diff AS rush_diff,
            (IFNULL(guid.multiply_coef, 1) * IFNULL(huch.multiply_coef, 1)) AS coef FROM data_bichilt bich
            JOIN data_tooluurcustomer tocu ON bich.tooluur_id = tocu.id JOIN data_tooluur tool ON tocu.tooluur_id = tool.id
            LEFT JOIN data_transformator guid ON tocu.guidliin_trans_id = guid.id
            LEFT JOIN data_transformator huch ON tocu.huchdeliin_trans_id = huch.id
            LEFT JOIN data_bichilt umnu ON umnu.id = bich.prev_bichilt_id LEFT JOIN data_avlaga avla ON bich.avlaga_id = avla.id
            WHERE bich.bichilt_date = '""" + bichilt_date + """'
            AND bich.tooluur_id IN (SELECT hasa.child_tool_cus_id FROM data_hasagdahtooluur hasa JOIN data_tooluurcustomer tocu ON
            tocu.id = hasa.head_tool_cus_id WHERE tocu.customer_code = '""" + str(code) + """') GROUP BY tocu.id"""

        child_tooluurs = Bichilt.objects.raw(qry)
    except Exception as e:
        print("Exception : %s" % e)
        child_tooluurs = None
    return child_tooluurs


@register.simple_tag
def get_head_diff(tocu_id, o_bichilt_date):
    try:
        hasagdah = HasagdahTooluur.objects.filter(head_tool_cus_id=tocu_id)
        if hasagdah.first() is not None:
            if hasagdah.first().head_tool_cus2_id is None:
                bichilt = Bichilt.objects.filter(tooluur=hasagdah.first().head_tool_cus, bichilt_date=o_bichilt_date).first()

                if bichilt is not None:
                    head_guid_coef = 1
                    head_huch_coef = 1

                    if hasagdah.first().head_tool_cus.guidliin_trans is not None and hasagdah.first().head_tool_cus.guidliin_trans != '':
                        head_guid_coef = float(hasagdah.first().head_tool_cus.guidliin_trans.multiply_coef)
                    if hasagdah.first().head_tool_cus.huchdeliin_trans is not None and hasagdah.first().head_tool_cus.huchdeliin_trans != '':
                        head_huch_coef = float(hasagdah.first().head_tool_cus.huchdeliin_trans.multiply_coef)

                    head_day_diffs = float(bichilt.day_diff) * head_huch_coef * head_guid_coef
                    ch_tocu_ids = hasagdah.values_list('child_tool_cus_id', flat=True)
                    ch_bichilts = Bichilt.objects.filter(tooluur_id__in=ch_tocu_ids, bichilt_date=o_bichilt_date)

                    child_day_diffs = 0
                    for ch_bichilt in ch_bichilts:
                        if ch_bichilt.tooluur.tooluur.tariff == '0':
                            child_day_diffs += float(ch_bichilt.day_diff)
                    return head_day_diffs - child_day_diffs
        else:
            ch_bichilt = Bichilt.objects.filter(tooluur_id=tocu_id, bichilt_date=o_bichilt_date).first()
            return float(ch_bichilt.day_diff)
    except ObjectDoesNotExist:
        return 0


@register.simple_tag
def get_tulburt_uilchilgee(code, bich_date):
    year = str(bich_date)[:4]
    month = str(bich_date)[5:7]
    if month[0] == '0':
        month = month[1]
    try:
        qry = """SELECT cuit.id, tuil.name, cuit.payment FROM data_customeruilchilgeetulbur cuit
            JOIN data_customer cust ON cuit.customer_id = cust.id
            JOIN data_tulburtuilchilgee tuil ON cuit.uilchilgee_id = tuil.id
            WHERE cuit.is_active = '1' AND cust.code = '"""+str(code)+"""' AND cuit.year = '"""+year+"""' AND cuit.month = '"""+month+"""'"""
        uilchilgee_tulburs = CustomerUilchilgeeTulbur.objects.raw(qry)
    except ObjectDoesNotExist:
        uilchilgee_tulburs = None
    return uilchilgee_tulburs


@register.simple_tag
def return_year_month(dates):
    date = {}
    date['year'] = int(str(dates)[:4])
    date['month'] = int(str(dates)[5:7])
    return date


# @register.simple_tag
# def update_avlaga(avlaga_id, total_price, uil_tulbur):
#     print("avlaga_id : " + str(avlaga_id))
#     print("total_price : " + str(total_price))
#     print("uil_tulbur : " + str(uil_tulbur))
#
#     if avlaga_id is not None:
#         avlaga = Avlaga.objects.filter(id=int(avlaga_id)).first()
#         print("avlaga id : " + str(avlaga.id))
#         if uil_tulbur is not None:
#             if str(uil_tulbur) != '':
#                 if int(total_price) > 0:
#                     avlaga.uilchilgeenii_tulbur = Decimal(uil_tulbur)
#         if str(total_price) != '':
#             if int(total_price) > 0:
#                 avlaga.heregleenii_tulbur = Decimal(total_price) - Decimal(avlaga.barimt_une)
#         if avlaga is not None:
#             avlaga.save()
#
#     return ''