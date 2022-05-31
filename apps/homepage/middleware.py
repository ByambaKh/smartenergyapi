__author__ = 'L'
from datetime import datetime, timedelta, time
from django.contrib.auth import logout
from django.conf import settings
from django.contrib import auth
from django.utils.deprecation import MiddlewareMixin

class SessionIdleTimeout(MiddlewareMixin):
    # def process_exception(self, request, exception):
    #     print (exception.__class__.__name__)
    #     print (exception.message)
    #     return None
    # def process_request(self, request):
    #     if request.user.is_authenticated():
    #         current_datetime = datetime.datetime.now()
    #         if ('last_login' in request.session):
    #             last = (current_datetime - request.session['last_login']).seconds
    #             if last > settings.SESSION_IDLE_TIMEOUT:
    #                 logout(request, '/login.html')
    #         else:
    #             request.session['last_login'] = current_datetime
    #     return None

    def _is_secure(self, request):
        if request.is_secure():
            return True

        if 'HTTP_X_SSL_PROTOCOL' in request.META:
            return True

        return False