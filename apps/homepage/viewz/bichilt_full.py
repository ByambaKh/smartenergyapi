# coding=utf-8
from django.shortcuts import render, redirect
from apps.data.models import *
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

class BichiltFull(LoginRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/borluulalt/bichilt_full.html"
    menu = "3"
    sub = "6"

    def get(self, request, *args, **kwargs):
        data = {
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        user_code = rq.get('user_code', '')
        turul = ''
        list = []
        paylist = []
        try:
            customer = Customer.objects.get(code=user_code)
            geree = Geree.objects.get(customer_code=user_code)
            if (customer.customer_angilal == '0'):
                try:
                    turul = AhuinHereglegch.objects.filter(code=customer.customer_type)[0].name
                except:
                    turul = ""
            elif (customer.customer_angilal == '1'):
                try:
                    turul = AanAngilal.objects.filter(code=customer.customer_type)[0].name
                except:
                    turul = ""
            try:
                tsikl = Cycle.objects.filter(code=geree.cycle_code)[0]
            except:
                tsikl = None
            try:
                tc = TooluurCustomer.objects.filter(customer=customer)
                bich = Bichilt.objects.filter(tooluur__in=tc)
                pay_ids = []
                for b in bich:
                    obj = {}
                    obj["id"] = b.id
                    obj["bichilt_date"] = b.bichilt_date
                    obj["tooluur"] = b.tooluur.tooluur.number
                    obj["total_diff"] = b.total_diff
                    obj["hereglee_price"] = b.hereglee_price
                    obj["sergeegdeh_price"] = b.sergeegdeh_price
                    obj["suuri_price"] = b.suuri_price
                    obj["chadal_price"] = b.chadal_price
                    obj["nuat"] = float(b.total_price) - float(b.total_price) / float(1.1)
                    obj["total_price"] = b.total_price
                    try:
                        a = Avlaga.objects.get(bichilt=b.id)
                        obj["uilchilgee"] = a.uilchilgeenii_tulbur
                        obj["uil_nuat"] = float(a.uilchilgeenii_tulbur) - float(a.uilchilgeenii_tulbur) / float(1.1)
                    except:
                        obj["uilchilgee"] = 0
                        obj["uil_nuat"] = 0
                    try:
                        payments = PaymentHistory.objects.filter(customer=customer, pay_date=b.bichilt_date)
                        for p in payments:
                            pay_ids.append(p.id)
                            obj["pay_date"] = p.pay_date
                            obj["pay_total"] = float(p.pay_total)
                    except:
                        obj["pay_total"] = int(0)
                    list.append(obj)
                    try:
                        pays = PaymentHistory.objects.filter(customer=customer)
                        for p in pays:
                            pobj = {}
                            if(p.id not in pay_ids):
                                pobj["pay_date"] = p.pay_date
                                pobj["pay_total"] = float(p.pay_total)
                                paylist.append(pobj)
                    except:
                        0
            except:
                tc = None
        except Customer.DoesNotExist:
            return self.error_builder(request, 'Энэ хэрэглэгчийн кодоор бүртгэлтэй хэрэглэгч олдсонгүй. Та хэрэглэгчийн кодоо шалгана уу.')
        except Geree.DoesNotExist:
            return self.error_builder(request, 'Энэ хэрэглэгчийн кодоор бүртгэлтэй хэрэглэгч олдсонгүй. Та хэрэглэгчийн кодоо шалгана уу.')
        data = {
            "customer": customer,
            "geree": geree,
            "turul": turul,
            "cyc": tsikl,
            "bichlist": list,
            "paylist": paylist,
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)

    def error_builder(self, request, description):
        messages.warning(request, description)
        data = {
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)
