from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib import messages


class ZaavarchilgaaList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_zaavarchilgaa'
    template_name = 'homepage/lavlah/zaavarchilgaa.html'
    menu = '7'
    starter_q = "SELECT zaa.id, zaa.title, zaa.description, cat.name AS cat_name FROM data_zaavarchilgaa zaa" \
                " JOIN data_zaavarchilgaacategory cat ON zaa.category_id=cat.id" \
                " WHERE zaa.is_active = 1"

    def get(self, request, activeTab, *args, **kwargs):
        q = self.starter_q
        q = q + " ORDER BY zaa.created_date DESC"

        try:
            zaavarchilgaas = Zaavarchilgaa.objects.raw(q)
        except ObjectDoesNotExist:
            zaavarchilgaas = None

        try:
            categories = ZaavarchilgaaCategory.objects.filter(is_active=1).order_by('name')
        except ObjectDoesNotExist:
            categories = None

        data = {
            'zaavarchilgaas': zaavarchilgaas,
            'categories': categories,
            'menu': self.menu,
            'category_action': '/home/lavlagaa/add_zaavarchilgaa_category',
            'activeTab': str(activeTab),
        }
        return render(request, self.template_name, data)
    
    def post(self, request, activeTab, *args, **kwargs):
        title = request.POST['title']
        category = request.POST['category']
        description = request.POST['description']

        q = self.starter_q

        if title != '':
            q = q + " AND zaa.title LIKE '%%" + title + "%%'"
        if description != '':
            q = q + " AND zaa.description LIKE '%%" + description + "%%'"
        if category != '':
            q = q + " AND zaa.category_id LIKE '%%" + category + "%%'"
            category = int(category)

        try:
            zaavarchilgaas = Zaavarchilgaa.objects.raw(q)
        except ObjectDoesNotExist:
            zaavarchilgaas = None
        
        data = {
            'zaavarchilgaas': zaavarchilgaas,
            'categories': ZaavarchilgaaCategory.objects.filter(is_active=1).order_by('name'),
            'menu': self.menu,
            'activeTab': str(activeTab),
            'search_q': {
                'title': title,
                'category': category,
                'description': description,
            }
        }
        return render(request, self.template_name, data)


class ZaavarchilgaaAdd(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.add_zaavarchilgaa'
    template_name = 'homepage/lavlah/add_zaavarchilgaa.html'
    menu = '7'

    try:
        categories = ZaavarchilgaaCategory.objects.filter(is_active=1).order_by('name')
    except ObjectDoesNotExist:
        categories = None

    def get(self, request, *args, **kwargs):
        data = {
            'categories': self.categories,
            'action': '/home/lavlagaa/add_zaavarchilgaa',
            'menu': self.menu,
        }
        return render(request, self.template_name, data)   

    def post(self, request, *args, **kwargs):
        title = request.POST['title']
        category = request.POST['category']
        description = request.POST['description']

        try:
            Zaavarchilgaa.objects.get(title=title, is_active='1')
            messages.error(request, 'Зааварчилгааны гарчиг давхардаж байна.')
            return redirect('/home/lavlagaa/add_zaavarchilgaa')
        except ObjectDoesNotExist:
            try:
                zaavarchilgaa = Zaavarchilgaa(title=title, category_id=category, description=description)
                zaavarchilgaa.created_user_id = request.user.id
                zaavarchilgaa.save()
                messages.success(request, 'Амжилттай хадгалагдлаа!')
            except Exception:
                messages.error(request, 'Хадгалахад алдаа гарлаа!')
                return redirect('/home/lavlagaa/add_zaavarchilgaa')

        if 'save_and_continue' in request.POST:
            return redirect('/home/lavlagaa/add_zaavarchilgaa')
        else:
            return redirect('/home/lavlagaa/zaavarchilgaa/1/')


class ZaavarchilgaaEdit(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.change_zaavarchilgaa'
    template_name = "homepage/lavlah/add_zaavarchilgaa.html"
    menu = '7'

    def get(self, request, id, *args, **kwargs):
        try:
            zaavarchilgaa = Zaavarchilgaa.objects.get(id=id)
        except ObjectDoesNotExist:
            messages.error(request, 'Алдаа гарлаа!')
            return redirect('/home/lavlagaa/zaavarchilgaa/1/')

        data = {
            'categories': ZaavarchilgaaAdd.categories,
            'zaavarchilgaa': zaavarchilgaa,
            'action': '/home/lavlagaa/edit_zaavarchilgaa/'+id+'/',
            'menu': self.menu,
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        title = request.POST['title']
        category = request.POST['category']
        description = request.POST['description']


        try:
            zaavarchilgaa = Zaavarchilgaa.objects.get(id=id)
            zaavarchilgaa.title = title
            zaavarchilgaa.category_id = category
            zaavarchilgaa.description = description
            zaavarchilgaa.save()
            messages.success(request, 'Амжилттай засварлагдлаа!')
        except Exception:
            messages.error(request, 'Хадгалахад алдаа гарлаа!')
            return redirect('/home/lavlagaa/add_zaavarchilgaa')

        return redirect('/home/lavlagaa/zaavarchilgaa/1/')


class ZaavarchilgaaDel(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_zaavarchilgaa'
    template_name = "homepage/lavlah/zaavarchilgaa.html"

    def get(self, request, id, *args, **kwargs):
        try:
            zaavarchilgaa = Zaavarchilgaa.objects.get(id=id)
            zaavarchilgaa.is_active = 0
            zaavarchilgaa.save()
            messages.success(request, 'Амжилттай устгагдлаа!')
        except Exception:
            messages.error(request, 'Устгахад алдаа гарлаа!')

        return redirect("/home/lavlagaa/zaavarchilgaa/1/")

    def post(self, request, *args, **kwargs):
        return redirect('/home/lavlagaa/zaavarchilgaa/1/')


class ZaavarchilgaaCatgoryAdd(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/zaavarchilgaa.html"
    permission_required = ('data.add_zaavarchilgaacatgory')

    def get(self, request, *args, **kwargs):
        return redirect("/home/lavlagaa/zaavarchilgaa/2/")

    def post(self, request, *args, **kwargs):
        name = request.POST['name']

        try:
            ZaavarchilgaaCategory.objects.get(name=name, is_active=1)
            messages.error(request, 'Бүлгийн нэр давхардаж байна.')
        except ObjectDoesNotExist:
            try:
                zaavarchilgaaCategory = ZaavarchilgaaCategory(name=name)
                zaavarchilgaaCategory.created_user_id = request.user.id
                zaavarchilgaaCategory.save()
                messages.success(request, 'Амжилттай хадгалагдлаа!')
            except Exception:
                messages.error(request, 'Хадгалахад алдаа гарлаа!')

        return redirect('/home/lavlagaa/zaavarchilgaa/2/')


class ZaavarchilgaaCatgoryEdit(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/zaavarchilgaa.html"
    permission_required = ('data.change_zaavarchilgaacatgory')
    menu = '7'

    def get(self, request, id, *args, **kwargs):
        try:
            zaavarchilgaaCategory = ZaavarchilgaaCategory.objects.get(id=id)
        except Exception:
            zaavarchilgaaCategory = None

        try:
            categories = ZaavarchilgaaCategory.objects.filter(is_active=1).order_by('name')
        except Exception:
            categories = None

        try:
            zaavarchilgaas = Zaavarchilgaa.objects.raw(ZaavarchilgaaList.starter_q + ' ORDER BY zaa.created_date DESC')
        except ObjectDoesNotExist:
            zaavarchilgaas = None

        data = {
            'zaavarchilgaaCategory': zaavarchilgaaCategory,
            'zaavarchilgaas': zaavarchilgaas,
            'categories': categories,
            'category_action': '/home/lavlagaa/edit_zaavarchilgaa_category/'+id+'/',
            'menu': self.menu,
            'activeTab': '2'
        }
        return render(request, self.template_name, data)

    def post(self, request, id, *args, **kwargs):
        name = request.POST['name']

        try:
            ZaavarchilgaaCategory.objects.get(name=name, is_active=1)
            messages.error(request, 'Бүлгийн нэр давхардаж байна.')
            return redirect('/home/lavlagaa/edit_zaavarchilgaa_category/'+id+'/')
        except ObjectDoesNotExist:
            try:
                zaavarchilgaaCategory = ZaavarchilgaaCategory.objects.get(id=id)
                zaavarchilgaaCategory.name = name
                zaavarchilgaaCategory.save()
                messages.success(request, 'Амжилттай засварлагдлаа!')
            except Exception:
                messages.error(request, 'Засварлахад алдаа гарлаа!')

        return redirect('/home/lavlagaa/zaavarchilgaa/2/')


class ZaavarchilgaaCatgoryDel(LoginRequiredMixin,PermissionRequiredMixin, View):
    login_url = '/login'
    template_name = "homepage/lavlah/zaavarchilgaa.html"
    permission_required = ('data.delete_zaavarchilgaacatgory')

    def get(self, request, id, *args, **kwargs):
        try:
            zaavarchilgaaCategory = ZaavarchilgaaCategory.objects.get(id=id)
            zaavarchilgaaCategory.is_active = 0
            zaavarchilgaaCategory.save()
            messages.success(request, 'Амжилттай устгагдлаа!')
        except Exception:
            messages.error(request, 'Устгахад алдаа гарлаа!')
        return redirect("/home/lavlagaa/zaavarchilgaa/2/")

    def post(self, request, *args, **kwargs):
        return redirect('/home/lavlagaa/zaavarchilgaa/2/')