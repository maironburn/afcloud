# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfMailServer
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

    mail_conf=AfMailServer.objects.count()
    
    if request.method == "POST":
        
        form= ConfigMailForm(request.POST or None)
        
        if form.is_valid():
            instance= None
            if mail_conf:
                instance = AfMailServer.objects.first()
            else:
                instance=form.save(commit=False)
            
            instance.email_server   = form.cleaned_data['email_server']
            instance.port           = form.cleaned_data['port']
            instance.usuario        = form.cleaned_data['usuario']
            instance.passwd         = form.cleaned_data['passwd']
            instance.tls            = form.cleaned_data['tls']
            instance.save()
            messages.success(request, 'Configuración de correo guardada con éxito', extra_tags='Configuración de correo')
            return HttpResponseRedirect('/startpage')
        
        else:
            return render(request, template_name, {'form': form})
        
    else:
           
        if mail_conf:
            form = ConfigMailForm(initial={'mail_conf': AfMailServer.objects.first()})
        else:
            form = ConfigMailForm()
            
        return render(request, template_name, {'form': form})
    