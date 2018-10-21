# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfEntorno,AfProyecto,AfRelEntPro
from portal.Entornos.forms import EntornoForm
from django.db import IntegrityError
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from portal.Utils.logger import *
from django.contrib import messages
from portal.GlobalConf.forms import GlobalConfForm
from afcloud.settings import CRT_FILE,KEY_FILE,MEDIA_ROOT

logger=getLogger()



@login_required
@group_required('af_cloud_admin',)
def creaGlogalConf(request, template_name='globalconf.html', extra_context=None):

    value = 'nuevo'

    if request.method == "POST" and request.FILES:
        
        fichero_crt=handle_uploaded_file(request.FILES['crt_file'],'%s%s' % (MEDIA_ROOT, CRT_FILE))
        fichero_key=handle_uploaded_file(request.FILES['key_file'], '%s%s' % (MEDIA_ROOT, KEY_FILE))
        form = GlobalConfForm(request.POST, request.FILES)
 
        if form.is_valid():
            '''
            la configuración es unica y el fqdn esta definido como unique
            ...
            '''
            global_conf=form.save(commit=False)
            global_conf.is_done=True
            global_conf.save()
            messages.success(request,  'Configuración guardada con éxito', extra_tags='Creación de entornos')
            
            
            return HttpResponseRedirect('/administrar/globalconf')
        else:
            return render(request, template_name, {'form': form, 'value': value})
    else:
        form = GlobalConfForm()
        return render(request, template_name, {'form': form, 'value': value})
