# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfProyecto, AfUsuario,\
    AfTipoPerfil, AfPerfil,AfLineaCatalogo,AfInstancia, AfServicio

from django.db import IntegrityError
from portal.Catalogo.forms import CatalogRawForm,editCatalogRawForm
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from django.contrib import messages

logger=getLogger()


@login_required
def seccionActivaRedirect(request,id_proyecto):

    region_activa=request.session.get('seccion_activa',False)
    method_redirect={'catalogos': catalogosIndex}
    if region_activa:

        return method_redirect[region_activa](request,id_proyecto)


@login_required
def getCatalogoProyecto(request,id_proyecto):

    dict_servicios={}
    lst_serv=[]
    catalog=[]
    proyecto=AfProyecto.objects.get(id=id_proyecto)
    lca=AfLineaCatalogo.objects.filter(pro=proyecto)

    if len(lca):
        for s in lca:
            servicio=AfServicio.objects.get(id=s.ser.id)
            dict_servicios.update({servicio.ser_nombre: servicio})
            lst_serv.append(servicio.ser_nombre)
            if s.lca_activo:
                catalog.append(s)
    return dict_servicios, lst_serv, catalog


@login_required
@group_required('Gestor',)
def index(request, template_name='CatalogoIndex.html', extra_context=None):

    context=get_extra_content(request)
    request.session['seccion_activa'] = 'catalogo'

    if len(context['proyectos']):
        id_proyecto_seleccionado=request.session.get('id_proyecto_seleccionado', False)
        if id_proyecto_seleccionado:
            return catalogosIndex(request,id_proyecto_seleccionado,extra_context= context)

    return TemplateResponse(request, template_name, context)

@login_required
@group_required('Gestor',)
def  catalogosIndex(request, id_proyecto, template_name='CatalogoIndex.html', extra_context=None):
    try:
        # para las busquedas
        name = request.GET['p']
    except:
        name = ''
    request.session['seccion_activa'] = 'catalogos'
    dict_servicios,lst_servicios,catalog = getCatalogoProyecto (request,id_proyecto)
    if name == '':
        servicios = sorted(lst_servicios)
        e = 'no'
    else:
        filtrado={}
        lst_servicios= [x for x in lst_servicios if name in x.ser_nombre ]
        for i in lst_servicios:
            for k,v in dict_servicios.items():
                if i == k:
                    filtrado.update({k:v})
        integrantes=filtrado
        e = 'si'

    paginator = Paginator(servicios, 10)
    try:
        number = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        number = paginator.page(1)
    except EmptyPage:
        number = paginator.page(paginator.num_pages)
    c = paginator.page(number)
    context = {'p': c, 'e': e, 'servicios': dict_servicios, 'catalog': catalog}

    if extra_context:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)




@login_required
@group_required('Gestor',)
def nuevoCatalogo(request,id_proyecto, template_name='newCatalogo.html'):
    value = 'nuevo'

    dict_servicios, lst_serv, catalog= getCatalogoProyecto (request, id_proyecto)
    
    if request.method == "POST":

        form = CatalogRawForm(request.POST or None)
        form.setProyect(id_proyecto)
        
        if form.is_valid():
            
            form.save()

            messages.success(request,  'Catálogo añadido con éxito', extra_tags='Creación de catálogos')
            return HttpResponseRedirect('/catalogo/proyecto/%s' % (id_proyecto))
        else:
            return render(request, template_name, {'form': form, 'value': value})
    else:
        nombre_proyecto= request.session.get('proyecto_seleccionado', False)
        #exluimos del nuevo catalogo servicios inactivos
        #data={'service_queryset': AfServicio.objects.filter(ser_activo=True).exclude(id__in=[c.ser.id for c in catalog ])}
        # se admiten multiples servicios 
        # precarga de las tarifas base de los servicios
        svc=AfServicio.objects.filter(ser_activo=True)
        data={'service_queryset': svc}
        dict_svc={}
        for s in svc:
            dict_svc.update({s.id : s.ser_tarifa})
            
        form = CatalogRawForm(initial=data)
        return render(request, template_name, {'form': form, 'value': value, 'nombre_proyecto': nombre_proyecto, 'id': id_proyecto, 'dict_svc': dict_svc})


@login_required
@group_required('Gestor',)
def editarCatalogo(request,id_proyecto, id_servicio,template_name='editarCatalogo.html'):
    value = 'editar'


    proyecto=AfProyecto.objects.get(id=id_proyecto)
    lca=AfLineaCatalogo.objects.get(id=id_servicio)
    form = editCatalogRawForm(request.POST or None, instance=lca)

    if request.method == 'POST':

        if form.is_valid():

            form.setProyect(id_proyecto)
            form.save()

            messages.success(request,  'Catálogo editado con éxito', extra_tags='Edición de catálogos')
            return HttpResponseRedirect('/catalogo/proyecto/%s' % (id_proyecto))
        
    svc=AfServicio.objects.filter(ser_activo=True)    
    dict_svc={}
    for s in svc:
        dict_svc.update({s.id : s.ser_tarifa})

    return render(request, template_name, {'form': form, 'value': value,'id': proyecto.id,'dict_svc': dict_svc})

@login_required
@group_required('Gestor',)
def eliminarCatalogo(request, id_proyecto, id_servicio):

    proyecto= AfProyecto.objects.get(id=id_proyecto)
    linea_catalogo= AfLineaCatalogo.objects.get(id=id_servicio)
    try:
        linea_catalogo.delete()

    except IntegrityError as ie:
        e = 'no'
        af_catalog=AfLineaCatalogo.objects.all()
        paginator = Paginator(af_catalog, 10)
        try:
            number = int(request.GET.get('page', '1'))
        except PageNotAnInteger:
            number = paginator.page(1)
        except EmptyPage:
            number = paginator.page(paginator.num_pages)
        c = paginator.page(number)
        context = {'p': c, 'e': e, 'mensaje': 'No se puede eliminar este catáolog porque tiene servicios asociados'}
        return TemplateResponse(request, 'users.html', context)

    messages.success(request,  'Catálogo eliminado con éxito', extra_tags='Eliminación de catálogos')
    return HttpResponseRedirect('/catalogo/proyecto/%s' % (id_proyecto))
