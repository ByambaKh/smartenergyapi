import xlwt
from xlwt import Alignment, Borders

__author__ = 'L'
from django.shortcuts import render, HttpResponse
from django.views import View
from apps.homepage.forms import *
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from apps.extra import *
import simplejson


class BichiltBalanceCalculator():
    get_ded_stants_q = """
        SELECT name, code, id, etseg_ded_stants 
        FROM data_dedstants 
        WHERE ( etseg_ded_stants=0 OR etseg_ded_stants=null )
        and is_active=1 """
    get_bair_q = "SELECT name, id FROM data_bair WHERE id IN (SELECT bair_id FROM data_tooluurcustomer WHERE id IN (SELECT tooluur_id FROM data_bichilt WHERE user_type = '2' AND month='%s' AND year='%s'))"
    get_dedstants_bichilt_q = "SELECT *FROM data_bichilt as bi INNER JOIN data_tooluurcustomer as tocu ON bi.tooluur_id=tocu.id WHERE tocu.dedstants_id='%s' and month='%s' and year='%s' and bi.is_active='1'"
    get_child_tooluur_bichilt_q = """
        SELECT *
        FROM data_bichilt AS bi 
        INNER JOIN data_tooluurcustomer AS tocu ON bi.tooluur_id=tocu.id 
        WHERE  bi.month='%s' AND bi.year='%s' AND tocu.id IN (
            SELECT id 
            FROM data_tooluurcustomer 
            WHERE flow_id IN (
                SELECT id  
                FROM data_tooluurcustomer 
                WHERE dedstants_id=%s
                and flow_type=0
            )
            and customer_id is null
        ) """
    get_child_tooluur_withparent_bichilt_q = "select *from data_bichilt as bi INNER JOIN data_tooluurcustomer as tocu ON bi.tooluur_id=tocu.id WHERE bi.month='%s' and bi.year='%s' and tocu.dedstants_id in (select id from data_dedstants where etseg_ded_stants='%s' and is_active='1');"
    get_bair_child_bichilt_q = 'SELECT *FROM data_bichilt WHERE tooluur_id IN (SELECT id FROM data_tooluurcustomer WHERE month="%s" AND year="%s" AND flow_id IN (SELECT id FROM data_tooluurcustomer WHERE bair_id=%s AND is_active=1));'

    connected_bairs = []

    its_bottom_dedstants = False

    def get_balanceditems_by_date(self, month, year, parent_id, type):
        if type == 0:
            return self.get_ded_stantsitems_by_date(month, year, parent_id)
        else:
            return self.get_bairs_by_date(month, year)

    def get_ded_stantsitems_by_date(self, month, year, parent_id):
        sub_stations = self.get_sub_stations(month, year, parent_id)
        ded_stants_items = []
        for item in sub_stations:
            if (self.its_bottom_dedstants):
                q = """
                    select *
                    from data_bichilt b
                    join data_tooluurcustomer tc on b.tooluur_id=tc.id
                    join data_tooluurcustomer tc_parent on tc.flow_id=tc_parent.id
                    and b.is_active=1
                    and b.month=""" + str(month) + """
                    and b.year=""" + str(year) + """
                    and tc_parent.flow_type=0
                    and tc_parent.dedstants_id= """ + str(item.id)
                dedstants_bichilt = Bichilt.objects.raw(q)
            else:
                dedstants_bichilt = Bichilt.objects.filter(
                    is_active='1', month=month, year=year, tooluur__dedstants_id=item.id, tooluur__flow_type=0
                    , tooluur__is_active=1
                )
            self_energy_balance = 0
            for bichilt_item in dedstants_bichilt:
                self_energy_balance = self_energy_balance + self.calculate_energy_balance(bichilt_item)
            each_ded_stants = self.create_dic()
            each_ded_stants["id"] = item.id
            each_ded_stants["parent_id"] = item.etseg_ded_stants
            each_ded_stants["name"] = item.name
            each_ded_stants["self_balance"] = str(self_energy_balance)
            q = """
                SELECT h.id
                FROM data_tooluurcustomer tc
                join data_tooluurcustomer tc_child on tc.id = tc_child.flow_id
                join data_tooluurcustomer tc2 on tc.tooluur_id=tc2.tooluur_id
                join data_hasagdahtooluur h on tc2.id = h.head_tool_cus_id
                and tc_child.id = h.child_tool_cus_id
                and tc.dedstants_id = """ + str(item.id) + """
                and tc.is_active = 1
                and tc2.is_active = 1
            """
            if len(list(HasagdahTooluur.objects.raw(q))) > 0:
                each_ded_stants["childs_balance"] = str(self_energy_balance)
            else:
                each_ded_stants["childs_balance"] = self.calculate_child_energy_coff(year, month, item.id, 0)
            each_ded_stants = self.get_parent_name(each_ded_stants)
            each_ded_stants = self.calculate_lost_balance(each_ded_stants)
            ded_stants_items.append(each_ded_stants)
        return ded_stants_items

    def get_bairs_by_date(self, month, year):
        bairs = list(Bair.objects.raw(self.get_bair_q % (month, year)))
        bair_items = []
        for item in bairs:
            bair_bichilts = Bichilt.objects.filter(tooluur__bair_id=item.id, year=year, month=month)
            self_energy_balance = 0
            for bichilt_item in bair_bichilts:
                self_energy_balance = self_energy_balance + self.calculate_energy_balance(bichilt_item)
            each_bair = self.create_dic()
            each_bair["id"] = item.id
            each_bair["self_balance"] = str(self_energy_balance)
            each_bair["name"] = item.name
            each_bair["childs_balance"] = self.calculate_child_energy_coff(year, month, item.id, 1)
            each_bair = self.calculate_lost_balance(each_bair)
            bair_items.append(each_bair)
        return bair_items

    def get_sub_stations(self, month, year, parent_id):
        if parent_id == "0":
            # sub_stations = DedStants.objects.filter(Q(etseg_ded_stants=0) | Q(etseg_ded_stants=None), is_active="1")
            sub_stations = DedStants.objects.raw(self.get_ded_stants_q)
        else:
            sub_stations = list(DedStants.objects.filter(etseg_ded_stants=parent_id, is_active="1"))
            if len(sub_stations) == 0:
                sub_stations = list(DedStants.objects.filter(id=parent_id, is_active="1"))
                self.its_bottom_dedstants = True
        return sub_stations

    def get_childs(self, month, year, id, type):
        if type == 0:
            if (self.its_bottom_dedstants):
                q = """
                    SELECT b.*
                    FROM data_tooluurcustomer tc
                    join data_tooluurcustomer tc_parent on tc.flow_id=tc_parent.id 
                    join data_tooluurcustomer tc_child on tc_child.flow_id=tc.id
                    join data_bichilt b on tc_child.id=b.tooluur_id
                    and tc_parent.dedstants_id= """ + str(id) + """
                    and tc_parent.flow_type=0
                    and b.month=    """ + month + """
                    and b.year= """ + year
            else:
                q = """
                        SELECT *
                        FROM data_bichilt AS bi 
                        INNER JOIN data_tooluurcustomer AS tc_child ON bi.tooluur_id=tc_child.id 
                        join data_tooluurcustomer tc on tc_child.flow_id=tc.id
                        and tc.dedstants_id=%s
                        and tc.flow_type=0
                        and tc_child.customer_id is null
                        and bi.month=%s AND bi.year=%s """ % (str(id), month, year)
            child_list = list(Bichilt.objects.raw(q))
            # bichilt_list = Bichilt.objects.filter(year=year, month=month, tooluur__flow_id=id)
            # print("bichilt_list ORM === >", bichilt_list)
            # print("bichilt_list RAW === >", child_list)
            # print(q)
        else:
            child_list = Bichilt.objects.raw(self.get_bair_child_bichilt_q % (month, year, id))
        return child_list

    def calculate_child_energy_coff(self, current_year, current_month, id, type):
        child_list = self.get_childs(current_month, current_year, id, type)
        child_energy_balance = 0
        for child in child_list:
            child_energy_balance = child_energy_balance + self.calculate_energy_balance(child)
        return child_energy_balance

    def calculate_energy_balance(self, bichilt):
        coff = self.get_multiple_coeff(bichilt.tooluur)
        if bichilt.total_diff is not None:
            self_energy_balance = Decimal(bichilt.total_diff) * coff
        else:
            self_energy_balance = 0
        return self_energy_balance

    def calculate_lost_balance(self, dic):
        self_balance = Decimal(dic["self_balance"])
        childs_balance = Decimal(dic["childs_balance"])
        total_diff = self_balance - childs_balance
        if self_balance != 0:
            total_percentage = 100 - childs_balance * 100 / self_balance
            dic["lose_percentage"] = str(total_percentage)
        else:
            dic["lose_percentage"] = str("Боломжгүй")
        dic["lose_balance"] = str(total_diff)
        return dic

    def get_parent_name(self, dic):
        name = ""
        if dic["parent_id"] != "" and dic["parent_id"] != None:
            parent_stations = DedStants.objects.filter(id=Decimal(dic["parent_id"]))
            if len(parent_stations) > 0:
                name = parent_stations[0].name
        dic["parent_name"] = name
        return dic

    def create_dic(self):
        each_ded_stants = {
            "id": "",
            "parent_id": "",
            "parent_name": "",
            "self_balance": "",
            "name": "",
            "lose_percent": "0",
            "lose_balance": "0",
            "childs_balance": "",
        }
        return each_ded_stants

    def change_user_type(self, bichilt):
        if bichilt.type == "0":
            bichilt.type = "1"
            bichilt.save()
            return True
        return False

    def get_child_dedstants(self, type, id):
        item = []
        try:
            if type == 0:
                item = [DedStants.objects.get(id=id)]
            else:
                item = DedStants.objects.filter(etseg_ded_stants=id)
        except DedStants.DoesNotExist:
            no_error = ""
        return item

    def set_balance_submit(self, month, year, id):
        bairs = []
        no_more_child = True
        balancable_bichilts = []
        b = 0
        while no_more_child == True:
            items = self.get_child_dedstants(b, id)
            if len(items) > 0:
                for item in items:
                    q = self.get_balance_query(2, 1, item.id)
                    tooluurs = TooluurCustomer.objects.raw(q)
                    for tooluur_item in tooluurs:
                        bichilts = Bichilt.objects.filter(tooluur_id=tooluur_item.id, year=year, month=month)
                        if len(bichilts) > 0:
                            balancable_bichilts.append(bichilts.first())
                        if tooluur_item.customer_angilal == "2":
                            bairs.append(tooluur_item)
                b += 1
            else:
                no_more_child = False
        for bair_item in bairs:
            q = self.get_balance_query(4, 1, bair_item.id)
            tooluurs = TooluurCustomer.objects.raw(q)
            for tooluur_item in tooluurs:
                bichilts = Bichilt.objects.filter(tooluur_id=tooluur_item.id, year=year, month=month)
                if len(bichilts) > 0:
                    balancable_bichilts.append(bichilts.first())
        return balancable_bichilts

    def get_related_dedstants(self, id, year, month):
        related_array = []
        self.connected_bairs = []
        no_more_child = True
        while no_more_child == True:
            items = self.get_child_dedstants(len(related_array), id)
            if len(items) > 0:
                for item in items:
                    dic = {"name": item.name, "id": item.id}
                    dic["tooluurs"] = self.get_dedstants_balanced_values(item.id, year=year, month=month)
                    related_array.append(dic)
                    id = item.id
            else:
                no_more_child = False
        # bair_dic = {"name": "Орон сууцнуудын", "id": ""}
        # bair_dic["tooluurs"] = self.get_connected_bairs_balanced_values(year, month)
        # related_array.append(bair_dic)
        return related_array

    def get_prev_bichilt(self, item_tooluur, type):
        bichilt_list = item_tooluur.bichilt_set.all().order_by('created_date')
        if type == 0:
            if len(bichilt_list) > 0:
                bichilt = bichilt_list[0]
                balance = float(bichilt.day_balance) + float(bichilt.night_balance) + float(bichilt.rush_balance)
            else:
                balance_value_night = item_tooluur.tooluur.balance_value_night
                if balance_value_night == '':
                    balance_value_night = 0
                balance_value_rush = item_tooluur.tooluur.balance_value_rush
                if balance_value_rush == '':
                    balance_value_rush = 0
                balance = float(item_tooluur.tooluur.balance_value) + float(balance_value_night) + float(
                    balance_value_rush)
        return str(balance)

    def get_balance_query(self, level, type, id):
        q = """
            SELECT tc_child_""" + str(level) + """.*
            FROM data_tooluurcustomer tc_child_1 """
        if (level > 1):
            q += """
            join data_tooluurcustomer tc_child_2 on tc_child_1.id=tc_child_2.flow_id
            """
        if (level > 2):
            q += """
            join data_tooluurcustomer tc_child_3 on tc_child_2.id=tc_child_3.flow_id
            """
        if (level > 3):
            q += """
            join data_tooluurcustomer tc_child_4 on tc_child_3.id=tc_child_4.flow_id
            """
        q += """
            where tc_child_1.dedstants_id=%s """ % id
        return q

    def get_tooluurcus_by_from_tolgoi(self, level, type, id, year, month):
        q = """
                    SELECT distinct tc_child_""" + str(level) + """.*
                    FROM data_tooluurcustomer tc_child_1 """
        if (level > 1):
            q += """
                    join data_tooluurcustomer tc_child_2 on tc_child_1.id=tc_child_2.flow_id
                    and tc_child_2.flow_type != 0
                    and ( 
                        tc_child_2.id in (
                            select distinct flow_id
                            from data_tooluurcustomer tc_child_2_child
                        ) or tc_child_2.flow_type = 2
                    )
                    """
        if (level > 2):
            q += """
                    join data_tooluurcustomer tc_child_3 on tc_child_2.id=tc_child_3.flow_id
                    and tc_child_3.flow_type != 0
                    and tc_child_3.bair_id is null
                    join data_tooluurcustomer tc_child_3_child on tc_child_3.id = tc_child_3_child.flow_id
                    """
        if (level > 3):
            q += """
                    join data_tooluurcustomer tc_child_4 on tc_child_3.id = tc_child_4.flow_id
                    and tc_child_4.bair_id is null
                    join data_tooluurcustomer tc_child_4_child on tc_child_4.id = tc_child_4_child.flow_id
                    """
        q += """    where tc_child_1.dedstants_id = %s
                    and tc_child_1.flow_type=0 
                    AND tc_child_1.is_active = 1
                    """ % id
        tooluur_cus = TooluurCustomer.objects.raw(q)
        items = []
        for item in tooluur_cus:
            bair_bichilts = Bichilt.objects.filter(tooluur_id=item.id, year=year, month=month).order_by('id')
            if len(bair_bichilts) > 0:
                for bichilt in bair_bichilts:
                    dic = {}
                    dic["last_bichilt"] = float(bichilt.day_balance) + float(bichilt.night_balance) + float(
                        bichilt.rush_balance)
                    try:
                        prev_bichilt = Bichilt.objects.get(id=bichilt.prev_bichilt_id)
                        prev_value = float(prev_bichilt.day_balance) + float(prev_bichilt.night_balance) + float(
                            prev_bichilt.rush_balance)
                    except Bichilt.DoesNotExist:
                        tooluur = Tooluur.objects.get(id=item.tooluur_id)
                        prev_value = float(tooluur.balance_value)
                    dic["prev_bichilt"] = prev_value
                    if level < 30:
                        if bichilt.total_diff is not None:
                            dic["zoruu"] = bichilt.total_diff
                        else:
                            dic["zoruu"] = 0
                    else:
                        dic["zoruu"] = 0
                    dic["self_balance"] = self.calculate_energy_balance(bichilt)
                    if level < 3:
                        dic["child_balance"] = self.calculate_energy_balance(bichilt)
                    else:
                        dic["child_balance"] = float(bichilt.total_diff)
                    dic["id"] = item.id
                    dic["dedstants_id"] = 0
                    dic["name"] = item.tooluur.name
                    dic["multiple_coeff"] = self.get_multiple_coeff(item)
                    dic["number"] = item.tooluur.number
                    items.append(dic)
            else:
                dic = {}
                dic["last_bichilt"] = 0
                prev_value = self.get_prev_bichilt(item, 0)
                dic["prev_bichilt"] = prev_value
                dic["zoruu"] = 0
                dic["self_balance"] = 0
                dic["child_balance"] = 0
                dic["id"] = item.id
                dic["dedstants_id"] = 0
                dic["name"] = item.tooluur.name
                dic["multiple_coeff"] = self.get_multiple_coeff(item)
                dic["number"] = item.tooluur.number
                items.append(dic)
        return items

    def get_dedstants_balanced_values(self, id, year, month):
        balanced_values = []
        dic = []
        sub_dic = {}
        tooluurs = self.get_tooluurcus_by_from_tolgoi(0, 0, id=id, year=year, month=month)
        sub_dic["tooluurs"] = tooluurs
        sub_dic["type"] = 0
        dic.append(sub_dic)
        balanced_values.append(dic)
        return balanced_values

    def get_connected_bairs_balanced_values(self, year, month):
        balanced_values = []
        for bair_id in self.connected_bairs:
            dic = []
            for type in range(0, 2):
                sub_dic = {}
                tooluurs = self.get_tooluurcus_by_from_tolgoi(4, type, id=bair_id["id"], year=year, month=month)
                sub_dic["tooluurs"] = tooluurs
                sub_dic["type"] = type
                sub_dic["name"] = bair_id["name"]
                dic.append(sub_dic)
            balanced_values.append(dic)
        return balanced_values

    def get_multiple_coeff(self, tooluur_cus):
        amp_coff = 1
        volt_coff = 1
        if tooluur_cus.guidliin_trans != None:
            amp_coff = Decimal(tooluur_cus.guidliin_trans.multiply_coef)
        if tooluur_cus.huchdeliin_trans != None:
            volt_coff = Decimal(tooluur_cus.huchdeliin_trans.multiply_coef)
        return amp_coff * volt_coff


class BalanceView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = 'homepage/borluulalt/bichilt_balance.html'
    login_url = '/home/index'
    permission_required = 'data.view_bichiltbalance'
    # permission_required = ('data.view_bichiltbalance', 'data.change_bichiltbalance')
    menu = "3"
    sub = "8"

    def get(self, request, id, *args, **kwargs):
        year_array = get_years()
        month_array = get_months()
        current_date = datetime.datetime.now().date()
        current_year = str(current_date.year)
        if 'month' in request.session:
            current_month = request.session['month']
        else:
            current_month = str(current_date.month)

        b_cal = BichiltBalanceCalculator()

        ded_stantss = DedStants.objects.filter(is_active=1)
        bairs = Bair.objects.filter(is_active=1)

        ded_stants_items = b_cal.get_balanceditems_by_date(current_month, current_year, str(id), 0)
        data = {
            "urlz": "/home/borluulalt/bichilt_balance/" + id,
            "years": year_array,
            "type": "0",
            "months": month_array,
            "current_year": current_year,
            "current_month": current_month,
            "data": ded_stants_items,
            "ded_stantss": ded_stantss,
            "selected_dedstants": int(id),
            "selected_bair": 0,
            "bairs": bairs,
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        selected_year = rq.get('year_select', '')
        selected_month = rq.get('month_select', '')
        request.session['month'] = selected_month
        type = rq.get('select_angilal', '0')
        selected_ded_stants = rq.get('select_ded_stants', '0')
        selected_bair = rq.get('selected_bair', '0')
        year_array = get_years()
        month_array = get_months()
        current_year = selected_year
        current_month = selected_month
        if selected_ded_stants != '0':
            id = selected_ded_stants
        ded_stantss = DedStants.objects.filter(is_active=1)
        bairs = Bair.objects.filter(is_active=1)
        data = {
            "urlz": "/home/borluulalt/bichilt_balance/" + id,
            "type": type,
            "years": year_array,
            "months": month_array,
            "current_year": current_year,
            "current_month": current_month,
            "selected_stants": int(selected_ded_stants),
            "selected_bair": int(selected_bair),
            "ded_stantss": ded_stantss,
            "bairs": bairs,
            "menu": self.menu,
            "sub": self.sub
        }
        b_cal = BichiltBalanceCalculator()
        ded_stants_items = b_cal.get_balanceditems_by_date(current_month, current_year, str(id), int(type))
        data["data"] = ded_stants_items
        if "balance_submit" in rq:
            sub_stations = b_cal.get_sub_stations(selected_month, selected_year, str(id))
            change_to_type_count = 0
            count = 0
            for item in sub_stations:
                substation_bichilt_q = b_cal.get_dedstants_bichilt_q % (str(item.id), selected_month, selected_year)
                substation_childs = b_cal.get_substation_childs(current_month, current_year, item.code, str(id))
                dedstants_bichilt = list(Bichilt.objects.raw(substation_bichilt_q))
                if len(dedstants_bichilt) != 0:
                    self_bichilt = dedstants_bichilt[0]
                    if b_cal.change_user_type(self_bichilt):
                        change_to_type_count += 1
                    count += 1
                for child in substation_childs:
                    if b_cal.change_user_type(child):
                        change_to_type_count += 1
                    count += 1
            success = {
                "count": str(count),
                "success_count": str(change_to_type_count)
            }
            data["success"] = success
        return render(request, self.template_name, data)

    def export_balance_xls(request, type, id, year, month):
        try:
            item1 = DedStants.objects.get(id=id)
            name = str(item1.id) + "_balance_" + year + "_" + month + ".xls"
        except:
            name = "balance.xls"
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="%s"' % name
        rb = BichiltBalanceCalculator()
        custom_style = ExportStyles()
        wb = xlwt.Workbook(encoding='utf-8')
        columns = ['Д/д', 'Шугамын нэр', 'Тоолуурын дугаар', 'Эхний заалт', 'Эцсийн заалт', 'Зөрүү', 'Үржих коэфф',
                   'ХАЦЭХ кВт цаг', 'Түгээсэн ЦЭХ кВт цаг', 'Алдагдал %-иар']
        bv = BalanceView()
        row_num = 0
        ws = wb.add_sheet(item1.name + " баланс", cell_overwrite_ok=True)
        header_name = item1.name + "-н энерги балансын тооцоо\n%s оны %s-р сар" % (year, month)
        ws.write_merge(row_num, 1, 0, 9, header_name, custom_style.center_header_style)
        row_num += 2
        connected_dedstants = []
        for level in range(1, 5):
            num = 1
            total_self_balance = 0
            total_child_balance = 0
            tooluurs = rb.get_tooluurcus_by_from_tolgoi(level, 0, id=id, year=year, month=month)
            if len(tooluurs) > 0:
                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], custom_style.normal_bold_bordered_style)
                    if col_num == 1 and col_num == 5:
                        ws.col(col_num).width = len(columns[col_num]) * 600
                    else:
                        ws.col(col_num).width = len(columns[col_num]) * 300
                row_num += 1
            for tooluur in tooluurs:
                col_num = 0
                ws.write(row_num, col_num, str(num), custom_style.center_text_with_border)
                col_num += 1
                ws.write(row_num, col_num, tooluur["name"], custom_style.center_text_with_border)
                col_num += 1
                ws.write(row_num, col_num, tooluur["number"], custom_style.center_text_with_border)
                col_num += 1
                ws.write(row_num, col_num, str(round(float(tooluur["prev_bichilt"]), 2)),
                         custom_style.center_text_with_border)
                col_num += 1
                ws.write(row_num, col_num, str(round(float(tooluur["last_bichilt"]), 2)),
                         custom_style.center_text_with_border)
                col_num += 1
                ws.write(row_num, col_num, str(round(float(tooluur["zoruu"]), 2)),
                         custom_style.center_text_with_border)
                col_num += 1
                ws.write(row_num, col_num, str(round(float(tooluur["multiple_coeff"]), 2)),
                         custom_style.center_text_with_border)
                col_num += 1
                ws.write(row_num, col_num, str(round(tooluur["self_balance"], 2)),
                         custom_style.center_text_with_border)
                total_self_balance += float(tooluur["self_balance"])
                col_num += 1
                total_child_balance += float(tooluur["child_balance"])
                col_num += 1
                # ws.write(row_num, col_num, "", custom_style.center_text_with_border)
                if tooluur["dedstants_id"] != 0:
                    # Холбогдолтой дэд станцуудыг бүртгэх
                    connected_dedstants.append(tooluur["dedstants_id"])
                num += 1
                row_num += 1
            if len(tooluurs) > 0:
                for custom_col_num in range(0, 10):
                    if custom_col_num == 1:
                        ws.write(row_num, custom_col_num, "Гаргалгааны дүн",
                                 custom_style.center_bold_text_with_border)
                    elif custom_col_num == 7:
                        ws.write(row_num, custom_col_num, str(round(total_self_balance, 2)),
                                 custom_style.get_right_alignment_bold())
                row_num += 1
                row_num = bv.xls_child_tooluurs(ws, row_num, id, year, month, total_self_balance, level)
            row_num += 1
        bv.xls_bair(wb, custom_style, id, columns, year, month)
        wb.save(response)
        return response

    def xls_bair(self, wb, custom_style, id, columns, year, month):
        ws = wb.add_sheet("Орон сууцнуудын баланс")
        for col_num in range(len(columns)):
            ws.col(col_num).width = 4000
        q = """
            select *
            from (
                SELECT distinct b.id
                , b.name
                , tc.dedstants_id
                FROM data_tooluurcustomer tc
                left join data_tooluurcustomer tc_child on tc.id=tc_child.flow_id
                left join data_tooluurcustomer tc_child_2 on tc_child.id=tc_child_2.flow_id
                left join data_tooluurcustomer tc_child_3 on tc_child_2.id=tc_child_3.flow_id
                left join data_tooluurcustomer tc_child_4 on tc_child_3.id=tc_child_4.flow_id
                join data_bair b on tc_child_4.bair_id=b.id
                    union
                SELECT distinct b.id
                , b.name
                , tc.dedstants_id
                FROM data_tooluurcustomer tc
                left join data_tooluurcustomer tc_child on tc.id=tc_child.flow_id
                left join data_tooluurcustomer tc_child_2 on tc_child.id=tc_child_2.flow_id
                join data_bair b on tc_child_2.bair_id=b.id
            ) a
            where dedstants_id= """ + id + """
            order by name
            """
        Bairs = Bair.objects.raw(q)
        row_num = 0
        for b in Bairs:
            ws.write(row_num, 1, "Байр " + b.name + " - н баланс тооцоо", custom_style.normal_bold_style)
            row_num += 1
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], custom_style.normal_bold_bordered_style)
            q = """
                SELECT b.*
                , t.name
                , t.number
                , ifnull ( b_prev.day_balance , t.balance_value ) day_balance_prev
                , IFNULL(th.multiply_coef,1)*IFNULL(tg.multiply_coef ,1) multiply_coef
                FROM data_tooluurcustomer tc
                join data_tooluur t on tc.tooluur_id=t.id
                join data_bichilt b on tc.id=b.tooluur_id
                and tc.bair_id=""" + str(b.id) + """
                and b.year=""" + year + """
                and b.month=""" + month + """
                left join data_bichilt b_prev on b.prev_bichilt_id=b_prev.id
                left join data_transformator th on tc.huchdeliin_trans_id=th.id
                left join data_transformator tg on tc.guidliin_trans_id=tg.id 
                order by t.name
                """
            Bichilts = Bichilt.objects.raw(q)
            num = 0
            bought_sum = 0
            for b1 in Bichilts:
                row_num += 1
                num += 1
                ws.write(row_num, 0, num, xlwt.XFStyle())
                ws.write(row_num, 1, b1.name, custom_style.center_text_with_border)
                ws.write(row_num, 2, b1.number, custom_style.center_text_with_border)
                ws.write(row_num, 3, b1.day_balance_prev, custom_style.center_text_with_border)
                ws.write(row_num, 4, b1.day_balance, custom_style.center_text_with_border)
                ws.write(row_num, 5, b1.total_diff, custom_style.center_text_with_border)
                ws.write(row_num, 6, b1.multiply_coef, custom_style.center_text_with_border)
                bought = float(b1.multiply_coef) * float(0 if b1.total_diff is None else b1.total_diff)
                bought_sum += bought
                ws.write(row_num, 7, bought, custom_style.center_text_with_border)
            row_num += 1
            ws.write(row_num, 1, "Гаргалгааны дүн", custom_style.center_bold_text_with_border)
            ws.write(row_num, 7, bought_sum, custom_style.center_text_with_border)
            q = """
                select *
                from (
                    SELECT b.*
                    , ifnull(addr.address_name, c.first_name) address_name
                    , t.number
                    , b_prev.day_balance day_balance_prev
                    , IFNULL(th.multiply_coef,1)*IFNULL(tg.multiply_coef ,1) multiply_coef
                    FROM data_tooluurcustomer tc
                    join data_tooluurcustomer tc_child on tc.id=tc_child.flow_id
                    join data_customer c on tc_child.customer_id=c.id
                    join data_tooluur t on tc_child.tooluur_id=t.id
                    join data_bichilt b on tc_child.id=b.tooluur_id
                    join data_bichilt b_prev on b.prev_bichilt_id=b_prev.id
                    and tc.bair_id= """ + str(b.id) + """
                    and b.year=""" + year + """
                    and b.month=""" + month + """
                    left join data_address addr on c.id = addr.customer_id
                    left join data_transformator th on tc_child.huchdeliin_trans_id=th.id
                    left join data_transformator tg on tc_child.guidliin_trans_id=tg.id
                ) bichilt
                order by REPLACE(address_name, ' ', '') , id
                """
            Bichilts = Bichilt.objects.raw(q)
            num = 0
            distributed_sum = 0
            for b in Bichilts:
                row_num += 1
                num += 1
                ws.write(row_num, 0, num, xlwt.XFStyle())
                ws.write(row_num, 1, b.address_name, custom_style.center_text_with_border)
                ws.write(row_num, 2, b.number, custom_style.center_text_with_border)
                ws.write(row_num, 3, b.day_balance_prev, custom_style.center_text_with_border)
                ws.write(row_num, 4, b.day_balance, custom_style.center_text_with_border)
                ws.write(row_num, 5, b.total_diff, custom_style.center_text_with_border)
                ws.write(row_num, 6, b.multiply_coef, custom_style.center_text_with_border)
                distributed = float(b.multiply_coef) * float(b.total_diff)
                distributed_sum += distributed
                ws.write(row_num, 8, distributed, custom_style.center_text_with_border)
            row_num += 1
            ws.write_merge(row_num, row_num, 0, 5, "Энерги балансын дүн", custom_style.center_bold_text_with_border)
            ws.write(row_num, 6, bought_sum - distributed_sum, custom_style.center_bold_text_with_border)
            ws.write(row_num, 7, bought_sum, custom_style.center_text_with_border)
            ws.write(row_num, 8, distributed_sum, custom_style.center_text_with_border)
            try:
                ws.write(row_num, 9, str(round(100 - distributed_sum / bought_sum * 100, 2)) + "%",
                         custom_style.center_bold_text_with_border)
            except:
                ws.write(row_num, 9, "", custom_style.center_bold_text_with_border)
            row_num += 1
        ws.col(0).width = 900
        ws.col(1).width = 8900
        ws.col(2).width = 5000
        ws.col(8).width = 5900

    def xls_child_tooluurs(self, ws, row_num, id, year, month, total_self_balance, level):
        custom_style = ExportStyles()
        q = """
            SELECT distinct t.id
            , t.name
            , t.number
            , IFNULL( b_prev.day_balance , t.balance_value ) day_balance_prev
            , b.day_balance
            , b.total_diff
            , IFNULL(th.multiply_coef,1)*IFNULL(tg.multiply_coef ,1) multiply_coef
            FROM data_tooluurcustomer tc
            join data_tooluurcustomer tc_child_1 on tc.id=tc_child_1.flow_id
            and tc_child_1.customer_angilal = 0
            and tc_child_1.is_active = 1
             """
        if (level > 1):
            q += """
            join data_tooluurcustomer tc_child_2 on tc_child_1.id=tc_child_2.flow_id
            and tc_child_1.flow_type != 0
            """
        if (level > 2):
            q += """
            join data_tooluurcustomer tc_child_3 on tc_child_2.id=tc_child_3.flow_id
            and tc_child_2.flow_type != 0
            and tc_child_2.bair_id is null
            """
        if (level > 3):
            q += """
            join data_tooluurcustomer tc_child_4 on tc_child_3.id=tc_child_4.flow_id
            """
        q += """
            join data_tooluur t on tc_child_""" + str(level) + """.tooluur_id=t.id
            join data_bichilt b on tc_child_""" + str(level) + """.id=b.tooluur_id 
            left join data_bichilt b_prev on b.prev_bichilt_id=b_prev.id
            left join data_transformator th on tc_child_""" + str(level) + """.huchdeliin_trans_id=th.id
            left join data_transformator tg on tc_child_""" + str(level) + """.guidliin_trans_id=tg.id
            where tc.dedstants_id=""" + id + """
            and tc.flow_type=0
            and b.year=""" + year + """
            and b.month=""" + month + """
            order by t.name , b.id """
        Bichilts = Tooluur.objects.raw(q)
        num = 1
        distributed_sum = 0
        for b in Bichilts:
            ws.write(row_num, 0, num, custom_style.center_text_with_border)
            ws.write(row_num, 1, b.name, custom_style.center_text_with_border)
            ws.write(row_num, 2, b.number, custom_style.center_text_with_border)
            ws.write(row_num, 3, b.day_balance_prev, custom_style.center_text_with_border)
            ws.write(row_num, 4, b.day_balance, custom_style.center_text_with_border)
            ws.write(row_num, 5, b.total_diff, custom_style.center_text_with_border)
            ws.write(row_num, 6, b.multiply_coef, custom_style.center_text_with_border)
            distributed = float(b.multiply_coef) * float(0 if b.total_diff is None else b.total_diff)
            distributed_sum += distributed
            ws.write(row_num, 8, distributed, custom_style.center_text_with_border)
            num += 1
            row_num += 1
        customers = []
        q = """
            SELECT distinct c.id , c.first_name , b.total_diff * IFNULL ( th.multiply_coef , 1 ) * 
                IFNULL ( tg.multiply_coef , 1 ) + IFNULL ( b2.total_diff , 0 ) * IFNULL ( th2.multiply_coef , 1 ) * 
                IFNULL ( tg2.multiply_coef , 1 )  - 
                sum( b_child.total_diff * IFNULL ( th_child.multiply_coef , 1 ) * IFNULL ( tg_child.multiply_coef , 1 ) ) distributed
            FROM data_tooluurcustomer tc_1 """
        if level > 1:
            q += """
                join data_tooluurcustomer tc_2 on tc_1.id = tc_2.flow_id  
            """
        q += """
            join data_tooluurcustomer tc_customer on tc_""" + str(level) + """.tooluur_id = tc_customer.tooluur_id
            join data_tooluurcustomer tc_child on tc_""" + str(level) + """.id = tc_child.flow_id 
            left join data_transformator th_child on tc_child.huchdeliin_trans_id = th_child.id
            left join data_transformator tg_child on tc_child.guidliin_trans_id = tg_child.id
            join data_bichilt b_child on tc_child.id = b_child.tooluur_id 
            and b_child.year = """ + year + """
            and b_child.month = """ + month + """
            join data_bichilt b on tc_""" + str(level) + """.id = b.tooluur_id
            and b.year = """ + year + """
            and b.month = """ + month + """
            left join data_transformator th on tc_""" + str(level) + """.huchdeliin_trans_id = th.id
            left join data_transformator tg on tc_""" + str(level) + """.guidliin_trans_id = tg.id
            """
        q += """
            join data_hasagdahtooluur h on tc_customer.id = h.head_tool_cus_id
            and tc_child.id = h.child_tool_cus_id
            left join data_tooluurcustomer tc_customer_2 on h.head_tool_cus2_id = tc_customer_2.id  
            left join data_bichilt b2 on tc_customer_2.id = b2.tooluur_id 
            and b2.year = """ + year + """
            and b2.month = """ + month + """
            left join data_transformator th2 on tc_customer_2.huchdeliin_trans_id = th2.id
            left join data_transformator tg2 on tc_customer_2.guidliin_trans_id = tg2.id
            join data_customer c on tc_customer.customer_id = c.id
            and tc_1.dedstants_id = """ + id + """
            and tc_1.flow_type = 0
            and tc_1.is_active = 1
            and tc_customer.is_active = 1 
            group by c.id """
        if level < 3:
            customers = Customer.objects.raw(q)
        for c in customers:
            ws.write(row_num, 0, num, custom_style.center_text_with_border)
            ws.write(row_num, 1, c.first_name, custom_style.center_text_with_border)
            ws.write(row_num, 8, c.distributed, custom_style.center_text_with_border)
            distributed_sum = total_self_balance
            num += 1
            row_num += 1
        ws.write_merge(row_num, row_num, 0, 5, "Энерги балансын дүн", custom_style.center_bold_text_with_border)
        ws.write(row_num, 6, total_self_balance - distributed_sum, custom_style.center_bold_text_with_border)
        ws.write(row_num, 7, total_self_balance, custom_style.center_bold_text_with_border)
        ws.write(row_num, 8, distributed_sum, custom_style.center_bold_text_with_border)
        ws.write(row_num, 9,
                 str(round(100 - distributed_sum / (total_self_balance, 1)[total_self_balance == 0] * 100, 2)) + "%",
                 custom_style.center_bold_text_with_border)
        return row_num

    def submit_balance(request, type, id, year, month):
        data = {}
        b_cal = BichiltBalanceCalculator()
        change_to_type_count = 0
        count = 0
        bichilts = b_cal.set_balance_submit(month=month, year=year, id=id)
        for bichilt_item in bichilts:
            print(bichilt_item.tooluur.customer.first_name)
            if b_cal.change_user_type(bichilt_item):
                change_to_type_count += 1
            count += 1
        success = {
            "count": str(count),
            "success_count": str(change_to_type_count)
        }
        data["success"] = success
        return HttpResponse(simplejson.dumps(data), content_type='application/json')


class ExportStyles():
    thin_border = Borders.THIN
    borders = Borders()
    borders.left = thin_border
    borders.right = thin_border
    borders.bottom = thin_border
    borders.top = thin_border

    alignment_center = Alignment()
    alignment_center.horz = Alignment.HORZ_CENTER

    alignment_right = Alignment()
    alignment_right.horz = Alignment.HORZ_RIGHT

    center_header_style = xlwt.XFStyle()
    center_header_style.alignment.vert = Alignment.VERT_CENTER
    center_header_style.alignment.horz = Alignment.HORZ_CENTER
    center_header_style.font.bold = True
    center_header_style.font.height = 0x00F0

    normal_bold_style = xlwt.XFStyle()
    normal_bold_style.font.bold = True

    normal_bold_bordered_style = xlwt.XFStyle()
    normal_bold_bordered_style.font.bold = True
    normal_bold_bordered_style.borders = borders

    normal_bordered_style = xlwt.XFStyle()
    normal_bordered_style.borders = borders

    center_text_with_border = normal_bordered_style
    center_text_with_border.alignment = alignment_center

    right_text_with_border = normal_bordered_style
    right_text_with_border.alignment = alignment_right

    right_bold_number_with_border = None

    center_bold_text_with_border = normal_bold_bordered_style
    center_bold_text_with_border.alignment = alignment_center

    def get_right_alignment_bold(self):
        if self.right_bold_number_with_border == None:
            alignment = Alignment()
            alignment.horz = Alignment.HORZ_RIGHT
            self.right_bold_number_with_border = self.normal_bold_bordered_style
            self.right_bold_number_with_border.alignment = alignment
        return self.right_bold_number_with_border

        # def get_excel(self, ws, row_number, text):
        #     for custom_col_num in range(0, 9):
        #         if custom_col_num == 1:
        #             ws.write(row_number, custom_col_num, text, self.center_text_with_border)
        #         else:
        #             ws.write(row_number, custom_col_num, "", self.center_text_with_border)

        # Sheet header, first row
        # # Sheet body, remaining rows
        # font_style = xlwt.XFStyle()
        #
        # rows = b
        # for row in rows:
        #     row_num += 1
        #     col_num = 0
        #
        #     ws.write(row_num, col_num, row["name"], font_style)
        #     col_num += 1
        #     ws.write(row_num, col_num, row["self_balance"], font_style)
        #     col_num += 1
        #     ws.write(row_num, col_num, row["childs_balance"], font_style)
        #     col_num += 1
        #     ws.write(row_num, col_num, row["lose_balance"], font_style)
        #     col_num += 1
        #     ws.write(row_num, col_num, row["lose_percentage"], font_style)
        #     col_num += 1
        #     ws.write(row_num, col_num, row["parent_name"], font_style)
        #     c = row["childs"]
        #     while (c != None):
        #         for r in c:
        #             row_num += 1
        #             col_num = 0
        #
        #             ws.write(row_num, col_num, r["name"], font_style)
        #             col_num += 1
        #             ws.write(row_num, col_num, r["self_balance"], font_style)
        #             col_num += 1
        #             ws.write(row_num, col_num, r["childs_balance"], font_style)
        #             col_num += 1
        #             ws.write(row_num, col_num, r["lose_balance"], font_style)
        #             col_num += 1
        #             ws.write(row_num, col_num, r["lose_percentage"], font_style)
        #             col_num += 1
        #             ws.write(row_num, col_num, r["parent_name"], font_style)
        #             c = r["childs"]
