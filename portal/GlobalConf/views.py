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
from portal.GlobalConf.forms import GlobalConfForm
from afcloud.settings import CRT_FILE,KEY_FILE,MEDIA_ROOT
import OpenSSL.crypto

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
            '''
            la configuración es unica 
            ...
            '''
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
        form = GlobalConfForm()
        return render(request, template_name, {'form': form, 'value': value})
