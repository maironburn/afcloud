# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfGlobalconf,AfIncidencia,AfEstadosIncidencia, \
AfNotasIncidencia,AfMailServer,AfUserNotify, AfTipoNotify, AfNotify_Tipo_instancia
from django.http import JsonResponse
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from portal.Utils.logger import *
from django.contrib import messages
from portal.Incidencias.forms import IncidenciasForm,AfNotasIncidenciaForm
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
from portal.Common.CustomMailBackEnd import CustomMailBackEnd
import datetime

logger=getLogger()


def getIncidenciasInfo(incidencias):

    list_it_estados=[]
    notas_asociadas = []
    for it in incidencias:

        notas_asociadas= AfNotasIncidencia.objects.filter(incidencia=it).order_by('fecha_creacion')
        estado=  it.estado.estado if it.estado else 'No definido'
           
        list_it_estados.append({'incidencias'        : it, 'estado_name' : estado,
                                'notas_asociadas'    : notas_asociadas})
        notas_asociadas=[]

    return list_it_estados


@login_required
def getItDetails(request, id, template_name='detalles_incidencia.html', notify_id=False):

    try:
        it= AfIncidencia.objects.get(id=id)
        incidencia_instance= [it]
        instancias_info= getIncidenciasInfo(incidencia_instance) # definido en aux_meth
        response=TemplateResponse(request, template_name, {'incidencias_info': instancias_info }).rendered_content

        data={'action': 'detalles_incidencia', 'html':response, 'available_info': len(instancias_info)}

        # flag que indica que la consulta viene hecha de la vista de notificaciones
        if notify_id:
            user_notify=AfUserNotify.objects.get(id=notify_id)
            if not user_notify.readed:
                user_notify.readed= True
                user_notify.save()
            
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
    hasNotificationPending(request)
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

'''
    EmailMultiAlternatives (self, subject='', body='', from_email=None, to=None, bcc=None,
                 connection=None, attachments=None, headers=None, alternatives=None,
                 cc=None, reply_to=None):
'''
def send_notify_mail(kwargs):

    asunto      = kwargs.get   ('asunto',"default value")
    cuerpo      = kwargs.get   ('cuerpo',"default value")
    estado      = kwargs.get   ('estado',"Abierta")
    from_mail   = kwargs.get   ('from_mail')
    to_email    = kwargs.get   ('to_email')

    cmbe= CustomMailBackEnd()
    conx= cmbe.get_connection()
    template    =kwargs.get   ('template',None)

    if template:
        htmly       = get_template (template + ".html")
        plaintext   = get_template (template + ".txt")
    else:
        htmly       = get_template ('mail_incidencia.html')
        plaintext   = get_template ('mail_incidencia.txt')

    d = { 'username': ('%s %s (%s)') % (from_mail.user.first_name,from_mail.user.first_name,from_mail.user.username) , 
         'contenido' :cuerpo, 'fecha': datetime.datetime.now(), 'estado': estado}

    text_content = plaintext.render(d)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(asunto, text_content, from_mail.user.email, to_email, connection=conx)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def create_UserNotify(kwargs):

    to_user     = kwargs.get   ('to_user'          , None)
    m_from      = kwargs.get   ('from_mail'         , None)
    tipo_notify = kwargs.get   ('tipo_notificacion' , None)
    incidencia  = kwargs.get   ('incidencia'        , None)
    user_notify = kwargs.get   ('user_notify'       , None)

    if isinstance(to_user,list):
        for user in to_user:
            notify = AfUserNotify.objects.create(owner= user, to_user=user, from_user=m_from, fecha_creacion=datetime.datetime.now())
            n_tipo = AfTipoNotify.objects.get(short_desc=tipo_notify)
            n_t_i  = AfNotify_Tipo_instancia.objects.create(notify=notify, tipo=n_tipo, incidencia=incidencia)
        
        
@login_required
@group_required('af_cloud_admin',)
def crearIncidencia(request, template_name='incidencias.html', extra_context=None):

    if request.method == "POST":

        form = IncidenciasForm(request.POST)

        if form.is_valid():

            try:

                asunto      = form.cleaned_data['asunto']
                cuerpo      = form.cleaned_data['cuerpo']
                af_user     = AfUsuario.objects.get (user=request.user)
                gconf       = AfGlobalconf.objects.first()
                to_email    = gconf.email

                dict_mail={'asunto': asunto, 'cuerpo': cuerpo, 'from_mail': af_user, 'to_email':to_email,
                           'estado': 'Abierta', 'to_email' : [to_email], 'tipo_notificacion' : "ITC" }
                # configuracion de correo realizada ?
                mail_conf=AfMailServer.objects.count()
                if mail_conf:
                    send_notify_mail (dict_mail)


                incidencia      = AfIncidencia.objects.create(usu=af_user, asunto=asunto, cuerpo=cuerpo)
                estado          = AfEstadosIncidencia.objects.get(estado='Abierta')
                incidencia.estado = estado
                incidencia.save()
                
                to_users=AfUsuario.objects.filter(usu_administrador=True)
                dict_mail.update({'to_user': list(to_users), 'incidencia': incidencia})
                
                create_UserNotify(dict_mail)
        
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


def getToMail_NotifyTo (from_user,instance):
    
    lst_to_mail=[]
    notify_to= None
    
    if from_user.usu_administrador:
        notify_to= [instance.usu]
        lst_to_mail.append(instance.usu.user.email)
    else:
        msg_to= AfUsuario.objects.filter(usu_administrador=True)
        lst_to_mail= [u.user.email for u in msg_to]
        notify_to=list(msg_to)
    
    return notify_to, lst_to_mail
                   
@login_required
@group_required(None)
def addNotaIncidencia(request, id, template_name='editarIncidencia.html'):
    
    try:
        instance         = AfIncidencia.objects.get(id=id)
        from_user        = AfUsuario.objects.get(user=request.user)
        estado_read_only = not from_user.usu_administrador
        
        if request.method == 'POST':

            form     = AfNotasIncidenciaForm(request.POST or None, initial={'instance': instance, 'status_ro': estado_read_only})

            if form.is_valid():

                asunto      = form.cleaned_data['asunto']
                cuerpo      = form.cleaned_data['notas']
                estado      = form.cleaned_data['estado'] if form.cleaned_data['estado'] else instance.estado
                instance.estado         = estado
                nota                    = AfNotasIncidencia.objects.create (autor=from_user, incidencia=instance,notas=cuerpo, asunto=asunto)
                instance.fecha_updated=nota.fecha_creacion
                instance.save()
                # si el usuario q add la nota es el administrador, el receptor es el "iniciador" de la incidencia
                # notify_to , lista de afusuarios, lst_mail; lista de correos
                notify_to, lst_to_mail  = getToMail_NotifyTo(from_user, instance) 
   
                tipo_notificacion=AfTipoNotify.objects.get(short_desc='ITM')
                
                dict_notify={
                    'instance' : instance, 
                    'from_user': from_user,
                    'notify_to': notify_to,
                    'tipo_notificacion':  tipo_notificacion         
                             }
                deliverNotify(dict_notify)

                dict_mail={
                            'asunto' : asunto,   'cuerpo' : cuerpo, 'from_mail' : from_user,
                            'to_email' : lst_to_mail, 'estado' : estado.estado , 'template'  : 'nota_incidencia',
                            'tipo_notificacion' :'ITM' ,  'incidencia' : instance, 'to_users': notify_to
                            }
                    
                mail_conf=AfMailServer.objects.count()
                if mail_conf:
                    send_notify_mail (dict_mail)

                messages.success(request,  'Nota añadida con éxito', extra_tags='Actuación en incidencia')
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

def deliverNotify(kwargs):
    
    tipo_notificacion = kwargs.get     ('tipo_notificacion' , None)
    instance    = kwargs.get     ('instance'          , None)
    notify_to   = kwargs.get     ('notify_to'         , None)
    from_user   = kwargs.get     ('from_user'         , None)
    
    
    ids_notify_incidencia= list(AfNotify_Tipo_instancia.objects.filter(incidencia= instance).values_list('notify', flat=True))
    
    for u in notify_to:
        has_notify_asociada=AfUserNotify.objects.filter(owner=u, id__in=ids_notify_incidencia).count()
        if has_notify_asociada:
            
            notify = AfUserNotify.objects.get(owner=u, id__in=ids_notify_incidencia)
            notify.to_user   = u
            notify.from_user = from_user
            notify.readed    = False
            notify.fecha_creacion = instance.fecha_updated
            notify.save()
            
            noti_tipo_instancia = AfNotify_Tipo_instancia.objects.get(notify=notify, incidencia=instance)
            noti_tipo_instancia.tipo=tipo_notificacion
            noti_tipo_instancia.save()
        else:
            notify = AfUserNotify.objects.create(owner= u, to_user=u, from_user=from_user, fecha_creacion=datetime.datetime.now())
            n_t_i  = AfNotify_Tipo_instancia.objects.create(notify=notify, tipo=tipo_notificacion, incidencia=instance)
                
    

@login_required
@group_required('af_cloud_admin',)
def eliminarIncidencia(request, id):
    
    try:
        
        incidencia= AfIncidencia.objects.filter(id=id)
        incidencia.delete()
        
    except ObjectDoesNotExist as dne:

        messages.error(request, "La incidencia que solicita eliminar no existe")
        return HttpResponseRedirect('/administrar/incidencias')

    except Exception as e:
        pass
    
    messages.success(request,  'Incidencia eliminada con éxito', extra_tags='Eliminación de incidencias')
    return HttpResponseRedirect('/administrar/incidencias')

    