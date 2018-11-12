# coding=utf-8

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfProyecto, AfUsuario,\
    AfTipoPerfil, AfPerfil,AfRelEntPro, AfLineaCatalogo, AfServicio, AfEntorno, AfInstancia,\
    AfCiclo, AfGlobalconf
from django.http import JsonResponse
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from django.db import IntegrityError
from portal.Despliegues.forms import InstanciaForm,creaInstanciaForm
from django.contrib import messages
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

logger=getLogger()

@login_required
def seccionActivaRedirect(request,id):

    region_activa=request.session.get('seccion_activa',False)
    method_redirect={'despliegues': desplieguesIndex}
    if region_activa:
        return method_redirect[region_activa](request,id)


@login_required
def getInstancias(request, id_proyecto):

    proyecto=AfProyecto.objects.get(id=id_proyecto)
    lcas= AfLineaCatalogo.objects.filter(pro=proyecto)
    dictio_inst_list=[]
    lst_instancias=[]
   
    for lc in lcas:

        despliegues=AfInstancia.objects.filter(lca=lc)
        for i in despliegues:
            lst_instancias.append(i)
            ns=proyecto.pro_nombre
            fichero_entorno= i.rep.ent.ent_config_file.path
            kuber=Kuber(fichero_entorno)
            resp= kuber.list_namespaced_deployment(i.ins_unique_name, ns)

            if resp:
                
                dictio_inst_list.append(
                           {'nombre_entorno'    : i.rep.ent.ent_nombre ,
                            'nombre_servicio'   : lc.ser.ser_nombre,
                            'nombre_despliegue' : i.ins_unique_name,
                            'running'           : resp['replicas'], 
                            'replicas_min'      : lc.ser.ser_min_replicas,
                            'replicas_max'      : lc.ser.ser_max_replicas,
                            'estado'            : i.ins_activo,
                            'uri'               : i.ins_uri,
                            'creation_date'     : resp['creation_timestamp'],
                            'id'                : i.id
                            }
                           )

    return dictio_inst_list, lst_instancias



@login_required
@group_required(None,'Miembro')
def index(request, template_name='DesplieguesIndex.html', extra_context=None):

    request.session['seccion_activa'] = 'despliegues'
    context=get_extra_content(request)
    if len(context['proyectos']):
        id_proyecto_seleccionado=request.session.get('id_proyecto_seleccionado', False)
        if id_proyecto_seleccionado:
            return desplieguesIndex(request,id_proyecto_seleccionado)

    return TemplateResponse(request, template_name, context)


@login_required
@group_required(None,'Miembro')
def  desplieguesIndex(request, id_proyecto, template_name='DesplieguesIndex.html', extra_context=None):

    try:
        name = request.GET.get('p') if request.GET.get('p') else ''
        request.session['seccion_activa'] = 'despliegues'
        instancias,lst_despliegues = getInstancias (request,id_proyecto)
    
    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False
        messages.error(request, "No existen despliegues asociados al proyecto solicitado")
        
        return TemplateResponse(request, template_name, None)
        
    except Exception as e:
        pass
    
    if name == '':
        lst_despliegues=sorted(lst_despliegues, key=lambda p: lst_despliegues, reverse=False)
        e = 'no'
    else:

        filtrado=[]
        lst_despliegues= [x for x in lst_despliegues if name in  x.lca.ser.ser_nombre]
        for i in lst_despliegues:
            for e in instancias:
                if name in e['nombre_servicio']:
                    filtrado.append(e)
        instancias=filtrado
        filtrado={}
        e = 'si'

    paginator = Paginator(lst_despliegues, 10)
    extra_context=get_extra_content(request)
    try:
        number = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        number = paginator.page(1)
    except EmptyPage:
        number = paginator.page(paginator.num_pages)
    c = paginator.page(number)
    context = {'p': c, 'e': e, 'despliegues': lst_despliegues, 'instancias': instancias}
    if extra_context:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def getMaxMinReplic(svc):

    dic_replic={}
    for s in svc:
        dic_replic.update({s.id: {'min'           : s.ser_min_replicas,
                                  'max'           : s.ser_max_replicas,
                                  'ser_yaml_file' : s.ser_yaml_file.path}
                                  })

    return dic_replic


@login_required
@group_required(None)
def nuevoDespliegue(request, id_proyecto, template_name='newDespliegue.html'):
    value = 'nuevo'

    try:
        instancias,lst_despliegues = getInstancias (request,id_proyecto)
        proyecto=AfProyecto.objects.get(id=id_proyecto)
    
    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False
        messages.error(request, "Despliegue solicitado de un proyecto inexistente")
        return TemplateResponse(request, template_name, None)
    
    if request.method == "POST":

        form = creaInstanciaForm(request.POST or None)
        servicio=form.getServicio()
        entorno= form.getEntorno()
        lca= AfLineaCatalogo.objects.get(pro=proyecto,ser=servicio)

        yaml_file=servicio.ser_yaml_file.path
        kube_conf= entorno.ent.ent_config_file.path
        min= request.POST.get('ser_min_replicas', False)
        max= request.POST.get('ser_max_replicas', False)
        unique_instance_name = request.POST.get('ins_unique_name', False)
        namespace= proyecto.pro_nombre_k8s
        fqdn= AfGlobalconf.objects.values('fqdn')

        '''
         comprobar en is valid q no existe otro deployment con el mismo nombre
        '''
        if form.is_valid():
            operation_result=False
            try:
                kuber=Kuber(kube_conf)
                #fichero_yaml, target_namespace
                kwargs={
                        'fichero_yaml'         : yaml_file , #'yaml_file',
                        'namespace'            : namespace,
                        'replicas_min'         : min,
                        'replicas_max'         : max,
                        'unique_instance_name' : unique_instance_name,
                        'nfs_server'           : entorno.ent.nfs_server,
                        'env_name'             : entorno.ent.ent_nombre,
                        'fqdn'                 : fqdn[0]['fqdn']
                        }
                
                operation_result=kuber.createServiceStack(**kwargs)
                #kuber.updateIngressPostDeploy(**kwargs)
                #form.setConOkStatus()
            except Exception as e:
                logger.error(" %s , Fichero de entorno K8s no valido %s" % (__name__,kube_conf))

            if operation_result:
                #host: ns.env.fqdn/unique_name_ins-svc
                uri= ('https://%s.%s.%s/%s-svc' % (namespace, entorno.ent.ent_nombre, fqdn[0]['fqdn'], unique_instance_name))
                instancia=AfInstancia.objects.create(lca=lca,rep=entorno, ins_unique_name=unique_instance_name, ins_uri=uri)
                ciclo= AfCiclo.objects.create(ins=instancia)
                messages.success(request,  'Despliegue creado con éxito', extra_tags='Creación de despligues')
                return HttpResponseRedirect('/despliegue/proyecto/%s' % (id_proyecto))
        
        return render(request, template_name, {'form': form, 'value': value})
    
    else:
        data= {}
        dict_serv_extra= []
        nombre_proyecto= request.session.get('proyecto_seleccionado', False)
        id_servicios=AfLineaCatalogo.objects.filter(pro=proyecto).select_related('ser').values_list('ser_id', flat=True)
        svc=AfServicio.objects.filter(id__in=[id_servicios], ser_deleted=False)
        if len(svc):
            dict_serv_extra= getMaxMinReplic(svc)
            data={
                    'entorno_queryset':AfRelEntPro.objects.filter(pro__id=id_proyecto),
                    'service_queryset': svc
                  }
        
        form = InstanciaForm(data)

        return render(request, template_name, {'form': form, 'value': value, 'nombre_proyecto': nombre_proyecto,'dict_serv_extra': dict_serv_extra})


@login_required
@group_required(None)
def refreshReplicas(request,id_proyecto):
    
    try:
        proyecto=AfProyecto.objects.get(id=id_proyecto)
        response=getDetallesProyecto(proyecto)
        replicas={}
        for r in response:
            replicas.update({r['id'] : r['status']})
            
        data={'action': 'refresh_replicas', 'response':replicas}
        return JsonResponse({'data':data})
    
    except Exception as e:
        pass
    
    data={'action': 'refresh_replicas', 'response':False}
    return JsonResponse({'data':data})

@login_required
@group_required(None)
def modifyDeploymentReplicas(request, id_instancia, replicas, required_level=2 ):
    
    try:
        instance=AfInstancia.objects.get(id=id_instancia)
        entorno_file= instance.rep.ent.ent_config_file.path
        replicas=int(replicas)
        replicas_definidas_servicio=instance.lca.ser.ser_min_replicas
        namespace = instance.lca.pro.pro_nombre
   
        kuber=Kuber(entorno_file)        
        replicas_spec =replicas_definidas_servicio if replicas else 0 
        kuber.modifyDeploymentReplicas(instance.ins_unique_name, namespace,  replicas_spec)
        
        if replicas_spec:
            messages.success(request,  'Despliegue lanzado con éxito', extra_tags='Estado de despliegue')
        else:
            messages.success(request,  'Repliegue lanzado con éxito' , extra_tags='Estado de despliegue')
            
                
    except Exception as e:
        messages.error(request,  'Ocurrió algún error al tratar de cambiar el estado del despliegue', extra_tags='Estado de despliegue')
        print ('Exception modifyDeploymentReplicas')
    
    return HttpResponseRedirect('/despliegue/proyecto/%s' % (instance.lca.pro.id))
    
@login_required
@group_required(None)
def manualmodifyDeploymentReplicas(request, id_instancia, replicas, required_level=2 ):
    
    try:
        instance=AfInstancia.objects.get(id=id_instancia)
        entorno_file= instance.rep.ent.ent_config_file.path
        replicas=int(replicas)        
        namespace = instance.lca.pro.pro_nombre
        kuber=Kuber(entorno_file)                
        kuber.modifyDeploymentReplicas(instance.ins_unique_name, namespace,  replicas)        
        messages.success(request,  'Modificación de réplicas lanzadas con éxito', extra_tags='Estado de despliegue')
       
    except Exception as e:
        messages.error(request,  'Ocurrió algún error al tratar de cambiar el estado del despliegue', extra_tags='Estado de despliegue')
        print ('Exception modifyDeploymentReplicas')
    
    return HttpResponseRedirect('/despliegue/proyecto/%s' % (instance.lca.pro.id))
    
        

@login_required
@group_required(None)
def eliminarDespliegue(request, id_proyecto, id_instancia, required_level=2):

    try:
        
        instance             = AfInstancia.objects.get  (id=id_instancia)
        env_name             = instance.rep.ent.ent_nombre
        proyecto             = AfProyecto.objects.get(id=id_proyecto)
        f_config_entorno     = instance.rep.ent.ent_config_file.path
        lineas_catalog       = AfLineaCatalogo.objects.filter(pro=proyecto)
        lst_ins=[]
        for lc in lineas_catalog:
            lst_ins.extend(AfInstancia.objects.filter(lca=lc))

        instancias_asociadas = [i for i in list(lst_ins) if i !=instance]        
        fqdn= AfGlobalconf.objects.values('fqdn')
        
        kwargs={
                'unique_instance_name' :  instance.ins_unique_name,
                'namespace'            :  proyecto.pro_nombre_k8s,
                'services'             :  instancias_asociadas,
                'fqdn'                 :  fqdn[0]['fqdn'],
                'env_name'             :  env_name       
                }
        
        kuber=Kuber(f_config_entorno)
        if len(instancias_asociadas):
            kuber.unpublishFromIngress(kwargs)
        else:
            kuber.delete_namespaced_ingress(kwargs)
            
        kuber.delete_Instacia(**kwargs)
        instance.delete()

    except IntegrityError as ie:
        e = 'no'
        
    messages.success(request,  'Despligue elminado con éxito', extra_tags='Eliminación de despliegues')
    return HttpResponseRedirect('/despliegue/proyecto/%s' % (id_proyecto))
