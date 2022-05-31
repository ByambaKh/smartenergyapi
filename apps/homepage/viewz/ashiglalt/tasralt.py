import logging
from calendar import monthrange

import simplejson
import xlwt
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from datetime import datetime, date
from apps.data.models import DedStants, Tasralt, Shugam


class TasraltList(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_tasralt'
    template_name = "homepage/ashiglalt/tasralt_list.html"
    menu = '4'
    sub = '1'

    qry = "SELECT tas.id, tas.tasarsan_date, tas.zalgasan_date, tas.tasraltiin_hugatsaa, tas.amper, tas.voltage," \
          " tas.chadal, tas.dutuu_tugeesen, tas.ajillasan_hamgaalalt, tas.tasraltiin_shaltgaan," \
          " tas.avsan_arga_hemjee, ded.name AS ded_stants_name, shug.shugam_ner FROM data_tasralt tas" \
          " JOIN data_dedstants ded ON tas.ded_stants_id=ded.id" \
          " JOIN data_shugam shug ON tas.shugam_id=shug.id" \
          " WHERE tas.is_active=1"

    query = "SELECT id, ded_stants_id, COUNT(id) AS too, SUM(chadal) AS chadal, SUM(tasraltiin_hugatsaa) AS hugatsaa,"
    query += " SUM(dutuu_tugeesen) AS dutuu FROM data_tasralt WHERE is_active='1' AND "

    def get_last_day(self, year, month):
        month_last_day = str(monthrange(int(year), int(month))).split(',')
        month_last_day = str(month_last_day[1].replace(' ', '').replace(')', ''))
        return month_last_day

    try:
        ded_stants = DedStants.objects.filter(is_active=1).order_by('name')
    except ObjectDoesNotExist:
        ded_stants = None

    current_season = 0
    current_year = date.today().strftime("%Y")
    current_month = date.today().strftime("%m")
    start_month = end_month = 0
    if int(current_month) >= 1 and int(current_month) <= 3:
        current_season = 1
        start_month = 1
        end_month = 3
    if int(current_month) >= 4 and int(current_month) <= 6:
        current_season = 2
        start_month = 4
        end_month = 6
    if int(current_month) >= 7 and int(current_month) <= 9:
        current_season = 3
        start_month = 7
        end_month = 9
    if int(current_month) >= 10 and int(current_month) <= 12:
        current_season = 4
        start_month = 10
        end_month = 12

    tasralts_year = None
    tasralts_season = None
    tasralts_month = None
    year_tasralts_ded = []
    season_tasralts_ded = []
    month_tasralts_ded = []
    dedstants_ids = []

    def get(self, request, activeTab, *args, **kwargs):
        q = self.qry
        q = q + " ORDER BY tas.created_date DESC"

        if 'ded_stants' in request.GET:
            ded_stants_id = request.GET['ded_stants']
            result_set = []
            try:
                shugams = Shugam.objects.filter(ded_stants_id=ded_stants_id)
                for shugam in shugams:
                    result_set.append({'id': shugam.id, 'name': shugam.shugam_ner})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"Shugam" model has no object: %s', e)

        try:
            tasralt_list = Tasralt.objects.raw(q)
        except ObjectDoesNotExist:
            tasralt_list = None

        qry_year = self.query + "tasarsan_date>='" + self.current_year + "-01-01' AND zalgasan_date<='" + self.current_year + "-12-31'"

        start_date = str(self.current_year) + '-' + str(self.start_month) + '-01'
        end_date = str(self.current_year) + '-' + str(self.end_month) + '-' + str(self.get_last_day(self.current_year, self.end_month))
        qry_season = self.query + "tasarsan_date>='" + start_date + "' AND zalgasan_date<='" + end_date + "'"

        start_date = str(self.current_year) + '-' + str(self.current_month) + '-01'
        end_date = str(self.current_year) + '-' + str(self.current_month) + '-' + str(self.get_last_day(self.current_year, self.current_month))
        qry_month = self.query + "tasarsan_date>='" + start_date + "' AND zalgasan_date<='" + end_date + "'"

        try:
            TasraltList.tasralts_year = Tasralt.objects.raw(qry_year)
        except ObjectDoesNotExist:
            TasraltList.tasralts_year = None
        try:
            TasraltList.tasralts_season = Tasralt.objects.raw(qry_season)
        except ObjectDoesNotExist:
            TasraltList.tasralts_season = None
        try:
            TasraltList.tasralts_month = Tasralt.objects.raw(qry_month)
        except ObjectDoesNotExist:
            TasraltList.tasralts_month = None

        try:
            TasraltList.ded_stants_ids = Tasralt.objects.raw("SELECT id, ded_stants_id FROM data_tasralt GROUP BY ded_stants_id")
            for ded_stants_id in TasraltList.ded_stants_ids:
                self.dedstants_ids.append(ded_stants_id.ded_stants_id)
                qry_year_ded = self.query + "tasarsan_date>='" + self.current_year + "-01-01' AND zalgasan_date<='" + self.current_year + "-12-31' AND ded_stants_id="+str(ded_stants_id.ded_stants_id)
                try:
                    TasraltList.year_tasralts_ded.extend(list(Tasralt.objects.raw(qry_year_ded)))
                except ObjectDoesNotExist:
                    TasraltList.year_tasralts_ded.extend([])

                start_date = str(self.current_year) + '-' + str(self.start_month) + '-01'
                end_date = str(self.current_year) + '-' + str(self.end_month) + '-' + str(self.get_last_day(self.current_year, self.end_month))
                qry_season_ded = self.query + "tasarsan_date>='" + start_date + "' AND zalgasan_date<='" + end_date + "' AND ded_stants_id="+str(ded_stants_id.ded_stants_id)
                try:
                    TasraltList.season_tasralts_ded.extend(list(Tasralt.objects.raw(qry_season_ded)))
                except ObjectDoesNotExist:
                    TasraltList.season_tasralts_ded.extend([])

                start_date = str(self.current_year) + '-' + str(self.current_month) + '-01'
                end_date = str(self.current_year) + '-' + str(self.current_month) + '-' + str(self.get_last_day(self.current_year, self.current_month))
                qry_month_ded = self.query + "tasarsan_date>='" + start_date + "' AND zalgasan_date<='" + end_date + "' AND ded_stants_id="+str(ded_stants_id.ded_stants_id)
                try:
                    TasraltList.month_tasralts_ded.extend(list(Tasralt.objects.raw(qry_month_ded)))
                except ObjectDoesNotExist:
                    TasraltList.month_tasralts_ded.extend([])
        except ObjectDoesNotExist:
            self.dedstants_ids = []

        data = {
            'tasralt_list': tasralt_list,
            'tasralts_year': TasraltList.tasralts_year,
            'tasralts_season': TasraltList.tasralts_season,
            'tasralts_month': TasraltList.tasralts_month,
            'ded_stants': self.ded_stants,
            'dedstants_ids': TasraltList.dedstants_ids,
            'month_tasralts_ded': TasraltList.month_tasralts_ded,
            'season_tasralts_ded': TasraltList.season_tasralts_ded,
            'year_tasralts_ded': TasraltList.year_tasralts_ded,
            'menu': self.menu,
            'sub': self.sub,
            'activeTab': str(activeTab),
        }
        return render(request, self.template_name, data)

    def post(self, request, activeTab, *args, **kwargs):
        ded_stant = request.POST['ded_stant']
        shugam = request.POST['shugam']
        tasarsan_date = request.POST['tasarsan_date']
        zalgasan_date = request.POST['zalgasan_date']
        tasraltiin_hugatsaa = request.POST['tasraltiin_hugatsaa']
        ajillasan_hamgaalalt = request.POST['ajillasan_hamgaalalt']

        q = self.qry

        shugams = None
        if ded_stant != '':
            q = q + " AND tas.ded_stants_id LIKE '%%" + ded_stant + "%%'"
            try:
                shugams = Shugam.objects.filter(ded_stants_id=ded_stant)
            except ObjectDoesNotExist:
                shugams = None
        if shugam != '':
            q = q + " AND tas.shugam_id LIKE '%%" + shugam + "%%'"
        if tasarsan_date != '':
            q = q + " AND tas.tasarsan_date >= '" + tasarsan_date + "'"
        if zalgasan_date != '':
            q = q + " AND tas.zalgasan_date <= '" + zalgasan_date + "'"
        if tasraltiin_hugatsaa != '':
            q = q + " AND tas.tasraltiin_hugatsaa LIKE '%%" + tasraltiin_hugatsaa + "%%'"
        if ajillasan_hamgaalalt != '':
            q = q + " AND tas.ajillasan_hamgaalalt LIKE '%%" + ajillasan_hamgaalalt + "%%'"

        try:
            tasralt_list = Tasralt.objects.raw(q)
        except ObjectDoesNotExist:
            tasralt_list = None

        data = {
            'tasralt_list': tasralt_list,
            'ded_stants': self.ded_stants,
            'shugams': shugams,
            'menu': self.menu,
            'sub': self.sub,
            'activeTab': str(activeTab),
            'qry': {
                'ded_stant': int(ded_stant) if ded_stant != '' else ded_stant,
                'shugam': int(shugam) if shugam != '' else shugam,
                'tasarsan_date': tasarsan_date,
                'zalgasan_date': zalgasan_date,
                'tasraltiin_hugatsaa': tasraltiin_hugatsaa,
                'ajillasan_hamgaalalt': ajillasan_hamgaalalt,
            }
        }
        return render(request, self.template_name, data)

    def tasralt_list_xls(request):
        borders = xlwt.Borders()
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        header_title_border = xlwt.Borders()
        header_title_border.bottom = xlwt.Borders.THIN
        header_title_style = xlwt.XFStyle()
        header_title_style.font.bold = True
        header_title_style.borders = header_title_border
        title_style = xlwt.XFStyle()
        title_style.font.bold = True
        header_style = xlwt.XFStyle()
        header_style.font.bold = True
        header_style.alignment.wrap = True
        header_style.alignment.vert = xlwt.Alignment.VERT_CENTER
        header_style.borders = borders
        row_style = xlwt.XFStyle()
        row_style.borders = borders

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Ashiglalt_tasralt_tovch_tailan.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Sheet1')

        ws.write(0, 3, '[Ашиглалт] Тасралт товч тайлан', title_style)
        ws.write(2, 0, 'Тайлангийн хамрах хугацаа : ' + TasraltList.current_year + ' он, ' + str(TasraltList.current_season) + '-р улирал, ' + TasraltList.current_month + '-р сар', xlwt.XFStyle())
        ws.write(2, 6, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())

        col_width = [int(23 * 260), int(17 * 260), int(8 * 260), int(23 * 260), int(17 * 260), int(8 * 260), int(23 * 260), int(17 * 260)]
        for col_num in range(len(col_width)):
            ws.col(col_num).width = col_width[col_num]

        ws.write_merge(4, 4, 0, 7, 'НИЙТ', header_title_style)
        ws.write_merge(6, 6, 0, 1, TasraltList.current_year + ' он', title_style)
        ws.write_merge(6, 6, 3, 4, str(TasraltList.current_season) + '-р улирал', title_style)
        ws.write_merge(6, 6, 6, 7, TasraltList.current_month + '-р сар', title_style)

        ws.write(8, 0, 'Нийт тасарсан тоо : ', row_style)
        ws.write(9, 0, 'Нийт тасарсан хугацаа : ', row_style)
        ws.write(10, 0, 'Нийт чадал : ', row_style)
        ws.write(11, 0, 'Нийт дутуу түгээсэн ЭХ : ', row_style)

        qry_year = TasraltList.query + "tasarsan_date>='" + TasraltList.current_year + "-01-01' AND zalgasan_date<='" + TasraltList.current_year + "-12-31'"
        TasraltList.tasralts_year = Tasralt.objects.raw(qry_year)
        for tasralts_year in TasraltList.tasralts_year:
            ws.write(8, 1, str(round(tasralts_year.too, 2) if tasralts_year.too else 0), row_style)
            ws.write(9, 1, str(round(tasralts_year.hugatsaa, 2) if tasralts_year.hugatsaa else 0) + ' цаг', row_style)
            ws.write(10, 1, str(round(tasralts_year.chadal, 2) if tasralts_year.chadal else 0) + ' кВт', row_style)
            ws.write(11, 1, str(round(tasralts_year.dutuu, 2) if tasralts_year.dutuu else 0) + ' кВт/цаг', row_style)

        ws.write(8, 3, 'Нийт тасарсан тоо : ', row_style)
        ws.write(9, 3, 'Нийт тасарсан хугацаа : ', row_style)
        ws.write(10, 3, 'Нийт чадал : ', row_style)
        ws.write(11, 3, 'Нийт дутуу түгээсэн ЭХ : ', row_style)

        start_date = str(TasraltList.current_year) + '-' + str(TasraltList.current_month) + '-01'
        end_date = str(TasraltList.current_year) + '-' + str(TasraltList.current_month) + '-' + str(
            TasraltList.get_last_day(TasraltList,TasraltList.current_year, TasraltList.current_month))
        qry_season = TasraltList.query + "tasarsan_date>='" + start_date + "' AND zalgasan_date<='" + end_date + "'"
        TasraltList.tasralts_season = Tasralt.objects.raw(qry_season)

        for tasralts_season in TasraltList.tasralts_season:
            ws.write(8, 4, str(round(tasralts_season.too, 2) if tasralts_season.too else 0), row_style)
            ws.write(9, 4, str(round(tasralts_season.hugatsaa, 2) if tasralts_season.hugatsaa else 0) + ' цаг', row_style)
            ws.write(10, 4, str(round(tasralts_season.chadal, 2) if tasralts_season.chadal else 0) + ' кВт', row_style)
            ws.write(11, 4, str(round(tasralts_season.dutuu, 2) if tasralts_season.dutuu else 0) + ' кВт/цаг', row_style)

        ws.write(8, 6, 'Нийт тасарсан тоо : ', row_style)
        ws.write(9, 6, 'Нийт тасарсан хугацаа : ', row_style)
        ws.write(10, 6, 'Нийт чадал : ', row_style)
        ws.write(11, 6, 'Нийт дутуу түгээсэн ЭХ : ', row_style)

        qry_month = TasraltList.query + "tasarsan_date>='" + start_date + "' AND zalgasan_date<='" + end_date + "'"
        TasraltList.tasralts_month = Tasralt.objects.raw(qry_month)

        for tasralts_month in TasraltList.tasralts_month:
            ws.write(8, 7, str(round(tasralts_month.too, 2) if tasralts_month.too else 0), row_style)
            ws.write(9, 7, str(round(tasralts_month.hugatsaa, 2) if tasralts_month.hugatsaa else 0) + ' цаг', row_style)
            ws.write(10, 7, str(round(tasralts_month.chadal, 2) if tasralts_month.chadal else 0) + ' кВт', row_style)
            ws.write(11, 7, str(round(tasralts_month.dutuu, 2) if tasralts_month.dutuu else 0) + ' кВт/цаг', row_style)

        ws.write_merge(13, 13, 0, 7, 'ДЭД СТАНЦ', header_title_style)

        counter = 0
        row_num = 15
        print(TasraltList.dedstants_ids)

        for dedstants_ids in TasraltList.dedstants_ids:
            year_tasralts_ded = TasraltList.year_tasralts_ded[counter]
            season_tasralts_ded = TasraltList.season_tasralts_ded[counter]
            month_tasralts_ded = TasraltList.month_tasralts_ded[counter]

            ded_stants = DedStants.objects.get(id=dedstants_ids)
            ws.write_merge(row_num, row_num, 3, 4, ded_stants.name, header_title_style)
            row_num += 2
            ws.write_merge(row_num, row_num, 0, 1, TasraltList.current_year + ' он', title_style)
            ws.write_merge(row_num, row_num, 3, 4, str(TasraltList.current_season) + '-р улирал', title_style)
            ws.write_merge(row_num, row_num, 6, 7, TasraltList.current_month + '-р сар', title_style)

            if year_tasralts_ded and season_tasralts_ded and month_tasralts_ded:
                counter += 1
                row_num += 2
                ws.write(row_num, 0, 'Нийт тасарсан тоо : ', row_style)
                ws.write(row_num, 1, str(round(year_tasralts_ded.too, 2) if year_tasralts_ded.too else 0), row_style)
                ws.write(row_num, 3, 'Нийт тасарсан тоо : ', row_style)
                ws.write(row_num, 4, str(round(season_tasralts_ded.too, 2) if season_tasralts_ded.too else 0), row_style)
                ws.write(row_num, 6, 'Нийт тасарсан тоо : ', row_style)
                ws.write(row_num, 7, str(round(month_tasralts_ded.too, 2) if month_tasralts_ded.too else 0), row_style)
                row_num += 1
                ws.write(row_num, 0, 'Нийт тасарсан хугацаа : ', row_style)
                ws.write(row_num, 1, str(round(year_tasralts_ded.hugatsaa, 2) if year_tasralts_ded.hugatsaa else 0) + ' цаг', row_style)
                ws.write(row_num, 3, 'Нийт тасарсан хугацаа : ', row_style)
                ws.write(row_num, 4, str(round(season_tasralts_ded.hugatsaa, 2) if season_tasralts_ded.hugatsaa else 0) + ' цаг', row_style)
                ws.write(row_num, 6, 'Нийт тасарсан хугацаа : ', row_style)
                ws.write(row_num, 7, str(round(month_tasralts_ded.hugatsaa, 2) if month_tasralts_ded.hugatsaa else 0) + ' цаг', row_style)
                row_num += 1
                ws.write(row_num, 0, 'Нийт чадал : ', row_style)
                ws.write(row_num, 1, str(round(year_tasralts_ded.chadal, 2) if year_tasralts_ded.chadal else 0) + ' кВт', row_style)
                ws.write(row_num, 3, 'Нийт чадал : ', row_style)
                ws.write(row_num, 4, str(round(season_tasralts_ded.chadal, 2) if season_tasralts_ded.chadal else 0) + ' кВт', row_style)
                ws.write(row_num, 6, 'Нийт чадал : ', row_style)
                ws.write(row_num, 7, str(round(month_tasralts_ded.chadal, 2) if month_tasralts_ded.chadal else 0) + ' кВт', row_style)
                row_num += 1
                ws.write(row_num, 0, 'Нийт дутуу түгээсэн ЭХ : ', row_style)
                ws.write(row_num, 1, str(round(year_tasralts_ded.dutuu, 2) if year_tasralts_ded.dutuu else 0) + ' кВт/цаг', row_style)
                ws.write(row_num, 3, 'Нийт дутуу түгээсэн ЭХ : ', row_style)
                ws.write(row_num, 4, str(round(season_tasralts_ded.dutuu, 2) if season_tasralts_ded.dutuu else 0) + ' кВт/цаг', row_style)
                ws.write(row_num, 6, 'Нийт дутуу түгээсэн ЭХ : ', row_style)
                ws.write(row_num, 7, str(round(month_tasralts_ded.dutuu, 2) if month_tasralts_ded.dutuu else 0) + ' кВт/цаг', row_style)
            row_num += 2
        wb.save(response)
        return response


class TasraltAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_tasralt'
    template_name = "homepage/ashiglalt/tasralt_add.html"
    menu = '4'
    sub = '1'

    def get(self, request, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.filter(is_active=1).order_by('name')
        except ObjectDoesNotExist:
            ded_stants = None

        if 'ded_stants' in request.GET:
            ded_stants_id = request.GET['ded_stants']
            result_set = []
            try:
                shugams = Shugam.objects.filter(ded_stants_id=ded_stants_id)
                for shugam in shugams:
                    result_set.append({'id': shugam.id, 'name': shugam.shugam_ner})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"Shugam" model has no object: %s', e)

        data = {
            'action': '/home/ashiglalt/tasralt_add',
            'ded_stants': ded_stants,
            'menu': self.menu,
            'sub': self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.get(id=request.POST['ded_stants'])
        except ObjectDoesNotExist:
            ded_stants = None

        try:
            shugam = Shugam.objects.get(id=request.POST['shugam'])
        except ObjectDoesNotExist:
            shugam = None

        if ded_stants is not None and shugam is not None:
            tasarsan_date = datetime.strptime(request.POST['tasarsan_date'], '%Y-%m-%d %H:%M')
            zalgasan_date = datetime.strptime(request.POST['zalgasan_date'], '%Y-%m-%d %H:%M')

            try:
                tasralt = Tasralt.objects.create(ded_stants_id=request.POST['ded_stants'], tasarsan_date=tasarsan_date, zalgasan_date=zalgasan_date)
                tasralt.created_user_id = request.user.id
                tasralt.shugam = shugam
                tasralt.amper = request.POST['amper']
                tasralt.voltage = request.POST['voltage']
                tasralt.chadal = request.POST['chadal']
                tasralt.tasraltiin_hugatsaa = request.POST['tasraltiin_hugatsaa']
                tasralt.dutuu_tugeesen = request.POST['dutuu_tugeesen']
                tasralt.ajillasan_hamgaalalt = request.POST['ajillasan_hamgaalalt']
                tasralt.tasraltiin_shaltgaan = request.POST['tasraltiin_shaltgaan']
                tasralt.avsan_arga_hemjee = request.POST['avsan_arga_hemjee']
                tasralt.save()
                messages.success(request, 'Амжилттай хадгалагдлаа!')
            except ObjectDoesNotExist:
                messages.error(request, 'Хадгалахад алдаа гарлаа!')
                return redirect('/home/ashiglalt/tasralt_add')

            return redirect('/home/ashiglalt/tasralt_list/1/')


class TasraltEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_tasralt'
    template_name = 'homepage/ashiglalt/tasralt_add.html'
    menu = '4'
    sub = '1'

    def get(self, request, id, *args, **kwargs):
        try:
            tasralt = Tasralt.objects.get(id=id)
            shugams = Shugam.objects.filter(ded_stants_id=tasralt.ded_stants_id)
        except ObjectDoesNotExist:
            tasralt = None
            shugams = None
        try:
            ded_stants = DedStants.objects.filter(is_active=1)
        except ObjectDoesNotExist:
            ded_stants = None

        if 'ded_stants' in request.GET:
            ded_stants_id = request.GET['ded_stants']
            result_set = []
            try:
                shugams = Shugam.objects.filter(ded_stants_id=ded_stants_id)
                for shugam in shugams:
                    result_set.append({'id': shugam.id, 'name': shugam.shugam_ner})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"Shugam" model has no object: %s', e)

        data = {
            'action': '/home/ashiglalt/tasralt_edit/'+id+'/',
            'tasralt': tasralt,
            'ded_stants': ded_stants,
            'shugams': shugams,
            'menu': self.menu,
            'sub': self.sub,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.get(id=request.POST['ded_stants'])
        except ObjectDoesNotExist:
            ded_stants = None
        try:
            shugam = Shugam.objects.get(id=request.POST['shugam'])
        except ObjectDoesNotExist:
            shugam = None

        tasarsan_date = datetime.strptime(request.POST['tasarsan_date'], '%Y-%m-%d %H:%M')
        zalgasan_date = datetime.strptime(request.POST['zalgasan_date'], '%Y-%m-%d %H:%M')

        try:
            tasralt = Tasralt.objects.get(id=id)
            tasralt.ded_stants = ded_stants
            tasralt.shugam = shugam
            tasralt.amper = request.POST['amper']
            tasralt.voltage = request.POST['voltage']
            tasralt.chadal = request.POST['chadal']
            tasralt.tasarsan_date = tasarsan_date
            tasralt.zalgasan_date = zalgasan_date
            tasralt.tasraltiin_hugatsaa = request.POST['tasraltiin_hugatsaa']
            tasralt.dutuu_tugeesen = request.POST['dutuu_tugeesen']
            tasralt.ajillasan_hamgaalalt = request.POST['ajillasan_hamgaalalt']
            tasralt.tasraltiin_shaltgaan = request.POST['tasraltiin_shaltgaan']
            tasralt.avsan_arga_hemjee = request.POST['avsan_arga_hemjee']
            tasralt.save()
            messages.success(request, 'Амжилттай засварлагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Засварлахад алдаа гарлаа!')
            return redirect('/home/ashiglalt/tasralt_add')

        return redirect('/home/ashiglalt/tasralt_list/1/')


class TasraltDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_tasralt'

    def get(self, request, id, *args, **kwargs):
        try:
            tasralt = Tasralt.objects.get(id=id)
            tasralt.is_active = 0
            tasralt.save()
            messages.success(request, 'Амжилттай устгагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Устахад алдаа гарлаа!')

        return redirect('/home/ashiglalt/tasralt_list/1/')