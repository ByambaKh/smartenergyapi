__author__ = 'L'
from django.shortcuts import render, redirect
from apps.data.models import *
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

class OrgList(LoginRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/admin/org_list.html"
    starter_q = "SELECT *FROM data_org WHERE "
    menu = "10"
    sub = "1"

    def get(self, request, *args, **kwargs):
        orgs = Org.objects.filter(is_active="1")
        data = {
            "datas":orgs,
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        org_type = rq.get('org_type', '')
        phone = rq.get('phone', '')

        q = self.starter_q
        if name != '':
            q = self.append_add(q) + "name LIKE '%%" + name + "%%'"
        if phone != '':
            q = self.append_add(q) + "phone LIKE '%%" + phone + "%%'"
        if org_type != '':
            q = self.append_add(q) + "org_type LIKE '%%" + org_type + "%%'"
        q = self.append_add(q) + "is_active='1'"
        orgs = Org.objects.raw(q)
        data = {
            "datas":orgs,
            "search_q":{
                "name":name,
                "phone":phone,
                "org_type":org_type,
            },
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)

    def append_add(self, q):
        if q != self.starter_q:
            return q + " AND "
        return q

class OrgAdd(LoginRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/admin/org_add.html"
    menu = "10"
    sub = "1"

    def get(self, request, *args, **kwargs):
        data = {
            "urlz":"/home/org_add",
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        register = rq.get('register', '')# searchForm.cleaned_data['end_date']
        org_type = rq.get('org_type', '') #searchForm.cleaned_data['name']
        phone = rq.get('phone', '')#searchForm.cleaned_data['username']
        web = rq.get('web', '')#searchForm.cleaned_data['file_size']
        email = rq.get('email', '')#searchForm.cleaned_data['file_type']
        address = rq.get('address', '')#searchForm.cleaned_data['description']

        try:
            Org.objects.get(register=register)
            desc = register + " бүртгэлийн дугаартай байгууллага бүртгэгдсэн байна. Та шалгаад дахин оролдож үзнэ үү."
            return self.error_builder(request, desc)
        except Org.DoesNotExist:
            newOrg = Org.objects.create()
            newOrg.name = name
            newOrg.register = register
            newOrg.org_type = org_type
            newOrg.phone = phone
            newOrg.web = web
            newOrg.email = email
            newOrg.address = address
            newOrg.is_active = org_type
            newOrg.save()
            return redirect('/home/org_list')

    def error_builder(self, request, description):
        messages.error(request, description)
        data = {
            "urlz":"/home/org_add",
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)


class OrgEdit(LoginRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/admin/org_add.html"
    form_class = OrgAddForm
    menu = "10"
    sub = "1"


    def get(self, request, id, *args, **kwargs):
        print (id)
        selected_org = Org.objects.get(id=id)
        data = {
            "urlz":"/home/org_edit/" + id + "/",
            "edit_data":selected_org,
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, id,  *args, **kwargs):
        rq = request.POST
        name = rq.get('name', '')
        register = rq.get('register', '')# searchForm.cleaned_data['end_date']
        org_type = rq.get('org_type', '') #searchForm.cleaned_data['name']
        phone = rq.get('phone', '')#searchForm.cleaned_data['username']
        web = rq.get('web', '')#searchForm.cleaned_data['file_size']
        email = rq.get('email', '')#searchForm.cleaned_data['file_type']
        address = rq.get('address', '')#searchForm.cleaned_data['description']

        if name != "":
            print ("name is empty")
        newOrg = Org.objects.get(id=id)
        newOrg.name = name
        newOrg.register = register
        newOrg.org_type = org_type
        newOrg.phone = phone
        newOrg.web = web
        newOrg.email = email
        newOrg.address = address
        newOrg.save()
        return redirect('/home/org_list')

    def form_valid(self, form):
        print(form)

class OrgDelete(View):
    template_name = "homepage/admin/org_list.html"
    form_class = OrgAddForm

    def get(self, request, id, *args, **kwargs):
        print (id)
        selected_org = Org.objects.get(id=id)
        selected_org.delete()
        return render(request, self.template_name)



