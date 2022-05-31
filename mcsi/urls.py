"""mcsi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import *
from django.conf import settings
from django.conf.urls.static import static
from apps.homepage.views import loginz, auth_user, url_fixer

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^home/', include('apps.homepage.urls')),
    url(r'^api/', include('apps.api.urls')),
    url(r'^login', loginz, name='login'),
    url(r'^authenticate', auth_user, name='auth'),
    # url(r'session_security/', include('session_security.urls')),
    url(r'^$', url_fixer, name='url_fixer'),
    url(r'^home/$', url_fixer, name='url_fixer')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)