from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin


class RoleList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_group'
    template_name = "homepage/admin/role_list.html"
    menu = "10"
    sub = "2"

    def get(self, request, *args, **kwargs):
        roles = Group.objects.all()
        data = {
            "datas":roles,
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)


class RoleAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_group'
    template_name = "homepage/admin/role_add.html"
    menu = "10"
    sub = "2"

    def get(self, request, *args, **kwargs):
        perms = Permission.objects.filter(content_type_id__gte = 6).order_by('name')
        data = {
            "urlz":"/home/role_add",
            "perms":perms,
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)
    
    def post(self, request, *args, **kwargs):
        rq = request.POST
        
        rolename = rq.get('rolename', '')
        perm_ids = request.POST.getlist('perms')
        
        group = Group.objects.create(name=rolename)
        
        for perm_id in perm_ids:
            permission = Permission.objects.get(id=perm_id)
            group.permissions.add(permission)
        
        group.save()
        
        return redirect("/home/role_list")


class RoleEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_group'
    template_name = "homepage/admin/role_add.html"
    menu = "10"
    sub = "2"

    def get(self, request, id, *args, **kwargs):
        
        group = Group.objects.get(id=id)
        gp_perms = group.permissions.all()
        
        perms = Permission.objects.filter(content_type_id__gte = 6).order_by('name')
        
        data = {
            "urlz":"/home/role_edit/" + id,
            "role":group,
            "perms":perms,
            "gp_perms":gp_perms,
            "menu":self.menu,
            "sub":self.sub
        }
        return render(request, self.template_name, data)
    
    def post(self, request, id, *args, **kwargs):
        rq = request.POST
        
        rolename = rq.get('rolename', '')
        perm_ids = request.POST.getlist('perms')
        
        group = Group.objects.get(id=id)
        group.permissions.clear()
        group.name = rolename
        
        for perm_id in perm_ids:
            permission = Permission.objects.get(id=perm_id)
            group.permissions.add(permission)
        
        group.save()
        
        return redirect("/home/role_list")