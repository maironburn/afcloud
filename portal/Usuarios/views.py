# Create your views here.
# coding=utf-8

from django import forms
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
from portal.models import AfProyecto,AfUsuario, AfPerfil,AfTipoPerfil, AfGlobalconf, AfUserNotify,\
    AfEntorno
from django.contrib.auth.models import User
from portal.Usuarios.forms import *
#####
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.http import HttpResponseRedirect, QueryDict, HttpResponse
from django.shortcuts import render
from keyring.core import set_password
from django.db import IntegrityError
from collections import defaultdict
from portal.Integrantes.views import integrantesIndex
from portal.Catalogo.views import catalogosIndex
from portal.Despliegues.views import desplieguesIndex
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.signals import user_logged_in, user_logged_out 
from django.dispatch import receiver 


@login_required
@group_required('af_cloud_admin',)
def users(request, template_name='users.html', extra_context=None):
    usuarios = AfUsuario.objects.all()
    return TemplateResponse(request, template_name, context={'usuarios': usuarios})


@login_required
@group_required('af_cloud_admin',)
def userChangePass(request, id, template_name='cambiar_passwd.html', extra_context=None):

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


@receiver(user_logged_out) 
def _user_logged_out(sender, user, request, **kwargs):
    
    afuser=AfUsuario.objects.get(user=user)
    afuser.last_login=datetime.datetime.now()
    afuser.save()
    
    request.session['proyecto_seleccionado'] = False
    request.session['perfil'] = False
    request.session['numeric_profile'] = False
    request.session['proyectos'] = False
    request.session['afcloud_admin'] = False
    request.session['proyecto_seleccionado'] = False
    request.session['id_proyecto_seleccionado']=False
    

@login_required
def index(request, template_name='index.html', extra_context=None):


    usuario=request.user
    col=getProyectos(usuario,True)
    if not len(col['proyectos']):
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False
    
    
    current_projects= AfProyecto.objects.filter(pro_activo=True).values_list('id', flat=True)
    conf_global= AfGlobalconf.objects.first()
    afuser=AfUsuario.objects.get(user=usuario)

    notificaciones_pendientes=hasNotificationPending(request)
    
    if afuser.usu_administrador and (not conf_global or not conf_global.is_done):
        messages.success(request, "La configuración global del portal aun no ha sido realizada, " \
                                  "las opciones de administación de proyectos y servicios no estarán disponibles ")
    if  conf_global:
        globalconf_isdone=conf_global.is_done
    else:
        globalconf_isdone=False
    
    
    kwargs_startpage={'afuser': afuser , 'proyectos': current_projects, 'notificaciones': notificaciones_pendientes}
    #notificaciones_no_leidas= AfUserNotify.objects.filter(to_user=afuser, readed=False)
    global_info=getStartPage_info(**kwargs_startpage)
    context =   { 'proyectos'                : col['proyectos'],
                  'afcloud_admin'            : col['afcloud_admin'],
                  'globalconf_isdone'        : globalconf_isdone,
                  #'notificaciones_no_leidas' : notificaciones_no_leidas
                  'global_info': global_info
                  }

    request.session['globalconf_isdone']= globalconf_isdone
    request.session['proyectos']     = col['proyectos']

    #p_seleccionado= request.session.get('id_proyecto_seleccionado', False)
    p_seleccionado= False
    if p_seleccionado and int(p_seleccionado) not in current_projects:
        request.session['proyecto_seleccionado'] = False

    #request.session['notificaciones_no_leidas'] = True if notificaciones_no_leidas.count() else False
    request.session['afcloud_admin'] = col['afcloud_admin']


    
    return TemplateResponse(request, template_name, context)


def getStartPage_info(**kwargs):
    
    afuser=kwargs.get('afuser')
    proyectos=kwargs.get('proyectos')
    proyectos_lst=[]
    perfil_lst=[]
    
    env_lst=[]
    for p in proyectos:
        pro=AfProyecto.objects.get(id=p)
        proyectos_lst.append({'id': pro.id, 'nombre': pro.pro_nombre})
    
    user_info= {'usuario': afuser.user.username,
                 'nombre': afuser.user.first_name, 
                 'apellidos': afuser.user.last_name, 
                 'last_login': afuser.last_login,
                 'mail': afuser.user.email ,
                 'admin' : afuser.usu_administrador
                 }
    entornos= AfEntorno.objects.all()
    
    for e in entornos:
        env_lst.append({'ent_nombre': e.ent_nombre, 'ip': e.cluster_ip})
        
    roles= AfPerfil.objects.filter(usu=afuser)
    
    for r in roles:
        perfil_lst.append({'proyecto': r.pro.pro_nombre, 'perfil': r.tpe.tpe_nombre})
        
    info={'proyectos': proyectos_lst, 'entornos': env_lst, 'usuario_nfo': user_info, 'roles': roles}
    
    return info

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
    check_id_proyect= []
    current_projects= AfProyecto.objects.filter(pro_activo=True).values_list('id', flat=True)

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

    name = request.GET.get('p') if request.GET.get('p') else ''

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

    name = request.GET.get('p') if request.GET.get('p') else ''
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

    try:
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
            else:
                return render(request, template_name, {'form': form})
        else:
            form =userEditProfileForm(request.POST or None, instance=afuser.user)
            return TemplateResponse(request, template_name, context={'usuarios': afuser,'form': form, 'visualized_card': True})

    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False
        messages.error(request, "El proyecto solicitado a eliminar no existe")
        pass
        
    except Exception as ex:
        messages.error(request, "Uhmmm... %s"  % (format(ex)))
        pass        
    
    return HttpResponseRedirect('/startpage')

@login_required
@group_required('af_cloud_admin',)
def editAFUser(request, id, template_name='editUser.html'):

    try:
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

    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False        
        messages.error(request, "El usuario solicitado a editar no existe")
        pass
        
    except Exception as ex:
        messages.error(request, "Uhmmm... %s"  % (format(ex)))
        pass        
    
    return HttpResponseRedirect('/administrar/usuarios')

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

    try:
        afuser=AfUsuario.objects.get(id=id)
        if request.user==afuser.user:
            messages.error(request, 'No puede eliminarse así mismo !! ', extra_tags='Eliminación de usuarios')
        else:

            id_user=afuser.user.id
            user=User.objects.get(id=id_user)
            user.delete()

    
    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False
        messages.error(request, "El usuario solicitado a eliminar no existe")
        pass

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
