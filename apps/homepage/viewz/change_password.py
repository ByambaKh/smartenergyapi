from django.shortcuts import render, redirect
from apps.homepage.forms import *
from django.views import View
from django.contrib import messages


class ChangePassword(View):
    template_name = "homepage/change_password.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, None)

    def post(self, request, *args, **kwargs):
        old_pass = request.POST.get('old_pass', '')
        new_pass1 = request.POST.get('new_pass1', '')
        new_pass2 = request.POST.get('new_pass2', '')

        user = User.objects.filter(is_active=1, username=request.user.username).first()
        if user is not None:
            if user.check_password(old_pass):
                if new_pass1 == new_pass2:
                    user.set_password(new_pass1)
                    user.save()
                    messages.success(request, 'Нууц үг амжилттай солигдлоо!')
                else:
                    messages.warning(request, 'Шинэ нууц үг хоорондоо таарахгүй байна!')
            else:
                messages.warning(request, 'Хуучин нууц үг буруу байна!')
        else:
            messages.warning(request, 'Хэрэглэгч олдсонгүй!')
        return redirect('/home/change_password')