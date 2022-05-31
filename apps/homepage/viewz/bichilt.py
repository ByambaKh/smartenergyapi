# coding=utf-8
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import simplejson
from apps.homepage.viewz.bichilt_manager import *
from apps.homepage.viewz.services.posapi import PosapiMTA
from mcsi.utils import *
import xlwt
from django.contrib import messages
from apps.extra import *


class BichiltList(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = 'homepage/borluulalt/bichilt.html'
    login_url = '/home/index'
    permission_required = 'data.view_bichilt'

    q_bichilt_list = """
        SELECT bi.bichilt_date, bi.id, bi.day_balance, bi.night_balance, bi.rush_balance, bi.year, bi.month,
        bi.type, tol.number, cu.first_name, cu.last_name, cu.code, cu.customer_angilal, bi.sergeegdeh_price, bi.chadal_price,
        bi.hereglee_price, bi.suuri_price, bi.total_diff, bi.total_price
        FROM data_bichilt AS bi INNER JOIN data_tooluurcustomer AS to_cu ON bi.tooluur_id=to_cu.id
        JOIN data_customer AS cu ON to_cu.customer_id=cu.id
        JOIN data_tooluur AS tol ON to_cu.tooluur_id=tol.id """
    individual_bichilts = None
    substation_bichilts = None
    menu = "3"
    sub = "2"
    posapi = PosapiMTA()

    def get(self, request, activeTab, *args, **kwargs):
        page = request.GET.get('page', 1)

        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        if now.day < 25:
            if now.month == 1:
                now = now.replace(year=now.year - 1)
                now = now.replace(month=12)
            else:
                now = now.replace(month=now.month-1)
        else:
            now = now.replace(day=1)
        start_date = now.strftime("%Y-%m-%d")

        par0 = {"is_active": "1", "user_type": "1", "bichilt_date__range": (start_date, current_date)}
        # datas = Bichilt.objects.filter(**par0)

        par1 = {"is_active": "1", "user_type": "0", "bichilt_date__range":(start_date, current_date)}
        # ded_stants = Bichilt.objects.filter(**par1)

        par2 = {"is_active": "1", "user_type": "2", "bichilt_date__range": (start_date, current_date)}
        # bair = Bichilt.objects.filter(**par2)

        # BichiltList.individual_bichilts = datas
        # BichiltList.substation_bichilts = ded_stants
        staff_users = UserProfile.objects.filter(is_active=1)
        duureg = Duureg.objects.filter(is_active=1)

        # tooluur_ids_bichilts = datas.values_list('tooluur_id', flat=True)
        par3 = {"is_active": "1", "customer_angilal": "1"}
        # not_bichilts_list = TooluurCustomer.objects.filter(**par3).filter(~Q(id__in=tooluur_ids_bichilts))

        cycles = Cycle.objects.filter(is_active='1')

        data = {
            # "data_bichilt": datas,
            "start_date": start_date,
            "end_date": current_date,
            # "data_dedstants": ded_stants,
            # "data_bair": bair,
            "menu": self.menu,
            "sub": self.sub,
            "activeTab": str(activeTab),
            "created_users": staff_users,
            "duuregs": duureg,
            "cycles" : cycles,
            # "not_bichilts": not_bichilts_list,
            # "page_range": page_range
        }
        return render(request, self.template_name, data)

    def post(self, request, activeTab, *args, **kwargs):
        bich_man = BichiltManager()
        rq = request.POST
        start_date_q = rq.get('start_date', '')
        end_date = rq.get('end_date', '')
        tooluur_number = rq.get('tooluur_number', '')
        customer_code = rq.get('customer_code', '')
        user_name = rq.get('user_name', '')
        phone = rq.get('phone', '')
        address = rq.get('address', '')
        start_usage = rq.get('start_usage', '')
        end_usage = rq.get('end_usage', '')
        duureg = rq.get('select_duureg', '')
        horoo = rq.get('select_horoo', '')
        hothon = rq.get('select_hothon', '')
        egnee = rq.get('select_block', '')
        created_user = rq.get('created_user', '')
        is_problem = rq.get('is_problem', '')
        cycle = rq.get('cycle', '')

        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        if now.day < 25:
            if now.month == 1:
                now = now.replace(year=now.year - 1)
                now = now.replace(month=12)
            else:
                now = now.replace(month=now.month-1)
        else:
            now = now.replace(day=1)
        start_date = now.strftime("%Y-%m-%d")
        search_ahui_q = None
        search_ded_stants_q = None
        search_not_pay_q = None
        search_bair_q = None
        success_write = None
        duuregs = Duureg.objects.filter(is_active="1")
        horoos = None
        hothons = None
        egnees = None
        datas = None
        not_bichilts_list = None
        ded_stants = None
        bairs = None

        if 'search_ahui' in rq or 'write_to_avlaga' in rq or 'export_xls_customer' in rq:
            ahui_para = {}
            ahui_extra = []
            start_date_q = start_date_q + ' 00:00:00.000000'
            end_date = end_date + ' 23:59:59.999999'
            if start_date_q != '' and end_date != '':
                ahui_para["bichilt_date__range"] = (start_date_q, end_date)
            else:
                if start_date_q != '':
                    ahui_para["bichilt_date__gte"] = start_date_q
                if end_date != '':
                    ahui_para["bichilt_date__lte"] = end_date
            if tooluur_number != '':
                ahui_para["tooluur__tooluur__number__contains"] = tooluur_number
            if customer_code != '':
                ahui_para["tooluur__customer_code__contains"] = customer_code
            if user_name != '':
                ahui_para["tooluur__customer__first_name__icontains"] = user_name
            if start_usage != '':
                ahui_extra.append("day_balance > %s" % start_usage)
            if end_usage != '':
                ahui_extra.append("day_balance < %s" % end_usage)
            if is_problem != '':
                ahui_extra.append("is_problem = %s" % is_problem)
            if duureg != '':
                ahui_para["tooluur__customer__address__duureg_code"] = duureg
                if horoo != '':
                    ahui_para["tooluur__customer__address__horoo_code"] = horoo
                    horoos = Horoo.objects.filter(is_active="1", duureg__code=duureg)
                    if hothon != '':
                        ahui_para["tooluur__customer__address__hothon_code"] = hothon
                        hothons = Hothon.objects.filter(is_active="1", horoo__code=horoo)
                        if egnee != '':
                            ahui_para["tooluur__customer__address__block_code"] = egnee
                            egnees = Block.objects.filter(is_active="1", hothon__code=hothon)
            if created_user != '':
                ahui_para["created_user_id"] = str(created_user)
                created_user = int(created_user)
            ahui_para["user_type"] = "1"
            ahui_para["is_active"] = "1"

            datas = Bichilt.objects.filter(**ahui_para).extra(where=ahui_extra).order_by('bichilt_date')
            if 'export_xls_customer' in rq:
                return self.export_bichilt_indi_xls(datas)
            elif 'write_to_avlaga' in rq:
                total_count = 0
                writed_count = 0
                head_tooluurs = []
                head_tooluurs2 = []

                try:
                    q_head_tooluurs = "SELECT id, head_tool_cus_id FROM data_hasagdahtooluur WHERE is_active = '1' GROUP BY head_tool_cus_id ORDER BY head_tool_cus_id"
                    hts = HasagdahTooluur.objects.raw(q_head_tooluurs)
                    for ht in hts:
                        head_tooluurs.append(ht.head_tool_cus_id)
                except HasagdahTooluur.DoesNotExist:
                    print("HasagdahTooluur does not exist a object!")

                try:
                    q_head_tooluurs = "SELECT id, head_tool_cus2_id FROM data_hasagdahtooluur WHERE is_active = '1' GROUP BY head_tool_cus_id ORDER BY head_tool_cus_id"
                    hts = HasagdahTooluur.objects.raw(q_head_tooluurs)
                    for ht in hts:
                        head_tooluurs2.append(ht.head_tool_cus2_id)
                except HasagdahTooluur.DoesNotExist:
                    print("HasagdahTooluur does not exist a object!")

                for item in datas:
                    if item.type == "0":
                        if item.year != None and item.month != None:
                            tulbur_date = getPayDate(item.tooluur, int(item.year), int(item.month))

                            if item.tooluur.customer.customer_angilal == '0':
                                prices = PriceTariff.objects.filter(une_type=0)[:1].get()
                            else:
                                prices = PriceTariff.objects.filter(une_type=1)[:1].get()

                            udur_price = round(float(prices.odor_une) + float(prices.serg_une), 2)
                            shunu_price = round(float(prices.shono_une) + float(prices.serg_une), 2)
                            orgil_price = round(float(prices.orgil_une) + float(prices.serg_une), 2)
                            chadal_price = float(prices.chadal_une)

                            if item.tooluur.id in head_tooluurs:
                                chtcs = HasagdahTooluur.objects.filter(head_tool_cus=item.tooluur)
                                head_tool_cust = chtcs.first().head_tool_cus
                                head_tool_cust2 = chtcs.first().head_tool_cus2

                                if head_tool_cust.guidliin_trans != None and head_tool_cust.guidliin_trans != '':
                                    amp_coff = round(float(head_tool_cust.guidliin_trans.multiply_coef if head_tool_cust.guidliin_trans.multiply_coef else 1), 3)
                                else:
                                    amp_coff = 1
                                if head_tool_cust.huchdeliin_trans != None and head_tool_cust.huchdeliin_trans != '':
                                    huch_coff = round(float(head_tool_cust.huchdeliin_trans.multiply_coef if head_tool_cust.huchdeliin_trans.multiply_coef else 1), 3)
                                else:
                                    huch_coff = 1
                                head_coef = round(amp_coff * huch_coff, 3)

                                head_tool_price = head1_tool_price = head2_tool_price = 0

                                print("######################################################################")
                                prev_item = Bichilt.objects.filter(id=item.prev_bichilt_id).first()
                                if head_tool_cust.tooluur.tariff == "0":
                                    day_diff = round(round(float(item.day_balance), 2) - round(float(prev_item.day_balance), 2), 2)
                                    day_diff = round(day_diff * head_coef, 2)
                                    hd1_tool_price = round(day_diff * udur_price, 2)
                                    hd1_chadal_price = 0
                                    if item.tooluur.customer.customer_type != '0':
                                        try:
                                            power_sdate = Bichilt.objects.get(id=item.prev_bichilt_id)
                                            power_sdate = power_sdate.bichilt_date
                                            power_sdate = datetime.datetime.strptime(str(power_sdate)[:10], "%Y-%m-%d")
                                        except Bichilt.DoesNotExist:
                                            power_sdate = datetime.datetime.strptime("2017-10-25", "%Y-%m-%d")
                                        power_edate = item.bichilt_date
                                        diff_of_days = get_number_of_days(power_sdate, power_edate.date())
                                        if day_diff != 0:
                                            if diff_of_days <= 27:
                                                chadal_price = round(chadal_price / 30, 2)
                                                chadal_price = round(chadal_price * diff_of_days, 2)
                                            hd1_chadal_price = round(day_diff / diff_of_days, 2)
                                            hd1_chadal_price = round(hd1_chadal_price / 12, 2)
                                            hd1_chadal_price = round(hd1_chadal_price * chadal_price, 2)
                                        else:
                                            hd1_chadal_price = 0
                                    hd1_total_tool_price = round(hd1_tool_price + hd1_chadal_price, 2)
                                    head1_tool_price = round(head1_tool_price + hd1_total_tool_price, 2)
                                    print("hd1_number : " + str(item.tooluur.tooluur.number))
                                    print("hd1_coef : " + str(head_coef))
                                    print("hd1_day_diff : " + str(round(float(item.day_diff), 2)))
                                    print("hd1_total_diff : " + str(day_diff))
                                    print("hd1_tool_price : " + str(hd1_tool_price))
                                    print("hd1_chadal_price : " + str(hd1_chadal_price))
                                    print("hd1_total_tool_price : " + str(hd1_total_tool_price))
                                if head_tool_cust.tooluur.tariff == "1":
                                    day_diff = round(round(float(item.day_balance), 2) - round(float(prev_item.day_balance), 2), 2)
                                    night_diff = round(round(float(item.night_balance), 2) - round(float(prev_item.night_balance), 2), 2)
                                    day_diff = round(day_diff * head_coef, 2)
                                    night_diff = round(night_diff * head_coef, 2)
                                    hd1_tool_price1 = round(day_diff * udur_price, 2)
                                    hd1_tool_price2 = round(night_diff * shunu_price, 2)
                                    hd1_tool_price = round(hd1_tool_price1 + hd1_tool_price2, 2)
                                    hd1_chadal_price = 0
                                    if item.tooluur.customer.customer_type != '0':
                                        try:
                                            power_sdate = Bichilt.objects.get(id=item.prev_bichilt_id)
                                            power_sdate = power_sdate.bichilt_date
                                            power_sdate = datetime.datetime.strptime(str(power_sdate)[:10], "%Y-%m-%d")
                                        except Bichilt.DoesNotExist:
                                            power_sdate = datetime.datetime.strptime("2017-10-25", "%Y-%m-%d")
                                        power_edate = item.bichilt_date
                                        diff_of_days = get_number_of_days(power_sdate, power_edate.date())
                                        hd1_diff = round(day_diff + night_diff, 2)
                                        if hd1_diff != 0:
                                            if diff_of_days <= 27:
                                                chadal_price = round(chadal_price / 30, 2)
                                                chadal_price = round(chadal_price * diff_of_days, 2)
                                            hd1_chadal_price = round(hd1_diff / diff_of_days, 2)
                                            hd1_chadal_price = round(hd1_chadal_price / 12, 2)
                                            hd1_chadal_price = round(hd1_chadal_price * chadal_price, 2)
                                        else:
                                            hd1_chadal_price = 0
                                    hd1_total_tool_price = round(hd1_tool_price + hd1_chadal_price, 2)
                                    head1_tool_price = round(head1_tool_price + hd1_total_tool_price, 2)
                                    print("hd1_number : " + str(item.tooluur.tooluur.number))
                                    print("hd1_coef : " + str(head_coef))
                                    print("hd1_day_diff : " + str(round(float(item.day_diff), 2)))
                                    print("hd1_night_diff : " + str(round(float(item.night_diff), 2)))
                                    print("hd1_total_diff : " + str(hd1_diff))
                                    print("hd1_tool_price : " + str(hd1_tool_price))
                                    print("hd1_chadal_price : " + str(hd1_chadal_price))
                                    print("hd1_total_tool_price : " + str(hd1_total_tool_price))
                                if head_tool_cust.tooluur.tariff == "2":
                                    day_diff = round(round(float(item.day_balance), 2) - round(float(prev_item.day_balance), 2), 2)
                                    night_diff = round(round(float(item.night_balance), 2) - round(float(prev_item.night_balance), 2), 2)
                                    rush_diff = round(round(float(item.rush_balance), 2) - round(float(prev_item.rush_balance), 2), 2)
                                    day_diff = round(day_diff * head_coef, 2)
                                    night_diff = round(night_diff * head_coef, 2)
                                    rush_diff = round(rush_diff * head_coef, 2)
                                    hd1_tool_price1 = round(day_diff * udur_price, 2)
                                    hd1_tool_price2 = round(night_diff * shunu_price, 2)
                                    hd1_tool_price3 = round(rush_diff * orgil_price, 2)
                                    hd1_tool_price = round(hd1_tool_price1 + hd1_tool_price2, 2)
                                    hd1_tool_price = round(hd1_tool_price + hd1_tool_price3, 2)
                                    hd1_chadal_price = 0
                                    if item.tooluur.customer.customer_type != '0':
                                        try:
                                            power_sdate = Bichilt.objects.get(id=item.prev_bichilt_id)
                                            power_sdate = power_sdate.bichilt_date
                                            power_sdate = datetime.datetime.strptime(str(power_sdate)[:10], "%Y-%m-%d")
                                        except Bichilt.DoesNotExist:
                                            power_sdate = datetime.datetime.strptime("2017-10-25", "%Y-%m-%d")
                                        power_edate = item.bichilt_date
                                        diff_of_days = get_number_of_days(power_sdate, power_edate.date())
                                        if rush_diff != 0:
                                            if diff_of_days <= 27:
                                                chadal_price = round(chadal_price / 30, 2)
                                                chadal_price = round(chadal_price * diff_of_days, 2)
                                            hd1_chadal_price = round(rush_diff / diff_of_days, 2)
                                            hd1_chadal_price = round(hd1_chadal_price / 5, 2)
                                            hd1_chadal_price = round(hd1_chadal_price * chadal_price, 2)
                                        else:
                                            hd1_chadal_price = 0
                                    hd1_total_tool_price = round(hd1_tool_price + hd1_chadal_price, 2)
                                    head1_tool_price = round(head1_tool_price + hd1_total_tool_price, 2)
                                    print("hd1_number : " + str(item.tooluur.tooluur.number))
                                    print("hd1_coef : " + str(head_coef))
                                    print("hd1_day_diff : " + str(round(float(item.day_diff), 2)))
                                    print("hd1_night_diff : " + str(round(float(item.night_diff), 2)))
                                    print("hd1_rush_diff : " + str(round(float(item.rush_diff), 2)))
                                    print("hd1_rush_total_diff : " + str(rush_diff))
                                    print("hd1_tool_price : " + str(hd1_tool_price))
                                    print("hd1_chadal_price : " + str(hd1_chadal_price))
                                    print("hd1_total_tool_price : " + str(hd1_total_tool_price))
                                head_tool_price = round(head_tool_price + head1_tool_price, 2)
                                print("head1_tool_price : " + str(head1_tool_price))

                                if head_tool_cust2 is not None:
                                    if head_tool_cust2.guidliin_trans != None and head_tool_cust2.guidliin_trans != '':
                                        amp_coff2 = round(float(head_tool_cust2.guidliin_trans.multiply_coef if head_tool_cust2.guidliin_trans.multiply_coef else 1), 3)
                                    else:
                                        amp_coff2 = 1
                                    if head_tool_cust2.huchdeliin_trans != None and head_tool_cust2.huchdeliin_trans != '':
                                        huch_coff2 = round(float(head_tool_cust2.huchdeliin_trans.multiply_coef if head_tool_cust2.huchdeliin_trans.multiply_coef else 1), 3)
                                    else:
                                        huch_coff2 = 1
                                    head_coef2 = round(amp_coff2 * huch_coff2, 3)

                                    cust2_bich = Bichilt.objects.filter(tooluur=head_tool_cust2, bichilt_date=item.bichilt_date).first()

                                    if cust2_bich is not None:
                                        cust2_bich_prev = Bichilt.objects.filter(id=cust2_bich.prev_bichilt_id).first()
                                        if head_tool_cust2.tooluur.tariff == "0":
                                            day_diff2 = round(round(float(cust2_bich.day_balance), 2) - round(float(cust2_bich_prev.day_balance), 2), 2)
                                            day_diff2 = round(day_diff2 * head_coef2, 2)
                                            hd2_tool_price = round(day_diff2 * udur_price, 2)
                                            print("day_diff2 : " + str(day_diff2))
                                            print("udur_price : " + str(udur_price))
                                            hd2_chadal_price = 0
                                            if item.tooluur.customer.customer_type != '0':
                                                try:
                                                    power_sdate = Bichilt.objects.get(id=cust2_bich.prev_bichilt_id)
                                                    power_sdate = power_sdate.bichilt_date
                                                    power_sdate = datetime.datetime.strptime(str(power_sdate)[:10], "%Y-%m-%d")
                                                except Bichilt.DoesNotExist:
                                                    power_sdate = datetime.datetime.strptime("2017-10-25", "%Y-%m-%d")
                                                power_edate = cust2_bich.bichilt_date
                                                diff_of_days = get_number_of_days(power_sdate, power_edate.date())
                                                if day_diff2 != 0:
                                                    if diff_of_days <= 27:
                                                        chadal_price = round(chadal_price / 30, 2)
                                                        chadal_price = round(chadal_price * diff_of_days, 2)
                                                    hd2_chadal_price = round(day_diff2 / diff_of_days, 2)
                                                    hd2_chadal_price = round(hd2_chadal_price / 12, 2)
                                                    hd2_chadal_price = round(hd2_chadal_price * chadal_price, 2)
                                                else:
                                                    hd2_chadal_price = 0
                                            hd2_total_tool_price = round(hd2_tool_price + hd2_chadal_price, 2)
                                            head2_tool_price = round(head2_tool_price + hd2_total_tool_price, 2)
                                            print("hd2_number : " + str(cust2_bich.tooluur.tooluur.number))
                                            print("hd2_coef : " + str(head_coef2))
                                            print("hd2_day_diff : " + str(round(float(cust2_bich.day_diff), 2)))
                                            print("hd2_day_total_diff : " + str(day_diff2))
                                            print("hd2_tool_price : " + str(hd2_tool_price))
                                            print("hd2_chadal_price : " + str(hd2_chadal_price))
                                            print("hd2_total_tool_price : " + str(hd2_total_tool_price))
                                        if head_tool_cust2.tooluur.tariff == "1":
                                            day_diff2 = round(round(float(cust2_bich.day_balance), 2) - round(float(cust2_bich_prev.day_balance), 2), 2)
                                            night_diff2 = round(round(float(cust2_bich.night_balance), 2) - round(float(cust2_bich_prev.night_balance), 2), 2)
                                            day_diff2 = round(day_diff2 * head_coef2, 2)
                                            night_diff2 = round(night_diff2 * head_coef2, 2)
                                            hd2_tool_price1 = round(day_diff2 * udur_price, 2)
                                            hd2_tool_price2 = round(night_diff2 * shunu_price, 2)
                                            hd2_tool_price = round(hd2_tool_price1 + hd2_tool_price2, 2)
                                            hd2_chadal_price = 0
                                            if item.tooluur.customer.customer_type != '0':
                                                try:
                                                    power_sdate = Bichilt.objects.get(id=cust2_bich.prev_bichilt_id)
                                                    power_sdate = power_sdate.bichilt_date
                                                    power_sdate = datetime.datetime.strptime(str(power_sdate)[:10], "%Y-%m-%d")
                                                except Bichilt.DoesNotExist:
                                                    power_sdate = datetime.datetime.strptime("2017-10-25", "%Y-%m-%d")
                                                power_edate = cust2_bich.bichilt_date
                                                diff_of_days = get_number_of_days(power_sdate, power_edate.date())
                                                hd2_diff = round(day_diff2 + night_diff2, 2)
                                                if hd2_diff != 0:
                                                    if diff_of_days <= 27:
                                                        chadal_price = round(chadal_price / 30, 2)
                                                        chadal_price = round(chadal_price * diff_of_days, 2)
                                                    hd2_chadal_price = round(hd2_diff / diff_of_days, 2)
                                                    hd2_chadal_price = round(hd2_chadal_price / 12, 2)
                                                    hd2_chadal_price = round(hd2_chadal_price * chadal_price, 2)
                                                else:
                                                    hd2_chadal_price = 0
                                            hd2_total_tool_price = round(hd2_tool_price + hd2_chadal_price, 2)
                                            head2_tool_price = round(head2_tool_price + hd2_total_tool_price, 2)
                                            print("hd2_number : " + str(cust2_bich.tooluur.tooluur.number))
                                            print("hd2_coef : " + str(head_coef2))
                                            print("hd2_day_diff : " + str(round(float(cust2_bich.day_diff), 2)))
                                            print("hd2_night_diff : " + str(round(float(cust2_bich.night_diff), 2)))
                                            print("hd2_day_total_diff : " + str(day_diff2))
                                            print("hd2_night_total_diff : " + str(night_diff2))
                                            print("hd2_tool_price : " + str(hd2_tool_price))
                                            print("hd2_chadal_price : " + str(hd2_chadal_price))
                                            print("hd2_total_tool_price : " + str(hd2_total_tool_price))
                                        if head_tool_cust2.tooluur.tariff == "2":
                                            day_diff2 = round(round(float(cust2_bich.day_balance), 2) - round(float(cust2_bich_prev.day_balance), 2), 2)
                                            night_diff2 = round(round(float(cust2_bich.night_balance), 2) - round(float(cust2_bich_prev.night_balance), 2), 2)
                                            rush_diff2 = round(round(float(cust2_bich.rush_balance), 2) - round(float(cust2_bich_prev.rush_balance), 2), 2)
                                            day_diff2 = round(day_diff2 * head_coef2, 2)
                                            night_diff2 = round(night_diff2 * head_coef2, 2)
                                            rush_diff2 = round(rush_diff2 * head_coef2, 2)
                                            hd2_tool_price1 = round(day_diff2 * udur_price, 2)
                                            hd2_tool_price2 = round(night_diff2 * shunu_price, 2)
                                            hd2_tool_price3 = round(rush_diff2 * orgil_price, 2)
                                            hd2_tool_price = round(hd2_tool_price1 + hd2_tool_price2, 2)
                                            hd2_tool_price = round(hd2_tool_price + hd2_tool_price3, 2)
                                            hd2_chadal_price = 0
                                            if item.tooluur.customer.customer_type != '0':
                                                try:
                                                    power_sdate = Bichilt.objects.get(id=cust2_bich.prev_bichilt_id)
                                                    power_sdate = power_sdate.bichilt_date
                                                    power_sdate = datetime.datetime.strptime(str(power_sdate)[:10], "%Y-%m-%d")
                                                except Bichilt.DoesNotExist:
                                                    power_sdate = datetime.datetime.strptime("2017-10-25", "%Y-%m-%d")
                                                power_edate = cust2_bich.bichilt_date
                                                diff_of_days = get_number_of_days(power_sdate, power_edate.date())
                                                if rush_diff2 != 0:
                                                    if diff_of_days <= 27:
                                                        chadal_price = round(chadal_price / 30, 2)
                                                        chadal_price = round(chadal_price * diff_of_days, 2)
                                                    hd2_chadal_price = round(rush_diff2 / diff_of_days, 2)
                                                    hd2_chadal_price = round(hd2_chadal_price / 5, 2)
                                                    hd2_chadal_price = round(hd2_chadal_price * chadal_price, 2)
                                                else:
                                                    hd2_chadal_price = 0
                                            hd2_total_tool_price = round(hd2_tool_price + hd2_chadal_price, 2)
                                            head2_tool_price = round(head2_tool_price + hd2_total_tool_price, 2)
                                            print("hd2_number : " + str(cust2_bich.tooluur.tooluur.number))
                                            print("hd2_coef : " + str(head_coef2))
                                            print("hd2_day_diff : " + str(round(float(cust2_bich.day_diff), 2)))
                                            print("hd2_night_diff : " + str(round(float(cust2_bich.night_diff), 2)))
                                            print("hd2_rush_diff : " + str(round(float(cust2_bich.rush_diff), 2)))
                                            print("hd2_day_total_diff : " + str(day_diff2))
                                            print("hd2_night_total_diff : " + str(night_diff2))
                                            print("hd2_rush_total_diff : " + str(rush_diff2))
                                            print("hd2_tool_price : " + str(hd2_tool_price))
                                            print("hd2_chadal_price : " + str(hd2_chadal_price))
                                            print("hd2_total_tool_price : " + str(hd2_total_tool_price))

                                        print("head2_tool_price : " + str(head2_tool_price))
                                        head_tool_price = round(head_tool_price + head2_tool_price, 2)

                                print("head_tool_price : " + str(head_tool_price))
                                print("######################################################################")

                                chtc_counter = 0
                                child_tool_price = 0
                                huch_price = float(prices.chadal_une)
                                for chtc in chtcs:
                                    chtc_counter += 1
                                    try:
                                        ch_bichilt = Bichilt.objects.filter(tooluur=chtc.child_tool_cus, bichilt_date=item.bichilt_date).first()
                                    except Bichilt.DoesNotExist:
                                        ch_bichilt = None

                                    if ch_bichilt is not None:
                                        if ch_bichilt.tooluur.guidliin_trans != None and ch_bichilt.tooluur.guidliin_trans != '':
                                            ch_amp_coff = round(float(ch_bichilt.tooluur.guidliin_trans.multiply_coef if ch_bichilt.tooluur.guidliin_trans.multiply_coef else 1), 3)
                                        else:
                                            ch_amp_coff = 1
                                        if ch_bichilt.tooluur.huchdeliin_trans != None and ch_bichilt.tooluur.huchdeliin_trans != '':
                                            ch_huch_coff = round(float(ch_bichilt.tooluur.huchdeliin_trans.multiply_coef if ch_bichilt.tooluur.huchdeliin_trans.multiply_coef else 1), 3)
                                        else:
                                            ch_huch_coff = 1
                                        child_coef = round(ch_amp_coff * ch_huch_coff, 3)

                                        print("----------------------------------------------------------")
                                        ch_bichilt_prev = Bichilt.objects.filter(id=ch_bichilt.prev_bichilt_id).first()
                                        if ch_bichilt.tooluur.tooluur.tariff == "0":
                                            ch_day_diff = round(round(float(ch_bichilt.day_balance), 2) - round(float(ch_bichilt_prev.day_balance), 2), 2)
                                            ch_day_diff = round(ch_day_diff * child_coef, 2)
                                            ch_tool_price = round(ch_day_diff * udur_price, 2)
                                            ch_chadal_price = 0
                                            if item.tooluur.customer.customer_type != '0':
                                                try:
                                                    power_sdate = Bichilt.objects.get(id=ch_bichilt.prev_bichilt_id)
                                                    power_sdate = power_sdate.bichilt_date
                                                    power_sdate = datetime.datetime.strptime(str(power_sdate)[:10], "%Y-%m-%d")
                                                except Bichilt.DoesNotExist:
                                                    power_sdate = datetime.datetime.strptime("2017-10-25", "%Y-%m-%d")
                                                power_edate = ch_bichilt.bichilt_date
                                                diff_of_days = get_number_of_days(power_sdate, power_edate.date())
                                                if ch_day_diff != 0:
                                                    if diff_of_days <= 27:
                                                        huch_price = round(huch_price / 30, 2)
                                                        huch_price = round(huch_price * diff_of_days, 2)
                                                    ch_chadal_price = round(ch_day_diff / diff_of_days, 2)
                                                    ch_chadal_price = round(ch_chadal_price / 12, 2)
                                                    ch_chadal_price = round(ch_chadal_price * huch_price, 2)
                                                else:
                                                    ch_chadal_price = 0
                                            ch_total_tool_price = round(ch_tool_price + ch_chadal_price, 2)
                                            child_tool_price = round(child_tool_price + ch_total_tool_price, 2)
                                            print("ch_number : " + str(ch_bichilt.tooluur.tooluur.number))
                                            print("ch_coef : " + str(child_coef))
                                            print("ch_day_diff : " + str(ch_bichilt.day_diff))
                                            print("ch_tool_price : " + str(ch_tool_price))
                                            print("ch_chadal_price : " + str(ch_chadal_price))
                                            print("ch_tool_total_price : " + str(ch_total_tool_price))
                                        if ch_bichilt.tooluur.tooluur.tariff == "1":
                                            ch_day_diff = round(round(float(ch_bichilt.day_balance), 2) - round(float(ch_bichilt_prev.day_balance), 2), 2)
                                            ch_night_diff = round(round(float(ch_bichilt.night_balance), 2) - round(float(ch_bichilt_prev.night_balance), 2), 2)
                                            ch_day_diff = round(ch_day_diff * child_coef, 2)
                                            ch_night_diff = round(ch_night_diff * child_coef, 2)
                                            ch_tool_price1 = round(ch_day_diff * udur_price, 2)
                                            ch_tool_price2 = round(ch_night_diff * shunu_price, 2)
                                            ch_tool_price = round(ch_tool_price1 + ch_tool_price2, 2)
                                            ch_chadal_price = 0
                                            if item.tooluur.customer.customer_type != '0':
                                                try:
                                                    power_sdate = Bichilt.objects.get(id=ch_bichilt.prev_bichilt_id)
                                                    power_sdate = power_sdate.bichilt_date
                                                    power_sdate = datetime.datetime.strptime(str(power_sdate)[:10], "%Y-%m-%d")
                                                except Bichilt.DoesNotExist:
                                                    power_sdate = datetime.datetime.strptime("2017-10-25", "%Y-%m-%d")
                                                power_edate = ch_bichilt.bichilt_date
                                                diff_of_days = get_number_of_days(power_sdate, power_edate.date())
                                                ch_diff = round(ch_day_diff + ch_night_diff, 2)
                                                if ch_diff != 0:
                                                    if diff_of_days <= 27:
                                                        huch_price = round(huch_price / 30, 2)
                                                        huch_price = round(huch_price * diff_of_days, 2)
                                                    ch_chadal_price = round(ch_diff / diff_of_days, 2)
                                                    ch_chadal_price = round(ch_chadal_price / 12, 2)
                                                    ch_chadal_price = round(ch_chadal_price * huch_price, 2)
                                                else:
                                                    ch_chadal_price = 0
                                            ch_total_tool_price = round(ch_tool_price + ch_chadal_price, 2)
                                            child_tool_price = round(child_tool_price + ch_total_tool_price, 2)
                                            print("ch_number : " + str(ch_bichilt.tooluur.tooluur.number))
                                            print("ch_coef : " + str(child_coef))
                                            print("ch_day_diff : " + str(ch_bichilt.day_diff))
                                            print("ch_night_diff : " + str(ch_bichilt.night_diff))
                                            print("ch_tool_price : " + str(ch_tool_price))
                                            print("ch_chadal_price : " + str(ch_chadal_price))
                                            print("ch_tool_total_price : " + str(ch_total_tool_price))
                                        if ch_bichilt.tooluur.tooluur.tariff == "2":
                                            ch_day_diff = round(round(float(ch_bichilt.day_balance), 2) - round(float(ch_bichilt_prev.day_balance), 2), 2)
                                            ch_night_diff = round(round(float(ch_bichilt.night_balance), 2) - round(float(ch_bichilt_prev.night_balance), 2), 2)
                                            ch_rush_diff = round(round(float(ch_bichilt.rush_balance), 2) - round(float(ch_bichilt_prev.rush_balance), 2), 2)
                                            ch_day_diff = round(ch_day_diff * child_coef, 2)
                                            ch_night_diff = round(ch_night_diff * child_coef, 2)
                                            ch_rush_diff = round(ch_rush_diff * child_coef, 2)
                                            ch_tool_price1 = round(ch_day_diff * udur_price, 2)
                                            ch_tool_price2 = round(ch_night_diff * shunu_price, 2)
                                            ch_tool_price3 = round(ch_rush_diff * orgil_price, 2)
                                            ch_tool_price = round(ch_tool_price1 + ch_tool_price2, 2)
                                            ch_tool_price = round(ch_tool_price + ch_tool_price3, 2)
                                            ch_chadal_price = 0
                                            if item.tooluur.customer.customer_type != '0':
                                                try:
                                                    power_sdate = Bichilt.objects.get(id=ch_bichilt.prev_bichilt_id)
                                                    power_sdate = power_sdate.bichilt_date
                                                    power_sdate = datetime.datetime.strptime(str(power_sdate)[:10], "%Y-%m-%d")
                                                except Bichilt.DoesNotExist:
                                                    power_sdate = datetime.datetime.strptime("2017-10-25", "%Y-%m-%d")
                                                power_edate = ch_bichilt.bichilt_date
                                                diff_of_days = get_number_of_days(power_sdate, power_edate.date())
                                                if ch_rush_diff != 0:
                                                    if diff_of_days <= 27:
                                                        huch_price = round(huch_price / 30, 2)
                                                        huch_price = round(huch_price * diff_of_days, 2)
                                                    ch_chadal_price = round(ch_rush_diff / diff_of_days, 2)
                                                    ch_chadal_price = round(ch_chadal_price / 5, 2)
                                                    ch_chadal_price = round(ch_chadal_price * huch_price, 2)
                                                else:
                                                    ch_chadal_price = 0
                                            ch_total_tool_price = round(ch_tool_price + ch_chadal_price, 2)
                                            child_tool_price = round(child_tool_price + ch_total_tool_price, 2)
                                            print("ch_number : " + str(ch_bichilt.tooluur.tooluur.number))
                                            print("ch_coef : " + str(child_coef))
                                            print("ch_day_diff : " + str(ch_bichilt.day_diff))
                                            print("ch_night_diff : " + str(ch_bichilt.night_diff))
                                            print("ch_rush_diff : " + str(ch_bichilt.rush_diff))
                                            print("ch_tool_price : " + str(ch_tool_price))
                                            print("ch_chadal_price : " + str(ch_chadal_price))
                                            print("ch_tool_total_price : " + str(ch_total_tool_price))
                                        print("----------------------------------------------------------")
                                print("all_child_tool_price : " + str(child_tool_price))

                                sp_tool_price = 0
                                if int(head_tool_cust.id) == 3308:
                                    tooluur = Tooluur.objects.filter(id=3241).first().balance_value
                                    sp_tool_price = round(round(float(tooluur), 2) * udur_price, 2)
                                    try:
                                        power_sdate = Bichilt.objects.get(id=item.prev_bichilt_id)
                                        power_sdate = power_sdate.bichilt_date
                                        power_sdate = datetime.datetime.strptime(str(power_sdate)[:10], "%Y-%m-%d")
                                    except Bichilt.DoesNotExist:
                                        power_sdate = datetime.datetime.strptime("2017-10-25", "%Y-%m-%d")
                                    power_edate = item.bichilt_date
                                    diff_of_days = get_number_of_days(power_sdate, power_edate.date())
                                    if diff_of_days <= 27:
                                        huch_price = round(huch_price / 30, 2)
                                        huch_price = round(huch_price * diff_of_days, 2)
                                    sp_chadal_price = round(float(tooluur) / diff_of_days, 2)
                                    sp_chadal_price = round(sp_chadal_price / 12, 2)
                                    sp_chadal_price = round(sp_chadal_price * huch_price, 2)
                                    sp_tool_price = round(sp_tool_price + sp_chadal_price, 2)
                                    print("sp_tool_price : " + str(sp_tool_price))
                                head_tool_price = round(round(head_tool_price - child_tool_price, 2) - sp_tool_price, 2)
                                print("head_tool_price : " + str(head_tool_price))
                                print("######################################################################")
                                total_price = bich_man.add_nuat_price(head_tool_price)
                            else:
                                total_price = round(float(item.total_price if item.total_price else 0.0), 2)
                                if item.tooluur.id in head_tooluurs2:
                                    total_price = 0.0
                                print("######################################################################")
                                print("number : " + str(item.tooluur.tooluur.number))
                                print("total_price : " + str(total_price))
                                print("######################################################################")

                            if float(item.total_diff) > 0.0:
                                iluu = 0
                                payment = Payment.objects.filter(customer=item.tooluur.customer).first()
                                if payment is not None:
                                    if float(payment.uldegdel) > 1:
                                        iluu = float(payment.uldegdel)

                                try:
                                    avlaga = Avlaga.objects.get(year=item.year, month=item.month, customer=item.tooluur.customer)
                                    if iluu > (total_price + round(float(avlaga.pay_uld), 2)):
                                        if payment is not None:
                                            avlaga.pay_uld = 0.0
                                            avlaga.pay_type = '1'
                                            avlaga.paid_date = datetime.datetime.now()
                                            payment.uldegdel = round(iluu - round(float(avlaga.pay_uld), 2) + total_price, 2)
                                            payment.save()
                                    else:
                                        avlaga.pay_uld = round(float(avlaga.pay_uld) + total_price - iluu, 2)
                                        if payment is not None:
                                            payment.uldegdel = 0.0
                                            payment.save()
                                    avlaga.heregleenii_tulbur = round(float(avlaga.heregleenii_tulbur) + total_price, 2)
                                    avlaga.ald_huvi = float(prices.ald_huvi)
                                    avlaga.save()
                                except ObjectDoesNotExist:
                                    avlaga = Avlaga.objects.create(customer=item.tooluur.customer, created_user_id=request.user.id, tulbur_date=tulbur_date, year=item.year, month=item.month)
                                    if iluu > (total_price + bich_man.add_nuat_price(prices.barimt_une)):
                                        print("iluu : " + str(iluu) + " > total_price : " + str(total_price))
                                        if payment is not None:
                                            avlaga.pay_uld = 0.0
                                            avlaga.pay_type = '1'
                                            avlaga.paid_date = datetime.datetime.now()
                                            payment.uldegdel = round(iluu - total_price, 2) - bich_man.add_nuat_price(prices.barimt_une)
                                            payment.save()
                                    else:
                                        avlaga.pay_uld = round(total_price - iluu, 2) + bich_man.add_nuat_price(prices.barimt_une)
                                        if payment is not None:
                                            payment.uldegdel = 0.0
                                            payment.save()
                                    avlaga.heregleenii_tulbur = total_price
                                    avlaga.ald_huvi = float(prices.ald_huvi)
                                    avlaga.barimt_une = bich_man.add_nuat_price(prices.barimt_une)
                                    avlaga.save()

                                item.type = "2"
                                item.avlaga = avlaga
                                item.save()
                                writed_count += 1

                total_count += 1
                success_write = {
                    "total_count":total_count,
                    "write_count":writed_count,
                }
            elif 'search_ahui' in rq:
                par = {"is_active":"1", "user_type":"1", "bichilt_date__range": (start_date, current_date)}
                ded_stants = Bichilt.objects.filter(**par)
                par1 = {"is_active": "1", "user_type": "2", "bichilt_date__range": (start_date, current_date)}
                bairs = Bichilt.objects.filter(**par1)
                search_ahui_q = {
                    "start_date":start_date_q[:10],
                    "end_date":end_date[:10],
                    "tooluur_number":tooluur_number,
                    "customer_code":customer_code,
                    "user_name":user_name,
                    "start_usage":start_usage,
                    "end_usage":end_usage,
                    "duureg": duureg,
                    "hothon": hothon,
                    "egnee": egnee,
                    "created_user": created_user,
                    "is_problem": is_problem,
                    "horoo":horoo
                }
        elif 'search_dedstants' in rq or 'export_xls_deds' in rq:
            ded_stants_para = {}
            ded_stants_extra = []
            if start_date_q != '' and end_date != '':
                ded_stants_para["bichilt_date__range"] = (start_date_q, end_date)
            else:
                if start_date_q != '':
                    ded_stants_para["bichilt_date__gte"] = start_date_q
                if end_date != '':
                    ded_stants_para["bichilt_date__lte"] = end_date
            if tooluur_number != '':
                ded_stants_para["tooluur__tooluur__number__contains"] = tooluur_number
            if user_name != '':
                ded_stants_para["tooluur__dedstants__name__icontains"] = user_name
            if start_usage != '':
                ded_stants_extra.append("day_balance > %s"%start_usage)
            if end_usage != '':
                ded_stants_extra.append("day_balance < %s" % end_usage)
            ded_stants_para["user_type"] = "0"
            ded_stants_para["is_active"] = "1"
            ded_stants = Bichilt.objects.filter(**ded_stants_para).extra(where=ded_stants_extra)
            if 'search_dedstants' in rq:
                ahui_q = """SELECT bi.bichilt_date, bi.id, bi.day_balance, bi.night_balance, bi.rush_balance, bi.year, bi.month,
                                bi.type, tol.number, bi.sergeegdeh_price, bi.chadal_price,
                                bi.hereglee_price, bi.suuri_price, bi.total_diff, bi.total_price
                                FROM data_bichilt AS bi
                                JOIN data_tooluurcustomer AS to_cu ON bi.tooluur_id=to_cu.id
                                JOIN data_tooluur AS tol ON to_cu.tooluur_id=tol.id
                                WHERE bi.is_active='1'
                                AND bi.user_type='0'
                                AND bi.bichilt_date BETWEEN '%s' AND '%s'""" % (start_date, current_date)
                datas = list(Bichilt.objects.raw(ahui_q))
                par1 = {"is_active": "1", "user_type": "2", "bichilt_date__range": (start_date, current_date)}
                bairs = Bichilt.objects.filter(**par1)
                search_ded_stants_q = {
                    "tooluur_number":tooluur_number,
                    "customer_code":customer_code,
                    "user_name":user_name,
                    "start_usage":start_usage,
                    "end_usage":end_usage,
                    "start_date":start_date_q,
                    "end_date":end_date,
                }
            else:
                return self.export_bichilt_station_xls(ded_stants)
        elif 'search_bair' in rq or 'export_xls_bair' in rq:
            bair_para = {}
            if start_date_q != '' and end_date != '':
                bair_para["bichilt_date__range"] = (start_date_q, end_date)
            else:
                if start_date_q != '':
                    bair_para["bichilt_date__gte"] = start_date_q
                if end_date != '':
                    bair_para["bichilt_date__lte"] = end_date
            if tooluur_number != '':
                bair_para["tooluur__tooluur__number__contains"] = tooluur_number
            if user_name != '':
                bair_para["tooluur__bair__name__contains"] = user_name
            if start_usage != '':
                bair_para["day_balance__gte"] = start_usage
            if end_usage != '':
                bair_para["day_balance__lte"] = end_usage
            bair_para["user_type"] = "2"
            bair_para["is_active"] = "1"
            bairs = Bichilt.objects.filter(**bair_para)
            if 'export_xls_bair' in rq:
                return self.export_bichilt_bair_xls(bairs)
            else:
                par = {"is_active": "1", "user_type": "1", "bichilt_date__range": (start_date, current_date)}
                ded_stants = Bichilt.objects.filter(**par)
                ahui_q = self.q_bichilt_list + " WHERE bi.is_active='1' AND bi.user_type='0' AND bi.bichilt_date BETWEEN '%s' AND '%s'" % (
                start_date, current_date)
                datas = list(Bichilt.objects.raw(ahui_q))
                search_bair_q = {
                    "tooluur_number": tooluur_number,
                    "customer_code": customer_code,
                    "user_name": user_name,
                    "start_usage": start_usage,
                    "end_usage": end_usage,
                    "start_date": start_date_q,
                    "end_date": end_date,
                }
        elif 'search_not_pay_q' in rq:
            q = """SELECT tocu.id
                FROM data_tooluurcustomer tocu JOIN data_tooluur tool ON tocu.tooluur_id = tool.id
                JOIN data_customer cust ON tocu.customer_id = cust.id AND cust.is_active = '1'
                JOIN data_geree gere ON gere.customer_code = cust.code AND gere.is_active = '1'
                JOIN data_address addr ON cust.id = addr.customer_id AND addr.is_active = '1'
                JOIN data_bichilt bich ON tocu.id = bich.tooluur_id AND bich.is_active = '1'
                WHERE tocu.is_active = '1'AND gere.cycle_code = '""" + cycle + """' AND bich.bichilt_date BETWEEN '
                """ + start_date_q + """ 00:00:00.000000' AND '""" + end_date + """ 23:59:59.999999' GROUP BY tocu.id"""
            bichilt_list = TooluurCustomer.objects.raw(q)

            tooluur_ids_bichilts = ''
            for bichilt_l in bichilt_list:
                tooluur_ids_bichilts += str(bichilt_l.id) + ', '
            if len(tooluur_ids_bichilts) > 2:
                tooluur_ids_bichilts = tooluur_ids_bichilts[:-2]

            q2 = """SELECT tocu.id, tool.number, cust.code, cust.last_name, cust.first_name, cust.phone, addr.address_name
                FROM data_tooluurcustomer tocu JOIN data_tooluur tool ON tocu.tooluur_id = tool.id
                JOIN data_customer cust ON tocu.customer_id = cust.id AND cust.is_active = '1'
                JOIN data_geree gere ON gere.customer_code = cust.code AND gere.is_active = '1'
                JOIN data_address addr ON cust.id = addr.customer_id AND addr.is_active = '1'
                WHERE tocu.is_active = '1'"""

            if len(tooluur_ids_bichilts) > 1:
                q2 += " AND tocu.id NOT IN (" + tooluur_ids_bichilts + ")"
            if tooluur_number != '':
                q2 += " AND tool.number LIKE '%%" + tooluur_number + "%%'"
            if customer_code != '':
                q2 += " AND cust.code LIKE '%%" + customer_code + "%%'"
            if user_name != '':
                q2 += " AND cust.first_name LIKE '%%" + user_name + "%%'"
            if phone != '':
                q2 += " AND cust.phone LIKE '%%" + phone + "%%'"
            if cycle != '':
                q2 += " AND gere.cycle_code = '" + cycle + "'"
            if address != '':
                q2 += " AND addr.address_name LIKE '%%" + address + "%%'"
            q2 += " GROUP BY tocu.id"
            not_bichilts_list = TooluurCustomer.objects.raw(q2)

            search_not_pay_q = {
                "start_date": start_date_q,
                "end_date": end_date,
                "tooluur_number": tooluur_number,
                "customer_code": customer_code,
                "user_name": user_name,
                "cycle": cycle,
                "phone": phone,
                "address": address,
            }
        else:
            tooluur_ids_bichilts = datas.values_list('tooluur_id', flat=True)
            par3 = {"is_active": "1"}
            not_bichilts_list = TooluurCustomer.objects.filter(**par3).filter(~Q(id__in=tooluur_ids_bichilts))

        year_array = get_years()
        month_array = get_months()
        BichiltList.individual_bichilts = datas
        BichiltList.substation_bichilts = ded_stants
        staff_users = UserProfile.objects.filter(is_active=1)
        cycles = Cycle.objects.filter(is_active='1')

        data = {
            "search_q":search_ahui_q,
            "search_not_pay_q":search_not_pay_q,
            "search_dedstants_q":search_ded_stants_q,
            "search_bair_q":search_bair_q,
            "activeTab":str(activeTab),
            "not_bichilts": not_bichilts_list,
            "years":year_array,
            "data_bichilt":datas,
            "data_dedstants":ded_stants,
            "data_bair":bairs,
            "created_users": staff_users,
            "months":month_array,
            "start_date":start_date,
            "end_date":current_date,
            "success":success_write,
            "menu":self.menu,
            "sub":self.sub,
            "duuregs":duuregs,
            "horoo": horoos,
            "hothon": hothons,
            "egnee": egnees,
            "cycles": cycles
        }
        return render(request, self.template_name, data)

    def append_add(self, q):
        if q != self.q_bichilt_list:
            return q + " AND "
        elif q == self.q_bichilt_list:
            q = q + " WHERE "
        return q

    def append_or(self, q):
        if q != self.q_bichilt_list:
            return q + " AND "
        return q

    def export_bichilt_bair_xls(self,rows):
        response = HttpResponse(content_type='application/ms-excel')
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        filename = "bichilt_stations-" + current_date + ".xls"
        response['Content-Disposition'] = 'attachment; filename="%s"'%filename
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Bichilt')
        # Sheet header, first row
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['Тоолуурын №', 'Байрны дугаар', 'Бичилтийн огноо', 'Өдөр', 'Шөнө', 'Оргил цаг', 'Нийт зөрүү',]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        for row in rows:
            row_num += 1
            col_num = 0
            toolur_number = row.tooluur.tooluur.number
            if toolur_number == None:
                toolur_number = "0.0"
            bair_name = ''
            if row.tooluur.bair != None:
                bair_name = row.tooluur.bair.name
            date = str(row.bichilt_date)
            day_balance = row.day_balance
            night_balance = row.night_balance
            rush_balance = row.rush_balance
            total_diff = row.total_diff
            ws.write(row_num, col_num, toolur_number, font_style)
            col_num +=1
            ws.write(row_num, col_num, bair_name, font_style)
            col_num +=1
            ws.write(row_num, col_num, date, font_style)
            col_num +=1
            ws.write(row_num, col_num, day_balance, font_style)
            col_num +=1
            ws.write(row_num, col_num, night_balance, font_style)
            col_num +=1
            ws.write(row_num, col_num, rush_balance, font_style)
            col_num +=1
            ws.write(row_num, col_num, total_diff, font_style)
        wb.save(response)
        return response

    def export_bichilt_indi_xls(self,rows):
        response = HttpResponse(content_type='application/ms-excel')
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        filename = "bichilt_huvi_hereglegch-" + current_date + ".xls"
        response['Content-Disposition'] = 'attachment; filename="%s"'%filename

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Bichilt')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['Тоолуурын №', 'Хэрэглэгчийн нэр', 'Хэрэглэгчийн код', 'Бичилтийн огноо', 'СЭХ төлбөр', 'Чадлын төлбөр','Хэрэглээний төлбөр','Суурь төлбөр','Нийт Зөрүү','Нийт төлбөр','Төлөв',]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        for row in rows:
            row_num += 1
            col_num = 0
            full_name = row.tooluur.customer.first_name + ' ' + row.tooluur.customer.last_name
            toolur_number = row.tooluur.tooluur.number
            if toolur_number == None:
                toolur_number = "0.0"
            customer_code = row.tooluur.customer.code
            if customer_code == None:
                customer_code = "0.0"
            bichilt_date = row.bichilt_date
            sergeegdeh_price = row.sergeegdeh_price
            if sergeegdeh_price == None:
                sergeegdeh_price = "0.0"
            chadal_price = row.chadal_price
            if chadal_price == None:
                chadal_price = "0.0"
            hereglee_price = row.hereglee_price
            if hereglee_price == None:
                hereglee_price = "0.0"
            suuri_price = row.suuri_price
            if suuri_price == None:
                suuri_price = "0.0"
            total_diff = row.total_diff
            if total_diff == None:
                total_diff = "0.0"
            total_price = row.total_price
            if total_price == None:
                total_price = "0.0"
            status = ''

            if row.type == "0":
                status = 'Бичилт хийгдсэн'
            elif row.type == "1":
                status = 'Баланс тооцогдсон'
            elif row.type == "2":
                status = 'Авлага үүссэн'

            ws.write(row_num, col_num, toolur_number, font_style)
            col_num +=1
            ws.write(row_num, col_num, full_name, font_style)
            col_num += 1
            ws.write(row_num, col_num, customer_code, font_style)
            col_num += 1
            ws.write(row_num, col_num, str(bichilt_date), font_style)
            col_num += 1
            ws.write(row_num, col_num, sergeegdeh_price, font_style)
            col_num += 1
            ws.write(row_num, col_num, chadal_price, font_style)
            col_num += 1
            ws.write(row_num, col_num, hereglee_price, font_style)
            col_num += 1
            ws.write(row_num, col_num, suuri_price, font_style)
            col_num += 1
            ws.write(row_num, col_num, total_diff, font_style)
            col_num += 1
            ws.write(row_num, col_num, total_price, font_style)
            col_num += 1
            ws.write(row_num, col_num, status, font_style)

        wb.save(response)
        return response


    def export_bichilt_station_xls(self,rows):
        response = HttpResponse(content_type='application/ms-excel')
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        filename = "bichilt_stations-" + current_date + ".xls"
        response['Content-Disposition'] = 'attachment; filename="%s"'%filename

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Bichilt')

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['Тоолуурын №', 'Дэд станцын дугаар', 'Бичилтийн огноо', 'Өдөр', 'Шөнө', 'Оргил цаг', 'Нийт зөрүү',]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        ded_stants_para = {}
        ded_stants_para["user_type"] = "0"
        ded_stants_para["is_active"] = "1"
        # rows = Bichilt.objects.filter(**ded_stants_para)
        for row in rows:
            row_num += 1
            col_num = 0
            toolur_number = row.tooluur.tooluur.number
            if toolur_number == None:
                toolur_number = "0.0"
            sub_station_name = ''
            if row.tooluur.dedstants != None:
                sub_station_name = row.tooluur.dedstants.name
            date = str(row.bichilt_date)
            day_balance = row.day_balance
            night_balance = row.night_balance
            rush_balance = row.rush_balance
            total_diff = row.total_diff
            ws.write(row_num, col_num, toolur_number, font_style)
            col_num +=1
            ws.write(row_num, col_num, sub_station_name, font_style)
            col_num +=1
            ws.write(row_num, col_num, date, font_style)
            col_num +=1
            ws.write(row_num, col_num, day_balance, font_style)
            col_num +=1
            ws.write(row_num, col_num, night_balance, font_style)
            col_num +=1
            ws.write(row_num, col_num, rush_balance, font_style)
            col_num +=1
            ws.write(row_num, col_num, total_diff, font_style)
        wb.save(response)
        return response


class BichiltAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'data.add_bichilt'
    template_name = 'homepage/borluulalt/bichilt_add.html'
    login_url = '/home/index'
    menu = "3"
    sub = "2"

    def get(self, request, *args, **kwargs):
        data = {
            "urlz":"/home/borluulalt/bichilt_add",
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        bich_man = BichiltManager()
        rq = request.POST
        bichilt_date = rq.get('bichilt_date', '')
        user_code = rq.get('user_code', '')
        tooluur_number = rq.get('tooluur_select', '')
        day = rq.get('day_zaalt', '')
        night = rq.get('night_zaalt', '')
        zadgai_bichilt = rq.get('zadgai_bichilt', '0')
        description = rq.get('description', '')
        is_problem = rq.get('is_problem', '')

        if is_problem == '':
            is_problem = "0"
        if night == '':
            night = "0"
        rush = rq.get('rush_zaalt', '')
        if rush == '':
            rush = "0"
        b_date = datetime.datetime.strptime(bichilt_date, '%Y-%m-%d')
        response = bich_man.create_bichilt("1", tooluur_number, user_code, b_date, zadgai_bichilt, day, night, rush, description, request.user.id, is_problem)

        if response["code"] == 400:
            return self.error_builder_with_return( request, response["code"], response["description"], bichilt_date)
        else:
            return self.success_builder_with_return(request, bichilt_date)

    def error_builder_with_return(self, request, code, description, date):
        messages.error(request, description)
        data = {
            "add_q":{
                "bichilt_date":date,
            },
            "error":{
                "code":code,
                "description":description
            },
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)

    def success_builder_with_return(self, request, date):
        messages.success(request, "Амжилттай хадгалагдлаа.")
        print(request)
        data = {
                "add_q":{
                    "bichilt_date":date,
                },
                "success":"True",
                "menu":self.menu,
                "sub":self.sub
            }
        return render(request, self.template_name, data)


class BichiltEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = 'homepage/borluulalt/bichilt_add.html'
    login_url = '/home/index'
    permission_required = 'data.change_bichilt'
    NUAT = 0.1
    POWER_TIME_BY_USER = 12
    POWER_TIME_BY_ORG = 5
    menu = "3"
    sub = "2"

    def get(self, request, id, *args, **kwargs):
        selected_bichilt = None
        try:
            selected_bichilt = Bichilt.objects.get(id=id)
        except Bichilt.DoesNotExist:
            redirect("/home/borluulalt/bichilt_list/1/")
        prev_bichilt = {}
        if selected_bichilt.prev_bichilt_id != "0" and selected_bichilt.prev_bichilt_id != None:
            prev = Bichilt.objects.get(id=selected_bichilt.prev_bichilt_id)
            prev_bichilt['day'] = prev.day_balance
            prev_bichilt['night'] = prev.night_balance
            prev_bichilt['rush'] = prev.rush_balance
            prev_bichilt['created_date'] =  prev.bichilt_date.strftime("%Y-%m-%d")
        else:
            prev_bichilt['day'] = selected_bichilt.tooluur.tooluur.balance_value
            prev_bichilt['night'] = selected_bichilt.tooluur.tooluur.balance_value_night
            prev_bichilt['rush'] = selected_bichilt.tooluur.tooluur.balance_value_rush
            prev_bichilt['created_date'] =  selected_bichilt.tooluur.tooluur.installed_date.strftime("%Y-%m-%d")
        amp_coff = 1
        if selected_bichilt.tooluur.customer.customer_angilal == "0":
            customer_angilal = "1"
            if selected_bichilt.tooluur.guidliin_trans != None:
                amp_coff = float(selected_bichilt.tooluur.guidliin_trans.multiply_coef)
        else:
            customer_angilal = "0"
        geree = Geree.objects.get(customer_code=selected_bichilt.tooluur.customer.code, is_active=1)
        customer_name = selected_bichilt.tooluur.customer.last_name + " " + selected_bichilt.tooluur.customer.first_name
        # customer_address = selected_bichilt.tooluur.customer.address.address_name
        try:
            tariff = PriceTariff.objects.get(bus_type=geree.bus_type, une_type=customer_angilal, is_active=1)
            price = {
                "day_price": tariff.odor_une,
                "night_price": tariff.shono_une,
                "rush_price": tariff.orgil_une
            }
        except PriceTariff.DoesNotExist:
            price = {
                "day_price": 1,
                "night_price": 1,
                "rush_price": 1
            }
        print(selected_bichilt.is_zadgai)
        data = {
            "urlz":"/home/borluulalt/bichilt_edit/" + id + "/",
            "edit_data":selected_bichilt,
            "prev_data":prev_bichilt,
            "add_q":{
                "bichilt_date":selected_bichilt.bichilt_date.strftime("%Y-%m-%d"),
            },
            "tooluur_name": selected_bichilt.tooluur.tooluur.number + " " + selected_bichilt.tooluur.tooluur.name,
            "price":price,
            "coeff":amp_coff,
            "customer_name":customer_name,
            # "customer_address":customer_address,
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        bich_man = BichiltManager()
        rq = request.POST
        bichilt_date = rq.get('bichilt_date', '')
        zadgai_bichilt = rq.get('zadgai_bichilt', '0')
        description = rq.get('description', '')
        day = rq.get('day_zaalt', '')
        night = rq.get('night_zaalt', '')
        is_problem = rq.get('is_problem', '')
        if is_problem == '':
            is_problem = "0"
        if night == '':
            night = "0"
        rush = rq.get('rush_zaalt', '')
        if rush == '':
            rush = "0"
        selected_bichilt = None
        try:
            selected_bichilt = Bichilt.objects.get(id=id)
        except Bichilt.DoesNotExist:
            redirect("/home/borluulalt/bichilt_list/1/")
        b_date = datetime.datetime.strptime(bichilt_date, '%Y-%m-%d')
        response = bich_man.edit_bichilt("1", selected_bichilt, b_date, zadgai_bichilt, day, night, rush, description, request.user.id, is_problem)
        if response["code"] == 400:
            return BichiltAdd.error_builder_with_return(self, request, response["code"], response["description"], bichilt_date)
        return redirect("/home/borluulalt/bichilt_list/1/")


class BichiltSubStationAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = 'homepage/borluulalt/bichilt_ded_stants_add.html'
    q_bichil_list = "to"
    login_url = '/home/index'
    permission_required = 'data.add_bichilt'
    menu = "3"
    sub = "2"

    def get(self, request, *args, **kwargs):
        data = {}
        ded_stants = DedStants.objects.filter(is_active="1")
        data["ded_stants"] = ded_stants
        data["urlz"] = "/home/borluulalt/bichilt_ded_stants_add"
        data["menu"] = self.menu
        data["sub"] = self.sub
        return render(request, self.template_name, data)


    def post(self, request, *args, **kwargs):
        bich_man = BichiltManager()
        rq = request.POST
        bichilt_date = rq.get('bichilt_date', '')
        dedstants_code = rq.get('station_code_select', '')
        tooluur_number = rq.get('tooluur_select', '')
        day = rq.get('day_zaalt', '')
        night = rq.get('night_zaalt', '')
        if night == '' or night == None:
            night = "0"
        rush = rq.get('rush_zaalt', '')
        if rush == '' or rush == None:
            rush = "0"
        b_date = datetime.datetime.strptime(bichilt_date, '%Y-%m-%d')
        response = bich_man.create_bichilt("0", tooluur_number, dedstants_code, b_date, "0", day, night, rush, "", request.user.id, "0")
        if response["code"] == 400:
            return self.error_builder_with_return(request, response["code"], response["description"], bichilt_date)
        else:
            return self.success_builder_with_return(request, bichilt_date)

    def error_builder_with_return(self, request, code, description, date):
        ded_stants = DedStants.objects.filter(is_active="1")
        messages.warning(request, description)

        data = {
            "add_q":{
                "bichilt_date":date,
            },
            "error":{
                "code":code,
                "description":description
            },
            "menu":self.menu,
            "sub":self.sub
        }
        data["ded_stants"] = ded_stants
        data["urlz"] = "/home/borluulalt/bichilt_add"
        return render(request, self.template_name, data)

    def success_builder_with_return(self, request, date):
        messages.success(request, "Амжилттай хадгалагдлаа.")
        data = {
                "add_q":{
                    "bichilt_date":date,
                },
                "success":"True",
                "menu":self.menu,
                "sub":self.sub
            }
        ded_stants = DedStants.objects.filter(is_active="1")
        data["ded_stants"] = ded_stants
        data["urlz"] = "/home/borluulalt/bichilt_ded_stants_add"
        return render(request, self.template_name, data)


class BichiltSubStationEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = 'homepage/borluulalt/bichilt_ded_stants_add.html'
    login_url = '/home/index'
    permission_required = 'data.change_bichilt'
    menu = "3"
    sub = "2"

    def get(self, request, id, *args, **kwargs):
        selected_bichilt = None
        try:
            selected_bichilt = Bichilt.objects.get(id=id)
        except Bichilt.DoesNotExist:
            redirect("/home/borluulalt/bichilt_list/3/")
        prev_bichilt = {}
        if selected_bichilt.prev_bichilt_id != "0" and selected_bichilt.prev_bichilt_id != None:
            prev = Bichilt.objects.get(id=selected_bichilt.prev_bichilt_id)
            prev_bichilt['day'] = prev.day_balance
            prev_bichilt['night'] = prev.night_balance
            prev_bichilt['rush'] = prev.rush_balance
            prev_bichilt['created_date'] =  prev.bichilt_date.strftime("%Y-%m-%d")
        else:
            prev_bichilt['day'] = selected_bichilt.tooluur.tooluur.balance_value
            prev_bichilt['night'] = selected_bichilt.tooluur.tooluur.balance_value_night
            prev_bichilt['rush'] = selected_bichilt.tooluur.tooluur.balance_value_rush
            prev_bichilt['created_date'] =  selected_bichilt.tooluur.tooluur.installed_date.strftime("%Y-%m-%d")

        data = {
            "urlz":"/home/borluulalt/bichilt_ded_stants_edit/" + id + "/",
            "edit_data":selected_bichilt,
            "prev_data":prev_bichilt,
            "add_q":{
                "bichilt_date":selected_bichilt.bichilt_date.strftime("%Y-%m-%d"),
            },
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        bichilt_date = rq.get('bichilt_date', '')
        day = rq.get('day_zaalt', '')
        night = rq.get('night_zaalt', '')
        if night == '':
            night = "0"
        rush = rq.get('rush_zaalt', '')
        if rush == '':
            rush = "0"

        selected_bichilt = None
        try:
            selected_bichilt = Bichilt.objects.get(id=id)
        except Bichilt.DoesNotExist:
            redirect("/home/borluulalt/bichilt_list/3/")
        b_date = datetime.datetime.strptime(bichilt_date, '%Y-%m-%d')
        response = BichiltManager().edit_bichilt("0", selected_bichilt, b_date, "0", day, night, rush, "", request.user.id, "0")
        if response["code"] == 400:
            return selected_bichilt.error_builder_with_return(request, response["code"], response["description"], bichilt_date)
        messages.success(request, "Амжилттай хадгалагдлаа.")
        return redirect("/home/borluulalt/bichilt_list/3/")


class BichiltView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = 'homepage/borluulalt/bichilt_add.html'
    login_url = '/home/index'
    permission_required = 'data.view_bichilt'
    menu = "3"
    sub = "2"

    def get(self, request, id, *args, **kwargs):
        selected_bichilt = None
        customer_address = ''
        try:
            selected_bichilt = Bichilt.objects.get(id=id)
            address = Address.objects.filter(customer=selected_bichilt.tooluur.customer).first()
            if address is not None:
                customer_address = address.address_name
        except Bichilt.DoesNotExist:
            redirect("/home/borluulalt/bichilt_list/1/")
        prev_bichilt = {}
        if selected_bichilt.prev_bichilt_id != "0" and selected_bichilt.prev_bichilt_id != None:
            prev = Bichilt.objects.get(id=selected_bichilt.prev_bichilt_id)
            prev_bichilt['day'] = prev.day_balance
            prev_bichilt['night'] = prev.night_balance
            prev_bichilt['rush'] = prev.rush_balance
            prev_bichilt['created_date'] =  prev.bichilt_date.strftime("%Y-%m-%d")
        else:
            prev_bichilt['day'] = selected_bichilt.tooluur.tooluur.balance_value
            prev_bichilt['night'] = selected_bichilt.tooluur.tooluur.balance_value_night
            prev_bichilt['rush'] = selected_bichilt.tooluur.tooluur.balance_value_rush
            prev_bichilt['created_date'] =  selected_bichilt.tooluur.tooluur.installed_date.strftime("%Y-%m-%d")
        customer_name = selected_bichilt.tooluur.customer.last_name + " " + selected_bichilt.tooluur.customer.first_name
        geree = Geree.objects.filter(customer_code=selected_bichilt.tooluur.customer_code).first()
        if selected_bichilt.tooluur.customer.customer_angilal == "0":
            customer_angilal = "1"
            amp_coff = 1
            if selected_bichilt.tooluur.guidliin_trans != None:
                amp_coff = selected_bichilt.tooluur.guidliin_trans.multiply_coef
        else:
            customer_angilal = "0"
            geree = Geree.objects.get(customer_code=selected_bichilt.tooluur.customer_code)
            amp_coff = 1

        try:
            if geree is not None:
                tariff = PriceTariff.objects.get(bus_type=geree.bus_type, une_type=customer_angilal)

            price = {
                "day_price":tariff.odor_une,
                "night_price":tariff.shono_une,
                "rush_price":tariff.orgil_une
            }
        except PriceTariff.DoesNotExist:
            price = {
                "day_price":1,
                "night_price":1,
                "rush_price":1
            }
        data = {
            "urlz":"/home/borluulalt/bichilt_edit/" + id + "/",
            "edit_data":selected_bichilt,
            "prev_data":prev_bichilt,
            "price":price,
            "coeff":amp_coff,
            "customer_name":customer_name,
            "customer_address":customer_address,
            "tooluur_name":selected_bichilt.tooluur.tooluur.number + " " + selected_bichilt.tooluur.tooluur.name,
            "type":"1",
            "add_q":{
                "bichilt_date":selected_bichilt.bichilt_date.strftime("%Y-%m-%d"),
            },
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)


class BichiltSubStationView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = 'homepage/borluulalt/bichilt_ded_stants_add.html'
    login_url = '/home/index'
    permission_required = 'data.view_bichilt'

    def get(self, request, id, *args, **kwargs):
        selected_bichilt = None
        try:
            selected_bichilt = Bichilt.objects.get(id=id)
        except Bichilt.DoesNotExist:
            redirect("/home/borluulalt/bichilt_list/3/")
        prev_bichilt = {}
        if selected_bichilt.prev_bichilt_id != "0" and selected_bichilt.prev_bichilt_id != None:
            prev = Bichilt.objects.get(id=selected_bichilt.prev_bichilt_id)
            prev_bichilt['day'] = prev.day_balance
            prev_bichilt['night'] = prev.night_balance
            prev_bichilt['rush'] = prev.rush_balance
            prev_bichilt['created_date'] =  prev.bichilt_date.strftime("%Y-%m-%d")
        else:
            prev_bichilt['day'] = selected_bichilt.tooluur.tooluur.balance_value
            prev_bichilt['night'] = selected_bichilt.tooluur.tooluur.balance_value_night
            prev_bichilt['rush'] = selected_bichilt.tooluur.tooluur.balance_value_rush
            prev_bichilt['created_date'] =  selected_bichilt.tooluur.tooluur.installed_date.strftime("%Y-%m-%d")
        data = {
            "urlz":"/home/borluulalt/bichilt_ded_stants_edit/" + id + "/",
            "edit_data":selected_bichilt,
            "prev_data":prev_bichilt,
            "type":"1",
            "add_q":{
                "bichilt_date":selected_bichilt.bichilt_date.strftime("%Y-%m-%d"),
            },
        }
        return render(request, self.template_name, data)


class BichiltRemove(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_bichilt'

    def get(self, request, id, *args, **kwargs):
        paths = str(request.path).split('/')
        # path = paths[len(paths)]
        print(str(request.path))
        # print(str(path))

        try:
            selected_bichilt = Bichilt.objects.filter(id=id).first()
            if selected_bichilt is not None:
                selected_bichilt.delete()
                messages.success(request, "Амжилттай устгагдлаа.")
            else:
                messages.error(request, "Устахад алдаа гарлаа.")
            return redirect("/home/borluulalt/bichilt_list/1/")
        except:
            return redirect("/home/borluulalt/bichilt_list/1/")

def get_user_zaalt(request):
    data = {}
    error = {}
    last_bichilt = {}
    customer_data = {}
    tooluur = []
    code = request.GET['user_code']
    tooluur_customers = TooluurCustomer.objects.filter(customer_code=code, is_active=1)
    if len(tooluur_customers) > 0:
        i = 0
        tooluur_cus = None
        for item in tooluur_customers:
            if i == 0:
                i += 1
                tooluur_cus = item
                bichilt_list = item.bichilt_set.all()
                if len(bichilt_list) > 0:
                    bichilt = bichilt_list[0]
                    last_bichilt['last_date'] = bichilt.bichilt_date.strftime("%Y-%m-%d")
                    last_bichilt['day'] = bichilt.day_balance
                    last_bichilt['night'] = bichilt.night_balance
                    last_bichilt['rush'] = bichilt.rush_balance
                else:
                    last_bichilt['last_date'] = item.tooluur.installed_date.strftime("%Y-%m-%d")
                    last_bichilt['day'] = item.tooluur.balance_value
                    last_bichilt['night'] = item.tooluur.balance_value_night
                    last_bichilt['rush'] = item.tooluur.balance_value_rush
            tooluur.append({'tooluur_code': item.tooluur.number, 'tooluur_id': item.tooluur.id, 'tooluur_type':item.tooluur.tariff, 'tooluur_name':item.tooluur.name})

        avg_q = "SELECT to_cu.id, AVG(bi.day_diff) as day_avg, AVG(bi.rush_diff) as rush_avg, AVG(bi.night_diff) as night_avg  FROM data_bichilt bi INNER JOIN data_tooluurcustomer AS to_cu ON bi.tooluur_id = to_cu.id WHERE to_cu.id=%s ORDER BY month , year DESC LIMIT 3;"%tooluur_cus.id

        avg_list = list(Bichilt.objects.raw(avg_q))
        averages = None
        if len(avg_list) > 0:
            avg = avg_list[0]
            averages = {}
            averages["day_avg"] = avg.day_avg
            averages["night_avg"] = avg.day_avg
            averages["rush_avg"] = avg.day_avg
        data["averages"] = averages

        customer = Customer.objects.get(code=code, is_active=1)
        customer_data["name"] = customer.first_name + ' '+ customer.last_name
        # customer_data["address"] = customer.address_name
        # print("customer angilal = ", customer.customer_angilal)
        if customer.customer_angilal == "0":
            customer_angilal = "1"
            amp_coff = 1
            if tooluur_cus != None:
                if tooluur_cus.guidliin_trans != None:
                    amp_coff = float(tooluur_cus.guidliin_trans.multiply_coef)
            data["coeff"] = amp_coff

        else:
            customer_angilal = "0"
            data["coeff"] = 1
        geree = Geree.objects.get(customer_code=code, is_active=1)
        try:
            tariff = PriceTariff.objects.get(bus_type=geree.bus_type, une_type=customer_angilal, is_active=1)
            data['price'] = {
                "day_price":tariff.odor_une,
                "night_price":tariff.shono_une,
                "rush_price":tariff.orgil_une
            }
        except PriceTariff.DoesNotExist:
            data['price'] = {
                "day_price":1,
                "night_price":1,
                "rush_price":1
            }
    else:
        error['code'] = '1001'
        error['description'] = 'Хэрэглэгчийн дугаар буруу байна. Та дахин шалгаад оруулна уу.'
    if len(error) > 0:
        data['error'] = error
    data['last_bichilt'] = last_bichilt
    data['tooluurs'] = tooluur
    data['customer'] = customer_data
    return HttpResponse(simplejson.dumps(data),  content_type='application/json')


def get_tooluur_zaalt(request):
    data = {}
    last_bichilt = {}
    tooluur_id = request.GET['tooluur_id']
    user_code = request.GET['code']
    type = request.GET['type']
    tooluur_customer = None
    if type == "0":
        tooluur_customer = TooluurCustomer.objects.get(tooluur__number=tooluur_id, customer_code=user_code, is_active=1)
        if tooluur_customer.customer.customer_angilal == "0":
            customer_angilal = "1"
            amp_coff = 1
            if tooluur_customer.guidliin_trans != None:
                amp_coff = tooluur_customer.guidliin_trans.multiply_coef
            data["coeff"] = amp_coff
        else:
            customer_angilal = "0"
            data["coeff"] = 1

        geree = Geree.objects.get(customer_code=user_code)
        try:
            tariff = PriceTariff.objects.get(bus_type=geree.bus_type, une_type=customer_angilal)
            data['price'] = {
                "day_price":tariff.odor_une,
                "night_price":tariff.shono_une,
                "rush_price":tariff.orgil_une
            }
        except PriceTariff.DoesNotExist:
            data['price'] = {
                "day_price":1,
                "night_price":1,
                "rush_price":1
            }
    elif type == "1":
        tooluur_customer = TooluurCustomer.objects.get(tooluur__number=tooluur_id, dedstants__id=user_code, is_active=1)
    elif type == "2":
        tooluur_customer = TooluurCustomer.objects.get(tooluur__number=tooluur_id, bair__id=user_code, is_active=1)

    bichilt_list = tooluur_customer.bichilt_set.all().order_by('-id')
    if len(bichilt_list) > 0:
        bichilt = bichilt_list[0]
        last_bichilt['last_date'] = bichilt.bichilt_date.strftime("%Y-%m-%d")
        last_bichilt['day'] = bichilt.day_balance
        last_bichilt['night'] = bichilt.night_balance
        last_bichilt['rush'] = bichilt.rush_balance
    else:
        last_bichilt['last_date'] = tooluur_customer.tooluur.installed_date.strftime("%Y-%m-%d")
        last_bichilt['day'] = tooluur_customer.tooluur.balance_value
        last_bichilt['night'] = tooluur_customer.tooluur.balance_value_night
        last_bichilt['rush'] = tooluur_customer.tooluur.balance_value_rush

    avg_q = "SELECT to_cu.id, AVG(bi.day_diff) as day_avg, AVG(bi.rush_diff) as rush_avg, AVG(bi.night_diff) as night_avg  FROM data_bichilt bi INNER JOIN data_tooluurcustomer AS to_cu ON bi.tooluur_id = to_cu.id WHERE to_cu.id=%s ORDER BY month , year DESC LIMIT 3;" % tooluur_customer.id
    avg_list = list(Bichilt.objects.raw(avg_q))
    averages = None
    if len(avg_list) > 0:
        avg = avg_list[0]
        averages = {}
        averages["day_avg"] = avg.day_avg
        averages["night_avg"] = avg.day_avg
        averages["rush_avg"] = avg.day_avg
    data["averages"] = averages
    data['last_bichilt'] = last_bichilt
    data['tooluur_type'] = tooluur_customer.tooluur.tariff
    return HttpResponse(simplejson.dumps(data),  content_type='application/json')

def get_sub_stations_tooluur(request):
    data = {}
    tooluur = []
    station_id = request.GET['station_id']
    tooluur_customers = TooluurCustomer.objects.filter(dedstants_id=station_id, is_active="1")
    if len(tooluur_customers) > 0:
        for item in tooluur_customers:
            tooluur.append({'tooluur_code': item.tooluur.number, 'tooluur_name': item.tooluur.name, 'tooluur_id': item.tooluur.id, 'tooluur_type':item.tooluur.tariff})
    data['tooluurs'] = tooluur
    return HttpResponse(simplejson.dumps(data),  content_type='application/json')