import calendar
import datetime
from apps.data.models import *


def getPayDate(TooluurCustomer, year, month):
    geree = Geree.objects.filter(customer_code=TooluurCustomer.customer_code, is_active='1').first()
    cycle = Cycle.objects.filter(code=geree.cycle_code).first()

    tulbur_tuluh = str(cycle.tulbur_tuluh)

    if cycle.code == '9' or cycle.code == '10':
        if month < 12:
            month = month + 1
        else:
            month = 1
            year += 1

    if month == 2 and (cycle.code == '7' or cycle.code == '8'):
        last_day = get_last_day(year, month)
        if int(last_day) == 28:
            tulbur_tuluh = '02'
        else:
            tulbur_tuluh = '01'
        month = 3

    pay_day = datetime.datetime.strptime(str(year)+'-'+str(month)+'-'+tulbur_tuluh, '%Y-%m-%d')

    return pay_day


def get_last_day(year, month):
    month_last_day = str(calendar.monthrange(int(year), int(month))).split(',')
    month_last_day = str(month_last_day[1].replace(' ', '').replace(')', ''))
    return month_last_day