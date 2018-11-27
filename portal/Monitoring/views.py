# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfProyecto, AfEntorno
from portal.Monitoring.forms import MonitoringForm,adminMonitoringForm
from django.db import IntegrityError
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from django.contrib import messages
from afcloud.settings import GRAFANA_PORT, URL_PREFIX, URL_SUFIX, URL_THEME
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse


dict_widget= {
                    'pod_usage'             : '',
                    'cpu_usage'             : '',
                    'memory_usage'          : '',
                    'disk_usage'            : '',
                    'pod_capacity'          : '',
                    'cpu_capacity'          : '',
                    'mem_capacity'          : '',
                    'disk_capacity'         : '',
                    'deployment_replicas'   : ''
                }
        
@login_required
@group_required('Gestor',)
def  monitoringIndex(request,  template_name='monitoring_Index.html', extra_context=None):
    try:
        # para las busquedas
        name = request.GET.get('p') if request.GET.get('p') else ''
        #integrantes,usu_integrantes = getIntegrantesProyecto (request,id_proyecto)
        e=''
        envs = None
        data_dict=None
        proyecto_seleccionado= request.session.get('id_proyecto_seleccionado', None)
        if proyecto_seleccionado:
            entornos= AfRelEntPro.objects.filter(pro=proyecto_seleccionado)
            envs = []
            for e in list(entornos):
                envs.append(e.ent)
            data_dict={
                        'proyecto':request.session.get('proyecto_seleccionado'),
                        'entornos': envs}
 
    
        form= MonitoringForm()
        
    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False    
            
        messages.error(request, "")
        return TemplateResponse(request, template_name, None)

    except Exception as e:
        pass

    context = {'p': data_dict, 'form': form}

    return render(request, template_name, {'form': form,
                                           'proyecto': request.session.get('proyecto_seleccionado'),
                                           'entornos': envs
                                           })


def adminMonitoring(request,  template_name='admin_monitoring_Index.html', extra_context=None):
    
    try:

        lst_proj_env=[]
        proyectos= AfProyecto.objects.all()
        
        for p in proyectos:
            dict_proj_env={}
            entornos= AfRelEntPro.objects.filter(pro=p)
            for e in entornos:
                lst_widgets = monitoringWidgets (request, e.ent.id, p.pro_nombre)
                dict_proj_env = {'proyecto':  p.pro_nombre, 'entornos': e.ent , 'widgets' : lst_widgets}
             
            lst_proj_env.append(dict_proj_env)
            
        form= adminMonitoringForm()
        
    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False    
            
        messages.error(request, "")
        return TemplateResponse(request, template_name, None)

    except Exception as e:
        pass

    context = {'form': form, 'data' : lst_proj_env }

    return render(request, template_name, context)    



def monitoringWidgets(request, id_env,ns=None):

    
    #widget_url='http://%s:%s/%s%s&panelId=%s&from=%s&to=%s&theme=light'
    widget_url='http://%s:%s/%s%s&panelId=%s&from=' #%s&to=%s&theme=light
    lst_iframe = []
    
    try:
        entorno    = AfEntorno.objects.get(id=id_env)
        entorno_ip = entorno.cluster_ip
        widget_list = (
            ('4', 'Cluster Pod Usage'),
            ('5', 'Cluster CPU Usage'),
            ('6', 'Cluster Memory Usage'),
            ('7', 'Cluster Disk Usage'),
            ('9', 'Cluster Pod Capacity'),
            ('10', 'Cluster CPU Usage'),
            ('11', 'Cluster Mem Usage'),
            ('12', 'Cluster Disk Usage'),
            ('16', 'Deployment Replicas'),
            )    

        ns= 'All' if ns is None else ns
        lst_iframe = []
        
        for w in widget_list:
            #entorno + '/' + widgets + '/' + from + '/' + to;
            lst_iframe.append({'id_widget': w[0],'widget_url': widget_url % (entorno_ip, GRAFANA_PORT, URL_PREFIX, ns, w[0])})
        
                
    except ObjectDoesNotExist as dne:

        messages.error(request, "Error en la petición de monitorización")
        return HttpResponseRedirect('/startpage')

    except Exception as e:
        #messages.success(request,  'Proyecto editado con éxito', extra_tags='Edición de proyecto')
        pass
    
    return lst_iframe



def  monitoringRequest(request,  id_env, id_widgets, r_from, r_to):
    
    widget_url='http://%s:%s/%s%s&panelId=%s&from=%s&to=%s&theme=light'
    #entorno + '/' + widgets + '/' + from + '/' + to;
    try:
        entorno    = AfEntorno.objects.get(id=id_env)
        entorno_ip = entorno.cluster_ip
        widgets    = id_widgets.split('_')
        r_from     = r_from
        r_to       = r_to
        ns= 'All'
        lst_iframe = []

        for w in widgets:
            lst_iframe.append(widget_url % (entorno_ip, GRAFANA_PORT, URL_PREFIX, ns, w, r_from, r_to))
        
    except Exception as e:
        pass

    data={'action': 'monitoringRequest', 'available_info': len(lst_iframe), 'lst_iframe': lst_iframe}

    return JsonResponse({'data':data})

