# Create your views here.
# coding=utf-8
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from portal.models import AfEntorno,AfProyecto,AfRelEntPro
from portal.Entornos.forms import EntornoForm
from django.db import IntegrityError
from portal.Utils.decorators import *
from portal.Utils.aux_meth import *
from portal.Utils.logger import *
from django.contrib import messages
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist


logger=getLogger()



def set_bulk_num_proyectos(entornos):
    for e in entornos:
        proyectos=[]
        ent_pro=AfRelEntPro.objects.filter(ent=e)
        num=ent_pro.count()
        e.set_num_proyectos(num)
        for ep in ent_pro:
            proyectos.append(ep.pro.pro_nombre)
        e.proyectos_list=proyectos
        e.proyectos_list_str=e.get_proyectos_str()


@login_required
@group_required('af_cloud_admin',)
def administrarEntornos(request, template_name='entornosIndex.html', extra_context=None):
    try:
        # para las busquedas
        name = request.GET['p']
    except:
        name = ''

    if name == '':
        entornos = AfEntorno.objects.filter(ent_deleted=False).order_by('ent_nombre')
        e = 'no'
    else:
        entornos = AfEntorno.objects.filter(ent_nombre__icontains=name,ent_deleted=False)
        e = 'si'

    set_bulk_num_proyectos(entornos)
    hasNotificationPending(request)
    paginator = Paginator(entornos, 10)
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
def administrarEntornosOrdered(request, orden, ascendente, template_name='entornosIndex.html', extra_content=None):

    name = request.GET.get('p') if request.GET.get('p') else ''

    ordenar = ''
    e = 'no' # parametro q actua como flag indicando q se ha realizado una busqueda

    if int(ascendente) == 0:
        ordenar = '-'

    reverse = False
    campo={1:'ent_nombre', 2: 'ent_uri', 3: 'ent_username', 4: 'ent_activo' }

    entornos=  AfEntorno.objects.filter(ent_deleted=False)

    if int(ascendente) == 0:
            ordenar = '-'
            reverse=True

    if name=='':

        if int(orden):

            if int(orden)!=3:
                ordenar+=campo[int(orden)]
                ent = entornos.order_by(ordenar)
                set_bulk_num_proyectos(ent)

            else:
                set_bulk_num_proyectos(entornos)
                ent=sorted(entornos, key=lambda e: e.num_proyectos, reverse=reverse)

    else:
            ent= entornos.filter(ent_nombre__icontains=name)
            e = 'si'
            set_bulk_num_proyectos(ent)

    paginator = Paginator(ent, 10)
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
def nuevoEntorno(request,template_name='newEntorno.html'):

    value = 'nuevo'
    kuber = None

    logger.debug("*AFCLOUD*: %s, Meth: %s, urlConf: %s" % (__name__, request.method, request.path))

    if request.method == "POST" and request.FILES:
        form = EntornoForm(request.POST, request.FILES)
        fichero_config=handle_uploaded_file(request.FILES['ent_config_file'])
        fichero_json_registry= handle_uploaded_file(request.FILES['ent_json_file'])
        rook_ip= None

        try:
            kuber=Kuber( (MEDIA_ROOT+ '%s') %(fichero_config))
            client=kuber.getClient()
            rook_ip= kuber.get_rook_nfs_ip()
            form.setConOkStatus()
            
            
        except Exception as e:
            logger.error(" %s , Fichero de entorno K8s no valido %s" % (__name__,fichero_config))

        if form.is_valid():

                
            entorno = form.save(commit=False)
            cluster_ip= kuber.getClusterIP()
            if cluster_ip:
                entorno.cluster_ip =cluster_ip
                
            entorno.setConfigfile  ((MEDIA_ROOT+ '%s') %(fichero_config))
            entorno.setRegistryfile((MEDIA_ROOT+ '%s') %(fichero_json_registry))

            local_file = open((MEDIA_ROOT+ '%s') %(fichero_config))
            djangofile= File(local_file)

            entorno.ent_config_file.save(fichero_config,djangofile )
            entorno.registry_hash = entorno.getRegistryHash ((MEDIA_ROOT+ '%s') %(fichero_json_registry))
            entorno.nfs_server = rook_ip
            entorno.save()
            local_file.close()

            messages.success(request,  'Entorno creado con éxito', extra_tags='Creación de entornos')
            return HttpResponseRedirect('/administrar/entornos')
        else:
            messages.error(request,  'Fichero config k8s no válido', extra_tags='fichero_config')
            return render(request, template_name, {'form': form, 'value': value, 'visualized_card': True})
    else:
        form = EntornoForm()
        return render(request, template_name, {'form': form, 'value': value, 'visualized_card': True})




@login_required
@group_required('af_cloud_admin',)
def editarEntorno(request, id,template_name='editarEntorno.html'):

    try:
        value = 'editar'
        entorno= AfEntorno.objects.get(id=id)
        form = EntornoForm(request.POST or None, instance=entorno)

    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False        
        messages.error(request, "El entorno solicitado para edición no existe")
        return TemplateResponse(request, template_name, None)
        #return render(request, template_name, {'form': form, 'value': value,'id': id})

    if request.method == 'POST':
        if form.is_valid():
            entorno.save()
            messages.success(request,  'Entorno editado con éxito', extra_tags='Edición de entornos')
            return HttpResponseRedirect('/administrar/entornos')

    return render(request, template_name, {'form': form, 'value': value,'id': id, 'visualized_card': True})

@login_required
@group_required('af_cloud_admin',)
def borrarEntorno(request, id):

    try:
        entorno= AfEntorno.objects.get(id=id)
        entorno.ent_deleted=True
        entorno.save()
        #entorno.delete()
    except ObjectDoesNotExist as dne:
        request.session['proyecto_seleccionado']    = False
        request.session['id_proyecto_seleccionado'] = False        
        messages.error(request, "El entorno a eliminar solicitado no existe")
        return HttpResponseRedirect('/administrar/entornos')

        '''borrar el fichero de configuracion del entorno '''
    except IntegrityError:
        entornos = AfEntorno.objects.all()
        set_bulk_num_proyectos(entornos)
        e = 'no'
        paginator = Paginator(entornos, 10)
        try:
            number = int(request.GET.get('page', '1'))
        except PageNotAnInteger:
            number = paginator.page(1)
        except EmptyPage:
            number = paginator.page(paginator.num_pages)
        c = paginator.page(number)
        context = {'p': c, 'e': e, 'mensaje': 'No se puede eliminar este entorno porque tiene despliegues asociados'}
        return TemplateResponse(request, 'entornosIndex.html', context)

    messages.success(request,  'Entorno borrado con éxito', extra_tags='Borrado de entornos')
    return HttpResponseRedirect('/administrar/entornos')
