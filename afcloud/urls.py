"""clonVirtualSpaces URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib.staticfiles import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import path
from portal.Usuarios.views import userChangePass,users
from portal.Usuarios import views as user_views

urlpatterns = [
    url(r'^$', auth_views.LoginView.as_view (template_name="login.html")),
    url(r'^login/$', auth_views.LoginView.as_view (template_name="login.html")),
    url(r'^logout/$', auth_views.LogoutView.as_view (template_name="logged_out.html")),
    url(r'^admin/', admin.site.urls),
    url(r'^user/pass/(?P<id>\d+)', userChangePass, name='passwordChange'),
    url(r'^usuarios/', users, name='usuarios'),
    #url(r'^proyectos/$', ProyectosList.as_view (template_name="logged_out.html"),
    url(r'^', include('portal.urls'))
    ]
