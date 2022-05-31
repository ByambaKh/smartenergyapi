from django.shortcuts import render, redirect, HttpResponse
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages
import simplejson


class OroltGaraltList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_oroltgaralt'
    template_name = "homepage/burtgel/orolt_and_garalt_list.html"
    menu = "2"
    sub = "4"

    query = """SELECT tocu.id, tc.id AS h_id, ct.code AS h_code, ct.last_name h_last_name, ct.first_name AS h_first_name, br.name h_bair_name,
        ds.code AS h_deds_code, ds.name AS h_deds_name, tl.number AS h_tool_num, tl.name AS h_tool_name,
        cust.code AS ch_code, cust.last_name AS ch_last_name, cust.first_name AS ch_first_name, bair.name AS ch_bair_name,
        deds.code AS ch_deds_code, deds.name AS ch_deds_name, tool.number AS ch_tool_num, tool.name AS ch_tool_name
        FROM data_tooluurcustomer tocu JOIN data_tooluur tool ON tocu.tooluur_id = tool.id AND tool.is_active = '1'
        LEFT JOIN data_customer cust ON tocu.customer_id = cust.id AND cust.is_active = '1'
        LEFT JOIN data_bair bair ON tocu.bair_id = bair.id AND bair.is_active = '1'
        LEFT JOIN data_dedstants deds ON tocu.dedstants_id = deds.id AND deds.is_active = '1'
        LEFT JOIN data_tooluurcustomer tc ON tocu.flow_id = tc.id AND tc.is_active = '1'
        LEFT JOIN data_tooluur tl ON tc.tooluur_id = tl.id AND tl.is_active = '1'
        LEFT JOIN data_customer ct ON tc.customer_id = ct.id AND ct.is_active = '1'
        LEFT JOIN data_bair br ON tc.bair_id = br.id AND br.is_active = '1'
        LEFT JOIN data_dedstants ds ON tc.dedstants_id = ds.id AND ds.is_active = '1' WHERE tocu.is_active = '1'"""

    def get(self, request, *args, **kwargs):
        tooluur_customers = TooluurCustomer.objects.raw(self.query)
        data = {
            "tooluur_customers": tooluur_customers,
            "menu": self.menu,
            "sub": self.sub,
            "urlz": '/home/add_orolt_garalt'
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        h_tool_num = request.POST.get('h_tool_num', '')
        h_tool_name = request.POST.get('h_tool_name', '')
        ch_tool_num = request.POST.get('ch_tool_num', '')
        ch_tool_name = request.POST.get('ch_tool_name', '')

        query = self.query

        if h_tool_num != '':
            query += " AND tl.number = " + str(h_tool_num)
        if h_tool_name != '':
            query += " AND tl.name LIKE '%%" + str(h_tool_name) + "%%'"
        if ch_tool_num != '':
            query += " AND tool.number = " + str(ch_tool_num)
        if ch_tool_name != '':
            query += " AND tool.name LIKE '%%" + str(ch_tool_name) + "%%'"

        search_q = {
            'h_tool_num': h_tool_num,
            'h_tool_name': h_tool_name,
            'ch_tool_num': ch_tool_num,
            'ch_tool_name': ch_tool_name,
        }

        tooluur_customers = TooluurCustomer.objects.raw(query)
        data = {
            "tooluur_customers": tooluur_customers,
            "search_q": search_q,
            "menu": self.menu,
            "sub": self.sub,
            "urlz": '/home/add_orolt_garalt'
        }
        return render(request, self.template_name, data)


class OroltGaraltDelete(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_oroltgaralt'
    template_name = "homepage/burtgel/orolt_and_garalt_list.html"
    menu = "2"
    sub = "4"

    def get(self, request, id, *args, **kwargs):
        if id is not None and int(id) > 0:
            tc = TooluurCustomer.objects.filter(id=int(id), is_active='1').first()
            if tc is not None:
                tc.flow_id = '0'
                tc.save()
                messages.success(request, 'Холболт амжилттай салгагдлаа.')
            else:
                messages.error(request, 'Холболт салгах явц амжилтгүй боллоо.')
        else:
            messages.error(request, 'Холболт салгах явц амжилтгүй боллоо.')
        return redirect('/home/orolt_and_garalt_list')

    def post(self, request, *args, **kwargs):
        return None


class OroltGaraltView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_oroltgaralt'
    template_name = "homepage/burtgel/add_orolt_garalt.html"
    menu = "2"
    sub = "4"

    def get(self, request, *args, **kwargs):
        # objs = Bair.objects.filter(is_active="1")
        # data = {
        #     "datas": objs,
        #     "menu": self.menu,
        #     "sub": self.sub,
        # }
        # return render(request, self.template_name, data)

        data = {
            "menu": self.menu,
            "sub": self.sub,
            "urlz": '/home/add_orolt_garalt'
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        # rq = request.POST
        # name = rq.get('name', '')
        # para = {}
        # if name != '':
        #     para["name__contains"] = name
        # para["is_active"] = "1"
        # objs = Horoo.objects.filter(**para)
        # data = {
        #     "datas": objs,
        #     "search_q": {
        #         "name": name,
        #     },
        #     "menu": self.menu,
        # }
        # return render(request, self.template_name, data)
        return redirect('/home/orolt_and_garalt_list')


class OroltGaraltAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_oroltgaralt'
    template_name = "homepage/burtgel/add_orolt_garalt.html"
    menu = "2"
    sub = "4"

    def get(self, request, *args, **kwargs):
        data = {
            "menu": self.menu,
            "sub": self.sub,
            "urlz": '/home/add_orolt_garalt'
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        selected_tooluurCustomer_id = rq.get('select_tooluur', '')
        flow_id = rq.get('select_input_tooluur', '')
        print(flow_id)
        if flow_id == '':
            messages.warning(request, 'Тоолуур буруу байна. Та тоолуураа сонгоно уу.')
            return self.warning_with_redirect()
        try:
            selected_to_cu = TooluurCustomer.objects.get(id=selected_tooluurCustomer_id)
            flow_to_cu = TooluurCustomer.objects.get(id=flow_id)
            selected_to_cu.flow_id = flow_id
            selected_to_cu.save()
            messages.success(request, "Амжилттай хадгалагдлаа.")
            return redirect('/home/orolt_and_garalt_list')
        except TooluurCustomer.DoesNotExist:
            messages.warning(request, "Алдаа гарлаа.")
            return self.warning_with_redirect()

    def warning_with_redirect(self):
        return redirect('/home/orolt_and_garalt_list')


class NewOroltGaraltAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_oroltgaralt'
    template_name = "homepage/burtgel/new_add_orolt_garalt.html"
    menu = "2"
    sub = "4"

    def get(self, request, *args, **kwargs):
        data = {
            "menu": self.menu,
            "sub": self.sub,
            "urlz": '/home/new_add_orolt_garalt'
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        selected_tooluurCustomer_id = rq.get('select_tooluur', '')
        tooluur_customer_ids = rq.getlist('select_input_tooluur')
        tooluurflow = TooluurFlow.objects.filter(child_tool_cus_id=selected_tooluurCustomer_id)
        tooluurflow.delete()
        for tooluur_customer_id in tooluur_customer_ids:
            if tooluur_customer_id == '':
                messages.warning(request, 'Тоолуур буруу байна. Та тоолуураа сонгоно уу.')
                return self.warning_with_redirect()
            try:
                selected_to_cu = TooluurCustomer.objects.get(id=selected_tooluurCustomer_id)
                flow_to_cu = TooluurCustomer.objects.get(id=tooluur_customer_id)
                if flow_to_cu.flow_type == "2":
                    messages.warning(request, 'Оролтын тоолуур буруу байна. Та өөр тоолуур сонгоно уу.')
                    return self.warning_with_redirect()
                selected_to_cu.flow_id = tooluur_customer_id
                tooluurflow = TooluurFlow.objects.create(head_tool_cus_id=tooluur_customer_id,
                                                         child_tool_cus_id=selected_tooluurCustomer_id)
                tooluurflow.save()
            except TooluurCustomer.DoesNotExist:
                messages.warning(request, "Алдаа гарлаа.")
                return self.warning_with_redirect()
        messages.success(request, "Амжилттай хадгалагдлаа.")
        return redirect('/home/orolt_and_garalt_list')

    def warning_with_redirect(self):
        return redirect('/home/orolt_and_garalt_list')


def get_input_customers(request):
    code = request.GET['code']
    selected_customer = request.GET['selected_customer']
    type = request.GET['type']
    result_set = []

    if code == '0':
        list = DedStants.objects.filter(is_active="1").order_by('name')
        if type == 0:
            list = list.exclude(id=selected_customer)
        for obj in list:
            if obj.name != '':
                result_set.append({'name': obj.name, 'code': obj.code, 'id': obj.id})
    if code == '1':
        list = Customer.objects.filter(is_active="1").order_by('code')
        for obj in list:
            if obj.code != '':
                result_set.append({'name': obj.code, 'id': obj.id})
    if code == '2':
        list = Bair.objects.filter(is_active="1").order_by('name')
        for obj in list:
            if obj.name != '':
                result_set.append({'name': obj.name, 'id': obj.id})

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def get_tooluur_by_angilal(request):
    code = request.GET['code']
    angilal = request.GET['angilal']
    result_set = []
    if angilal == '0':
        list = TooluurCustomer.objects.filter(is_active='1', dedstants__id=code)
    if angilal == '1':
        list = TooluurCustomer.objects.filter(is_active='1', customer_id=code, flow_type=0)
    if angilal == '2':
        list = TooluurCustomer.objects.filter(is_active='1', bair__id=code, flow_type=0)
    for obj in list:
        result_set.append(
            {'number': obj.tooluur.number, 'id': obj.id, 'flow_type': obj.flow_type, 'input_type': obj.input_type})
    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def get_selected_input_tooluur(request):
    code = request.GET['code']
    angilal = request.GET['angilal']
    selected_tooluur = request.GET['selected_tooluur']
    flow_type = "0"
    list = None
    try:
        tooluur = TooluurCustomer.objects.get(id=selected_tooluur)
        if tooluur.flow_type == "0":
            flow_type = "1"
        else:
            flow_type = "0"
    except TooluurCustomer.DoesNotExist:
        tooluur = None
        no_error = ""
    result_set = []
    if angilal == '0':
        list = TooluurCustomer.objects.filter(is_active='1', dedstants__id=code)
    if angilal == '1':
        list = TooluurCustomer.objects.filter(is_active='1', customer_id=code, flow_type=0)
    if angilal == '2':
        list = TooluurCustomer.objects.filter(is_active='1', bair__id=code, flow_type=0)
    for obj in list:
        result_set.append(
            {'number': obj.tooluur.number, 'id': obj.id, 'flow_type': obj.flow_type, 'input_type': obj.input_type})
    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def get_tooluur_input(request):
    code = request.GET['id']
    result_set = {}
    tooluur = TooluurCustomer.objects.get(id=code)
    try:
        # if tooluur.flow_type == "0":
        tooluurCustomer = TooluurCustomer.objects.get(id=tooluur.flow_id)
        # else:
        #     tooluurCustomer = TooluurCustomer.objects.filter(flow_id=code)
        result_set['flow_type'] = tooluur.flow_type
        print(tooluurCustomer),
        result_set["tooluur"] = {'id': tooluurCustomer.id, 'customer_angilal': tooluurCustomer.customer_angilal,
                                 'dedstants': {}, 'customer': {}, 'bair': {}}
        if tooluurCustomer.customer_angilal == "0":
            result_set["tooluur"]["dedstants"] = {'id': tooluurCustomer.dedstants.id}
        elif tooluurCustomer.customer_angilal == "1":
            result_set["tooluur"]["customer"] = {'id': tooluurCustomer.customer.id}
        else:
            result_set["tooluur"]["bair"] = {'id': tooluurCustomer.bair.id}

        customers = []

        if tooluurCustomer.customer_angilal == "0":
            list = DedStants.objects.filter(is_active="1").order_by('name')
            if tooluur.customer_angilal == "0":
                list = list.exclude(id=tooluur.dedstants.id)
            for obj in list:
                customers.append({'name': obj.name, 'code': obj.code, 'id': obj.id})
            tooluurs = TooluurCustomer.objects.filter(is_active=1, flow_type=tooluurCustomer.flow_type,
                                                      dedstants__id=tooluurCustomer.dedstants.id)
        elif tooluurCustomer.customer_angilal == "1":
            list = Customer.objects.filter(is_active=1)
            for obj in list:
                customers.append({'name': obj.code, 'id': obj.id})
            tooluurs = TooluurCustomer.objects.filter(is_active=1, flow_type="0",
                                                      customer__id=tooluurCustomer.customer.id)
        else:
            list = Bair.objects.filter(is_active=1)
            for obj in list:
                customers.append({'name': obj.name, 'id': obj.id})
            tooluurs = TooluurCustomer.objects.filter(is_active=1, flow_type="0", bair__id=tooluurCustomer.bair.id)
        tooluur_list = []
        for obj in tooluurs:
            tooluur_list.append(
                {'number': obj.tooluur.number, 'id': obj.id, 'flow_type': obj.flow_type, 'input_type': obj.input_type})
        print(tooluur_list)
        result_set["customers"] = customers
        result_set["tooluurs"] = tooluur_list
    except TooluurCustomer.DoesNotExist:
        result_set["error"] = {'code': 404, 'description': 'Тоолуур байхгүй байна.', 'flow_type': tooluur.flow_type}

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def new_get_tooluur_input(request):
    code = request.GET['id']
    result_set = {}
    tooluur = TooluurCustomer.objects.get(id=code)
    try:
        if tooluur.flow_type == "0":
            tooluurCustomer = TooluurCustomer.objects.get(id=tooluur.flow_id)
        else:
            tooluurCustomer = TooluurCustomer.objects.filter(flow_id=code)
        result_set['flow_type'] = tooluur.flow_type
        print(tooluurCustomer),
        result_set["tooluur"] = {'id': tooluurCustomer.id, 'customer_angilal': tooluurCustomer.customer_angilal,
                                 'dedstants': {}, 'customer': {}, 'bair': {}}
        if tooluurCustomer.customer_angilal == "0":
            result_set["tooluur"]["dedstants"] = {'id': tooluurCustomer.dedstants.id}
            query = " tc.dedstants_id = " + str(tooluurCustomer.dedstants.id)
        elif tooluurCustomer.customer_angilal == "1":
            result_set["tooluur"]["customer"] = {'id': tooluurCustomer.customer.id}
        else:
            result_set["tooluur"]["bair"] = {'id': tooluurCustomer.bair.id}
            query = " tc.bair_id = " + str(tooluurCustomer.bair.id)
        customers = []

        if tooluurCustomer.customer_angilal == "0":
            list = DedStants.objects.filter(is_active="1").order_by('name')
            if tooluur.customer_angilal == "0":
                list = list.exclude(id=tooluur.dedstants.id)
            for obj in list:
                customers.append({'name': obj.name, 'code': obj.code, 'id': obj.id})
            tooluurs = TooluurCustomer.objects.filter(is_active=1, flow_type=tooluurCustomer.flow_type,
                                                      dedstants__id=tooluurCustomer.dedstants.id)
        elif tooluurCustomer.customer_angilal == "1":
            list = Customer.objects.filter(is_active=1)
            for obj in list:
                customers.append({'code': obj.code, 'id': obj.id})
            tooluurs = TooluurCustomer.objects.filter(is_active=1, flow_type="0",
                                                      customer__id=tooluurCustomer.customer.id)
        else:
            list = Bair.objects.filter(is_active=1)
            for obj in list:
                customers.append({'name': obj.name, 'id': obj.id})
            tooluurs = TooluurCustomer.objects.filter(is_active=1, flow_type="0", bair__id=tooluurCustomer.bair.id)
        query = """
            SELECT t.number 
            , tc.id  
            , f.head_tool_cus_id is_selected
            , '' flow_type
            , '' input_type
            , f.id
            FROM mcsi.data_tooluurcustomer tc
            join data_tooluur t on tc.tooluur_id=t.id 
            and """ + query + """
            and t.is_active=1
            left join data_tooluurflow f on tc.id = f.head_tool_cus_id
            and f.child_tool_cus_id=""" + code
        tooluurs = TooluurFlow.objects.raw(query)
        tooluur_list = []
        for obj in tooluurs:
            tooluur_list.append(
                {'number': obj.number, 'id': obj.id, 'flow_type': obj.flow_type, 'input_type': obj.input_type,
                 'is_selected': obj.is_selected
                 })
        print(tooluur_list)
        result_set["customers"] = customers
        result_set["tooluurs"] = tooluur_list
    except TooluurCustomer.DoesNotExist:
        result_set["error"] = {'code': 404, 'description': 'Тоолуур байхгүй байна.', 'flow_type': tooluur.flow_type}

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
