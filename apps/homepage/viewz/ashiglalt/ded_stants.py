from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import View
from apps.data.models import DedStants


class AshiglaltDedStants(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_ashiglalt_dedstants'
    template_name = "homepage/ashiglalt/ded_stants.html"
    menu = '4'
    sub = '8'

    def get(self, request, activeTab, *args, **kwargs):
        amgalan_ttg = []
        amgalan_ded = []
        zalaat_ttg = []
        zalaat_ded = []
        tuul_ttg = []
        tuul_ded = []
        uildver_ttg = []
        uildver_ded = []
        umnud_ttg = []
        umnud_ded = []

        try:
            amg_ded_stants = DedStants.objects.filter(is_active='1').filter(angilal_id=1)
            for ded_stant in amg_ded_stants:
                amgalan_ded.append(ded_stant.id)
                qry_ded = "SELECT id, (SELECT COUNT(id) FROM data_tasralt WHERE is_active='1' AND ded_stants_id="+str(ded_stant.id)+") AS tasralt_too,"
                qry_ded += " (SELECT IFNULL(SUM(tasraltiin_hugatsaa), 0) FROM data_tasralt WHERE is_active='1' AND ded_stants_id="+str(ded_stant.id)+") AS tasralt_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_tasralt WHERE is_active='1' AND ded_stants_id="+str(ded_stant.id)+") AS tasralt_dutuu,"
                qry_ded += " (SELECT COUNT(id) FROM data_taslalt WHERE is_active='1' AND ded_stants_id="+str(ded_stant.id)+") AS taslalt_too,"
                qry_ded += " (SELECT IFNULL(SUM(tasalsan_hugatsaa), 0) FROM data_taslalt WHERE is_active='1' AND ded_stants_id="+str(ded_stant.id)+") AS taslalt_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_taslalt WHERE is_active='1' AND ded_stants_id="+str(ded_stant.id)+") AS taslalt_dutuu,"
                qry_ded += " (SELECT COUNT(id) FROM data_gemtel WHERE is_active='1' AND ded_stants_id="+str(ded_stant.id)+") AS gemtel_too,"
                qry_ded += " (SELECT IFNULL(SUM(gemtsen_hugatsaa), 0) FROM data_gemtel WHERE is_active='1' AND ded_stants_id="+str(ded_stant.id)+") AS gemtel_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_gemtel WHERE is_active='1' AND ded_stants_id="+str(ded_stant.id)+") AS gemtel_dutuu"
                qry_ded += " FROM data_dedstants LIMIT 1"
                amgalan_ttg.extend(list(DedStants.objects.raw(qry_ded)))
        except ObjectDoesNotExist:
            amgalan_ded = []
            amgalan_ttg = []

        try:
            zal_ded_stants = DedStants.objects.filter(is_active='1').filter(angilal_id=2)
            for ded_stant in zal_ded_stants:
                zalaat_ded.append(ded_stant.id)
                qry_ded = "SELECT id, (SELECT COUNT(id) FROM data_tasralt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS tasralt_too,"
                qry_ded += " (SELECT IFNULL(SUM(tasraltiin_hugatsaa), 0) FROM data_tasralt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS tasralt_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_tasralt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS tasralt_dutuu,"
                qry_ded += " (SELECT COUNT(id) FROM data_taslalt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS taslalt_too,"
                qry_ded += " (SELECT IFNULL(SUM(tasalsan_hugatsaa), 0) FROM data_taslalt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS taslalt_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_taslalt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS taslalt_dutuu,"
                qry_ded += " (SELECT COUNT(id) FROM data_gemtel WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS gemtel_too,"
                qry_ded += " (SELECT IFNULL(SUM(gemtsen_hugatsaa), 0) FROM data_gemtel WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS gemtel_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_gemtel WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS gemtel_dutuu"
                qry_ded += " FROM data_dedstants LIMIT 1"
                zalaat_ttg.extend(list(DedStants.objects.raw(qry_ded)))
        except ObjectDoesNotExist:
            zalaat_ded = []
            zalaat_ttg = []

        try:
            tul_ded_stants = DedStants.objects.filter(is_active='1').filter(angilal_id=3)
            for ded_stant in tul_ded_stants:
                tuul_ded.append(ded_stant.id)
                qry_ded = "SELECT id, (SELECT COUNT(id) FROM data_tasralt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS tasralt_too,"
                qry_ded += " (SELECT IFNULL(SUM(tasraltiin_hugatsaa), 0) FROM data_tasralt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS tasralt_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_tasralt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS tasralt_dutuu,"
                qry_ded += " (SELECT COUNT(id) FROM data_taslalt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS taslalt_too,"
                qry_ded += " (SELECT IFNULL(SUM(tasalsan_hugatsaa), 0) FROM data_taslalt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS taslalt_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_taslalt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS taslalt_dutuu,"
                qry_ded += " (SELECT COUNT(id) FROM data_gemtel WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS gemtel_too,"
                qry_ded += " (SELECT IFNULL(SUM(gemtsen_hugatsaa), 0) FROM data_gemtel WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS gemtel_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_gemtel WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS gemtel_dutuu"
                qry_ded += " FROM data_dedstants LIMIT 1"
                tuul_ttg.extend(list(DedStants.objects.raw(qry_ded)))
        except ObjectDoesNotExist:
            tuul_ded = []
            tuul_ttg = []

        try:
            uil_ded_stants = DedStants.objects.filter(is_active='1').filter(angilal_id=4)
            for ded_stant in uil_ded_stants:
                uildver_ded.append(ded_stant.id)
                qry_ded = "SELECT id, (SELECT COUNT(id) FROM data_tasralt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS tasralt_too,"
                qry_ded += " (SELECT IFNULL(SUM(tasraltiin_hugatsaa), 0) FROM data_tasralt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS tasralt_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_tasralt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS tasralt_dutuu,"
                qry_ded += " (SELECT COUNT(id) FROM data_taslalt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS taslalt_too,"
                qry_ded += " (SELECT IFNULL(SUM(tasalsan_hugatsaa), 0) FROM data_taslalt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS taslalt_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_taslalt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS taslalt_dutuu,"
                qry_ded += " (SELECT COUNT(id) FROM data_gemtel WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS gemtel_too,"
                qry_ded += " (SELECT IFNULL(SUM(gemtsen_hugatsaa), 0) FROM data_gemtel WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS gemtel_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_gemtel WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS gemtel_dutuu"
                qry_ded += " FROM data_dedstants LIMIT 1"
                uildver_ttg.extend(list(DedStants.objects.raw(qry_ded)))
        except ObjectDoesNotExist:
            uildver_ded = []
            uildver_ttg = []

        try:
            umn_ded_stants = DedStants.objects.filter(is_active='1').filter(angilal_id=5)
            for ded_stant in umn_ded_stants:
                umnud_ded.append(ded_stant.id)
                qry_ded = "SELECT id, (SELECT COUNT(id) FROM data_tasralt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS tasralt_too,"
                qry_ded += " (SELECT IFNULL(SUM(tasraltiin_hugatsaa), 0) FROM data_tasralt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS tasralt_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_tasralt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS tasralt_dutuu,"
                qry_ded += " (SELECT COUNT(id) FROM data_taslalt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS taslalt_too,"
                qry_ded += " (SELECT IFNULL(SUM(tasalsan_hugatsaa), 0) FROM data_taslalt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS taslalt_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_taslalt WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS taslalt_dutuu,"
                qry_ded += " (SELECT COUNT(id) FROM data_gemtel WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS gemtel_too,"
                qry_ded += " (SELECT IFNULL(SUM(gemtsen_hugatsaa), 0) FROM data_gemtel WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS gemtel_hugatsaa,"
                qry_ded += " (SELECT IFNULL(SUM(dutuu_tugeesen), 0) FROM data_gemtel WHERE is_active='1' AND ded_stants_id=" + str(ded_stant.id) + ") AS gemtel_dutuu"
                qry_ded += " FROM data_dedstants LIMIT 1"
                umnud_ttg.extend(list(DedStants.objects.raw(qry_ded)))
        except ObjectDoesNotExist:
            umnud_ttg = []
            umnud_ded = []

        data = {
            'amgalan_ded': amgalan_ded,
            'amgalan_ttg': amgalan_ttg,
            'zalaat_ded': zalaat_ded,
            'zalaat_ttg': zalaat_ttg,
            'tuul_ded': tuul_ded,
            'tuul_ttg': tuul_ttg,
            'uildver_ded': uildver_ded,
            'uildver_ttg': uildver_ttg,
            'umnud_ded': umnud_ded,
            'umnud_ttg': umnud_ttg,
            'menu': self.menu,
            'sub': self.sub,
            'activeTab': str(activeTab),
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        return None