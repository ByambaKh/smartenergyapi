from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import FormView
from apps.extra import *
from django.core.urlresolvers import reverse


class FileControlPage(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.view_files'
    template_name = "homepage/file_control/file_control.html"
    form_class = FilesSearchForm
    menu = "9"

    def get(self, request, *args, **kwargs):
        try:
            files = Files.objects.filter(is_active="1")
        except Files.DoesNotExist:
            files = None
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        if now.day > 1:
            now = now.replace(day=1)
        start_date = now.strftime("%Y-%m-%d")
        data = {
            "datas": files,
            "menu" : self.menu,
            "search_q": {
                "start_created_date": start_date,
                "end_created_date": current_date,
            },
        }
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        rq = request.POST
        start_date = rq.get('start_date', '')
        end_date = rq.get('end_date', '')  # searchForm.cleaned_data['end_date']
        name = rq.get('name', '')  # searchForm.cleaned_data['name']
        username = rq.get('username', '')  # searchForm.cleaned_data['username']
        file_size = rq.get('file_size', '')  # searchForm.cleaned_data['file_size']
        file_type = rq.get('file_type', '')  # searchForm.cleaned_data['file_type']
        description = rq.get('description', '')  # searchForm.cleaned_data['description']

        file_para = {}

        if start_date != '' and end_date != '':
            file_para['created_date__range'] = (start_date, end_date)
        else:
            if start_date != '':
                file_para['created_date__gte'] = start_date
            if end_date != '':
                file_para['created_date__lte'] = end_date
        if name != '':
            file_para['name__contains'] = name
        if username != '':
            file_para['created_user_fullname__contains'] = username
        if file_size != '':
            file_para['file_size__lte'] = file_size
        if file_type != '':
            file_para['file_type'] = file_type
        if description != '':
            file_para['file_description__contains'] = description
        file_para['is_active'] = '1'

        try:
            files = Files.objects.filter(**file_para)
        except Files.DoesNotExist:
            files = None

        data = {
            "datas": files,
            "search_q": {
                "start_date": start_date,
                "end_date": end_date,
                "name": name,
                "username": username,
                "file_size": file_size,
                "file_type": file_type,
                "description": description,
            },
            "menu": self.menu
        }
        return render(request, self.template_name, data)


class FileUpload(FormView):
    form_class = FilesForm

    def form_valid(self, form):
        file = Files()
        uploaded_file = self.get_form_kwargs().get('files')['docfile']
        type = form.cleaned_data['select_type']
        uploaded_file_name = uploaded_file.name
        uploaded_file_size = GetHumanReadable(uploaded_file.size, precision=2)
        uploaded_file_type = GetConvertedFileType(uploaded_file.content_type)
        file.file_type = uploaded_file_type
        file.docfile = uploaded_file
        file.name = uploaded_file_name
        file.file_description = form.cleaned_data['description']
        file.file_size = uploaded_file_size
        file.type = type
        file.save()
        return redirect('/home/files/')

    def form_invalid(self, form):
        print("invalid upload form")

    def get_success_url(self):
        return reverse('profile_image', kwargs={'pk': self.id})


class FileDeletePage(LoginRequiredMixin, View):
    login_url = '/home/index'
    permission_required = 'data.delete_files'

    def get(self, request, id):
        file_id = id
        file = Files.objects.get(pk=file_id)
        file.is_active = "0"
        file.save()
        return redirect('/home/files/')