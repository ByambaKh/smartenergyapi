import xlwt
from django.contrib import messages

from apps.homepage.forms import *
from django.views import View
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin


class TechList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/burtgel/tech_nuhtsul.html"
    permission_required = 'data.view_technicalproposal'
    tech_q = "SELECT id, tech_code, req_chadal, approve_chadal, approve_date, tech_name, tech_utas, tech_address FROM data_technicalproposal WHERE is_active = 1 "
    xls_list = None
    req_xls_list = None
    menu = "2"
    sub = "1"

    def get(self, request, activeTab, *args, **kwargs):
        q = self.tech_q
        q = q + " order by created_date desc"

        objs = TechnicalProposal.objects.raw(q)
        requests = UserTechnicalProposal.objects.all()
        dedstants = DedStants.objects.filter(is_active="1")
        TechList.xls_list = objs
        TechList.req_xls_list = requests

        data = {
            'activeTab': int(activeTab),
            "datas": objs,
            "requests": requests,
            "dedstants": dedstants,
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, activeTab, *args, **kwargs):
        rq = request.POST

        para = {}
        search_q = {}
        search_req = {}
        q = self.tech_q
        requests = None
        objs = None

        if 'tech_search' in rq or 'export_xls_1' in rq:
            code = rq.get('code', '')
            name = rq.get('name', '')
            req_chadal = rq.get('req_chadal', '')
            approve_chadal = rq.get('approve_chadal', '')
            address = rq.get('address', '')
            phone = rq.get('phone', '')
            zoriulalt = rq.get('zoriulalt', '')

            if code != '':
                q = q + " and tech_code LIKE '%%" + code + "%%'"
            if name != '':
                q = q + " and tech_name LIKE '%%" + name + "%%'"
            if req_chadal != '':
                q = q + " and req_chadal <" + req_chadal
            if approve_chadal != '':
                q = q + " and approve_chadal <" + approve_chadal
            if address != '':
                q = q + " and tech_address LIKE '%%" + address + "%%'"
            if phone != '':
                q = q + " and tech_utas LIKE '%%" + phone + "%%'"
            if zoriulalt != '':
                q = q + " and zoriulalt LIKE '%%" + zoriulalt + "%%'"

            q = q + " order by created_date desc"

            activeTab = 1
            search_q = {'code': code, 'name': name, 'approve_chadal': approve_chadal, 'req_chadal': req_chadal,
                        'address': address, 'phone': phone, 'zoriulalt': zoriulalt}

            objs = TechnicalProposal.objects.raw(q)

            if 'export_xls_1' in rq:
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename="technical_proposal.xls"'

                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet('Users')

                row_num = 0

                font_style = xlwt.XFStyle()
                font_style.font.bold = True

                columns = ['Дугаар', 'Овог нэр', 'Хүссэн чадал', 'Суурилагдсан чадал', 'Утасны дугаар', 'Байршил']

                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)

                # Sheet body, remaining rows
                font_style = xlwt.XFStyle()

                for row in objs:
                    row_num += 1
                    col_num = 0

                    ws.write(row_num, col_num, row.tech_code, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.tech_name, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.req_chadal, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.approve_chadal, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.tech_utas, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.tech_address, font_style)

                wb.save(response)
                return response

        if 'req_search' in rq or 'export_xls_2' in rq:
            req_name = rq.get('req_name', '')
            req_phone = rq.get('req_phone', '')
            req_address = rq.get('req_address', '')
            req_is_active = rq.get('req_is_active', '')

            if req_name != '':
                para.update({'name__contains': req_name})
            if req_phone != '':
                para.update({'phone__contains': req_phone})
            if req_address != '':
                para.update({'obj_address__contains': req_address})
            if req_is_active != '2':
                para.update({'is_active': req_is_active})

            activeTab = 2
            search_req = {'name': req_name, 'phone': req_phone, 'address': req_address, 'req_is_active': req_is_active}

            requests = UserTechnicalProposal.objects.filter(**para).order_by('-created_date')

            if 'export_xls_2' in rq:
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename="technical_proposal_request.xls"'

                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet('Users')

                row_num = 0

                font_style = xlwt.XFStyle()
                font_style.font.bold = True

                columns = ['Нэр', 'Утас', 'Обьектын байршил', 'Хэрэглэгчийн зэрэглэл', 'Шалтгаан', 'Өргөдөл',
                           'Тооцооны нийт чадал', 'Олгогдсон эсэх']

                for col_num in range(len(columns)):
                    ws.write(row_num, col_num, columns[col_num], font_style)

                # Sheet body, remaining rows
                font_style = xlwt.XFStyle()

                for row in requests:
                    row_num += 1
                    col_num = 0

                    ws.write(row_num, col_num, row.name, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.phone, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.obj_address, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.zereglel, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.tech_shaltgaan, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.urgudul, font_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.toots_niit_chadal, font_style)
                    col_num += 1
                    if row.is_active == '1':
                        ws.write(row_num, col_num, 'Олгогдоогүй', font_style)
                    else:
                        ws.write(row_num, col_num, 'Олгогдсон', font_style)

                wb.save(response)
                return response

        data = {
            'activeTab': activeTab,
            "datas": objs,
            "requests": requests,
            "search_q": search_q,
            "search_req": search_req,
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)


class TechAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/burtgel/add_tech.html"
    permission_required = 'data.add_technicalproposal'
    menu = "2"
    sub = "1"

    def get(self, request, *args, **kwargs):
        files = Files.objects.filter(is_active="1", type="1")
        dedstants = DedStants.objects.filter(is_active="1").order_by('name')

        data = {
            "files": files,
            "dedstants": dedstants,
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST

        tech_code = rq.get('tech_code', '')
        tech_name = rq.get('tech_name', '')
        tech_utas = rq.get('tech_utas', '')
        tech_address = rq.get('tech_address', '')
        zoriulalt = rq.get('zoriulalt', '')
        req_chadal = rq.get('req_chadal', '')
        req_date = rq.get('req_date', '')
        approve_chadal = rq.get('approve_chadal', '')
        approve_date = rq.get('approve_date', '')
        dedstants = rq.get('dedstants', '')
        file = rq.get('file', '')

        tech = TechnicalProposal.objects.create(tech_code=tech_code)

        tech.req_chadal = req_chadal
        tech.req_date = req_date
        tech.approve_chadal = approve_chadal
        tech.approve_date = approve_date
        tech.tech_name = tech_name
        tech.tech_utas = tech_utas
        tech.tech_address = tech_address
        tech.zoriulalt = zoriulalt
        tech.dedstants = DedStants.objects.get(id=dedstants)
        if file != '':
            tech.file = Files.objects.get(id=int(file))

        tech.save()

        messages.success(request, "Амжилттай хадгалагдлаа.")

        return redirect('/home/tech_nuhtsul/1/')


class ProposalEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_technicalproposal'
    template_name = "homepage/burtgel/add_tech.html"
    menu = "2"
    sub = "1"

    def get(self, request, id, *args, **kwargs):
        tech = TechnicalProposal.objects.get(id=id)
        files = Files.objects.filter(is_active="1", type="1")
        dedstants = DedStants.objects.filter(is_active="1").order_by('name')
        req_date = tech.req_date.strftime("%Y-%m-%d")
        approve_date = tech.approve_date.strftime("%Y-%m-%d")

        data = {
            "files": files,
            "dedstants": dedstants,
            "tech": tech,
            "req_date": req_date,
            "approve_date": approve_date,
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST

        tech_code = rq.get('tech_code', '')
        tech_name = rq.get('tech_name', '')
        tech_utas = rq.get('tech_utas', '')
        tech_address = rq.get('tech_address', '')
        zoriulalt = rq.get('zoriulalt', '')
        req_chadal = rq.get('req_chadal', '')
        req_date = rq.get('req_date', '')
        approve_chadal = rq.get('approve_chadal', '')
        approve_date = rq.get('approve_date', '')
        dedstants = rq.get('dedstants', '')
        file = rq.get('file', '')

        tech = TechnicalProposal.objects.get(id=id)

        tech.tech_code = tech_code
        tech.req_chadal = req_chadal
        tech.req_date = req_date
        tech.approve_chadal = approve_chadal
        tech.approve_date = approve_date
        tech.tech_name = tech_name
        tech.tech_utas = tech_utas
        tech.tech_address = tech_address
        tech.zoriulalt = zoriulalt
        tech.dedstants = DedStants.objects.get(id=dedstants)
        if file != '':
            tech.file = Files.objects.get(id=int(file))

        tech.save()

        messages.success(request, "Амжилттай хадгалагдлаа.")

        return redirect('/home/tech_nuhtsul/1/')


class ConfirmTech(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_technicalproposal'
    template_name = "homepage/burtgel/confirm_tech.html"
    menu = "2"
    sub = "1"

    def get(self, request, id, *args, **kwargs):
        requests = UserTechnicalProposal.objects.get(id=id)
        dedstants = DedStants.objects.filter(is_active="1")
        is_edit = requests.is_active

        data = {
            "is_edit": is_edit,
            "requests": requests,
            "dedstants": dedstants,
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST

        tech_code = rq.get('tech_number', '')
        approve_date = rq.get('approve_date', '')
        approve_chadal = rq.get('approve_chadal', '')
        zoriulalt = rq.get('zoriulalt', '')
        tech_dedstants = rq.get('tech_dedstants', '')

        req = UserTechnicalProposal.objects.get(id=id)
        req.is_active = '0'

        try:
            tech = TechnicalProposal.objects.get(request_id=id)
        except TechnicalProposal.DoesNotExist:
            tech = TechnicalProposal.objects.create(request=req)

        tech.tech_code = tech_code
        tech.req_chadal = req.toots_niit_chadal
        tech.req_date = req.created_date
        tech.approve_chadal = approve_chadal
        tech.approve_date = approve_date
        tech.tech_name = req.name
        tech.tech_utas = req.phone
        tech.tech_address = req.obj_address
        tech.zoriulalt = zoriulalt
        tech.dedstants = DedStants.objects.get(id=tech_dedstants)

        req.save()
        tech.save()

        messages.success(request, "Амжилттай хадгалагдлаа.")

        return redirect('/home/tech_nuhtsul/2/')
