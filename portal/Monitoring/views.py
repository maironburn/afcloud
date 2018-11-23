# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfProyecto, AfEntorno
from portal.Monitoring.forms import MonitoringForm
from django.db import IntegrityError
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist



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



def  monitoringRequest(request,  id_env, id_widgets, r_from, r_to):
    #entorno + '/' + widgets + '/' + from + '/' + to;
    
    try:
        entorno = AfEntorno.objects.get(id=id_env)
        widgets = id_widgets.split('_')
        r_from  = r_from
        r_to    = r_to
        
    except Exception as e:
        pass
    
