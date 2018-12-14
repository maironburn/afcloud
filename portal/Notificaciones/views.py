# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfUserNotify, AfNotify_Tipo_instancia,AfTipoNotify, AfIncidencia, AfInstancia, AfLineaCatalogo, AfPerfil
from django.db import IntegrityError
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

def viewNotifyInfo(notificaciones):
    

    dict_rel_tipo_instancia= { "ITC":  "incidencia", "ITM" : "incidencia", 
                               "DM" :  "despliegue",  "DC"  : "despliegue",
                               "IC" :  "integrante"   ,  "IM"  : "integrante",
                               "CC" :  "catalogo", "CM": "catalogo"
        }
        
    dict_rel_tipo_template=  { "ITC":  "detalles_incidencia.html", "ITM" : "detalles_incidencia.html", 
                               "DM" :  "despliegue",  "DC"  : "despliegue",
                               "IC" :  "integrante"   ,  "IM"  : "integrante",
                               "CC" :  "catalogo", "CM": "catalogo"
        }
            
    lst_notificaciones=[]
    
    for n in notificaciones:
        tipo_rel_inst=AfNotify_Tipo_instancia.objects.get(notify=n)
        tipo_desc= tipo_rel_inst.tipo.desc
        instancia_asociada= dict_rel_tipo_instancia[ tipo_rel_inst.tipo.short_desc]
        instancia= getattr(tipo_rel_inst, instancia_asociada)
        template= dict_rel_tipo_template[ tipo_rel_inst.tipo.short_desc]
        instancia_asociada_nfo ={'instancia': instancia, 'tipo_desc': tipo_desc, 'template': template}
        lst_notificaciones.append(instancia_asociada_nfo)
        
    return lst_notificaciones



def getNotifyDescription(notificaciones):
    
    dict_rel_tipo_instancia= { "ITC":  "incidencia", "ITM" : "incidencia", 
                               "DM" :  "despliegue",  "DC"  : "despliegue",
                               "IC" :  "integrante"   ,  "IM"  : "integrante",
                               "CC" :  "catalogo", "CM": "catalogo"
        }
        
    lst_notificaciones=[]
    
    for n in notificaciones:
        try:
            tipo_rel_inst = AfNotify_Tipo_instancia.objects.filter(notify__owner=n.owner)
            for tri in tipo_rel_inst:
                tipo_desc  = tri.tipo.desc
                instancia_asociada= dict_rel_tipo_instancia[ tri.tipo.short_desc]
                instancia= getattr(tri, instancia_asociada)
                
                notify_nfo ={'notificacion': n, 'tipo_desc': tipo_desc, 'instancia_asociada': instancia_asociada, 'instancia_rel_id': instancia.id}
                lst_notificaciones.append(notify_nfo)
                
        except Exception as e:
            
            pass
        
    return lst_notificaciones


@login_required
def notificacionesIndex(request, template_name='notificacionesIndex.html', extra_context=None):
    try:
        # para las busquedas
        #name = request.GET.get('p') if request.GET.get('p') else ''
        af_user= AfUsuario.objects.get(user=request.user)
        notificaciones= AfUserNotify.objects.filter(to_user=af_user)
        lst_notify_info=getNotifyDescription(notificaciones)
        e=''

    except ObjectDoesNotExist as dne:
            
        messages.error(request, "No existen notificaciones para el usuario solicitado")
        return TemplateResponse(request, template_name, None)

    except Exception as e:
        pass


    hasNotificationPending(request)
    paginator = Paginator(lst_notify_info, 10)
    try:
        number = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        number = paginator.page(1)
    except EmptyPage:
        number = paginator.page(paginator.num_pages)
    c = paginator.page(number)
    context = {'p': c, 'e': e}

 
    return TemplateResponse(request, template_name, context)


def getNotifyDetails(request, id, template_name='consultar_notificacion.html'):

    try:
        
        notify_instance = AfUserNotify.objects.get(id=id)
        notify_instance.readed=True
        notify_instance.save()
        
        lst_notify_instance= [notify_instance]
        response=TemplateResponse(request, template_name, {'consultar_notificaciones': lst_notify_instance }).rendered_content
        data={'action': 'consultar_notificaciones', 'html':response, 'available_info': len(lst_notify_instance)}
        
        notificaciones_no_leidas= AfUserNotify.objects.filter(readed=False)
        request.session['notificaciones_no_leidas'] = True if notificaciones_no_leidas.count() else False
        
    except ObjectDoesNotExist as dne:
        
        messages.error(request, "La notificación sobre la que se solicita información no existe")
        return HttpResponseRedirect('/consultarNotificaciones')

    except Exception as e:
        pass

    return JsonResponse({'data':data})


def eliminarNotificacion(request, id):
    
    try:
        
        notificacion= AfUserNotify.objects.filter(id=id)
        notificacion.delete()
        
    except ObjectDoesNotExist as dne:

        messages.error(request, "La notificación que solicita eliminar no existe")
        return HttpResponseRedirect('/consultarNotificaciones')

    except Exception as e:
        pass
    
    messages.success(request,  'Notificación eliminada con éxito', extra_tags='Eliminación de notificaciones')
    return HttpResponseRedirect('/consultarNotificaciones')
