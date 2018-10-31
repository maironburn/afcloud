# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfProyecto, AfUsuario,\
    AfTipoPerfil, AfPerfil, User

from django.db import IntegrityError
from portal.Integrantes.forms import IntegrantesRawForm
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from django.contrib import messages
 

@login_required
def seccionActivaRedirect(request,id):

    region_activa=request.session.get('seccion_activa',False)
    method_redirect={'integrantes': integrantesIndex}
    if region_activa:
        return method_redirect[region_activa](request,id)


@login_required
def getIntegrantesProyecto(request,id_proyecto):

    name = ''
    integrantes={}
    usu_integrantes=[]
    proyecto=AfProyecto.objects.get(id=id_proyecto)
    af_perfil=AfPerfil.objects.filter(pro=proyecto)
    if len(af_perfil):
        for afp in af_perfil:
            integrantes.update({afp.usu : afp.tpe.tpe_nombre })
            usu_integrantes.append(afp.usu)

    return integrantes, usu_integrantes


@login_required
@group_required('Gestor',)
def index(request, template_name='integrantesIndex.html', extra_context=None):


    context=get_extra_content(request)
    request.session['seccion_activa'] = 'integrantes'

    if len(context['proyectos']):
        id_proyecto_seleccionado=request.session.get('id_proyecto_seleccionado', False)
        if id_proyecto_seleccionado:
            return integrantesIndex(request,id_proyecto_seleccionado,extra_context= context)


    return TemplateResponse(request, template_name, context)


def get_integrante_by_filtered_username(name, usu_integrantes, integrantes):

    filtrado={}
    usu_integrantes= [x for x in usu_integrantes if name in x.user.username ]
    for i in usu_integrantes:
        for k,v in integrantes.items():
            if i == k:
                filtrado.update({k:v})
        integrantes=filtrado
        e = 'si'

    return integrantes

@login_required
@group_required('Gestor',)
def  integrantesIndex(request, id_proyecto, template_name='integrantesIndex.html', extra_context=None):
    try:
        # para las busquedas
        name = request.GET['p']
        e=''
    except:
        name = ''

    if extra_context is None:
        extra_context=get_extra_content(request)


    integrantes,usu_integrantes = getIntegrantesProyecto (request,id_proyecto)
    if name == '':
        usu_integrantes = sorted(usu_integrantes, key=lambda p: p.user.username, reverse=False)
        e = 'no'
    else:

        integrantes=get_integrante_by_filtered_username(name,usu_integrantes,integrantes )


    paginator = Paginator(usu_integrantes, 10)
    try:
        number = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        number = paginator.page(1)
    except EmptyPage:
        number = paginator.page(paginator.num_pages)
    c = paginator.page(number)
    context = {'p': c, 'e': e, 'integrantes': integrantes}

    if extra_context:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)



@login_required
@group_required('Gestor',)
def integrantesIndexOrdered(request,id_proyecto, orden, ascendente, template_name='integrantesIndexOrdered.html', extra_context=None):
    try:

        e = 'no'
        if extra_context is None:
            extra_context=get_extra_content(request)

        name = request.GET['p']
    except:
        name = ''

    ordenar  = ''
    integrantes,usu_integrantes = getIntegrantesProyecto (request,id_proyecto)
    reverse=False
    filtrado=[]

    if int(ascendente) == 0:
        ordenar = '-'
        reverse=True

    campo={1: sorted(usu_integrantes, key=lambda p: p.user.username, reverse=reverse),
           2: sorted(usu_integrantes, key=lambda p: p.usu_administrador, reverse=reverse),
           3: sorted(usu_integrantes, key=lambda p: '%s %s' % (p.user.first_name,p.user.last_name), reverse=reverse),
           4: sorted(usu_integrantes, key=lambda p: p.usu_administrador, reverse=reverse),
           5: sorted(usu_integrantes, key=lambda p: p.user.is_active, reverse=reverse)}

    if name == '':

        if int(orden) and int(orden)!=4:

            usu_integrantes= campo[int(orden)]
            for i in usu_integrantes:
                filtrado.append({i:integrantes[i]})
            integrantes=filtrado
            e = 'si'

        if int(orden)==4:
            #usu_integrantes=sorted(integrantes.items(), key=lambda(k,v): v[1], reverse=reverse)
            pass
    else:
        #usuarios = AfUsuario.objects.filter(usu_nombre__icontains=name)
        integrantes=get_integrante_by_filtered_username(name,usu_integrantes,integrantes )
        e = 'si'

    paginator = Paginator(usu_integrantes, 10)
    try:
        number = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        number = paginator.page(1)
    except EmptyPage:
        number = paginator.page(paginator.num_pages)
    c = paginator.page(number)
    context = {'p': c, 'e': e, 'integrantes': integrantes}

    return TemplateResponse(request, template_name, context)



@login_required
@group_required('Gestor',)
def nuevoIntegrante(request,id_proyecto, template_name='newIntegrante.html'):
    from portal.Integrantes.forms import IntegrantesRawForm
    value = 'nuevo'

    integrantes_perfil, usu_integrantes= getIntegrantesProyecto (request,id_proyecto)

    if request.method == "POST":
        user_id=int(request.POST.get('user', None))
        user_instance=AfUsuario.objects.get(id=user_id)
        perfil_id =int(request.POST.get('perfil', None))

        tperfil_instance=AfTipoPerfil.objects.get(id=perfil_id)
        proyecto=AfProyecto.objects.get(id=id_proyecto)
        data={'user' : user_instance,'tperfil' :tperfil_instance}
        form = IntegrantesRawForm(initial=data)

        if form.is_valid():

            af_perfil=AfPerfil.objects.create(usu=user_instance, pro=proyecto,tpe=tperfil_instance,per_activo=True)
            af_perfil.save()
            messages.success(request,  'Integrante añadido con éxito', extra_tags='Adición de integrantes')
            return HttpResponseRedirect('/integrantes/proyecto/%s' % (proyecto.id))
        else:
            return render(request, template_name, {'form': form, 'value': value})
    else:
        nombre_proyecto= request.session.get('proyecto_seleccionado', False)
        data={'user_queryset': AfUsuario.objects.exclude(id__in=[x.id for  x in usu_integrantes])}
        form = IntegrantesRawForm(initial=data)
        return render(request, template_name, {'form': form, 'value': value, 'nombre_proyecto': nombre_proyecto})

@login_required
@group_required('Gestor',)
def editarIntegrante(request,id_proyecto, id_integrante,template_name='editarIntegrante.html'):
    from portal.Integrantes.forms import IntegrantesRawForm
    value = 'editar'

    user_instance=AfUsuario.objects.get(user__id=id_integrante)
    proyecto=AfProyecto.objects.get(id=id_proyecto)
    perfil_instance= AfPerfil.objects.get(usu=user_instance,pro=proyecto)
    tperfil=perfil_instance.tpe

    data={'user' : user_instance,'tperfil' :tperfil}
    form = IntegrantesRawForm(initial=data)
        
    if request.method == 'POST':
        if form.is_valid():
            tperfil=request.POST.get('perfil', False)
            obj_perfil=AfTipoPerfil.objects.get(id=tperfil)
            perfil_instance.delete()
            form.save(user_instance,obj_perfil,proyecto)
            messages.success(request,  'Integrante editado con éxito', extra_tags='Edición de integrantes')
            return HttpResponseRedirect('/integrantes/proyecto/%s' % (proyecto.id))

    return render(request, template_name, {'form': form, 'value': value,'id': proyecto.id, 'nombre_proyecto': proyecto.pro_nombre, 'nombre_integrante': user_instance.user.username})

@login_required
@group_required('Gestor',)
def eliminarIntegrante(request, id_proyecto, id_integrante):

    user=User.objects.get(id=id_integrante)
    afuser=AfUsuario.objects.get(user=user)
    proyecto=AfProyecto.objects.get(id=id_proyecto)
    perfil_instance= AfPerfil.objects.get(usu=afuser,pro=proyecto)
    try:
        perfil_instance.delete()

    except IntegrityError as ie:
        e = 'no'
        afusers=AfUsuario.objects.all()
        paginator = Paginator(afusers, 10)
        try:
            number = int(request.GET.get('page', '1'))
        except PageNotAnInteger:
            number = paginator.page(1)
        except EmptyPage:
            number = paginator.page(paginator.num_pages)
        c = paginator.page(number)
        context = {'p': c, 'e': e, 'mensaje': 'No se puede eliminar este usuario porque tiene despliegues asociados'}
        return TemplateResponse(request, 'users.html', context)
    
    messages.success(request,  'Integrante editado con éxito', extra_tags='Eliminación de integrantes')
    return HttpResponseRedirect('/integrantes/proyecto/%s' % (proyecto.id))
