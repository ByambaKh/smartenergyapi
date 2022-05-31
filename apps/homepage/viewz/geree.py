# coding=utf-8
import xlwt
import datetime
import simplejson
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, HttpResponse
from pymysql import IntegrityError
from django.views import View
from apps.homepage.forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from random import randrange
from django.contrib.auth.models import User


class GereeList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_geree'
    template_name = "homepage/burtgel/geree_list.html"
    qry = "SELECT co.id, co.contract_number, co.contract_expire_date, co.is_active, cu.register, cu.email, cu.code, cu.first_name, cu.last_name, cu.phone, ad.address_name" \
          " FROM data_geree AS co INNER JOIN data_customer AS cu ON co.customer_code = cu.code LEFT JOIN data_address AS ad ON cu.id = ad.customer_id" \
          " WHERE cu.is_active = 1 AND co.is_active = 1 AND cu.customer_angilal = "
    xlshome = None
    xlsorg = None
    menu = "2"
    sub = "2"

    def get(self, request, activeTab, *args, **kwargs):
        homeQry = self.qry + '1 order by co.customer_code'
        orgQry = self.qry + '0 order by co.customer_code'

        homeUsers = list(Geree.objects.raw(homeQry))
        orgs = list(Geree.objects.raw(orgQry))

        data = {
            "homeUsers": homeUsers,
            "orgs": orgs,
            "activeTab": int(activeTab),
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, activeTab, *args, **kwargs):
        rq = request.POST

        customer_code = rq.get('user_code', '')
        contract_number = rq.get('contract_number', '')
        customer_name = rq.get('customer_name', '')
        address = rq.get('address', '')
        phone = rq.get('phone', '')
        contract_expire_date_start = rq.get('contract_expire_date_start', '')
        contract_expire_date_end = rq.get('contract_expire_date_end', '')

        homeQry = self.qry + "'1'"
        orgQry = self.qry + "'0'"
        search_q = {}
        search_o = {}

        homeUsers = orgs = None

        if 'homeUserSearch' in rq or 'export_xls_users' in rq:
            if customer_code != '':
                homeQry = homeQry + " AND cu.code LIKE '%%" + customer_code + "%%'"
            if contract_number != '':
                homeQry = homeQry + " AND co.contract_number LIKE '%%" + contract_number + "%%'"
            if customer_name != '':
                homeQry = homeQry + " AND (cu.first_name LIKE '%%" + customer_name + "%%' OR cu.last_name LIKE '%%" + customer_name + "%%')"
            if address != '':
                homeQry = homeQry + " AND ad.address_name LIKE '%%" + address + "%%'"
            if phone != '':
                homeQry = homeQry + " AND cu.phone LIKE '%%" + phone + "%%'"
            if contract_expire_date_start != '' and contract_expire_date_end != '':
                homeQry = homeQry + " AND co.contract_expire_date BETWEEN '" + contract_expire_date_start + "' AND '" + contract_expire_date_end + "' "
            elif contract_expire_date_start != '':
                homeQry = homeQry + " AND co.contract_expire_date >= '" + contract_expire_date_start + "' "
            elif contract_expire_date_end != '':
                homeQry = homeQry + " AND co.contract_expire_date <= '" + contract_expire_date_end + "' "

            activeTab = 1
            search_q = {'customer_code': customer_code, 'contract_number': contract_number,
                        'customer_name': customer_name, 'address': address, 'phone': phone,
                        'contract_expire_date_start': contract_expire_date_start,
                        'contract_expire_date_end': contract_expire_date_end}

            homeUsers = list(Geree.objects.raw(homeQry + ' order by co.customer_code'))

            if 'export_xls_users' in rq:
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename="geree.xls"'

                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet('Users')

                # Sheet header, first row
                row_num = 0

                borders = xlwt.Borders()
                borders.left = xlwt.Borders.THIN
                borders.right = xlwt.Borders.THIN
                borders.top = xlwt.Borders.THIN
                borders.bottom = xlwt.Borders.THIN

                row_style = xlwt.XFStyle()
                row_style.borders = borders

                header_style = xlwt.XFStyle()
                header_style.font.bold = True
                header_style.alignment.wrap = True
                header_style.alignment.vert = xlwt.Alignment.VERT_CENTER
                header_style.borders = borders

                columns = ['Гэрээний №', 'Код', 'Хэрэглэгчийн нэр', 'Регистр', 'Имэйл', 'Утасны дугаар', 'Хаяг',
                           'Гэрээ дуусах огноо']
                col_width = [int(12 * 260), int(12 * 260), int(30 * 260), int(12 * 260), int(12 * 260), int(12 * 260),
                             int(40 * 260), int(12 * 260)]

                for col_num in range(len(columns)):
                    ws.col(col_num).width = col_width[col_num]
                    ws.write(row_num, col_num, columns[col_num], header_style)

                # Sheet body, remaining rows
                font_style = xlwt.XFStyle()

                for row in homeUsers:
                    row_num += 1
                    col_num = 0
                    full_name = row.first_name + ' ' + row.last_name

                    ws.write(row_num, col_num, row.contract_number, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.code, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, full_name, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.register, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.email, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.phone, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.address_name, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, str(row.contract_expire_date.date()), row_style)

                wb.save(response)
                return response

        elif 'orgSearch' in rq or 'export_xls_orgs' in rq:
            if customer_code != '':
                orgQry = orgQry + " AND cu.code LIKE '%%" + customer_code + "%%'"
            if contract_number != '':
                orgQry = orgQry + " AND co.contract_number LIKE '%%" + contract_number + "%%'"
            if customer_name != '':
                orgQry = orgQry + " AND (cu.first_name LIKE '%%" + customer_name + "%%' OR cu.last_name LIKE '%%" + customer_name + "%%')"
            if address != '':
                orgQry = orgQry + " AND ad.address_name LIKE '%%" + address + "%%'"
            if phone != '':
                orgQry = orgQry + " AND cu.phone LIKE '%%" + phone + "%%'"
            if contract_expire_date_start != '' and contract_expire_date_end != '':
                orgQry = orgQry + " AND co.contract_expire_date BETWEEN '" + contract_expire_date_start + "' AND '" + contract_expire_date_end + "' "
            elif contract_expire_date_start != '':
                orgQry = orgQry + " AND co.contract_expire_date >= '" + contract_expire_date_start + "' "
            elif contract_expire_date_end != '':
                orgQry = orgQry + " AND co.contract_expire_date <= '" + contract_expire_date_end + "' "

            activeTab = 2
            search_o = {'customer_code': customer_code, 'contract_number': contract_number,
                        'customer_name': customer_name, 'address': address, 'phone': phone,
                        'contract_expire_date_start': contract_expire_date_start,
                        'contract_expire_date_end': contract_expire_date_end}

            orgs = list(Geree.objects.raw(orgQry + ' order by co.customer_code'))

            if 'export_xls_orgs' in rq:
                response = HttpResponse(content_type='application/ms-excel')
                response['Content-Disposition'] = 'attachment; filename="geree.xls"'

                wb = xlwt.Workbook(encoding='utf-8')
                ws = wb.add_sheet('Users')

                # Sheet header, first row
                row_num = 0

                borders = xlwt.Borders()
                borders.left = xlwt.Borders.THIN
                borders.right = xlwt.Borders.THIN
                borders.top = xlwt.Borders.THIN
                borders.bottom = xlwt.Borders.THIN

                row_style = xlwt.XFStyle()
                row_style.borders = borders

                header_style = xlwt.XFStyle()
                header_style.font.bold = True
                header_style.alignment.wrap = True
                header_style.alignment.vert = xlwt.Alignment.VERT_CENTER
                header_style.borders = borders

                columns = ['Гэрээний №', 'Код', 'Хэрэглэгчийн нэр', 'Регистр', 'Имэйл', 'Утасны дугаар', 'Хаяг', 'Гэрээ дуусах огноо']
                col_width = [int(12 * 260), int(12 * 260), int(30 * 260), int(12 * 260), int(12 * 260), int(12 * 260), int(40 * 260), int(12 * 260)]

                for col_num in range(len(columns)):
                    ws.col(col_num).width = col_width[col_num]
                    ws.write(row_num, col_num, columns[col_num], header_style)

                # Sheet body, remaining rows
                font_style = xlwt.XFStyle()

                for row in orgs:
                    row_num += 1
                    col_num = 0
                    full_name = row.first_name + ' ' + row.last_name

                    ws.write(row_num, col_num, row.contract_number, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.code, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, full_name, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.register, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.email, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.phone, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, row.address_name, row_style)
                    col_num += 1
                    ws.write(row_num, col_num, str(row.contract_expire_date.date()), row_style)

                wb.save(response)
                return response

        data = {
            "homeUsers": homeUsers,
            "orgs": orgs,
            "search_q": search_q,
            "search_o": search_o,
            "activeTab": activeTab,
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)


class GereeAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/burtgel/geree_add.html"
    permission_required = 'data.add_geree'
    menu = "2"
    sub = "2"

    def get(self, request, *args, **kwargs):
        aimag = Aimag.objects.filter(is_active='1')
        bank = Bank.objects.filter(is_active='1')
        cycle = Cycle.objects.filter(is_active='1')
        dedStants = DedStants.objects.filter(is_active='1')
        zaag = Files.objects.filter(is_active='1')
        technical = TechnicalProposal.objects.filter(is_active='1')

        data = {
            "urlz": "/home/geree_add",
            "aimag": aimag,
            "bank": bank,
            "cycle": cycle,
            "dedStants": dedStants,
            "zaag": zaag,
            "technical": technical,
            "angilal": 0,
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):

        rq = request.POST

        address = Address.objects.create()
        address.aimag_code = rq.get('select_aimag', '')
        address.duureg_code = rq.get('select_duureg', '')
        address.horoo_code = rq.get('select_horoo', '')
        if rq.get('select_hothon', '') != '':
            hothon = Hothon.objects.get(id=int(rq.get('select_hothon', '')))
            if hothon is not None:
                address.hothon_code = hothon.code
        address.block_code = rq.get('select_block', '')
        address.building_number = rq.get('building_number', '')
        address.toot = rq.get('toot', '')
        address_text = ""
        if address.aimag_code != '' and address.aimag_code != None:
            address_text += Aimag.objects.get(code=address.aimag_code).name + ", "
        if address.duureg_code != '' and address.duureg_code != None:
            address_text += Duureg.objects.get(code=address.duureg_code).name + ", "
        if address.horoo_code != '' and address.horoo_code != None:
            address_text += Horoo.objects.get(code=rq.get('select_horoo', '')).name + ", "
        if address.hothon_code != '' and address.hothon_code != None:
            address_text += Hothon.objects.get(id=int(rq.get('select_hothon', ''))).name + ", "
        if address.block_code != '' and address.block_code != None:
            address_text += Block.objects.get(code=rq.get('select_block', '')).name + "-эгнээ, "
        if address.building_number != '' and address.building_number != None:
            address_text += address.building_number + "-р байр, "
        if address.toot != '' and address.toot != None:
            address_text += address.building_number + " тоот."
        address.address_name = address_text

        if rq.get('last_name', '') is None:
            lastname = " "
        else:
            lastname = rq.get('last_name', '')

        customer = Customer.objects.create()
        customer.code = rq.get('code', '')
        customer.register = rq.get('register', '')
        customer.last_name = lastname
        customer.first_name = rq.get('first_name', '')
        customer.customer_angilal = rq.get('select_angilal', '')
        customer.customer_type = rq.get('select_type', '')
        customer.phone = rq.get('phone', '')
        customer.phone2 = rq.get('phone2', '')
        customer.email = rq.get('email', '')

        geree = Geree.objects.create()
        geree.customer_code = customer.code
        geree.type_code = rq.get('select_type', '')
        geree.cycle_code = rq.get('select_cycle', '')
        geree.ezemshliin_zaag = rq.get('ezemshliin_zaag', '')
        geree.bank_code = rq.get('select_bank', '')
        geree.dedstants_code = rq.get('select_dedstants', '')
        geree.bus_type = rq.get('select_bus', '')
        geree.contract_number = rq.get('contract_number', '')
        if len(str(rq.get('contract_made_date', ''))) >= 10:
            geree.contract_made_date = datetime.datetime.strptime(rq.get('contract_made_date', ''), '%Y-%m-%d')
        if len(str(rq.get('contract_expire_date', ''))) >= 10:
            geree.contract_expire_date = datetime.datetime.strptime(rq.get('contract_expire_date', ''), '%Y-%m-%d')
        if len(str(rq.get('contract_extend_date', ''))) >= 10:
            geree.contract_extend_date = datetime.datetime.strptime(rq.get('contract_extend_date', ''), '%Y-%m-%d')
        geree.description = rq.get('description', '')

        if rq.get('technical', '') != "":
            tech = TechnicalProposal.objects.get(id = rq.get('technical', ''))
            geree.technical_proposal = tech

        # cus_email = Customer.objects.filter(email=rq.get('email', ''))
        cus_code = Customer.objects.filter(code=rq.get('code', ''), is_active='1').first()
        geree_code = Geree.objects.filter(contract_number=rq.get('contract_number', ''), is_active='1').first()

        msg = ""

        if cus_code is None and geree_code is None:
            customer.save()
            address.customer = customer
            address.save()
            geree.save()

            if customer.customer_angilal == '1':
                activeTab = '1'
            else:
                activeTab = '2'

            return redirect('/home/geree_list/' + activeTab + '/')

        # elif len(cus_email) != 0:
        #     messages.warning(request, "Мэйл хаяг системд бүртгэгдсэн байна. Та өөр мэйл хаяг ашиглана уу")
        elif geree_code is not None:
            messages.warning(request, "Оруулсан дугаартай гэрээ системд бүртгэгдсэн байна.")
        elif cus_code is not None:
            messages.warning(request, "Оруулсан кодтой хэрэглэгч системд бүртгэгдсэн байна.")

        geree_bank = Bank.objects.filter(code=geree.bank_code)
        bank = Bank.objects.filter(is_active='1')
        cycle = Cycle.objects.filter(is_active='1')
        dedStants = DedStants.objects.filter(is_active='1')
        zaag = Files.objects.filter(is_active='1')
        technical = TechnicalProposal.objects.filter(is_active='1')

        aimag = Aimag.objects.filter(is_active='1')
        duureg = Aimag.objects.get(code=address.aimag_code).duureg_set.filter(is_active="1")
        horoo = Duureg.objects.get(code=address.duureg_code).horoo_set.filter(is_active="1")
        hothon = Horoo.objects.get(code=address.horoo_code).hothon_set.filter(is_active="1")
        egnee = Hothon.objects.get(code=address.hothon_code).block_set.filter(is_active="1")

        made_date = geree.contract_made_date
        expire_date = geree.contract_expire_date
        extend_date = geree.contract_extend_date

        if customer.customer_angilal == '0':
            customer_type = AanAngilal.objects.filter(is_active="1")
        if customer.customer_angilal == '1':
            customer_type = AhuinHereglegch.objects.filter(is_active="1")

        messages.success(request, "Амжилттай хадгалагдлаа.")

        data = {
            "urlz": "/home/geree_add",
            "geree": geree,
            "customer": customer,
            "address": address,
            "aimag": aimag,
            "duureg": duureg,
            "horoo": horoo,
            "hothon": hothon,
            "egnee": egnee,
            "geree_bank": geree_bank[0],
            "bank": bank,
            "cycle": cycle,
            "dedStants": dedStants,
            "zaag": zaag,
            "technical": technical,
            "made_date": made_date,
            "expire_date": expire_date,
            "extend_date": extend_date,
            "customer_type": customer_type,
            "menu": self.menu,
            "sub": self.sub
        }

        return render(request, self.template_name, data)

    def form_valid(self, form):
        print(form)


class GereeEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_geree'
    template_name = "homepage/burtgel/geree_add.html"
    menu = "2"
    sub = "2"

    def get(self, request, id, *args, **kwargs):
        geree = Geree.objects.get(id=id)
        customer = Customer.objects.get(code=geree.customer_code)
        geree_bank = Bank.objects.filter(code=geree.bank_code).first()
        bank = Bank.objects.filter(is_active='1')
        cycle = Cycle.objects.filter(is_active='1')
        dedStants = DedStants.objects.filter(is_active='1')
        zaag = Files.objects.filter(is_active='1')
        technical = TechnicalProposal.objects.filter(is_active='1')

        try:
            address = Address.objects.filter(customer=customer).first()
        except ObjectDoesNotExist:
            address = None

        if address is not None:
            aimag = Aimag.objects.filter(is_active='1')
            if address.aimag_code != '' or address.aimag_code is not None:
                try:
                    duureg = Aimag.objects.get(code=address.aimag_code).duureg_set.filter(is_active="1")
                except ObjectDoesNotExist:
                    duureg = Aimag.objects.filter(is_active='1')
            else:
                duureg = Aimag.objects.filter(is_active='1')
            if address.duureg_code != '' or address.duureg_code is not None:
                try:
                    horoo = Duureg.objects.get(code=address.duureg_code).horoo_set.filter(is_active="1")
                except ObjectDoesNotExist:
                    horoo = Duureg.objects.filter(is_active="1")
            else:
                horoo = Duureg.objects.filter(is_active="1")
            if address.horoo_code != '' or address.horoo_code is not None:
                try:
                    hothon = Horoo.objects.get(code=address.horoo_code).hothon_set.filter(is_active="1")
                except ObjectDoesNotExist:
                    hothon = Horoo.objects.filter(is_active="1")
            else:
                hothon = Horoo.objects.filter(is_active="1")
            if address.hothon_code != "" or address.hothon_code is not None:
                try:
                    egnee = Hothon.objects.get(code=address.hothon_code).block_set.filter(is_active="1")
                except ObjectDoesNotExist:
                    egnee = Block.objects.filter(is_active="1")
            else:
                egnee = Block.objects.filter(is_active="1")
        else:
            aimag = Aimag.objects.filter(is_active='1')
            duureg = Duureg.objects.filter(is_active="1")
            horoo = Horoo.objects.filter(is_active="1")
            hothon = Hothon.objects.filter(is_active="1")
            egnee = Block.objects.filter(is_active="1")

        made_date = geree.contract_made_date
        expire_date = geree.contract_expire_date
        extend_date = geree.contract_extend_date

        customer_type = None
        if customer.customer_angilal == '0':
            customer_type = AanAngilal.objects.filter(is_active="1")
        if customer.customer_angilal == '1':
            customer_type = AhuinHereglegch.objects.filter(is_active="1")

        data = {
            "urlz": "/home/geree_edit/" + id + "/",
            "geree": geree,
            "customer": customer,
            "address": address,
            "aimag": aimag,
            "duureg": duureg,
            "horoo": horoo,
            "hothon": hothon,
            "egnee": egnee,
            "geree_bank": geree_bank,
            "bank": bank,
            "cycle": cycle,
            "dedStants": dedStants,
            "zaag": zaag,
            "technical": technical,
            "made_date": made_date,
            "expire_date": expire_date,
            "extend_date": extend_date,
            "customer_type": customer_type,
            "angilal": customer.customer_angilal,
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST

        try:
            addr = Address.objects.filter(customer_id=rq.get('customer_id', '')).first()
            if addr is None:
                addr = Address.objects.create()
        except ObjectDoesNotExist:
            addr = Address.objects.create()

        address_text = ''
        if rq.get('select_aimag', '') != '':
            addr.aimag_code = rq.get('select_aimag', '')
            aimag = Aimag.objects.filter(code=rq.get('select_aimag', '')).first()
            if aimag is not None:
                address_text += aimag.name + ', '
        if rq.get('select_duureg', '') != '':
            addr.duureg_code = rq.get('select_duureg', '')
            duureg = Duureg.objects.filter(code=rq.get('select_duureg', '')).first()
            if duureg is not None:
                address_text += duureg.name + ', '
        if rq.get('select_horoo', '') != '':
            addr.horoo_code = rq.get('select_horoo', '')
            horoo = Horoo.objects.filter(code=rq.get('select_horoo', '')).first()
            if horoo is not None:
                address_text += horoo.name + ', '
        if rq.get('select_hothon', '') != '':
            hothon = Hothon.objects.filter(id=int(rq.get('select_hothon', ''))).first()
            if hothon is not None:
                addr.hothon_code = hothon.code
                address_text += hothon.name + ', '
        if rq.get('select_block', '') != '':
            addr.block_code = rq.get('select_block', '')
            block = Block.objects.filter(code=rq.get('select_block', '')).first()
            if block is not None:
                address_text += block.name + '-эгнээ, '
        if rq.get('building_number', '') != '':
            addr.building_number = rq.get('building_number', '')
            address_text += rq.get('building_number', '') + '-р байр, '
        if rq.get('toot', '') != '':
            addr.toot = rq.get('toot', '')
            address_text += rq.get('toot', '') + ' тоот.'
        addr.address_name = address_text

        if rq.get('last_name', '') is None:
            lastname = " "
        else:
            lastname = rq.get('last_name', '')

        geree = Geree.objects.get(id=id)
        customer = Customer.objects.get(code=geree.customer_code)
        customer.code = rq.get('code', '')
        customer.register = rq.get('register', '')
        customer.last_name = lastname
        customer.first_name = rq.get('first_name', '')
        customer.customer_angilal = rq.get('select_angilal', '')
        customer.customer_type = rq.get('select_type', '')
        customer.phone = rq.get('phone', '')
        customer.phone2 = rq.get('phone2', '')
        customer.email = rq.get('email', '')

        geree.customer_code = customer.code
        geree.type_code = rq.get('select_type', '')
        geree.cycle_code = rq.get('select_cycle', '')
        geree.ezemshliin_zaag = rq.get('ezemshliin_zaag', '')
        geree.bank_code = rq.get('select_bank', '')
        geree.dedstants_code = rq.get('select_dedstants', '')
        geree.bus_type = rq.get('select_bus', '')
        geree.contract_number = rq.get('contract_number', '')
        if rq.get('contract_made_date', '') != '':
            geree.contract_made_date = datetime.datetime.strptime(rq.get('contract_made_date', ''), '%Y-%m-%d')
        else:
            geree.contract_made_date = None

        if rq.get('contract_expire_date', '') != '':
            geree.contract_expire_date = datetime.datetime.strptime(rq.get('contract_expire_date', ''), '%Y-%m-%d')
        else:
            geree.contract_expire_date = None

        if rq.get('contract_extend_date', '') != '':
            geree.contract_extend_date = datetime.datetime.strptime(rq.get('contract_extend_date', ''), '%Y-%m-%d')
        else:
            geree.contract_extend_date = None
        geree.description = rq.get('description', '')

        if rq.get('technical', '') != "":
            tech = TechnicalProposal.objects.get(id = rq.get('technical', ''))
            geree.technical_proposal = tech

        # cus_email = Customer.objects.filter(email=rq.get('email', '')).exclude(id=customer.id)
        cus_code = list(Customer.objects.filter(code=rq.get('code', ''), is_active='1'))
        geree_code = list(Geree.objects.filter(contract_number=rq.get('contract_number', ''), is_active='1'))

        if len(cus_code) == 1:
            addr.customer = customer
            addr.save()
            customer.save()
            geree.save()

            if customer.customer_angilal == '1':
                activeTab = '1'
            else:
                activeTab = '2'

            messages.success(request, "Амжилттай хадгалагдлаа.")

            return redirect('/home/geree_list/' + activeTab + '/')
        elif len(geree_code) > 1:
            messages.add_message(request, messages.WARNING, 'Оруулсан дугаартай гэрээ системд бүртгэгдсэн байна.')
        elif len(cus_code) > 1:
            messages.add_message(request, messages.WARNING, 'Оруулсан кодтой хэрэглэгч системд бүртгэгдсэн байна.')

        geree_bank = Bank.objects.filter(code=geree.bank_code).first()
        bank = Bank.objects.filter(is_active='1')
        cycle = Cycle.objects.filter(is_active='1')
        dedStants = DedStants.objects.filter(is_active='1')
        zaag = Files.objects.filter(is_active='1')
        technical = TechnicalProposal.objects.filter(is_active='1')

        aimag = Aimag.objects.filter(is_active='1')
        duureg = Aimag.objects.get(code=addr.aimag_code).duureg_set.filter(is_active="1")
        horoo = Duureg.objects.get(code=addr.duureg_code).horoo_set.filter(is_active="1")
        hothon = Horoo.objects.get(code=addr.horoo_code).hothon_set.filter(is_active="1")
        if addr.hothon_code != "":
            egnee = Hothon.objects.get(code=addr.hothon_code).block_set.filter(is_active="1")
        else:
            egnee = None

        made_date = geree.contract_made_date
        expire_date = geree.contract_expire_date
        extend_date = geree.contract_extend_date

        customer_type = None
        if customer.customer_angilal == '0':
            customer_type = AanAngilal.objects.filter(is_active="1")
        if customer.customer_angilal == '1':
            customer_type = AhuinHereglegch.objects.filter(is_active="1")

        messages.warning(request, "Та мэдээллээ дахин шалгана уу!")

        data = {
            "urlz": "/home/geree_add",
            "geree": geree,
            "customer": customer,
            "address": addr,
            "aimag": aimag,
            "duureg": duureg,
            "horoo": horoo,
            "hothon": hothon,
            "egnee": egnee,
            "geree_bank": geree_bank,
            "bank": bank,
            "cycle": cycle,
            "dedStants": dedStants,
            "zaag": zaag,
            "technical": technical,
            "made_date": made_date,
            "expire_date": expire_date,
            "extend_date": extend_date,
            "customer_type": customer_type,
            "menu": self.menu,
            "sub": self.sub
        }
        return render(request, self.template_name, data)


class GereeDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_geree'
    template_name = "homepage/burtgel/geree_list.html"

    def get(self, request, id, *args, **kwargs):
        geree = Geree.objects.get(id=id)
        customer = Customer.objects.get(code=geree.customer_code)
        geree.is_active = 0
        geree.customer_code = ''
        customer.is_active = 0
        customer.code = ''
        geree.save()
        customer.save()

        if customer.customer_angilal == '1':
            activeTab = '1'
        else:
            activeTab = '2'

        messages.success(request, "Амжилттай устгагдлаа.")

        return redirect("/home/geree_list/" + activeTab + '/')


def get_type(request):
    code = request.GET['code']
    result_set = []
    list = []

    if code == '0':
        list = AanAngilal.objects.filter(is_active="1")
    if code == '1':
        list = AhuinHereglegch.objects.filter(is_active="1")

    for obj in list:
        result_set.append({'name': obj.name, 'code': obj.code})

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def get_duureg(request):
    code = request.GET['code']
    result_set = []
    parent = Aimag.objects.get(code=code, is_active=1)
    list = parent.duureg_set.filter(is_active="1")
    for obj in list:
        result_set.append({'name': obj.name, 'code': obj.code})

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def get_horoo(request):
    code = request.GET['code']
    result_set = []
    if (code != ""):
        parent = Duureg.objects.get(code=code)
        list = parent.horoo_set.filter(is_active="1")
        for obj in list:
            result_set.append({'name': obj.name, 'code': obj.code})
    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def get_hothon(request):
    code = request.GET['code']
    result_set = []
    parent = Horoo.objects.get(code=code)
    list = parent.hothon_set.filter(is_active="1")
    for obj in list:
        result_set.append({'name': obj.name, 'code': str(obj.id)})

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def get_block(request):
    code = request.GET['code']
    result_set = []
    blocks = Block.objects.filter(hothon_id=int(code))
    if blocks is not None:
        for obj in blocks:
            result_set.append({'name': obj.name, 'code': obj.code})

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def get_dans(request):
    code = request.GET['code']

    bank = Bank.objects.get(id=code)
    result_set = {'dans': bank.dans}

    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')


def generate_pin():
    pin = randrange(1000, 9999, 4)
    return pin


# @permission_required('data.change_geree', login_url='/login')
def set_pin_code(request):
    code = request.GET['customer_code']
    print("code : " + str(code), flush=True)
    try:
        result_set = {}
        customer = Customer.objects.get(code=code)
        if customer:
            try:
                portal_user = User.objects.using('portal').get(username=code)
                portal_user.set_password(customer.pin_code)
                generated_pin = customer.pin_code
                portal_user.save(using='portal')
            except(ObjectDoesNotExist, IntegrityError):
                generated_pin = generate_pin()
                if customer.email == None:
                    email = ""
                else:
                    email = customer.email
                user = User.objects.using('portal').create(email=email, username=customer.code)
                user.set_password(generated_pin)
                user.first_name = customer.first_name
                user.last_name = customer.last_name
                user.is_superuser = 0
                user.is_staff = 0
                user.is_active = 1
                user.save(using='portal')
                customer.pin_code = generated_pin
                customer.save()
        else:
            generated_pin = customer.pin_code

        # print("generated_pin : " + str(generated_pin), flush=True)

        # print("customer : " + str(customer.first_name), flush=True)

        result_set["code"] = code
        result_set["pin"] = generated_pin
    except Customer.DoesNotExist:
        result_set = {"error": {"description": "No matched customer.", "code": 302}}
    return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
