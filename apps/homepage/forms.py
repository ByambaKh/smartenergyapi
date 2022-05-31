#-*- coding: utf-8 -*-
from django import forms
from apps.data.models import *


class AddAhuiHereglegch(forms.Form):
    name = forms.CharField(max_length = 255)
    is_active = forms.ChoiceField(choices = STATUS_CHOICES, required=True)


class AanAngilalForm(forms.Form):
    name = forms.CharField(max_length = 255)
    is_active = forms.ChoiceField(choices = STATUS_CHOICES, required=True)


class AddCallType(forms.Form):
    name = forms.CharField(max_length = 255)
    is_active = forms.ChoiceField(choices = STATUS_CHOICES, required=True)


class SearchForm(forms.Form):
    searchText = forms.CharField(max_length = 255)


class FilesForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes',
        max_length=444444,
    )
    select_type = forms.CharField(max_length = 255)
    description = forms.CharField(max_length = 255)


class FilesSearchForm(forms.Form):
    start_date = forms.DateTimeField()
    end_date = forms.DateTimeField()
    name = forms.CharField(max_length = 255)
    username = forms.CharField(max_length = 255)
    file_size = forms.CharField(max_length = 255)
    file_type = forms.ChoiceField(choices = FILE_CHOOSE_TYPE, required=True)
    description = forms.CharField(max_length = 255)


class OrgAddForm(forms.Form):
    name = forms.CharField(max_length = 255)
    register = forms.CharField(max_length = 255)
    org_type = forms.CharField(max_length = 255)
    phone = forms.CharField(max_length = 255)
    web = forms.CharField(max_length = 255)
    email = forms.CharField(max_length = 255)
    address = forms.CharField(max_length = 255)


class OrgSearchForm(forms.Form):
    name = forms.CharField(max_length = 255)
    org_type = forms.CharField(max_length = 255)
    phone = forms.CharField(max_length = 255)


class UserAddForm(forms.Form):
    username = forms.CharField(max_length = 255)
    first_name = forms.CharField(max_length = 255)
    last_name = forms.CharField(max_length = 255)
    email = forms.EmailField(max_length = 255)
    org_select = forms.CharField(max_length = 255)
    phone = forms.CharField(max_length = 255)
    role_select = forms.CharField(max_length = 255)
    password = forms.CharField(max_length = 255)
    password_check = forms.CharField(max_length = 255)


class LoginForm(forms.Form):
    username = forms.CharField(max_length = 255)
    password = forms.CharField(max_length = 255)


class SubCallType(forms.Form):
    name = forms.CharField(max_length = 255)
    is_active = forms.ChoiceField(choices = STATUS_CHOICES, required=True)
    general_type = forms.ModelChoiceField(queryset=CallGeneralType.objects.all())


class CableTrassForm(forms.Form):
    # trass = forms.FileField(label='Файлаа сонгоно уу!')
    class Meta:
        model = Cable


class GemtelZuragForm(forms.Form):
    # zurag = forms.ImageField(label='Зургаа сонгоно уу!')
    class Meta:
        model = Gemtel