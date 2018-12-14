# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfProyecto, AfEntorno, AfCiclo
from portal.Facturacion.forms import FacturacionForm
from django.db import IntegrityError
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from functools import reduce


        
@login_required
#@group_required('Gestor',)
def  facturacionIndex(request,  template_name='facturacion_Index.html', extra_context=None):
    try:
        

        envs = False
        data_dict=None
        proyecto_seleccionado = request.session.get('id_proyecto_seleccionado', False)
        envs_all = AfRelEntPro.objects.filter(pro=proyecto_seleccionado)
        ent_all=[]
        
        for env in envs_all:
            ent_all.append(env.ent)
            
        if proyecto_seleccionado:
            entornos= AfRelEntPro.objects.filter(pro=proyecto_seleccionado)
            envs = []
            for e in list(entornos):
                
                envs.append(e.ent)

        form= FacturacionForm()
        
    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False    
            
        messages.error(request, "")
        return TemplateResponse(request, template_name, None)

    except Exception as e:
        pass

    
    return render(request, template_name, {'form': form,
                                           'proyecto': request.session.get('proyecto_seleccionado'),
                                           'entornos': envs,
                                           'data_dict' :data_dict,
                                           'ent_all': ent_all
                                           })




def detalles_facturacion(request,template_name='facturacion_detalles.html', extra_context=None):
    
    try:
        
        f_from =int(request.GET.get('data[from]'))/1000
        f_t = int(request.GET.get('data[to]'))/1000
        entorno_param= request.GET.get('data[entorno]')
       
        f = datetime.utcfromtimestamp(f_from).strftime('%Y-%m-%d %H:%M:%S')
        t = datetime.utcfromtimestamp(f_t).strftime('%Y-%m-%d %H:%M:%S')
        env= AfEntorno.objects.get(id=entorno_param)
        proyecto_seleccionado = request.session.get('id_proyecto_seleccionado', False)
        proyecto=AfProyecto.objects.get(id=proyecto_seleccionado)
        ent_pro= AfRelEntPro.objects.get(ent=env, pro=proyecto)
        instancias=AfInstancia.objects.filter(rep=ent_pro)
        
        #string_app=[ x.ins_unique_name for x in instancias]
        #string_app='%7C'.join(string_app)
        
        ciclos_lst = []
        computo_global ={}
        
        afciclo= AfCiclo.objects.filter(pro=proyecto,cic_fecha_inicio__range=(f,t))
        for c in afciclo:
            
            importe=0
            horas=0
            if c.cic_fecha_fin:
                horas= c.cic_fecha_fin - c.cic_fecha_inicio    
            else:
                horas = datetime.now().replace(tzinfo=None) - c.cic_fecha_inicio.replace(tzinfo=None)
                
            horas= '%.2f' % (horas.total_seconds()/3600)
            
            kwargs= { 'ip_env': env.cluster_ip, 
                      #'app_name' : string_app,
                      'namespace': proyecto.pro_nombre,
                      'r_from' : f_from, 'r_to' : f_t 
                     }

            # calculo de la disponibilidad
            uptime= getPrometheusAvailability(**kwargs)
            start_time = round(c.cic_fecha_inicio.replace(tzinfo=None).timestamp())
            
            if c.cic_fecha_fin:
                end_time   = round(c.cic_fecha_fin.replace(tzinfo=None).timestamp())
            else:
                end_time   = round(datetime.now().replace(tzinfo=None).timestamp())  
            
            range_time=[ float(y) for x ,y in uptime.items() if x>=start_time and x<end_time ]
            average=1    
            if range_time:
                average= (reduce(lambda x, y: x + y, range_time) / len(range_time)) 
            importe = round(average * c.tarifa * round(float(horas),2),2)
            
            
            if c.ins_unique_name in computo_global.keys():
                computo_global[c.ins_unique_name][0]+= round(float(horas),2)
                computo_global[c.ins_unique_name][4]+= round(importe,2)
            else:
                computo_global.update({c.ins_unique_name: [round(float(horas),2), 
                                        c.tarifa, average* 100, env.ent_nombre, round(importe,2) , c.id]})

            c.cic_fecha_fin= 'Activo' if c.cic_fecha_fin is None else c.cic_fecha_fin
            
            dict_data= {
                'servicio' : c.ins_unique_name,
                'entorno'  : env.ent_nombre,
                'replicas' : c.num_replicas,
                'tarifa'   : c.tarifa,
                'f_ini'    : c.cic_fecha_inicio,
                'f_fin'    : c.cic_fecha_fin ,
                'horas'    : horas,
                'uptime'   : average
                }
            
            ciclos_lst.append(dict_data)
           
                
        paginator = Paginator(ciclos_lst, 10)
        try:
            number = int(request.GET.get('data[page]'))
        except PageNotAnInteger:
            number = paginator.page(1)
        except EmptyPage:
            number = paginator.page(paginator.num_pages)
        c = paginator.page(number)
        context = {'p': c , 'computo_global': computo_global}       
         
        response=TemplateResponse(request, template_name, context).rendered_content
        data={'action': 'detalles_facturacion', 'html':response, 'available_info': len(ciclos_lst)}
        
        return JsonResponse({'data':data})
    
    except Exception as e:
        pass
    
    data={'action': 'detalles_facturacion', 'response':False}
    return JsonResponse({'data':data})


def detalles_instancia_facturacion(request,id,template_name='facturacion_instancia_detalles.html', extra_context=None):
    
    try:
        
        f_from =int(request.GET.get('data[from]'))/1000
        f_t = int(request.GET.get('data[to]'))/1000
        entorno_param= request.GET.get('data[entorno]')
       
        f = datetime.utcfromtimestamp(f_from).strftime('%Y-%m-%d %H:%M:%S')
        t = datetime.utcfromtimestamp(f_t).strftime('%Y-%m-%d %H:%M:%S')
        env= AfEntorno.objects.get(id=entorno_param)
        proyecto_seleccionado = request.session.get('id_proyecto_seleccionado', False)
        proyecto=AfProyecto.objects.get(id=proyecto_seleccionado)
        ent_pro= AfRelEntPro.objects.get(ent=env, pro=proyecto)
       
        ciclos_lst = []
        computo_global ={}
        instance= AfCiclo.objects.get(id=id)
        afciclo= AfCiclo.objects.filter(ins_unique_name=instance.ins_unique_name, pro=proyecto,cic_fecha_inicio__range=(f,t))
        for c in afciclo:
                
            importe=0
            horas=0
            if c.cic_fecha_fin:
                horas= c.cic_fecha_fin.replace(tzinfo=None) - c.cic_fecha_inicio.replace(tzinfo=None)    
            else:
                horas = datetime.now() - c.cic_fecha_inicio.replace(tzinfo=None)
                    
            horas= '%.2f' % (horas.total_seconds()/3600)
                
            kwargs= {     'ip_env'   : env.cluster_ip, 
                          
                          'namespace': proyecto.pro_nombre,
                          'r_from'   : f_from, 'r_to' : f_t 
                         }

                # calculo de la disponibilidad
            uptime= getPrometheusAvailability(**kwargs)
            start_time = round(c.cic_fecha_inicio.replace(tzinfo=None).timestamp())
                
            if c.cic_fecha_fin:
                end_time   = round(c.cic_fecha_fin.replace(tzinfo=None).timestamp())
            else:
                end_time   = round(datetime.now().replace(tzinfo=None).timestamp())  
            
            average=1    
            range_time=[ float(y) for x ,y in uptime.items() if x>=start_time and x<end_time ]
            if range_time:
                average= (reduce(lambda x, y: x + y, range_time) / len(range_time)) 
            importe = average * c.tarifa * round(float(horas),2)
                
                
            if c.ins_unique_name in computo_global.keys():
                computo_global[c.ins_unique_name][0]+= round(float(horas),2)
                computo_global[c.ins_unique_name][4]+= importe
            else:
                computo_global.update({c.ins_unique_name: [round(float(horas),2), 
                                            c.tarifa, average* 100, env.ent_nombre, importe, c.id]})

            c.cic_fecha_fin= 'Activo' if c.cic_fecha_fin is None else c.cic_fecha_fin
                
            dict_data= {
                        'servicio' : c.ins_unique_name,
                        'entorno'  : env.ent_nombre,
                        'replicas' : c.num_replicas,
                        'tarifa'   : c.tarifa,
                        'f_ini'    : c.cic_fecha_inicio,
                        'f_fin'    : c.cic_fecha_fin ,
                        'horas'    : horas,
                        'uptime'   : round (average * 100,2),
                        'importe'  : round (importe ,2)
                    }
                
            ciclos_lst.append(dict_data)
               
                
        paginator = Paginator(ciclos_lst, 10)
        try:
            number = int(request.GET.get('data[page]'))
            
        except PageNotAnInteger:
            number = paginator.page(1)
        except EmptyPage:
            number = paginator.page(paginator.num_pages)
        c = paginator.page(number)
        context = {'p': c , 'computo_global': computo_global, 'ciclos_lst': ciclos_lst }       
         
        response=TemplateResponse(request, template_name, context).rendered_content
        data={'action': 'detalles_instance_facturacion', 'html':response, 'available_info': len(ciclos_lst)}
        
        return JsonResponse({'data':data})
    
    except Exception as e:
        pass
    
    data={'action': 'detalles_instance_facturacion', 'response':False}
    return JsonResponse({'data':data})

