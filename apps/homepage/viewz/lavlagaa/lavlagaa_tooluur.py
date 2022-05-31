import xlwt
from django.http import HttpResponse
from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class LavlahTooluur(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_tooluur'
    template_name = "homepage/lavlah/tooluur.html"
    starter_q = "SELECT t.id,t.number,t.name,t.mark,t.status,t.tariff,t.amper,t.voltage,t.expire_date,v.value as huchdel,a.value as guidel FROM data_tooluur AS t LEFT JOIN data_voltage AS v ON v.id=t.voltage LEFT JOIN data_amper AS a ON a.id=t.amper WHERE t.is_active = 1"
    menu = "7"
    xls = None

    def get(self, request, *args, **kwargs):
        q = self.starter_q
        q = q + " order by t.created_date desc"
        objs = Tooluur.objects.raw(q)
        LavlahTooluur.xls = objs
        marks = Tooluur.objects.raw("SELECT id, mark FROM data_tooluur WHERE is_active='1' GROUP BY mark ORDER BY mark")
        data = {
            "tooluur": objs,
            "marks": marks,
            'status_all': STATUS,
            "menu": self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):

        rq = request.POST
        status = rq.get('select_status', '')
        tariff = rq.get('select_tariff', '')
        tooluur_number = rq.get('tooluur_number', '')
        tooluur_name = rq.get('tooluur_name', '')
        tooluur_mark = rq.get('tooluur_mark', '')
        expire_date = rq.get('expire_date', '')
        q = self.starter_q

        if status != '':
            q = q + " AND status='" + status + "'"
        if tariff != '':
            q = q + " AND tariff='" + tariff + "'"
        if tooluur_name != '':
            q = q + " AND name LIKE '%%" + tooluur_name + "%%'"
        if tooluur_number != '':
            q = q + " AND number LIKE '%%" + tooluur_number + "%%'"
        if tooluur_mark != '':
            q = q + " AND mark LIKE '%%" + tooluur_mark + "%%'"
        if expire_date != '':
            q = q + " AND expire_date >= '" + expire_date + "' "
        objs = Tooluur.objects.raw(q)
        marks = Tooluur.objects.raw("SELECT id, mark FROM data_tooluur WHERE is_active='1' GROUP BY mark ORDER BY mark")
        if 'search' in rq:
            data = {
                "tooluur": objs,
                "marks": marks,
                'status_all': STATUS,
                "search_q": {
                    "status": status,
                    "tariff": tariff,
                    "tooluur_number": tooluur_number,
                    "tooluur_name": tooluur_name,
                    "tooluur_mark": tooluur_mark,
                    "expire_date": expire_date,
                },
                "menu": self.menu,
            }
            return render(request, self.template_name, data)
        elif 'download' in rq:
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="Export_tooluur_to_excel.xls"'
            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet('Sheet1')

            borders = xlwt.Borders()
            borders.left = xlwt.Borders.THIN
            borders.right = xlwt.Borders.THIN
            borders.top = xlwt.Borders.THIN
            borders.bottom = xlwt.Borders.THIN

            title_style = xlwt.XFStyle()
            title_style.font.bold = True

            header_style = xlwt.XFStyle()
            header_style.font.bold = True
            header_style.alignment.wrap = True
            header_style.alignment.vert = xlwt.Alignment.VERT_CENTER
            header_style.borders = borders

            row_style = xlwt.XFStyle()
            row_style.borders = borders

            ws.write(0, 1, 'Тоолуурын жагсаалт', title_style)
            row_num = 2

            columns = ['№', 'Тоолуурын дугаар', 'Тоолуурын нэршил', 'Тоолуурын марк', 'Төлөв', 'Тариф', 'Гүйдэл',
                       'Хүчдэл', 'Баталгаа дуусах огноо', 'Лацны дугаар']
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], header_style)
            for row in objs:
                row_num += 1

                status = ''
                if row.status == '0':
                    status = 'Ашиглагдаагүй'
                if row.status == '1':
                    status = 'Ашиглагдаж байгаа'
                if row.status == '2':
                    status = 'Ашиглалтаас гарсан'

                tariff = ''
                if row.tariff == '0':
                    tariff = '1 тарифт'
                if row.tariff == '1':
                    tariff = '2 тарифт'
                if row.tariff == '2':
                    tariff = '3 тарифт'

                ws.write(row_num, 0, row_num - 2, row_style)
                ws.write(row_num, 1, row.number, row_style)
                ws.write(row_num, 2, row.name, row_style)
                ws.write(row_num, 3, row.mark, row_style)
                ws.write(row_num, 4, status, row_style)
                ws.write(row_num, 5, tariff, row_style)
                ws.write(row_num, 6, str(row.huchdel) + 'B', row_style)
                ws.write(row_num, 7, str(row.guidel) + 'A', row_style)
                ws.write(row_num, 8, row.expire_date.strftime("%Y-%m-%d"), row_style)
                ws.write(row_num, 9, '', row_style)
            wb.save(response)
            return response


class LavlahTooluurAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_tooluur.html"
    permission_required = 'data.add_tooluur'
    menu = "7"

    def get(self, request, *args, **kwargs):
        guidel = Amper.objects.filter(is_active='1')
        huchdel = Voltage.objects.filter(is_active='1')
        tooluur_marks = list(
            Tooluur.objects.raw("SELECT id, mark FROM data_tooluur WHERE is_active='1' GROUP BY mark ORDER BY mark"))

        data = {
            "urlz": "/home/lavlagaa/add_tooluur",
            "guidel": guidel,
            "huchdel": huchdel,
            "marks": tooluur_marks,
            "menu": self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        tooluur_number = rq.get('number', '')
        tooluur_name = rq.get('name', '')
        mark = rq.get('mark', '')
        voltage = rq.get('ut', '')
        amper = rq.get('gt', '')
        tariff = rq.get('select_tariff', '')
        stamp_number = rq.get('stamp_number', '')
        cert_number = rq.get('cert_number', '')
        installed_date = rq.get('installed_date', '')
        expired_date = rq.get('expire_date', '')
        verified_date = rq.get('verified_date', '')
        try:
            Tooluur.objects.get(number=tooluur_number, is_active='1')
            messages.warning(request, "Тоолуурын дугаар системд бүртгэгдсэн байна. Та өөр дугаар ашиглана уу")
            guidel = Amper.objects.filter(is_active='1')
            huchdel = Voltage.objects.filter(is_active='1')
            tooluur_marks = TooluurMark.objects.filter(is_active='1')
            data = {
                "urlz": "/home/lavlagaa/add_tooluur",
                "number": tooluur_number,
                "name": tooluur_name,
                "mark": mark,
                "tariff": tariff,
                "status": rq.get('select_status', ''),
                "guidel": guidel,
                "huchdel": huchdel,
                "amper": amper,
                "voltage": voltage,
                "installed_date": installed_date,
                "verified_date": verified_date,
                "expire_date": expired_date,
                "stamp_number": stamp_number,
                "cert_number": cert_number,
                "marks": tooluur_marks,
                "menu": self.menu,
            }
            return render(request, self.template_name, data)
        except Tooluur.DoesNotExist:
            tooluur = Tooluur.objects.create(installed_date=installed_date, verified_date=verified_date,
                                             expire_date=expired_date)
            tooluur.number = tooluur_number
            tooluur.name = tooluur_name
            tooluur.mark = mark
            tooluur.voltage = voltage
            tooluur.amper = amper
            tooluur.status = "0"
            tooluur.tariff = tariff
            tooluur.stamp_number = stamp_number
            tooluur.cert_number = cert_number
            tooluur.save()

            messages.success(request, "Амжилттай бүртгэгдлээ.")
            if "save" in rq:
                return redirect('/home/lavlagaa/tooluur/')
            elif "save_and_continue" in rq:
                return redirect('/home/lavlagaa/add_tooluur')


class LavlagaaTooluurEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/add_tooluur.html"
    permission_required = 'data.change_tooluur'
    menu = "7"

    def get(self, request, id, *args, **kwargs):
        tooluur = Tooluur.objects.get(id=id)
        huchdel = Voltage.objects.filter(is_active='1')
        guidel = Amper.objects.filter(is_active='1')
        tooluur_marks = list(
            Tooluur.objects.raw("SELECT id, mark FROM data_tooluur WHERE is_active='1' GROUP BY mark ORDER BY mark"))
        # print(tooluur_marks)
        data = {
            "urlz": "/home/lavlagaa/edit_tooluur/" + id + "/",
            "tooluur": tooluur,
            "mark": tooluur.mark,
            "number": tooluur.number,
            "name": tooluur.name,
            "installed_date": tooluur.installed_date.strftime("%Y-%m-%d"),
            "verified_date": tooluur.verified_date.strftime("%Y-%m-%d"),
            "expire_date": tooluur.expire_date.strftime("%Y-%m-%d"),
            "huchdel": huchdel,
            "guidel": guidel,
            "ut": tooluur.voltage,
            "gt": tooluur.amper,
            "tariff": tooluur.tariff,
            "status": tooluur.status,
            "amper": tooluur.amper,
            "voltage": tooluur.voltage,
            "marks": tooluur_marks,
            "menu": self.menu,
            "stamp_number": tooluur.stamp_number,
            "cert_number": tooluur.cert_number
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        tooluur_number = rq.get('number', '')
        tooluur_name = rq.get('name', '')
        try:
            tooluur = Tooluur.objects.get(id=id)
            if tooluur.number != tooluur_number:
                try:
                    Tooluur.objects.get(number=tooluur_number, is_active='1')
                    messages.warning(request, 'Энэ тоолуурын дугаар бүртгэгдсэн байна.')
                    return redirect('/home/lavlagaa/tooluur/')
                except:
                    no_error = ""
            tooluur.number = rq.get('number', '')
            tooluur.name = rq.get('name', '')
            tooluur.mark = rq.get('mark', '')
            tooluur.installed_date = rq.get('installed_date', '')
            tooluur.verified_date = rq.get('verified_date', '')
            tooluur.expire_date = rq.get('expire_date')
            tooluur.status = rq.get('select_status', '')
            tooluur.tariff = rq.get('select_tariff', '')
            tooluur.voltage = int(rq.get('ut', ''))
            tooluur.amper = int(rq.get('gt', ''))
            tooluur.stamp_number = rq.get('stamp_number', '')
            tooluur.cert_number = rq.get('cert_number', '')
            tooluur.save()
            messages.success(request, 'Амжилттай хадгалагдлаа.')
            return redirect('/home/lavlagaa/tooluur')
        except Tooluur.DoesNotExist:
            messages.warning(request, 'Алдаа гарлаа')
            redirect('/home/lavlagaa/tooluur/')


class LavlagaaTooluurDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    template_name = "homepage/lavlah/tooluur.html"
    permission_required = 'data.delete_tooluur'

    def get(self, request, id, *args, **kwargs):
        try:
            t = Tooluur.objects.get(id=id)
            t.is_active = 0
            t.save()
            messages.success(request, 'Амжилттай устгагдлаа.')
        except Exception as e:
            print(e)
            messages.success(request, 'Устгахад алдаа гарлаа.')
        return redirect("/home/lavlagaa/tooluur")
