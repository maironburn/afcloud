# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfProyecto,AfPerfil,AfEntorno,AfRelEntPro, AfUsuario
from portal.Proyectos.forms import ProyectoForm,editProyectoForm
from django.http import JsonResponse
from  django.shortcuts  import get_object_or_404
from django.db import IntegrityError
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from django.contrib import messages
from portal.Kubernetes.Kuber import Kuber
from afcloud import settings
from django.core.exceptions import ObjectDoesNotExist

logger=getLogger()

@login_required
@group_required('af_cloud_admin',)
def administrarProyectos(request, template_name='proyectosIndex.html', extra_context=None):
    try:
        # para las busquedas
        name = request.GET['p']
    except:
        name = ''
    if name == '':
        proyectos = AfProyecto.objects.all().order_by('pro_nombre')
        e = 'no'
    else:
        proyectos = AfProyecto.objects.filter(pro_nombre__icontains=name)
        e = 'si'

    set_bulk_num_entornos(proyectos)
    set_bulk_num_integrantes(proyectos)
    paginator = Paginator(proyectos, 10)

    usuario=request.user
    col=getProyectos(usuario,True)
    request.session['proyectos']     = col['proyectos']
    hasNotificationPending(request)
       
    try:
        number = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        number = paginator.page(1)
    except EmptyPage:
        number = paginator.page(paginator.num_pages)
    c = paginator.page(number)
    context = {'p': c, 'e': e, 'visualized_card': True}
    return TemplateResponse(request, template_name, context)



# funciones auxiliares para los campos calculados num de integrantes y entornos
def set_bulk_num_entornos(proyectos):

    for p in proyectos:
        lst_entornos=[]
        entornos=AfRelEntPro.objects.filter(pro=p)
        ent_iterados=[]
        ids_entornos=AfRelEntPro.objects.filter(pro=p).values_list('ent_id', flat=True).distinct()

        for e in entornos:

            if e.ent.id not in ent_iterados:
                lst_entornos.append(e.ent.ent_nombre)
                ent_iterados.append(e.ent.id)

        p.set_entornos(lst_entornos)
        p.set_num_entornos(len(lst_entornos))
        p.entornos_str=p.get_entornos_str()


'''
listado de los integrantes de cada proyecto
'''
def set_bulk_num_integrantes(proyectos):

    for p in proyectos:
        lst_integrantes=[]
        perfiles=AfPerfil.objects.filter(pro=p)
        p.set_num_integrantes(len(perfiles))
        for perf in perfiles:
            if perf.usu.user.username not in lst_integrantes:
                lst_integrantes.append(perf.usu.user.username)

        p.set_integrantes(lst_integrantes)
        p.integrantes_str=p.get_integrantes_str()



@login_required
def detallesProyecto(request, id, template_name='detalles_proyecto.html'):

    try:
        proyecto_instance= AfProyecto.objects.get(id=id)
        instancias_info= getDetallesProyecto(proyecto_instance) # definido en aux_meth

        proyecto={'nombre': proyecto_instance.pro_nombre, 'desc': proyecto_instance.pro_descripcion, 'instancias_info': instancias_info}
        response=TemplateResponse(request, template_name, {'proyecto': proyecto, 'instancias_info': instancias_info }).rendered_content

        data={'action': 'detalles_proyecto', 'html':response, 'available_info': len(instancias_info)}
    
    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False
        messages.error(request, "El proyecto sobre el que se solicita información no existe")
        return HttpResponseRedirect('/administrar/proyectos')

    except Exception as e:
        #messages.success(request,  'Proyecto editado con éxito', extra_tags='Edición de proyecto')
        pass

    return JsonResponse({'data':data})


@login_required
@group_required('af_cloud_admin',)
def administrarProyectosOrdered(request, orden, ascendente, template_name='proyectosIndex.html', extra_content=None):
    try:
        name = request.GET['p']
    except:


        name = ''
    e = 'no' # parametro q actua como flag indicando q se ha realizado una busqueda
    ordenar = ''
    reverse = False
    campo={1:'pro_nombre', 2: 'num_integrantes', 3: 'num_proyectos', 4: 'pro_activo'}

    proyectos=AfProyecto.objects.all()

    if int(ascendente) == 0:
            ordenar = '-'
            reverse=True

    if name=='':

        if int(orden):

            if int(orden)!=2 and int(orden)!=3:
                ordenar+=campo[int(orden)]
                p = proyectos.order_by(ordenar)
                set_bulk_num_entornos(p)
                set_bulk_num_integrantes(p)
            else:
                set_bulk_num_integrantes(proyectos)
                set_bulk_num_entornos(proyectos)
                if int(orden)==3:
                    p=sorted(proyectos, key=lambda p: p.num_entornos, reverse=reverse)
                else:
                    p=sorted(proyectos, key=lambda p: p.num_integrantes, reverse=reverse)
    else:
            p = proyectos.filter(Nombre__icontains=name)
            e = 'si'
            set_bulk_num_entornos(p)
            set_bulk_num_integrantes(p)

    paginator = Paginator(p, 10)
    try:
        number = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        number = paginator.page(1)
    except EmptyPage:
        number = paginator.page(paginator.num_pages)
    c = paginator.page(number)
    context = {'p': c, 'e': e, 'visualized_card': True}
    return TemplateResponse(request, template_name, context)


@login_required
@group_required('af_cloud_admin',)
def nuevoProyecto(request,template_name='newProject.html'):
    value = 'nuevo'

    if request.method == "POST":
        form = ProyectoForm(request.POST or None)
        envs=request.POST.getlist('entornos', None)
        if envs:
            form.setEntornos(envs)
            
        if form.is_valid():
            form.clean()
            nombre=form.cleaned_data['pro_nombre']
            descripcion = form.cleaned_data['pro_descripcion']
            activo = form.cleaned_data['pro_activo']
            #form.saveProyect('new')
            p=form.save(commit=True)
            p.pro_nombre_k8s=nombre
            form.saveProyect(p)
            p.save()
            messages.success(request,  'Proyecto creado con éxito', extra_tags='Creación de proyecto')

            col=getProyectos(request.user, False)
            request.session['proyectos'] = col['proyectos']
            request.session['id_proyecto_seleccionado'] = False
            return HttpResponseRedirect('/administrar/proyectos')
        else:
            if not len(form.get_entornos()):
                messages.error(request, "No se puede crear un proyecto sin asociar a un entorno")

            return render(request, template_name, {'form': form, 'value': value, 'visualized_card': True})#, 'entornos': entornos})

    else:

        entornos=AfEntorno.objects.all()
        form = ProyectoForm()
        #form = ProyectoForm(initial={'entornos' : entornos})
        return TemplateResponse(request, template_name,  {'form': form,
                                                          'value': value ,
                                                          'entornos_associated': entornos
                                                          })



@login_required
@group_required('af_cloud_admin',)
def editarProyecto(request, id,template_name='editarProyecto.html'):

    try:

        value = 'editar'
        proyecto= AfProyecto.objects.get(id=id)
        entornos_associated=[]
        rel_ent_pro=AfRelEntPro.objects.filter(pro=proyecto)

        for ea in rel_ent_pro:
            entornos_associated.append(AfEntorno.objects.get(id=ea.ent.id))

        entornos_associated=rel_ent_pro.values_list('ent', flat=True)
        envs=AfEntorno.objects.filter(id__in=entornos_associated)

        form = editProyectoForm(request.POST or None, instance=proyecto,initial={'entornos': envs})

        if request.method == 'POST':
            if form.is_valid():
                data={'pro_nombre': request.POST.get('pro_nombre'),
                      'pro_descripcion': request.POST.get('pro_descripcion'),
                      'pro_activo': True if request.POST.get('pro_activo')=='on' else False,
                      'entornos' : request.POST.getlist('entornos')
                      }
                form.saveProyect(data, instancia=proyecto)
                messages.success(request,  'Proyecto editado con éxito', extra_tags='Edición de proyecto')
                return HttpResponseRedirect('/administrar/proyectos')
            else:
                messages.error(request, "No se puede modificar un proyecto sin entornos asociados")

        return render(request, template_name, {'form': form, 'value': value,'id': id,
                                               'nombre_proyecto': proyecto.pro_nombre,
                                               'entornos_associated': entornos_associated,
                                                'visualized_card': True
                                               })
    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False
        messages.error(request, "El proyecto solicitado para edición no existe")
        pass

    except Exception as ex:
        messages.error(request, "Uhmmm... %s"  % (format(ex)))
        pass

    return TemplateResponse(request, template_name, None)

@login_required
@group_required('af_cloud_admin',)
def borrarProyecto(request, id):

    try:
        proyecto= AfProyecto.objects.get(id=id)
        rel_ent_pro=AfRelEntPro.objects.filter(pro=proyecto)
        for ep in rel_ent_pro:
            kuber=Kuber(ep.ent.ent_config_file.path)
            kuber.deleteNamespace(proyecto.pro_nombre)
            instancias=AfInstancia.objects.filter(rep=ep)
            for i in list(instancias):
                print('trying to delete pv: %s-pv' % (i.ins_unique_name,))
                kuber.delete_persistent_volume({'unique_instance_name': i.ins_unique_name})

        proyecto.delete()
        logger.info("Proyecto borrado con exito")

        messages.success(request, 'Proyecto borrado con éxito', extra_tags='Eliminación de proyecto')
        id_proyecto_seleccionado=request.session.get('id_proyecto_seleccionado', False)
        if not AfProyecto.objects.count() or id_proyecto_seleccionado==id:
            #fuerza la actualizacion del dropdown de la proyectos
            request.session['proyecto_seleccionado']    = False
            request.session['id_proyecto_seleccionado'] = False

        return HttpResponseRedirect('/startpage')

    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False
        messages.error(request, "El proyecto solicitado a eliminar no existe")
        pass


    except IntegrityError as e:

        mensaje='No se puede eliminar este proyecto : '
        proyectos = AfRelEntPro.objects.filter(pro=proyecto)
        if len(proyectos):
            mensaje+='entornos asociados'
        integrantes= AfPerfil.objects.filter(pro_id=proyecto)
        if len(integrantes):
            mensaje+='integrantes asociados'
        e = 'no'
        paginator = Paginator(proyectos, 10)
        try:
            number = int(request.GET.get('page', '1'))
        except PageNotAnInteger:
            number = paginator.page(1)
        except EmptyPage:
            number = paginator.page(paginator.num_pages)
        c = paginator.page(number)
        context = {'p': c, 'e': e, 'mensaje': mensaje}
        return TemplateResponse(request, 'proyectosIndex.html', context)

    except Exception as ex:
        messages.error(request, "Uhmmm... %s"  % (format(ex)))
        pass
    
    return HttpResponseRedirect('/administrar/proyectos')
