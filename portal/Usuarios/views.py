# Create your views here.
# coding=utf-8

from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
from portal.models import AfProyecto,AfUsuario, AfPerfil,AfTipoPerfil, AfGlobalconf
from django.contrib.auth.models import User
from portal.Usuarios.forms import *
#####
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse

from django.http import HttpResponseRedirect, QueryDict, HttpResponse
from django.shortcuts import resolve_url, render_to_response, redirect, render
from keyring.core import set_password
from django.db import IntegrityError
from collections import defaultdict
from portal.Integrantes.views import integrantesIndex
from portal.Catalogo.views import catalogosIndex
from portal.Despliegues.views import desplieguesIndex
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from django.contrib import messages



@login_required
@group_required('af_cloud_admin',)
def users(request, template_name='users.html', extra_context=None):
    usuarios = AfUsuario.objects.all()
    return TemplateResponse(request, template_name, context={'usuarios': usuarios})


@login_required
@group_required('af_cloud_admin',)
def userChangePass(request, id, template_name='cambiar_passwd.html', extra_context=None):
    #usuario = User.objects.get(id=id)
    #afuser  = AfUsuario.objects.get(user=usuario)
    afuser=AfUsuario.objects.get(id=id)
    user=User.objects.get(id=afuser.user.id)

    form = SetPasswordForm(user, request.POST)

    if request.method == "POST":
        if form.is_valid() and form.clean_new_password2():
            form.save(user)
            usuarios = AfUsuario.objects.all().order_by('user__username')

            paginator = Paginator(usuarios, 10)
            try:
                number = int(request.GET.get('page', '1'))
            except PageNotAnInteger:
                number = paginator.page(1)
            except EmptyPage:
                number = paginator.page(paginator.num_pages)
            c = paginator.page(number)
            context = {'p': c, 'mensaje': 'Se ha cambiado la contraseña con éxito'}
            return TemplateResponse(request, 'users.html',context)

    return TemplateResponse(request, template_name, {'form': form, 'id': id, 'usuario': afuser.user.username})


@login_required
def index(request, template_name='index.html', extra_context=None):


    usuario=request.user
    col=getProyectos(usuario)
    conf_global= AfGlobalconf.objects.first()
    afuser=AfUsuario.objects.get(user=usuario)
    if afuser.usu_administrador and not conf_global.is_done:
        messages.success(request, "La configuración global del portal aun no ha sido realizada, " \
                                  "las opciones de administación de proyectos y servicios no estarán disponibles ")
        
    context = {'proyectos': col['proyectos'], 'afcloud_admin': col['afcloud_admin'], 
               'globalconf_isdone': conf_global.is_done}
    request.session['globalconf_isdone']= conf_global.is_done
    request.session['proyectos']     = col['proyectos']
    request.session['afcloud_admin'] = col['afcloud_admin']

    return TemplateResponse(request, template_name, context)



@login_required
def seccionActivaRedirect(request,id):

    region_activa=request.session.get('seccion_activa',False)
    method_redirect={'integrantes': integrantesIndex,
                     'catalogos': catalogosIndex,
                     'despliegues': desplieguesIndex
                     }
    return index(request)

    if region_activa:
        return method_redirect[region_activa](request,id)

@login_required
@group_required(None,'Miembro')
def selected_proyect(request, id_proyecto, template_name='index.html', extra_context=None):


    usuario= request.user
    tipo_perfil=getPerfilProyecto(id_proyecto,usuario )
    col=getProyectos(usuario)
    selected=AfProyecto.objects.get(id=id_proyecto)
    numeric_profile={'Miembro': 1, 'Operador':2, 'Gestor':3 }

    context = {'perfil': tipo_perfil , 'numeric_profile':numeric_profile [tipo_perfil] ,
               'proyectos': col['proyectos'], 'afcloud_admin': col['afcloud_admin'],
               'proyecto_seleccionado': selected.pro_nombre,
               'id_proyecto_seleccionado':id_proyecto}

    request.session['proyecto_seleccionado'] = selected.pro_nombre
    request.session['perfil'] = tipo_perfil
    request.session['numeric_profile'] = numeric_profile [tipo_perfil]
    request.session['proyectos'] = col['proyectos']
    request.session['afcloud_admin'] = col['afcloud_admin']
    request.session['proyecto_seleccionado'] = selected.pro_nombre
    request.session['id_proyecto_seleccionado']=id_proyecto

    template_response=seccionActivaRedirect(request,id)

    if template_response:
        return template_response
    else:
        return TemplateResponse(request, template_name, context)

@login_required
@group_required('af_cloud_admin',)
def admin_users(request, template_name='users.html', extra_context=None):

    try:
        # para las busquedas
        name = request.GET['p']
    except:
        name = ''
    if name == '':

        usuarios = AfUsuario.objects.all().order_by('user__username')
        e = 'no'
    else:

        usuarios =AfUsuario.objects.filter(user__username__icontains=name) | AfUsuario.objects.filter(user__first_name__icontains=name)
        e = 'si'
    paginator = Paginator(usuarios, 10)
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
def administrarUsuariosOrdered(request, orden, ascendente, template_name='users.html', extra_content=None):
    try:
        name = request.GET['p']
    except:
        name = ''
    ordenar = ''
    if int(ascendente) == 0:
        ordenar = '-'
    if int(orden):
        campo={1:'user__username', 2: 'user__first_name', 3: 'user__last_name', 4: 'user__is_active', 5: 'user__email', 6: 'usu_administrador' }
        ordenar+=campo[int(orden)]

    if name == '':
        usuarios = AfUsuario.objects.all().order_by(ordenar)
        e = 'no'
    else:
        usuarios= AfUsuario.objects.filter(user__first_name__icontains=name)
        e = 'si'

    paginator = Paginator(usuarios, 10)
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
@user_or_admin_is_allowed 
def modificarPerfil(request, id, template_name='userEditProfile.html'):
    #userEditProfileForm
    afuser =AfUsuario.objects.get(user__id=id)

    if request.method == "POST":

        form = userEditProfileForm(request.POST or None, instance=afuser.user)
        if form.is_valid():

            password= request.POST.get('password', False)
            user_updated=form.save(commit=False)
            if password:
                user_updated.set_password(password)
            user_updated.save()
            afuser.user=user_updated
            afuser.save()
            messages.success(request,  'Usuario editado con éxito', extra_tags='Edición de usuarios')
            
            return HttpResponseRedirect('/startpage')
            #return index(request,template_name='index.html')
        else:
            return render(request, template_name, {'form': form})
    else:
        form =userEditProfileForm(request.POST or None, instance=afuser.user)
        return TemplateResponse(request, template_name, context={'usuarios': afuser,'form': form})

    
    

@login_required
@group_required('af_cloud_admin',)
def editAFUser(request, id, template_name='editUser.html'):

    afuser =AfUsuario.objects.get(user__id=id)

    if request.method == "POST":

        form = editUserRawForm(request.POST or None, instance=afuser.user)
        if form.is_valid():

            afcloud_admin= True if request.POST.get('usu_administrador')=='on' else False
            password= request.POST.get('password', False)
            user_updated=form.save(commit=False)
            if password:
                user_updated.set_password(password)
            user_updated.save()
            afuser.user=user_updated
            afuser.usu_administrador=afcloud_admin
            afuser.save()
            messages.success(request,  'Usuario editado con éxito', extra_tags='Edición de usuarios')
            
            
            return HttpResponseRedirect('/administrar/usuarios')
        else:
            return render(request, template_name, {'form': form})
    else:
        form =editUserRawForm(request.POST or None, instance=afuser.user)
        return TemplateResponse(request, template_name, context={'usuarios': afuser,'form': form})

@login_required
@group_required('af_cloud_admin',)
def nuevoUsuario(request, template_name='newUser.html'):
    value = 'nuevo'

    if request.method == "POST":
        form = UserRawForm(request.POST or None)
    
        if form.is_valid():

            password  = form.cleaned_data['password']
            user_created=form.save(commit=True)
            user_created.set_password(password)
            user_created.save()
            #user_created.password=set_password(request.POST.get('password'))
            afcloud_admin= True if request.POST.get('usu_administrador')=='on' else False
            afusuario = AfUsuario(user=user_created, usu_administrador=afcloud_admin)
            afusuario.save()
            messages.success(request,  'Usuario creado con éxito', extra_tags='Creación de usuarios')
            return HttpResponseRedirect('/administrar/usuarios')
        else:
            return render(request, template_name, {'form': form, 'value': value})
    else:

        form = UserRawForm()
        return render(request, template_name, {'form': form, 'value': value})


@login_required
@group_required('af_cloud_admin',)
def deleteAFUser(request, id):

    afuser=AfUsuario.objects.get(id=id)

    try:
        if request.user==afuser.user:
            messages.error(request, 'No puede eliminarse así mismo !! ', extra_tags='Eliminación de usuarios')
        else:
            
            id_user=afuser.user.id
            user=User.objects.get(id=id_user)
            user.delete()


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

    messages.success(request,  'Usuario borrado con éxito', extra_tags='Eliminación de usuarios')
    return HttpResponseRedirect('/administrar/usuarios')
