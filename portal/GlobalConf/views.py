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
from portal.GlobalConf.forms import GlobalConfForm, IncidenciasForm
from afcloud.settings import CRT_FILE,KEY_FILE,MEDIA_ROOT
import OpenSSL.crypto
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect

logger=getLogger()



@login_required
@group_required('af_cloud_admin',)
def creaGlogalConf(request, template_name='globalconf.html', extra_context=None):

    value = 'nuevo'

    if request.method == "POST" and request.FILES:
        
        fichero_crt = handle_uploaded_file(request.FILES['crt_file'],'%s%s' % (MEDIA_ROOT, CRT_FILE))
        fichero_key = handle_uploaded_file(request.FILES['key_file'], '%s%s' % (MEDIA_ROOT, KEY_FILE))
        form        = GlobalConfForm(request.POST, request.FILES)
 
        if form.is_valid():

            instance= None
            is_done_previously_conf_global= AfGlobalconf.objects.count()
            if is_done_previously_conf_global:
                instance= AfGlobalconf.objects.first()
                form.set_fqdn(instance)
            else:
                instance=form.save(commit=False)
            
            cert_openssl=OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, open('%s%s%s' % (MEDIA_ROOT,CRT_FILE, fichero_crt), 'r').read())
            fields = dict(cert_openssl.get_subject().get_components())
            fqdn   = fields[b'CN'][2:].decode('utf-8')
            instance.fqdn=fqdn
            
            instance.is_done=True
            instance.save()
            
            messages.success(request,  'Configuración guardada con éxito, FQDN: %s' % (fqdn), extra_tags='Creación de entornos')
            
            
            return HttpResponseRedirect('/startpage')
        else:
            return render(request, template_name, {'form': form, 'value': value})
    else:
        
        glb_conf=AfGlobalconf.objects.count()
        if glb_conf:
            
            form = GlobalConfForm(initial={'global_conf': AfGlobalconf.objects.first()})
        return render(request, template_name, {'form': form, 'value': value})
    
    
@login_required
@group_required('af_cloud_admin',)
def crearIncidencia(request, template_name='incidencias.html', extra_context=None):

    if request.method == "POST":
        
        form = IncidenciasForm(request.POST)
 
        if form.is_valid():

            try:
                
                asunto = form.cleaned_data['asunto']
                cuerpo = form.cleaned_data['cuerpo']
                
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
             
            messages.success(request,  'Incidencia registrada con éxito' , extra_tags='Creación de incidencia')
            return HttpResponseRedirect('/startpage')
        else:
            return render(request, template_name, {'form': form})
    else:
        
        form = IncidenciasForm()
        return render(request, template_name, {'form': form})
'''    
    
def send_email(asunto, cuerpo):
    

    
    #from_email = request.POST.get('from_email', '')
    if subject and message and from_email:
        try:
            send_mail(subject, message, from_email, ['admin@example.com'])
            
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return HttpResponseRedirect('/contact/thanks/')
    else:
        # In reality we'd use a form class
        # to get proper validation errors.
        return HttpResponse('Make sure all fields are entered and valid.')    
'''