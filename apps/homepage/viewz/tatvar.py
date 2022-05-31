from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from apps.data.models import PosAPI
from apps.homepage.viewz.services.posapi import PosapiMTA
from datetime import datetime


class Tatvar(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_posapi'
    template_name = 'homepage/tatvar.html'
    menu = '3'
    sub = '6'

    posapi = PosapiMTA()

    def get(self, request, *args, **kwargs):
        amount = 0.0
        nonCashAmount = 0.0

        now = datetime.now()
        start_date = str(now.year) + '-' + str(now.month) + '-' + '01'
        if now.day < 10:
            now_day = '0' + str(now.day)
        else:
            now_day = str(now.day)
        end_date = str(now.year) + '-' + str(now.month) + '-' + now_day

        try:
            posapis = PosAPI.objects.filter(is_active='1', date__range=(start_date, end_date)).order_by('-created_date')
            if len(posapis) >= 1:
                for posapi in posapis:
                    amount += float(posapi.amount)
                    nonCashAmount += float(posapi.nonCashAmount)
        except ObjectDoesNotExist:
            posapis = None

        users = User.objects.filter(groups__name__in=['Борлуулалт тооцооны ахлах инженер', 'Борлуулалт тооцооны инженер'])

        data = {
            'menu': self.menu,
            'sub': self.sub,
            'users': users,
            'start_date': start_date,
            'end_date': end_date,
            'posapis': posapis,
            'amount': amount,
            'nonCashAmount': nonCashAmount
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        if 'send_invoice' in request.POST:
            try:
                posapis = PosAPI.objects.filter(is_active='1').order_by('-created_date')
            except ObjectDoesNotExist:
                posapis = None

            # try:
            #     certificate_path = '/etc/ssl/STAR_e-s_mn.crt'
            #     certificate_key_path = '/etc/ssl/e-s.key'
            #     # certificate_path = 'D:/Workspace/MCSI_SALES/Erchim/Certificate/STAR_e-s_mn.crt'
            #     # certificate_key_path = 'D:/Workspace/MCSI_SALES/Erchim/Certificate/e-s.key'
            #     url = 'https://e-s.mn/send_data_backend'
            #     cert = (certificate_path, certificate_key_path)
            #     response = requests.get(url, cert=cert, verify=False)
            #     print(response)
            # except Exception as e:
            #     response = None
            #     print('Exception : %s' %e)
            #
            # if response is not None and '200' in response:
            #     result_json = response.json()
            #     print(str(result_json))
            #     messages.success(request, 'Хэрэглэгчийн сайтны иБаримт амжилттай илгээгдлээ!')
            # else:
            #     messages.error(request, 'Хэрэглэгчийн сайтны иБаримт илгээхэд алдаа гарлаа!')

            return_json = {}
            try:
                return_json = self.posapi.pos_sendData()
            except Exception as e:
                return_json['success'] = False
                print('%s', e)

            data = {
                'menu': self.menu,
                'sub': self.sub,
                'posapis': posapis
            }

            if return_json['success']:
                try:
                    posapiss = PosAPI.objects.filter(is_send=0, is_active='1').order_by('-created_date')
                    if len(posapiss) >= 1:
                        for posapi in posapiss:
                            posapi.is_send = True
                            posapi.save()
                    else:
                        messages.info(request, 'Бүх баримт илгээгдсэн байна.!')
                        return render(request, self.template_name, data)
                except ObjectDoesNotExist:
                    messages.error(request, 'Илгээхэд алдаа гарлаа!')
                    return render(request, self.template_name, data)
                messages.success(request, 'Амжилттай илгээгдлээ!')
            else:
                messages.error(request, 'Илгээхэд алдаа гарлаа!')

            return render(request, self.template_name, data)
        else:
            start_date = request.POST.get('start_date', '')
            end_date = request.POST.get('end_date', '')
            is_send = request.POST.get('is_send', '')
            user = request.POST.get('user', '')
            customer_code = request.POST.get('customer_code', '')

            amount = 0.0
            nonCashAmount = 0.0

            start_date = datetime.strptime(start_date + ' 00:00:00', "%Y-%m-%d %H:%M:%S")
            end_date = datetime.strptime(end_date + ' 23:59:59', "%Y-%m-%d %H:%M:%S")
            users = User.objects.filter(groups__name='Борлуулалт тооцооны ахлах инженер')

            para = {'is_active': '1'}

            if user != '':
                para.update({'created_user_id': str(user)})
            if is_send == '0' and is_send != '':
                para.update({'is_send': False})
            elif is_send == '1' and is_send != '':
                para.update({'is_send': True})
            elif is_send == '':
                para.update({'is_send__in': (True, False)})
            if start_date != '' and end_date != '':
                para.update({'date__range': (start_date, end_date)})
            if customer_code != '':
                para.update({'pay_his__customer__code': customer_code})

            try:
                posapis = PosAPI.objects.filter(**para)
            except ObjectDoesNotExist:
                posapis = None

            if len(posapis) >= 1:
                for posapi in posapis:
                    amount += float(posapi.amount)
                    nonCashAmount += float(posapi.nonCashAmount)

            data = {
                'menu': self.menu,
                'posapis': posapis,
                'start_date': start_date,
                'end_date': end_date,
                'customer_code': customer_code,
                'is_send': is_send,
                'amount': amount,
                'users': users,
                'user_id': int(user) if user != '' else '',
                'nonCashAmount': nonCashAmount
            }
            return render(request, self.template_name, data)