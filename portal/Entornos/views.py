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
from portal.Kubernetes.Kuber import KuberConnectionFail

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
        #e.proyectos_list.append()


@login_required
@group_required('af_cloud_admin',)
def administrarEntornos(request, template_name='entornosIndex.html', extra_context=None):
    try:
        # para las busquedas
        name = request.GET['p']
    except:
        name = ''
    if name == '':
        entornos = AfEntorno.objects.all().order_by('ent_nombre')
        e = 'no'
    else:
        entornos = AfEntorno.objects.filter(ent_nombre__icontains=name)
        e = 'si'

    set_bulk_num_proyectos(entornos)
    paginator = Paginator(entornos, 10)
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
def administrarEntornosOrdered(request, orden, ascendente, template_name='entornosIndex.html', extra_content=None):
    try:
        name = request.GET['p']
    except:
        name = ''
    ordenar = ''
    e = 'no' # parametro q actua como flag indicando q se ha realizado una busqueda

    if int(ascendente) == 0:
        ordenar = '-'

    reverse = False
    campo={1:'ent_nombre', 2: 'ent_uri', 3: 'ent_username', 4: 'ent_activo' }

    entornos=  AfEntorno.objects.all()

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
    context = {'p': c, 'e': e}
    return TemplateResponse(request, template_name, context)


@login_required
@group_required('af_cloud_admin',)
def nuevoEntorno(request,template_name='newEntorno.html'):

    value = 'nuevo'
    test_env=False
    
    logger.debug("*AFCLOUD*: %s, Meth: %s, urlConf: %s" % (__name__, request.method, request.path))
    
    if request.method == "POST":
        form = EntornoForm(request.POST, request.FILES)
        if len(request.FILES):
            fichero_config=handle_uploaded_file(request.FILES['ent_config_file'])
            try:
                kuber=Kuber( (MEDIA_ROOT+ '%s') %(fichero_config))
                client=kuber.getClient()
                form.setConOkStatus()
            except KuberConnectionFail:
                pass

        if form.is_valid():
            AfEntorno = form.save(commit=False)
            
            AfEntorno.save()
            messages.success(request,  'Entorno creado con éxito', extra_tags='Creación de entornos')
            return HttpResponseRedirect('/administrar/entornos')
        else:
            return render(request, template_name, {'form': form, 'value': value})
    else:
        form = EntornoForm()
        return render(request, template_name, {'form': form, 'value': value})




@login_required
@group_required('af_cloud_admin',)
def editarEntorno(request, id,template_name='editarEntorno.html'):
    value = 'editar'
    entorno= AfEntorno.objects.get(id=id)
    form = EntornoForm(request.POST or None, instance=entorno)
        #v fields=('username','password','first_name','last_name','email','is_staff','is_active')
    if request.method == 'POST':
        if form.is_valid():
            entorno.save()
            messages.success(request,  'Entorno editado con éxito', extra_tags='Edición de entornos')
            return HttpResponseRedirect('/administrar/entornos')

    return render(request, template_name, {'form': form, 'value': value,'id': id})

@login_required
@group_required('af_cloud_admin',)
def borrarEntorno(request, id):

    entorno= AfEntorno.objects.get(id=id)
    # if request.method == "POST":
    try:
        entorno.delete()
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
        #return administrarEntornos(request, template_name='entornosIndex.html', context)
    messages.success(request,  'Entorno borrado con éxito', extra_tags='Borrado de entornos')
    return HttpResponseRedirect('/administrar/entornos')
    #return administrarEntornos(request, template_name='entornosIndex.html')
