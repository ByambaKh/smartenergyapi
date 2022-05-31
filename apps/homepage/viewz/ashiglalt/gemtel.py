import logging
from calendar import monthrange

import simplejson
import xlwt
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from datetime import datetime, date
from apps.data.models import DedStants, Shugam, Gemtel
from apps.homepage.forms import GemtelZuragForm


class GemtelList(PermissionRequiredMixin, LoginRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_gemtel'
    template_name = "homepage/ashiglalt/gemtel_list.html"
    menu = '4'
    sub = '5'

    qry = "SELECT gem.id, gem.gemtsen_date, gem.zalgasan_date, gem.gemtsen_hugatsaa, gem.amper, gem.voltage, gem.chadal," \
          " gem.dutuu_tugeesen, gem.gemtsen_shaltgaan, gem.zurag, ded.name AS ded_stants_name, shug.shugam_ner," \
          " aut.first_name, aut.last_name FROM data_gemtel gem" \
          " JOIN data_dedstants ded ON gem.ded_stants_id=ded.id" \
          " JOIN data_shugam shug ON gem.shugam_id=shug.id" \
          " JOIN auth_user aut ON gem.dispetcher_id=aut.id" \
          " WHERE gem.is_active=1"

    query = "SELECT id, COUNT(id) AS too, SUM(chadal) AS chadal, SUM(gemtsen_hugatsaa) AS hugatsaa,"
    query += " SUM(dutuu_tugeesen) AS dutuu FROM data_gemtel WHERE is_active='1' AND "

    def get_last_day(self, year, month):
        month_last_day = str(monthrange(int(year), int(month))).split(',')
        month_last_day = str(month_last_day[1].replace(' ', '').replace(')', ''))
        return month_last_day

    try:
        ded_stants = DedStants.objects.filter(is_active=1).order_by('name')
    except ObjectDoesNotExist:
        ded_stants = None
    try:
        dispetchers = User.objects.filter(Q(groups__name='Ахлах диспетчер инженер') | Q(groups__name='Диспетчер инженер'))
    except ObjectDoesNotExist:
        dispetchers = None

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

    gemtels_year = None
    gemtels_season = None
    gemtels_month = None
    year_gemtels_ded = []
    season_gemtels_ded = []
    month_gemtels_ded = []
    dedstants_ids = []

    def get(self, request, activeTab, *args, **kwargs):
        q = self.qry
        q = q + " ORDER BY gem.created_date DESC"

        if 'ded_stants' in request.GET:
            ded_stants_id = request.GET['ded_stants']
            print(ded_stants_id)
            result_set = []
            try:
                shugams = Shugam.objects.filter(ded_stants_id=ded_stants_id)
                for shugam in shugams:
                    result_set.append({'id': shugam.id, 'name': shugam.shugam_ner})
                return HttpResponse(simplejson.dumps(result_set), content_type='application/json')
            except ObjectDoesNotExist as e:
                logging.error('"Shugam" model has no object: %s', e)

        try:
            gemtel_list = Gemtel.objects.raw(q)
        except ObjectDoesNotExist:
            gemtel_list = None

        qry_year = self.query + "gemtsen_date>='" + self.current_year + "-01-01' AND zalgasan_date<='" + self.current_year + "-12-31'"

        start_date = str(self.current_year) + '-' + str(self.start_month) + '-01'
        end_date = str(self.current_year) + '-' + str(self.end_month) + '-' + str(self.get_last_day(self.current_year, self.end_month))
        qry_season = self.query + "gemtsen_date>='" + start_date + "' AND zalgasan_date<='" + end_date + "'"

        start_date = str(self.current_year) + '-' + str(self.current_month) + '-01'
        end_date = str(self.current_year) + '-' + str(self.current_month) + '-' + str(self.get_last_day(self.current_year, self.current_month))
        qry_month = self.query + "gemtsen_date>='" + start_date + "' AND zalgasan_date<='" + end_date + "'"

        try:
            GemtelList.gemtels_year = Gemtel.objects.raw(qry_year)
        except ObjectDoesNotExist:
            GemtelList.gemtels_year = None
        try:
            GemtelList.gemtels_season = Gemtel.objects.raw(qry_season)
        except ObjectDoesNotExist:
            GemtelList.gemtels_season = None
        try:
            GemtelList.gemtels_month = Gemtel.objects.raw(qry_month)
        except ObjectDoesNotExist:
            GemtelList.gemtels_month = None

        try:
            ded_stants_ids = Gemtel.objects.raw("SELECT id, ded_stants_id FROM data_gemtel GROUP BY ded_stants_id")
            for ded_stants_id in ded_stants_ids:
                GemtelList.dedstants_ids.append(ded_stants_id.ded_stants_id)
                qry_year_ded = self.query + "gemtsen_date>='" + self.current_year + "-01-01' AND zalgasan_date<='" + self.current_year + "-12-31' AND ded_stants_id="+str(ded_stants_id.ded_stants_id)
                try:
                    GemtelList.year_gemtels_ded.extend(list(Gemtel.objects.raw(qry_year_ded)))
                except ObjectDoesNotExist:
                    GemtelList.year_gemtels_ded.extend([])
                start_date = str(self.current_year) + '-' + str(self.start_month) + '-01'
                end_date = str(self.current_year) + '-' + str(self.end_month) + '-' + str(self.get_last_day(self.current_year, self.end_month))
                qry_season_ded = self.query + "gemtsen_date>='" + start_date + "' AND zalgasan_date<='" + end_date + "' AND ded_stants_id="+str(ded_stants_id.ded_stants_id)
                try:
                    GemtelList.season_gemtels_ded.extend(list(Gemtel.objects.raw(qry_season_ded)))
                except ObjectDoesNotExist:
                    GemtelList.season_gemtels_ded.extend([])
                start_date = str(self.current_year) + '-' + str(self.current_month) + '-01'
                end_date = str(self.current_year) + '-' + str(self.current_month) + '-' + str(self.get_last_day(self.current_year, self.current_month))
                qry_month_ded = self.query + "gemtsen_date>='" + start_date + "' AND zalgasan_date<='" + end_date + "' AND ded_stants_id="+str(ded_stants_id.ded_stants_id)
                try:
                    GemtelList.month_gemtels_ded.extend(list(Gemtel.objects.raw(qry_month_ded)))
                except ObjectDoesNotExist:
                    GemtelList.month_gemtels_ded.extend([])
        except ObjectDoesNotExist:
            GemtelList.dedstants_ids = []

        data = {
            'gemtel_list': gemtel_list,
            'gemtels_year': self.gemtels_year,
            'gemtels_season': self.gemtels_season,
            'gemtels_month': self.gemtels_month,
            'gemtels_year_ded': self.year_gemtels_ded,
            'gemtels_season_ded': self.season_gemtels_ded,
            'gemtels_month_ded': self.month_gemtels_ded,
            'dedstants_ids': self.dedstants_ids,
            'ded_stants': self.ded_stants,
            'dispetchers': self.dispetchers,
            'menu': self.menu,
            'sub': self.sub,
            'activeTab': str(activeTab),
        }
        return render(request, self.template_name, data)

    def post(self, request, activeTab, *args, **kwargs):
        ded_stants = request.POST['ded_stants']
        shugam = request.POST['shugam']
        gemtsen_date = request.POST['gemtsen_date']
        zalgasan_date = request.POST['zalgasan_date']
        gemtsen_hugatsaa = request.POST['gemtsen_hugatsaa']
        dispetcher = request.POST['dispetcher']

        q = self.qry
        shugams = None
        if ded_stants != '':
            q = q + " AND gem.ded_stants_id LIKE '%%" + ded_stants + "%%'"
            try:
                shugams = Shugam.objects.filter(ded_stants_id=ded_stants)
            except ObjectDoesNotExist:
                shugams = None
        if shugam != '':
            q = q + " AND gem.shugam_id LIKE '%%" + shugam + "%%'"
        if gemtsen_date != '':
            q = q + " AND gem.gemtsen_date LIKE '%%" + gemtsen_date + "%%'"
        if zalgasan_date != '':
            q = q + " AND gem.zalgasan_date LIKE '%%" + zalgasan_date + "%%'"
        if gemtsen_hugatsaa != '':
            q = q + " AND gem.gemtsen_hugatsaa LIKE '%%" + gemtsen_hugatsaa + "%%'"
        if dispetcher != '':
            q = q + " AND gem.dispetcher_id LIKE '%%" + dispetcher + "%%'"

        try:
            gemtel_list = Gemtel.objects.raw(q)
        except ObjectDoesNotExist:
            gemtel_list = None

        data = {
            'gemtel_list': gemtel_list,
            'ded_stants': self.ded_stants,
            'shugams': shugams,
            'dispetchers': self.dispetchers,
            'menu': self.menu,
            'sub': self.sub,
            'activeTab': str(activeTab),
            'qry': {
                'ded_stants': int(ded_stants) if ded_stants != '' else ded_stants,
                'shugam': int(shugam) if shugam != '' else shugam,
                'gemtsen_date': gemtsen_date,
                'zalgasan_date': zalgasan_date,
                'gemtsen_hugatsaa': gemtsen_hugatsaa,
                'dispetcher': int(dispetcher) if dispetcher != '' else dispetcher,
            }
        }
        return render(request, self.template_name, data)

    def gemtel_list_xls(request):
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
        response['Content-Disposition'] = 'attachment; filename="Ashiglalt_gemtel_tovch_tailan.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Sheet1')

        ws.write(0, 3, '[Ашиглалт] Гэмтэл товч тайлан', title_style)
        ws.write(2, 0, 'Тайлангийн хамрах хугацаа : ' + GemtelList.current_year + ' он, ' + str(GemtelList.current_season) + '-р улирал, ' + GemtelList.current_month + '-р сар', xlwt.XFStyle())
        ws.write(2, 6, 'Хэвлэсэн огноо : ' + date.today().strftime("%Y-%m-%d"), xlwt.XFStyle())

        col_width = [int(23 * 260), int(17 * 260), int(8 * 260), int(23 * 260), int(17 * 260), int(8 * 260), int(23 * 260), int(17 * 260)]
        for col_num in range(len(col_width)):
            ws.col(col_num).width = col_width[col_num]

        ws.write_merge(4, 4, 0, 7, 'НИЙТ', header_title_style)
        ws.write_merge(6, 6, 0, 1, GemtelList.current_year + ' он', title_style)
        ws.write_merge(6, 6, 3, 4, str(GemtelList.current_season) + '-р улирал', title_style)
        ws.write_merge(6, 6, 6, 7, GemtelList.current_month + '-р сар', title_style)

        ws.write(8, 0, 'Нийт гэмтсэн тоо : ', row_style)
        ws.write(9, 0, 'Нийт гэмтсэн хугацаа : ', row_style)
        ws.write(10, 0, 'Нийт чадал : ', row_style)
        ws.write(11, 0, 'Нийт дутуу түгээсэн ЭХ : ', row_style)
        for taslalts_year in GemtelList.gemtels_year:
            ws.write(8, 1, str(round(taslalts_year.too, 2) if taslalts_year.too else 0), row_style)
            ws.write(9, 1, str(round(taslalts_year.hugatsaa, 2) if taslalts_year.hugatsaa else 0) + ' цаг', row_style)
            ws.write(10, 1, str(round(taslalts_year.chadal, 2) if taslalts_year.chadal else 0) + ' кВт', row_style)
            ws.write(11, 1, str(round(taslalts_year.dutuu, 2) if taslalts_year.dutuu else 0) + ' кВт/цаг', row_style)

        ws.write(8, 3, 'Нийт гэмтсэн тоо : ', row_style)
        ws.write(9, 3, 'Нийт гэмтсэн хугацаа : ', row_style)
        ws.write(10, 3, 'Нийт чадал : ', row_style)
        ws.write(11, 3, 'Нийт дутуу түгээсэн ЭХ : ', row_style)
        for taslalts_season in GemtelList.gemtels_season:
            ws.write(8, 4, str(round(taslalts_season.too, 2) if taslalts_season.too else 0), row_style)
            ws.write(9, 4, str(round(taslalts_season.hugatsaa, 2) if taslalts_season.hugatsaa else 0) + ' цаг', row_style)
            ws.write(10, 4, str(round(taslalts_season.chadal, 2) if taslalts_season.chadal else 0) + ' кВт', row_style)
            ws.write(11, 4, str(round(taslalts_season.dutuu, 2) if taslalts_season.dutuu else 0) + ' кВт/цаг', row_style)

        ws.write(8, 6, 'Нийт гэмтсэн тоо : ', row_style)
        ws.write(9, 6, 'Нийт гэмтсэн хугацаа : ', row_style)
        ws.write(10, 6, 'Нийт чадал : ', row_style)
        ws.write(11, 6, 'Нийт дутуу түгээсэн ЭХ : ', row_style)
        for taslalts_month in GemtelList.gemtels_month:
            ws.write(8, 7, str(round(taslalts_month.too, 2) if taslalts_month.too else 0), row_style)
            ws.write(9, 7, str(round(taslalts_month.hugatsaa, 2) if taslalts_month.hugatsaa else 0) + ' цаг', row_style)
            ws.write(10, 7, str(round(taslalts_month.chadal, 2) if taslalts_month.chadal else 0) + ' кВт', row_style)
            ws.write(11, 7, str(round(taslalts_month.dutuu, 2) if taslalts_month.dutuu else 0) + ' кВт/цаг', row_style)

        ws.write_merge(13, 13, 0, 7, 'ДЭД СТАНЦ', header_title_style)

        counter = 0
        row_num = 15

        for dedstants_ids in GemtelList.dedstants_ids:
            year_taslalts_ded = GemtelList.year_gemtels_ded[counter]
            season_taslalts_ded = GemtelList.season_gemtels_ded[counter]
            month_taslalts_ded = GemtelList.month_gemtels_ded[counter]

            ded_stants = DedStants.objects.get(id=dedstants_ids)
            ws.write_merge(row_num, row_num, 3, 4, ded_stants.name, header_title_style)
            row_num += 2
            ws.write_merge(row_num, row_num, 0, 1, GemtelList.current_year + ' он', title_style)
            ws.write_merge(row_num, row_num, 3, 4, str(GemtelList.current_season) + '-р улирал', title_style)
            ws.write_merge(row_num, row_num, 6, 7, GemtelList.current_month + '-р сар', title_style)

            if year_taslalts_ded and season_taslalts_ded and month_taslalts_ded:
                counter += 1
                row_num += 2
                ws.write(row_num, 0, 'Нийт гэмтсэн тоо : ', row_style)
                ws.write(row_num, 1, str(round(year_taslalts_ded.too, 2) if year_taslalts_ded.too else 0), row_style)
                ws.write(row_num, 3, 'Нийт гэмтсэн тоо : ', row_style)
                ws.write(row_num, 4, str(round(season_taslalts_ded.too, 2) if season_taslalts_ded.too else 0), row_style)
                ws.write(row_num, 6, 'Нийт гэмтсэн тоо : ', row_style)
                ws.write(row_num, 7, str(round(month_taslalts_ded.too, 2) if month_taslalts_ded.too else 0), row_style)
                row_num += 1
                ws.write(row_num, 0, 'Нийт гэмтсэн хугацаа : ', row_style)
                ws.write(row_num, 1, str(round(year_taslalts_ded.hugatsaa, 2) if year_taslalts_ded.hugatsaa else 0) + ' цаг', row_style)
                ws.write(row_num, 3, 'Нийт гэмтсэн хугацаа : ', row_style)
                ws.write(row_num, 4, str(round(season_taslalts_ded.hugatsaa, 2) if season_taslalts_ded.hugatsaa else 0) + ' цаг', row_style)
                ws.write(row_num, 6, 'Нийт гэмтсэн хугацаа : ', row_style)
                ws.write(row_num, 7, str(round(month_taslalts_ded.hugatsaa, 2) if month_taslalts_ded.hugatsaa else 0) + ' цаг', row_style)
                row_num += 1
                ws.write(row_num, 0, 'Нийт чадал : ', row_style)
                ws.write(row_num, 1, str(round(year_taslalts_ded.chadal, 2) if year_taslalts_ded.chadal else 0) + ' кВт', row_style)
                ws.write(row_num, 3, 'Нийт чадал : ', row_style)
                ws.write(row_num, 4, str(round(season_taslalts_ded.chadal, 2) if season_taslalts_ded.chadal else 0) + ' кВт', row_style)
                ws.write(row_num, 6, 'Нийт чадал : ', row_style)
                ws.write(row_num, 7, str(round(month_taslalts_ded.chadal, 2) if month_taslalts_ded.chadal else 0) + ' кВт', row_style)
                row_num += 1
                ws.write(row_num, 0, 'Нийт дутуу түгээсэн ЭХ : ', row_style)
                ws.write(row_num, 1, str(round(year_taslalts_ded.dutuu, 2) if year_taslalts_ded.dutuu else 0) + ' кВт/цаг', row_style)
                ws.write(row_num, 3, 'Нийт дутуу түгээсэн ЭХ : ', row_style)
                ws.write(row_num, 4, str(round(season_taslalts_ded.dutuu, 2) if season_taslalts_ded.dutuu else 0) + ' кВт/цаг', row_style)
                ws.write(row_num, 6, 'Нийт дутуу түгээсэн ЭХ : ', row_style)
                ws.write(row_num, 7, str(round(month_taslalts_ded.dutuu, 2) if month_taslalts_ded.dutuu else 0) + ' кВт/цаг', row_style)
            row_num += 2
        wb.save(response)
        return response


class GemtelAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_gemtel'
    template_name = "homepage/ashiglalt/gemtel_add.html"
    menu = '4'
    sub = '5'

    def get(self, request, *args, **kwargs):
        try:
            ded_stants = DedStants.objects.filter(is_active=1).order_by('name')
        except ObjectDoesNotExist:
            ded_stants = None
        try:
            dispetchers = User.objects.filter(Q(groups__name='Ахлах диспетчер инженер') | Q(groups__name='Диспетчер инженер'))
        except ObjectDoesNotExist:
            dispetchers = None

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
            'action': '/home/ashiglalt/gemtel_add',
            'ded_stants': ded_stants,
            'dispetchers': dispetchers,
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
        try:
            dispetcher = User.objects.get(id=request.POST['dispetcher'])
        except ObjectDoesNotExist:
            dispetcher = None
        zurag = None
        if 'zurag' in request.FILES:
            form = GemtelZuragForm(request.POST, request.FILES)
            if form.is_valid():
                zurag = request.FILES['zurag']

        if ded_stants is not None and shugam is not None:
            gemtsen_date = datetime.strptime(request.POST['gemtsen_date'], '%Y-%m-%d %H:%M')
            zalgasan_date = datetime.strptime(request.POST['zalgasan_date'], '%Y-%m-%d %H:%M')

            try:
                gemtel = Gemtel.objects.create(ded_stants=ded_stants, shugam=shugam, dispetcher=dispetcher, gemtsen_date=gemtsen_date, zalgasan_date=zalgasan_date)
                gemtel.created_user_id = request.user.id
                gemtel.gemtsen_hugatsaa = request.POST['gemtsen_hugatsaa']
                gemtel.amper = request.POST['amper']
                gemtel.voltage = request.POST['voltage']
                gemtel.chadal = request.POST['chadal']
                gemtel.dutuu_tugeesen = request.POST['dutuu_tugeesen']
                gemtel.gemtsen_shaltgaan = request.POST['gemtsen_shaltgaan']
                gemtel.zurag = zurag
                gemtel.save()
                messages.success(request, 'Амжилттай хадгалагдлаа!')
            except ObjectDoesNotExist:
                messages.error(request, 'Хадгалахад алдаа гарлаа!')
                return redirect('/home/ashiglalt/gemtel_add')

            return redirect('/home/ashiglalt/gemtel_list/1/')


class GemtelEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_gemtel'
    template_name = 'homepage/ashiglalt/gemtel_add.html'
    menu = '4'
    sub = '5'

    def get(self, request, id, *args, **kwargs):
        try:
            gemtel = Gemtel.objects.get(id=id)
            shugams = Shugam.objects.filter(ded_stants_id=gemtel.ded_stants_id)
        except ObjectDoesNotExist:
            gemtel = None
            shugams = None
        try:
            ded_stants = DedStants.objects.filter(is_active=1)
        except ObjectDoesNotExist:
            ded_stants = None
        try:
            dispetchers = User.objects.filter(Q(groups__name='Ахлах диспетчер инженер') | Q(groups__name='Диспетчер инженер'))
        except ObjectDoesNotExist:
            dispetchers = None

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
            'action': '/home/ashiglalt/gemtel_edit/'+id+'/',
            'gemtel': gemtel,
            'ded_stants': ded_stants,
            'shugams': shugams,
            'dispetchers': dispetchers,
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
        try:
            dispetcher = User.objects.get(id=request.POST['dispetcher'])
        except ObjectDoesNotExist:
            dispetcher = None

        gemtsen_date = datetime.strptime(request.POST['gemtsen_date'], '%Y-%m-%d %H:%M')
        zalgasan_date = datetime.strptime(request.POST['zalgasan_date'], '%Y-%m-%d %H:%M')

        try:
            gemtel = Gemtel.objects.get(id=id)
            gemtel.ded_stants = ded_stants
            gemtel.shugam = shugam
            gemtel.gemtsen_date = gemtsen_date
            gemtel.zalgasan_date = zalgasan_date
            gemtel.gemtsen_hugatsaa = request.POST['gemtsen_hugatsaa']
            gemtel.amper = request.POST['amper']
            gemtel.voltage = request.POST['voltage']
            gemtel.chadal = request.POST['chadal']
            gemtel.dutuu_tugeesen = request.POST['dutuu_tugeesen']
            gemtel.dispetcher = dispetcher
            gemtel.gemtsen_shaltgaan = request.POST['gemtsen_shaltgaan']
            zurag = gemtel.zurag
            if 'zurag' in request.FILES:
                form = GemtelZuragForm(request.POST, request.FILES)
                if form.is_valid():
                    zurag = request.FILES['zurag']
            gemtel.zurag = zurag
            gemtel.save()
            messages.success(request, 'Амжилттай засварлагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Засварлахад алдаа гарлаа!')
            return redirect('/home/ashiglalt/gemtel_add')

        return redirect('/home/ashiglalt/gemtel_list/1/')


class GemtelDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_gemtel'

    def get(self, request, id, *args, **kwargs):
        try:
            gemtel = Gemtel.objects.get(id=id)
            gemtel.is_active = 0
            gemtel.save()
            messages.success(request, 'Амжилттай устгагдлаа!')
        except ObjectDoesNotExist:
            messages.error(request, 'Устахад алдаа гарлаа!')

        return redirect('/home/ashiglalt/gemtel_list/1/')