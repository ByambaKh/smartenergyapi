from django.conf.urls import url, include
from rest_framework import routers
from apps.api import views
from apps.api.views import AddZaaltView
from apps.api.views import NominPos,NominPosPayment
from apps.api import posViews
from apps.api import customerViews
from apps.api import systemViews

from apps.homepage.viewz.bank.most import *


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^customers/$', views.customer_list),
    url(r'^check_staff_available/$', views.check_staff_available),
    url(r'^zaalts/$', views.get_balance_list),
    url(r'^tooluurs/$', views.get_tooluur_list),
    url(r'^taslalt_list/$', views.taslalt_hiih_list),
    url(r'^dedstantss/$', views.get_dedstants_list),
    url(r'^bairs/$', views.get_bair_list),
    url(r'^pay_services/$', views.get_payservice_list),
    url(r'^add_pay_services', views.post_pay_service),
    url(r'^add_zaalt', AddZaaltView.as_view()),
    url(r'^nomin_pos/get_info', NominPos.as_view()),
    url(r'^nomin_pos/payment', NominPosPayment.as_view()),
    url(r'^checkInfo', systemViews.checkInfo),    
    url(r'^most_request', most_request),
    url(r'^payment/getUserElectricityInfo', posViews.getUserElectricityInfo),
    url(r'^payment/putUserElectricityInfo', posViews.putUserElectricityInfo),
    url(r'^customers/bank/add', customerViews.getCustomerBankAdd),
    url(r'^customers/bank/remove', customerViews.getCustomerBankRemove),
    url(r'^api-auth', include('rest_framework.urls', namespace='rest_framework'))
]