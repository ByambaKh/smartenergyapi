# coding=utf-8
import ctypes
import datetime
import json
import platform

from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import render_to_response
from apps.homepage.forms import *
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login


def index(request):
    if request.user.is_authenticated == False:
        return redirect('/login')
    return render_to_response('/version1homepage/index.html')


def url_fixer(request):
    return redirect("/home/index")


@login_required
def duudlaga(request):
    return render_to_response('/version1homepage/duudlaga.html')


class lavlah(LoginRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


@login_required
def enquire_price(request):
    return render_to_response('/version1homepage/lavlah/enquire_price.html')


@login_required
def call_type(request):
    calltype_info = CallType.objects.all()
    calltype_data = {
        "calltype_detail": calltype_info
    }
    return render_to_response('/version1homepage/lavlah/call_type.html', calltype_data)


@login_required
def call_type_add(request):
    if request.method == "POST":
        # Get the posted form
        NewForm = AddCallType(request.POST)
        print(NewForm)
        if NewForm.is_valid():
            newCallType = CallType.objects.create()
            newCallType.name = NewForm.cleaned_data['name']
            newCallType.user_type = NewForm.cleaned_data['is_active']
            newCallType.save()
            return redirect('/home/lavlagaa/call_type')

    return render(request, 'homepage/lavlah/calltype_add.html')


def loginz(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            try:
                next_url = request.GET['next']
                if next_url != None:
                    return redirect(next_url)
            except:
                return redirect('/home/index')
        else:            
            data = {
                "error": {
                    "description": "Та нэр эсвэл нууц үгээ зөв оруулна уу.",
                    "code": 101,
                }
            }
            return render(request, 'homepage/login.html', data)
    data = None
    try:
        next = request.GET['next']
        if next:
            data = {
                "next": next,
            }
    except:
        print("no next")

    return render(request, 'homepage/login.html', data)


def auth_user(request):
    userForm = LoginForm(request.POST)


if 'Windows' in platform.system():
    PosAPI = ctypes.cdll.LoadLibrary('./posapi/PosAPI.dll')
else:
    PosAPI = ctypes.cdll.LoadLibrary('/usr/lib/x86_64-linux-gnu/libPosAPI.so')


def pos_init(request):
    put = PosAPI.put
    put.restype = ctypes.c_char_p
    put.argtypes = [ctypes.c_char_p]
    c = ctypes.create_string_buffer((make_put('55000150', '10')).encode())
    result = put(c)
    parse_str = str(result, 'utf-8')
    messages.warning(request, str(json.loads(parse_str)))
    return redirect('/home/index')


def make_put(customerNo, amount):
    amount = float(amount)
    if customerNo != "":
        if len(str(customerNo)) < 7:
            customerNo = "1000000"
        print("customerNo : " + str(customerNo))

    put_params = "{\"billIdSuffix\": \"\", \"posNo\": \"0001\", \"districtCode\": \"23\", \"cashAmount\": \"0.00\", " \
            "\"vat\": \"" + str("{:.2f}".format((amount * 10) / 110)) + "\", \"invoiceId\": \"\"," \
            "\"reportMonth\": \"\", \"customerNo\": \"" + str(customerNo) + "\", \"billType\": \"\", \"stocks\": [{\"code\": \"6911\", " \
            "\"totalAmount\": \"" + str("{:.2f}".format(amount)) + "\", \"measureUnit\": \"кВт\", \"name\": \"Цахилгаан\", \"qty\": \"1.00\", " \
            "\"cityTax\": \"0.00\", \"vat\": \"" + str("{:.2f}".format((amount * 10) / 110)) + "\", \"barcode\": \"6911\", " \
            "\"unitPrice\": \"" + str("{:.2f}".format(amount - (amount * 10) / 110)) + "\"}], \"returnBillId\": \"\", \"taxType\": \"\", " \
            "\"amount\": \"" + str("{:.2f}".format(amount)) + "\", \"branchNo\": \"001\", " \
            "\"nonCashAmount\": \"" + str("{:.2f}".format(amount)) + "\", \"cityTax\": \"0.00\"}"
    return put_params