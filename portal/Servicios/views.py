# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfServicio
from portal.Servicios.forms import ServicioForm
from django.http import JsonResponse
from django.core import serializers
from django.db import IntegrityError
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
#from portal.Proyectos.forms_ori import ProyectoForm
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist


logger=getLogger()

@login_required
@group_required('af_cloud_admin',)
def administrarServicios(request, template_name='serviciosIndex.html', extra_context=None):
    try:
        # para las busquedas
        name = request.GET['p']
    except:
        name = ''
    if name == '':
        servicios = AfServicio.objects.filter(ser_deleted=False).order_by('ser_nombre')
        e = 'no'
    else:
        servicios = AfServicio.objects.filter(ser_nombre__icontains=name, ser_deleted=False)
        e = 'si'
    paginator = Paginator(servicios, 10)
    try:
        number = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        number = paginator.page(1)
    except EmptyPage:
        number = paginator.page(paginator.num_pages)
    c = paginator.page(number)
    context = {'p': c, 'e': e}
    return TemplateResponse(request, template_name, context)



@login_required
@group_required('af_cloud_admin',)
def administrarServiciosOrdered(request, orden, ascendente, template_name='serviciosIndex.html', extra_content=None):
    try:
        name = request.GET['p']
    except:
        name = ''
    ordenar = ''
    if int(ascendente) == 0:
        ordenar = '-'
    if int(orden):
        campo={1:'ser_nombre', 2: 'ser_tarifa', 3: 'ser_activo', 4: '', 5: '' }
        ordenar+=campo[int(orden)]


    if name == '':
        servicios = AfServicio.objects.filter(ser_deleted=False).order_by(ordenar)
        e = 'no'
    else:
        servicios = AfServicio.objects.filter(ser_nombre__icontains=name, ser_deleted=False)
        e = 'si'

    paginator = Paginator(servicios, 10)
    try:
        number = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        number = paginator.page(1)
    except EmptyPage:
        number = paginator.page(paginator.num_pages)
    c = paginator.page(number)
    context = {'p': c, 'e': e}
    return TemplateResponse(request, template_name, context)



@login_required
@group_required('af_cloud_admin',)
def nuevoServicio(request,template_name='newService.html'):

    value = 'nuevo'
    if request.method == "POST":

        fichero_yaml=handle_uploaded_file(request.FILES['ser_yaml_file'])
        form = ServicioForm(request.POST, request.FILES)
        form.setConfigfile(fichero_yaml)
        if form.is_valid():

            AfServicio = form.save(commit=False)
            AfServicio.save()
            messages.success(request,  'Servicio creado con éxito', extra_tags='Creación de servicios')
            return HttpResponseRedirect('/administrar/servicios')
        else:
            messages.success(request,  'El mínimo de replicas debe ser menor que el máximo', extra_tags='Replicas Error')
            return render(request, template_name, {'form': form, 'value': value})
    else:
        form = ServicioForm()
        return render(request, template_name, {'form': form, 'value': value})


@login_required
@group_required('af_cloud_admin',)
def editarServicio(request, id,template_name='editarServicio.html'):

    value = 'editar'
    try:
        servicio= AfServicio.objects.get(id=id)
        form = ServicioForm(request.POST or None, instance=servicio)

    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False
        messages.error(request, "El servicio a editar solicitado no existe")
        return HttpResponseRedirect('/administrar/servicios')

    if request.method == 'POST':
        if form.is_valid():
            servicio.save()
            messages.success(request,  'Servicio editado con éxito', extra_tags='Edición de servicios')
            return HttpResponseRedirect('/administrar/servicios')

    return render(request, template_name, {'form': form, 'value': value,'id': id, 'nombre_servicio': servicio.ser_nombre})

@login_required
@group_required('af_cloud_admin',)
def borrarServicio(request, id):

    try:

        servicio= AfServicio.objects.get(id=id)
        servicio.ser_deleted=True
        servicio.save()

    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False
        messages.error(request, "El servicio a eliminar no existe")
        return HttpResponseRedirect('/administrar/servicios')

    except IntegrityError:
        servicios = AfServicio.objects.all()
        e = 'no'
        paginator = Paginator(servicios, 10)
        try:
            number = int(request.GET.get('page', '1'))
        except PageNotAnInteger:
            number = paginator.page(1)
        except EmptyPage:
            number = paginator.page(paginator.num_pages)
        c = paginator.page(number)
        context = {'p': c, 'e': e, 'mensaje': 'No se puede eliminar este Servicio porque tiene catálogos asociados'}
        return TemplateResponse(request, 'serviciosIndex.html', context)

    messages.success(request,  'Servicio borrado con éxito', extra_tags='Eliminación de servicios')
    return HttpResponseRedirect('/administrar/servicios')
