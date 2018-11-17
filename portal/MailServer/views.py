# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfGlobalconf
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from portal.Utils.logger import *
from django.contrib import messages
from portal.MailServer.forms import ConfigMailForm
from afcloud.settings import CRT_FILE,KEY_FILE, MEDIA_ROOT
import OpenSSL.crypto
from django.http import HttpResponse, HttpResponseRedirect

logger=getLogger()


@login_required
@group_required('af_cloud_admin',)
def config_Mail(request, template_name='MailServerConf.html', extra_context=None):

    value = 'nuevo'
    form= ConfigMailForm()
    if request.method == "POST" and request.FILES:
        
        if form.is_valid():

            messages.success(request,  'Configuración guardada con éxito')
            return HttpResponseRedirect('/startpage')
        
        else:
            return render(request, template_name, {'form': form, 'value': value})
        
    else:
        
        
        return render(request, template_name, {'form': form, 'value': value})
    