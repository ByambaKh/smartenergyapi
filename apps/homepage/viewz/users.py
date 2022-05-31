from django.shortcuts import render, redirect
from django.views import View
from apps.homepage.forms import *
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin

class UserList(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/admin/user_list.html"
    menu = "10"
    sub = "3"
    permission_required = 'data.view_group'

    def get(self, request, *args, **kwargs):
        
        usr = User.objects.filter(is_active = True)
        
        users = UserProfile.objects.filter(user__in = usr)
        
        data = {
            "datas":users,
            "menu":self.menu,
            "sub":self.sub
        }
        
        return render(request, self.template_name, data)

class UserAdd(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/admin/user_add.html"
    menu = "10"
    sub = "3"
    permission_required = 'data.view_group'

    def get(self, request, *args, **kwargs):
        
        orgs = Org.objects.all()
        groups = Group.objects.all()
        
        error_name = ""
        error_code = 100
        
        data = {
            "urlz":"/home/user_add",
            "orgs":orgs,
            "groups":groups,
            "error":{
                "name":error_name,
                "error_code":error_code
            },
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        
        username = rq.get('username', '')
        firstname = rq.get('first_name', '')
        lastname = rq.get('last_name', '')
        phone = rq.get('phone', '')
        email = rq.get('email', '')
        password = rq.get('password', '')
        repassword = rq.get('password_check', '')
        org_register = rq.get('org_select', '')
        user_role = rq.get('role_select', '')
        group_id = rq.get('group_select', '')
        
        orgs = Org.objects.all()
        groups = Group.objects.all()

        error_name = ""
        error_code = 100
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
            print("its not existed user")
        if user == None:
            if password == repassword:
                print("matching pass")
                if user_role == "1":
                    user = User.objects.create_superuser(email=email, username=username, password=password)
                else:
                    user = User.objects.create_user(email=email, username=username, password=password)
                    grp = Group.objects.get(id=int(group_id)) 
                    grp.user_set.add(user)
#                     permissions = grp.permissions.all()
#                     user.user_permissions.set(permissions)
                    
                user.first_name = firstname
                user.last_name = lastname
                
                user.save()

                user_profile = UserProfile.objects.create(user=user)
                user_profile.user_id = user.id
                org = Org.objects.get(register=org_register)
                user_profile.org = org
                user_profile.phone = phone
                user_profile.save()

                return  redirect("/home/user_list")
            else:
                error_name = "Нууц үг таарахгүй байна."
                error_code = 110
        else:
            error_name = "Энэ нэвтрэх нэрээр бүртгэгдсэн байна. Та өөр нэр сонгоод дахин оролдож үзнэ үү."
            error_code = 109
        
        data = {
            "urlz":"/home/user_add",
            "error":{
                "name":error_name,
                "error_code":error_code
            },
            "orgs":orgs,
            "groups":groups,
            "add_q":{
                "username":username,
                "first_name":firstname,
                "last_name":lastname,
                "email":email,
                "phone":phone,
                "org_select":org_register,
                "role_select":user_role,
            },
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)

    def form_valid(self, form):
        print(form)

class UserEdit(LoginRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/admin/user_add.html"
    menu = "10"
    sub = "3"

    def get(self, request, id, *args, **kwargs):
        
        user = User.objects.get(id=id)
        profile = UserProfile.objects.get(user_id=id)
        groups = Group.objects.all()
        orgs = Org.objects.all()
        
        error_name = ""
        error_code = 100

        data = {
            "urlz":"/home/user_edit/" + id,
            "add_q":{
                "username":user.username,
                "first_name":user.first_name,
                "last_name":user.last_name,
                "email":user.email,
                "phone":profile.phone,
                "org_select":profile.org.register,
                "role_select": '1' if user.is_superuser else '0',
            },
            "orgs":orgs,
            "app_user":user,
            "groups":groups,
            "error":{
                "name":error_name,
                "error_code":error_code
            },
            "menu":self.menu,
            "sub":self.sub
        }
        
        return render(request, self.template_name, data)
        
    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        
        firstname = rq.get('first_name', '')
        lastname = rq.get('last_name', '')
        phone = rq.get('phone', '')
        email = rq.get('email', '')
        org_register = rq.get('org_select', '')
        user_role = rq.get('role_select', '')
        group_id = rq.get('group_select', '')
        
        user = User.objects.get(id=id)
        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        
        if request.user.is_superuser:
            
            grp = Group.objects.get(id=int(group_id))
            
            if user_role == "1":
                user.is_superuser = True
            else:
                user.is_superuser = False
        
            user.groups.clear()
            grp.user_set.add(user)
        
        user.save()

        user_profile = UserProfile.objects.get(user=user)
        user_profile.user_id = user.id
        org = Org.objects.get(register=org_register)
        user_profile.org = org
        user_profile.phone = phone
        user_profile.save()

        if request.user.is_superuser:
            return redirect("/home/user_list")
        else:
            return redirect("/home/index")

    def form_valid(self, form):
        print(form)
        
class UserDel(LoginRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/admin/user_list.html"
        
    def get(self, request, id, *args, **kwargs):
        
        user = User.objects.get(id=id)
        user.is_active = False
        user.save()
        
        return redirect("/home/user_list")
        
class UserRestore(LoginRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/admin/user_list.html"
        
    def get(self, request, id, *args, **kwargs):
        
        user = User.objects.get(id=id)
        user.set_password(user.username)
        
#         email = EmailMessage('Hello', 'World', to=['munkherdene.m@odi.com'])
#         email.send()
        
        user.save()
        messages.success(request, 'Нууц үг амжилттай сэргээгдлээ. Нууц үг нэвтрэх нэртэй адилхан боллоо')
        
        return redirect("/home/user_list")