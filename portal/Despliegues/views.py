# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfProyecto, AfUsuario,\
    AfTipoPerfil, AfPerfil,AfRelEntPro, AfLineaCatalogo, AfServicio, AfEntorno, AfInstancia,\
    AfCiclo

from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from django.db import IntegrityError
from portal.Despliegues.forms import InstanciaForm,creaInstanciaForm
from django.contrib import messages
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from django.contrib import messages

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
            dictio_inst_list.append({'nombre_entorno': i.rep.ent.ent_nombre ,
                        'nombre_servicio': lc.ser.ser_nombre,
                        'estado': i.ins_activo,
                        'uri': i.ins_uri,
                        'create_date': '',
                        'id': i.id
                        })

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
        name = request.GET['p']

    except:
        name = ''
    request.session['seccion_activa'] = 'despliegues'
    instancias,lst_despliegues = getInstancias (request,id_proyecto)

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
        #lst_despliegues=sorted(lst_despliegues, key=lambda p: p.lca.ser.ser_nombre, reverse=False)
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

    instancias,lst_despliegues = getInstancias (request,id_proyecto)
    proyecto=AfProyecto.objects.get(id=id_proyecto)

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
        namespace= proyecto.pro_nombre

        '''
         comprobar en is valid q no existe otro deployment con el mismo nombre
        '''
        if form.is_valid():

            try:
                kuber=Kuber(kube_conf)
                #fichero_yaml, target_namespace
                kwargs={'fichero_yaml': 'yaml_all_services_HsXeaZf.yaml' , #'yaml_file',
                        'namespace': namespace,
                        'replicas_min': min,
                        'replicas_max': max,
                        'unique_instance_name':unique_instance_name,
                        'nfs-server' : '10.244.0.103',
                        'env-name'   : entorno.ent.ent_nombre
                        }
                kuber.createServiceStack(**kwargs)

                #form.setConOkStatus()
            except Exception as e:
                logger.error(" %s , Fichero de entorno K8s no valido %s" % (__name__,kube_conf))


            #rel_ent_pro= AfRelEntPro.objects.get(pro=proyecto,ent=entorno)
            
            
            '''
            instancia=AfInstancia.objects.create(lca=lca,rep=entorno)
            ciclo= AfCiclo.objects.create(ins=instancia)
            '''
            messages.success(request,  'Despliegue creado con éxito', extra_tags='Creación de despligues')
            return HttpResponseRedirect('/despliegue/proyecto/%s' % (id_proyecto))
        else:
            return render(request, template_name, {'form': form, 'value': value})
    else:
        nombre_proyecto= request.session.get('proyecto_seleccionado', False)
        id_servicios=AfLineaCatalogo.objects.filter(pro=proyecto).select_related('ser').values_list('ser_id', flat=True)

        svc=AfServicio.objects.filter(id__in=[id_servicios])
        dict_serv_extra= getMaxMinReplic(svc)
        data={'entorno_queryset':AfRelEntPro.objects.filter(pro__id=id_proyecto),
              'service_queryset': svc
              }
        #.objects.filter(id__in=[c.ser.id for d in lst_despliegues])}
        form = InstanciaForm(data)

        return render(request, template_name, {'form': form, 'value': value, 'nombre_proyecto': nombre_proyecto,'dict_serv_extra': dict_serv_extra})



@login_required
@group_required(None)
def eliminarDespliegue(request, id_proyecto, id_instancia, required_level=2):

    instance=AfInstancia.objects.get(id=id_instancia)

    try:
        instance.delete()


    except IntegrityError as ie:
        e = 'no'
        '''
        afusers=AfUsuario.objects.all()
        paginator = Paginator(afusers, 10)
        try:
            number = int(request.GET.get('page', '1'))
        except PageNotAnInteger:
            number = paginator.page(1)
        except EmptyPage:
            number = paginator.page(paginator.num_pages)
        c = paginator.page(number)
        context = {'p': c, 'e': e, 'mensaje': 'No se puede eliminar este despliegue porque tiene  movidas asociados'}
        return TemplateResponse(request, 'users.html', context)
        #return administrarEntornos(request, template_name='entornosIndex.html', context)
    #return HttpResponseRedirect('/administrar/entornos')
        '''
    messages.success(request,  'Despligue elminado con éxito', extra_tags='Eliminación de despliegues')
    return HttpResponseRedirect('/despliegue/proyecto/%s' % (id_proyecto))
