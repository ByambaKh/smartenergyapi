from django.core.exceptions import ObjectDoesNotExist

__author__ = 'L'
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from highcharts.views import (HighChartsMultiAxesView, HighChartsLineView)
from apps.data.models import *
import datetime

from ctypes import *


class Dashboard(LoginRequiredMixin, View):
    template_name = 'homepage/index.html'
    login_url = '/login'
    menu_number = "1"

    def get(self, request, *args, **kwargs):
        current_date = datetime.datetime.now().date()
        subtitle = str(current_date.year) + "-" + str(current_date.month) + "-" + str(current_date.day) + " байдлаар"
        data = {}

        try:
            shugam_list = Shugam.objects.filter(is_active='1').order_by('ded_stants_id')
        except ObjectDoesNotExist:
            shugam_list = None

        try:
            ded_stants = DedStants.objects.filter(is_active='1').order_by('name')
        except ObjectDoesNotExist:
            ded_stants = None

        data["shugam_data"] = shugam_list
        data["ded_stants"] = ded_stants
        data['description'] = subtitle
        data['menu'] = self.menu_number

        return render(request, self.template_name, data)


class BarView(HighChartsMultiAxesView):
    chart = {'zoomType': 'xy'}
    tooltip = {'shared': 'false', 'valueDecimals': '2'}
    legend = {'layout': 'horizontal', 'align': 'center',
              'verticalAlign': 'bottom', 'floating': 'false', 
              'backgroundColor': '#FFFFFF', 'y': 20}
    xAxis = {'labels': {'rotation': 0}}
              
    @property
    def yaxis(self):
        y_axis = [{'labels': {'style': {'color': '#23CCEF'}},
                   'title': {'text': 'Тасралт', 'style': {'color': '#23CCEF'}},
                   'opposite': 'true'},
                  {'gridLineWidth': '0',
                   'title': {'text': 'Таслалт', 'style': {'color': '#FB404B'}},
                   'labels': {'style': {'color': '#FB404B'}, 'format': '{value:,.0f}'}}]
        return y_axis

    def get_data(self):
        current_date = datetime.datetime.now().date()
        current_year = str(current_date.year)

        q_by_bichilt = "select id, sum(total_diff) as sum_kv, sum(total_price) as sum_price, month, year from data_bichilt where year='%s' group by month"
        q_by_bichilt = q_by_bichilt%(current_year)

        bichilt_list = list(Bichilt.objects.raw(q_by_bichilt))
        tugrug_values = []
        kv_values = []

        for i in range(1, 13):
            self.categories.append(str(i))
            item = self.get_item_by_month(str(i), bichilt_list)
            if item == None:
                tugrug_values.append(0)
                kv_values.append(0)
            else:
                val1 = float(item.sum_kv if item.sum_kv else 0)
                val2 = float(item.sum_price if item.sum_price else 0)
                tugrug_values.append(val2)
                kv_values.append(val1)

        self.series = [
        {
            'name': 'Таслалт',
            'type': 'column',
            'data': tugrug_values,
            'color': '#FB404B',
        },
        {
            'name': 'Тасралт',
            'type': 'column',
            'yAxis': 1,
            'data': kv_values,
            'color': '#23CCEF',
        },
        {
            'name': 'Гэмтэл',
            'type': 'column',
            'data': tugrug_values,
            'color': '#008000',
        }]

        data = super(BarView, self).get_data()
        return data

    def get_item_by_month(self, month, array):
        for item in array:
            if item.month == month:
                return item


class LineView(HighChartsLineView):
    chart = {'type': 'line'}
    plotOptions = {
            'line': {
                'dataLabels': {
                    'enabled': 'true'
                },
                'enableMouseTracking': 'true'
            }
        }
    tooltip = {'shared': 'true', 'valueSuffix': ''}
    legend = {'layout': 'horizontal', 'align': 'center',
              'verticalAlign': 'bottom', 'floating': 'false', 
              'backgroundColor': '#FFFFFF', 'y': 20}

    def get_data(self):
        current_date = datetime.datetime.now().date()
        current_year = str(current_date.year)

        qry_tasralt = "SELECT id, COUNT(id) AS too, MONTH(tasarsan_date) AS month, YEAR(tasarsan_date) AS year FROM data_tasralt"
        qry_tasralt += " WHERE YEAR(tasarsan_date)='"+current_year+"' GROUP BY MONTH(tasarsan_date)"
        qry_taslalt = "SELECT id, COUNT(id) AS too, MONTH(tasalsan_date) AS month, YEAR(tasalsan_date) AS year FROM data_taslalt"
        qry_taslalt += " WHERE YEAR(tasalsan_date)='"+current_year+"' GROUP BY MONTH(tasalsan_date)"
        qry_gemtel = "SELECT id, COUNT(id) AS too, MONTH(gemtsen_date) AS month, YEAR(gemtsen_date) AS year FROM data_gemtel"
        qry_gemtel += " WHERE YEAR(gemtsen_date)='"+current_year+"' GROUP BY MONTH(gemtsen_date)"

        tasralt_list = list(Tasralt.objects.raw(qry_tasralt))
        tasralt_values = []

        taslalt_list = list(Taslalt.objects.raw(qry_taslalt))
        taslalt_values = []

        gemtel_list = list(Gemtel.objects.raw(qry_gemtel))
        gemtel_values = []

        for i in range(1, 13):
            self.categories.append(str(i))
            tasralt_item = self.get_item_by_month(str(i), tasralt_list)
            if tasralt_item is not None:
                tasralt_values.append(tasralt_item.too)
            else:
                tasralt_values.append(0)

            taslalt_item = self.get_item_by_month(str(i), taslalt_list)
            if taslalt_item is not None:
                taslalt_values.append(taslalt_item.too)
            else:
                taslalt_values.append(0)

            gemtel_item = self.get_item_by_month(str(i), gemtel_list)
            if gemtel_item is not None:
                gemtel_values.append(gemtel_item.too)
            else:
                gemtel_values.append(0)

        self.series = [{
            'name': 'Тасралт',
            'data': tasralt_values,
            'color': '#23CCEF',
        },
        {
            'name': 'Таслалт',
            'data': taslalt_values,
            'color': '#FB404B',
        },
        {
            'name': 'Гэмтэл',
            'data': gemtel_values,
            'color': '#008000',
        }]
        self.y_axis_title = "тоо"

        data = super(LineView, self).get_data()
        data['yAxis']['title'] = {"text": "тоо"}
        return data

    def get_item_by_month(self, month, array):
        for item in array:
            if str(item.month) == month:
                return item


class LineViewTime(HighChartsLineView):
    chart = {'type': 'line'}
    plotOptions = {
            'line': {
                'dataLabels': {
                    'enabled': 'true'
                },
                'enableMouseTracking': 'true'
            }
        }
    tooltip = {'shared': 'true', 'valueSuffix': ' цаг'}
    legend = {'layout': 'horizontal', 'align': 'center',
              'verticalAlign': 'bottom', 'floating': 'false',
              'backgroundColor': '#FFFFFF', 'y': 20}

    def get_data(self):
        current_date = datetime.datetime.now().date()
        current_year = str(current_date.year)

        qry_tasralt = "SELECT id, SUM(tasraltiin_hugatsaa) AS hugatsaa, MONTH(tasarsan_date) AS month, YEAR(tasarsan_date) AS year FROM data_tasralt"
        qry_tasralt += " WHERE YEAR(tasarsan_date)='"+current_year+"' GROUP BY MONTH(tasarsan_date)"
        qry_taslalt = "SELECT id, SUM(tasalsan_hugatsaa) AS hugatsaa, MONTH(tasalsan_date) AS month, YEAR(tasalsan_date) AS year FROM data_taslalt"
        qry_taslalt += " WHERE YEAR(tasalsan_date)='"+current_year+"' GROUP BY MONTH(tasalsan_date)"
        qry_gemtel = "SELECT id, SUM(gemtsen_hugatsaa) AS hugatsaa, MONTH(gemtsen_date) AS month, YEAR(gemtsen_date) AS year FROM data_gemtel"
        qry_gemtel += " WHERE YEAR(gemtsen_date)='"+current_year+"' GROUP BY MONTH(gemtsen_date)"

        tasralt_list = list(Tasralt.objects.raw(qry_tasralt))
        tasralt_values = []

        taslalt_list = list(Taslalt.objects.raw(qry_taslalt))
        taslalt_values = []

        gemtel_list = list(Gemtel.objects.raw(qry_gemtel))
        gemtel_values = []

        for i in range(1, 13):
            self.categories.append(str(i))
            tasralt_item = self.get_item_by_month(str(i), tasralt_list)
            if tasralt_item is not None:
                tasralt_values.append(tasralt_item.hugatsaa)
            else:
                tasralt_values.append(0)

            taslalt_item = self.get_item_by_month(str(i), taslalt_list)
            if taslalt_item is not None:
                taslalt_values.append(taslalt_item.hugatsaa)
            else:
                taslalt_values.append(0)

            gemtel_item = self.get_item_by_month(str(i), gemtel_list)
            if gemtel_item is not None:
                gemtel_values.append(gemtel_item.hugatsaa)
            else:
                gemtel_values.append(0)

        self.series = [{
            'name': 'Тасралт',
            'data': tasralt_values,
            'color': '#23CCEF',
        },
        {
            'name': 'Таслалт',
            'data': taslalt_values,
            'color': '#FB404B',
        },
        {
            'name': 'Гэмтэл',
            'data': gemtel_values,
            'color': '#008000',
        }]
        self.y_axis_title = "цаг"

        data = super(LineViewTime, self).get_data()
        data['yAxis']['title'] = {"text": "цаг"}
        return data

    def get_item_by_month(self, month, array):
        for item in array:
            if str(item.month) == month:
                return item