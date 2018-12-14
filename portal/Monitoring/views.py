# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfProyecto, AfEntorno
from portal.Monitoring.forms import MonitoringForm,adminMonitoringForm
from django.db import IntegrityError
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from django.contrib import messages
from afcloud.settings import GRAFANA_PORT, URL_PREFIX
from django.core.exceptions import ObjectDoesNotExist



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


def adminMonitoring (request, template_name='admin_monitoring_Index.html', extra_context=None):
    
    try:

        lst_proj_env=[]
        proyectos= AfProyecto.objects.all()
        rel_pro_ents=[]
        entornos_list=[]
        entornos_id_list=[]
        env= []
        lst_widgets =[]
        
        ent_all = AfEntorno.objects.all()
        if ent_all.count():
            for p in proyectos:
                dict_proj_env={}
                entornos= AfRelEntPro.objects.filter(pro=p)
                
                for e in entornos:
                    env.append(e.ent)
                    lst_widgets.extend(monitoringWidgets (request, e.ent.id, p.pro_nombre))
                    entornos_list.append(e.ent.ent_nombre)
                    entornos_id_list.append(str(e.ent.id))
                    
                dict_proj_env = {'proyecto':  p.pro_nombre, 'entornos': env , 'widgets' : lst_widgets}    
                env=[]
                rel_pro_ents.append ({'proyecto':  p.pro_nombre, 'entornos': ','.join(entornos_list), 'entornos_id' : ','.join(entornos_id_list)})
                entornos_list=[]
                lst_widgets = []
                entornos_id_list=[]
                
                lst_proj_env.append(dict_proj_env)
                
            form= adminMonitoringForm()
        else:
            messages.error(request, "No hay ningún entorno definido")
        
    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False    
            
        messages.error(request, "")
        return TemplateResponse(request, template_name, None)

    except Exception as e:
        pass

    context = {'form': form, 'data' : lst_proj_env , 'rel_pro_ents': rel_pro_ents, 'ent_all': ent_all}

    return render(request, template_name, context)    



def monitoringWidgets(request, id_env,ns=None):

    #widget_url='http://%s:%s/%s%s&var-app=All&panelId=%s' #%s&to=%s&theme=light
    
    widget_url='http://%s:%s/%s' 
    lst_iframe = []
    
    try:
        entorno    = AfEntorno.objects.get(id=id_env)
        entorno_ip = entorno.cluster_ip
        ns= 'All' if ns is None else ns
        lst_iframe = []
        
        for w in widget_list:
            lst_iframe.append({'ent_nombre': entorno.ent_nombre, 'entorno_id': entorno.id, 'id_widget': w[0],'widget_url': widget_url % (entorno_ip, GRAFANA_PORT, URL_PREFIX)})
        
                
    except ObjectDoesNotExist as dne:

        messages.error(request, "Error en la petición de monitorización")
        return HttpResponseRedirect('/startpage')

    except Exception as e:
        #messages.success(request,  'Proyecto editado con éxito', extra_tags='Edición de proyecto')
        pass
    
    return lst_iframe



def  monitoringRequest (request, template_name='monitoring_Index.html', extra_context=None):
    
    try:
        
        af_user  = AfUsuario.objects.get(user=request.user)
        id_proyecto = request.session['id_proyecto_seleccionado']
        pro= AfProyecto.objects.get(id=id_proyecto)

        entornos_list    = []
        entornos_id_list = []
        dict_proj_env    = {}
        rel_pro_ents     = []
        lst_proj_env     = []
        ent_all          = []
        pro_env=AfRelEntPro.objects.filter(pro=pro)
            
        for pe in pro_env:
            lst_widgets = monitoringWidgets (request, pe.ent.id, pro.pro_nombre)
            ent_all.append(pe.ent)
            dict_proj_env = {'proyecto':  pro.pro_nombre, 'entornos': pe.ent , 'widgets' : lst_widgets}                
            entornos_list.append(pe.ent.ent_nombre)
            entornos_id_list.append(str(pe.ent.id))
     
        rel_pro_ents.append ({'proyecto':  pro.pro_nombre, 'entornos': ','.join(entornos_list), 'entornos_id' : ','.join(entornos_id_list)})
        entornos_list=[]
        entornos_id_list=[]
            
        lst_proj_env.append(dict_proj_env)
            
        form= MonitoringForm()
        
    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False    
            
        messages.error(request, "")
        return TemplateResponse(request, template_name, None)

    except Exception as e:
        pass

    context = {'form': form, 'data' : lst_proj_env , 'rel_pro_ents': rel_pro_ents, 'ent_all': ent_all }

    return render(request, template_name, context)    

