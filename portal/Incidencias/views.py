# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfGlobalconf,AfIncidencia,AfRelIncidenciaEstado, AfEstadosIncidencia, AfNotasIncidencia
from django.http import JsonResponse
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from portal.Utils.logger import *
from django.contrib import messages
from portal.Incidencias.forms import IncidenciasForm,AfNotasIncidenciaForm,IncidenciasEditForm
from afcloud.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
import datetime

logger=getLogger()


def getIncidenciasInfo(incidencias):
    
    list_it_estados=[]
    notas_asociadas = []
    for it in incidencias:
        estado      = AfRelIncidenciaEstado.objects.get(incidencia=it)
        estado_name = estado.estado
        notas_asociadas= AfNotasIncidencia.objects.filter(incidencia=it).order_by('fecha_creacion')
        list_it_estados.append({'incidencias': it, 'estado': estado, 
                                'estado_name': estado_name,
                                'notas_asociadas' : notas_asociadas})
        notas_asociadas=[]
    
    return list_it_estados


@login_required
def getItDetails(request, id, template_name='detalles_incidencia.html'):

    try:
        incidencia_instance= [AfIncidencia.objects.get(id=id)]
        instancias_info= getIncidenciasInfo(incidencia_instance) # definido en aux_meth
        response=TemplateResponse(request, template_name, {'incidencias_info': instancias_info }).rendered_content

        data={'action': 'detalles_incidencia', 'html':response, 'available_info': len(instancias_info)}
    
    except ObjectDoesNotExist as dne:
        
        messages.error(request, "La incidencia sobre la que se solicita información no existe")
        return HttpResponseRedirect('/administrar/proyectos')

    except Exception as e:
        #messages.success(request,  'Proyecto editado con éxito', extra_tags='Edición de proyecto')
        pass

    return JsonResponse({'data':data})



@login_required
@group_required('af_cloud_admin',)
def administrarIncidencias(request, template_name='incidenciasIndex.html', extra_context=None):
    try:
        
        af_user=AfUsuario.objects.get(user=request.user)
        if af_user.usu_administrador:
            incidencias = AfIncidencia.objects.all().order_by('fecha_apertura')
        else:
            incidencias = AfIncidencia.objects.filter(usu=af_user).order_by('fecha_apertura')
        
    except Exception as e:
        logger.info("Exception en administrarIncidencias: %s" % format(e))
    
    
    list_it_estados = getIncidenciasInfo(incidencias)        
    paginator = Paginator(list_it_estados, 10)

    try:
        number = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        number = paginator.page(1)
    except EmptyPage:
        number = paginator.page(paginator.num_pages)
    c = paginator.page(number)
    context = {'p': c }
    return TemplateResponse(request, template_name, context)




def send_notify_mail(kwargs):
    
    asunto      = kwargs.get   ('asunto',"default value")
    cuerpo      = kwargs.get   ('cuerpo',"default value")
    estado      = kwargs.get   ('estado',"Abierta")
    from_email  = EMAIL_HOST_USER
    gconf       = AfGlobalconf.objects.first()
    to_email    = gconf.email
    template    =kwargs.get   ('template',None)
    if template:
        htmly       = get_template (template + ".html")
        plaintext   = get_template (template + ".txt")
    else:
        htmly       = get_template ('mail_incidencia.html')
        plaintext   = get_template ('mail_incidencia.txt')
        
    af_user = kwargs.get   ('af_user',"default value")
    d = { 'username': af_user.user.email , 'contenido' :cuerpo, 'fecha': datetime.datetime.now(), 'estado': estado}
                
    text_content = plaintext.render(d)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(asunto, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
                    
    
@login_required
@group_required('af_cloud_admin',)
def crearIncidencia(request, template_name='incidencias.html', extra_context=None):

    if request.method == "POST":
        
        form = IncidenciasForm(request.POST)
 
        if form.is_valid():

            try:
                
                asunto  = form.cleaned_data['asunto']
                cuerpo  = form.cleaned_data['cuerpo']
                af_user = AfUsuario.objects.get (user=request.user)

                dict_mail={'asunto': asunto, 'cuerpo': cuerpo, 'af_user': af_user}
                send_notify_mail (dict_mail)
                
                incidencia      = AfIncidencia.objects.create(usu=af_user, asunto=asunto, cuerpo=cuerpo)
                estado          = AfEstadosIncidencia.objects.get(estado='Abierta')
                asoc_it_estado  = AfRelIncidenciaEstado.objects.create(incidencia=incidencia, estado=estado)
                
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            
            except Exception as e:
                print ("exception sending mail : %s" % format(e))
                          
            messages.success(request,  'Incidencia registrada con éxito' , extra_tags='Creación de incidencia')
            return HttpResponseRedirect('/administrar/incidencias')
        else:
            return render(request, template_name, {'form': form})
    else:
        
        form = IncidenciasForm()
        return render(request, template_name, {'form': form})

@login_required
@group_required(None)
def addNotaIncidencia(request, id,template_name='editarIncidencia.html'):
    try:
        instance = AfIncidencia.objects.get(id=id)
        af_user   = AfUsuario.objects.get(user=request.user)
        estado_read_only= not af_user.usu_administrador
        if request.method == 'POST':
        
            form     = AfNotasIncidenciaForm(request.POST or None, initial={'instance': instance, 'status_ro': estado_read_only})
        
            if form.is_valid():
            
                asunto      = form.cleaned_data['asunto']
                cuerpo      = form.cleaned_data['notas']
                estado      = form.cleaned_data['estado']
            
                nota        = AfNotasIncidencia.objects.create(autor=af_user, incidencia=instance,notas=cuerpo, asunto=asunto)
                estado      = AfEstadosIncidencia.objects.get(estado=estado)
                instance.fecha_updated=nota.fecha_creacion
                instance.save()
                it_estado   = AfRelIncidenciaEstado.objects.get(incidencia=instance )
                it_estado.estado = estado
                it_estado.save ()
            
                dict_mail={'asunto': asunto, 'cuerpo': cuerpo, 'af_user': af_user, 'estado':estado, 'template': 'nota_incidencia'  }
                send_notify_mail (dict_mail)
                messages.success(request,  'Incidencia editada con éxito', extra_tags='Actuación en incidencia')
                return HttpResponseRedirect('/administrar/incidencias')

        form = AfNotasIncidenciaForm(initial={'instance': instance, 'status_ro': estado_read_only})
        return render(request, template_name, {'form': form, 'id': instance.id })
    
    except ObjectDoesNotExist as dne:
        messages.error(request, "La incidencia solicitada no existe")
        pass

    except Exception as ex:
        messages.error(request, "Uhmmm... %s"  % (format(ex)))
        pass

    return HttpResponseRedirect('/administrar/incidencias')

