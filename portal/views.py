# Create your views here.
# coding=utf-8

from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.response import TemplateResponse
from portal.models import AfServicio,AfProyecto
from django.contrib.auth.models import User

#from virtualSpaces.Portal.forms import DespliegueForm, CentroForm, ServidorForm


from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView
)


'''

@login_required
@staff_member_required(login_url='/')
@never_cache
def servicios(request, template_name='ServiciosIndex.html', extra_context=None):
    try:
        name = request.GET['p']
    except:
        name = ''
    if name == '':
        servicios = AfServicio.objects.all().order_by('-Fecha_alta')
        e = 'no'
    else:
        servicios = AfServicio.objects.filter(Nombre__icontains=name)
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
@staff_member_required(login_url='/')
def nuevadespliegue(request, template_name='Despliegue.html', extra_context=None):
    value = 'nuevo'
    if request.method == "POST":
        form = DespliegueForm(request.POST or None)
        if form.is_valid():
            despliegue = form.save(commit=False)
            despliegue.save()
            return redirect('/Despliegues/')
        else:
            return render(request, template_name, {'form': form, 'value': value})
            # return HttpResponseRedirect('DesplieguesIndex.html')
    else:
        form = DespliegueForm()
        # context = {'form': form}
        return render(request, template_name, {'form': form, 'value': value})
        # return render_to_response(template_name)


@login_required
@staff_member_required(login_url='/')
def editdespliegue(request, id, template_name='Despliegue.html'):
    value = 'ver'
    despliegue = Despliegue.objects.get(id=id)
    form = DespliegueForm(request.POST or None, instance=despliegue)
    # if request.method == "POST":
    #     form = despliegueForm(request.POST, instance=despliegue)
    if request.method == "POST":
        if form.is_valid():
            despliegue.save()
            # return render(request, template_name, {'form': form})
            return HttpResponseRedirect('/Despliegues/')
    return render(request, template_name, {'form': form, 'value': value, 'id': id})


@login_required
@staff_member_required(login_url='/')
def deletedespliegue(request, id):
    p = Despliegue.objects.all().order_by('-Fecha_alta')
    paginator = Paginator(p, 10)
    try:
        number = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        number = paginator.page(1)
    except EmptyPage:
        number = paginator.page(paginator.num_pages)
    c = paginator.page(number)
    try:
        despliegue = Despliegue.objects.get(id=id)
        centro = Centro.objects.get(id=despliegue.Codigo_centro_id)
        url2 = 'http://k-master/api/v1/namespaces/default/replicationcontrollers'
        d2 = json.load(urlopen(url2))
        items2 = d2['items']
        data = []
        desplegada = False
        for i in items2:
            metadata = i['metadata']
            name = metadata['name']
            data.append(name)
            # if name == "moodle-rc-" + centro.Codigo.encode('utf8', 'ignore'):
            if despliegue.Estado_despliegue_id_id == 1:
                desplegada = True
                mensaje = 'No se puede eliminar un despliegue activo, primero tiene que ser replegado'
                return render(request, 'DesplieguesIndex.html', {'p': c, 'e': 'no', 'mensaje': mensaje})
        # if request.method == "POST":
        if not desplegada and (despliegue.Estado_despliegue_id_id == 4 or despliegue.Estado_despliegue_id_id == 3):
            centro = Centro.objects.get(id=despliegue.Codigo_centro_id)
            # Delete DB of the moodle
            db = MySQLdb.connect(host="k-mysql", user="root", passwd="1s0tr0l2016")
            cursor = db.cursor()
            dbName = ""
            if despliegue.Catalogo_id_id == 1:
                dbName = "moodle" + centro.Codigo.encode('utf-8', 'ignore')
            else:
                dbName = "wp" + centro.Codigo.encode('utf-8', 'ignore')
            query = ("DROP DATABASE IF EXISTS " + dbName)
            cursor.execute(query)
            cursor.close()
            db.close()
            # Delete despliegue form Kportal
            despliegue.delete()
            return HttpResponseRedirect('/Despliegues/')
        else:
            mensaje = 'Para poder borrar un despliegue tiene que estar inactivo'
            return render(request, 'DesplieguesIndex.html', {'p': c, 'e': 'no', 'mensaje': mensaje})
            # return render(request, template_name, {'tipo': tipo, 'object': despliegue, 'del': delete})
    except:
        mensaje = 'No se puede borrar actualmente, pruebelo de nuevo mas tarde'
        return render(request, 'DesplieguesIndex.html', {'p': c, 'e': 'no', 'mensaje': mensaje})


@login_required
@staff_member_required(login_url='/')
def Servidores(request, template_name='ServidoresIndex.html', extra_context=None):
    try:
        name = request.GET['p']
    except:
        name = ''
    if name == '':
        servidores = Servidor.objects.all().order_by('-Fecha_alta')
        e = 'no'
    else:
        servidores = Servidor.objects.filter(Nombre__icontains=name)
        e = 'si'

    paginator = Paginator(servidores, 10)
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
@staff_member_required(login_url='/')
def nuevoServidor(request, template_name='Servidor.html', extra_context=None):
    value = 'nuevo'
    if request.method == "POST":
        form = ServidorForm(request.POST or None)
        if form.is_valid():
            Servidor = form.save(commit=False)
            Servidor.save()
            return HttpResponseRedirect('/Servidores')
        else:
            return render(request, template_name, {'form': form, 'value': value})
    else:
        form = ServidorForm()
        return render(request, template_name, {'form': form, 'value': value})

@login_required
@staff_member_required(login_url='/')
def editServidor(request, id, template_name='Servidor.html'):
    value = 'ver'
    servidor = Servidor.objects.get(id=id)
    despliegues = []

    form = ServidorForm(request.POST or None, instance=servidor)
    if request.method == "POST":
        if form.is_valid():
            servidor.save()
            # return render(request, template_name, {'form': form})
            # return HttpResponseRedirect('/Servidores/')
    url = 'http://k-master/api/v1/namespaces/default/pods'

    try:
        data = json.load(urllib2.urlopen(url))
    except:
        data = None
    if data is not None:
        items = data['items']
        for i in items:
            spec = i['spec']
            try:
                host = spec['host']
                metadata = i['metadata']
                name = metadata['generateName']
                if host == servidor.Nombre:
                    codigo = name[:(len(name) - 1)]
                    codigo = codigo[len(codigo) - 8: len(codigo)]
                    centro = Centro.objects.filter(Codigo=codigo)[0]
                    despliegue = Despliegue.objects.filter(Codigo_centro=centro.id)[0]
                    despliegues.append(despliegue)
            except:
                host = ''
    return render(request, template_name, {'form': form, 'value': value, 'id': id, 'despliegues': despliegues})


@login_required
@staff_member_required(login_url='/')
def deleteServidor(request, id):
    tipo = 'Servidor'
    servidor = Servidor.objects.get(id=id)
    # if request.method == "POST":
    try:
        servidor.delete()
    except:
        servidores = Servidor.objects.all().order_by('-Fecha_alta')
        e = 'no'
        paginator = Paginator(servidores, 10)
        try:
            number = int(request.GET.get('page', '1'))
        except PageNotAnInteger:
            number = paginator.page(1)
        except EmptyPage:
            number = paginator.page(paginator.num_pages)
        c = paginator.page(number)
        context = {'p': c, 'e': e, 'mensaje': 'No se puede eliminar este servidor porque tiene despliegues asociados'}
        return TemplateResponse(request, 'ServidoresIndex.html', context)
    return HttpResponseRedirect('/Servidores/')
# return render(request, template_name, {'tipo': tipo, 'object': servidor})


@login_required
@staff_member_required(login_url='/')
def Centros(request, template_name='CentroIndex.html', extra_context=None):
    try:
        name = request.GET['p']
    except:
        name = ''
    if name == '':
        centros = Centro.objects.all().order_by('Nombre')
        e = 'no'
    else:
        centros = Centro.objects.filter(Nombre__icontains=name)
        e = 'si'
    paginator = Paginator(centros, 10)
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
@staff_member_required(login_url='/')
def nuevoCentro(request, template_name='Centro.html', extra_context=None):
    if request.method == "POST":
        form = CentroForm(request.POST or None)
        if form.is_valid():
            centro = form.save(commit=False)
            centro.save()
            return HttpResponseRedirect('/Centros/')
        else:
            return render(request, template_name, {'form': form})
    else:
        form = CentroForm()
        return render(request, template_name, {'form': form})


@login_required
@staff_member_required
def editCentro(request, id, template_name='Centro.html'):
    value = 'edit'
    centro = Centro.objects.get(id=id)
    form = CentroForm(request.POST or None, instance=centro)
    if request.method == "POST":
        if form.is_valid():
            centro.save()
            # return render(request, template_name, {'form': form})
            return HttpResponseRedirect('/Centros/')
    return render(request, template_name, {'form': form, 'value': value, 'id': id, 'Nombre': centro.Nombre})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def deleteCentro(request, id):
    # tipo = 'Centro'
    centro = Centro.objects.get(id=id)
    # if request.method == "POST":
    p = Despliegue.objects.filter(Codigo_centro_id=centro.id)
    if not Despliegue.objects.filter(Codigo_centro_id=id):
        centro.delete()
        return HttpResponseRedirect('/Centros/')
    else:
        centros = Centro.objects.all().order_by('Nombre')
        paginator = Paginator(centros, 10)
        try:
            number = int(request.GET.get('page', '1'))
        except PageNotAnInteger:
            number = paginator.page(1)
        except EmptyPage:
            number = paginator.page(paginator.num_pages)
        c = paginator.page(number)
        context = {'p': c, 'e': 'no', 'mensaje': 'No se puede borrar un centro que tiene un despliegue asociado'}
        return render(request, 'CentroIndex.html', context)
        # return render(request,template_name, {'tipo': tipo, 'object': centro})
        # return HttpResponse(request)

'''
'''
@login_required
def vistaCatalogo(request, template_name='Catalogo.html', extra_content=None):
    # catalogo = Catalogo.objects.all()
    catalogoM = Catalogo.objects.get(id=1)
    catalogoW = Catalogo.objects.get(id=2)
    verM = Version.objects.filter(Catalogo_id_id=1)
    verW = Version.objects.filter(Catalogo_id_id=2)
    context = {'infoM': catalogoM.informacion, 'infoW': catalogoW.informacion, 'verM': verM, 'verW': verW}
    return render(request, template_name, context)


@login_required
@staff_member_required(login_url='/')
def desplieguesOrden(request, orden, ascendente, template_name='DesplieguesIndex.html', extra_content=None):
    try:
        name = request.GET['p']
    except:
        name = ''
    ordenar = ''
    if int(ascendente) == 0:
        ordenar = '-'
    if int(orden) == 1:
        ordenar += 'Fecha_alta'
    else:
        if int(orden) == 2:
            ordenar += 'Nombre'
        else:
            if int(orden) == 3:
                ordenar += 'Estado_despliegue_id'
            else:
                if int(orden) == 4:
                    ordenar += 'Catalogo_id'

    if name == '':
        despliegues = Despliegue.objects.all().order_by(ordenar)
        e = 'no'
    else:
        despliegues = Despliegue.objects.filter(Nombre__icontains=name)
        e = 'si'

    paginator = Paginator(despliegues, 10)
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
@staff_member_required(login_url='/')
def centrosOrdenados(request, orden, ascendente, template_name='CentroIndex.html', extra_content=None):
    try:
        name = request.GET['p']
    except:
        name = ''
    ordenar = ''
    if int(ascendente) == 0:
        ordenar = '-'
    if int(orden) == 1:
        ordenar += 'Nombre'
    else:
        if int(orden) == 2:
            ordenar += 'Codigo'
        else:
            if int(orden) == 3:
                ordenar += 'Provincia_id'
            else:
                if int(orden) == 4:
                    ordenar += 'Ubicacion'

    if name == '':
        centros = Centro.objects.all().order_by(ordenar)
        e = 'no'
    else:
        centros = Centro.objects.filter(Nombre__icontains=name)
        e = 'si'

    paginator = Paginator(centros, 10)
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
@staff_member_required(login_url='/')
def servidoresOrdenados(request, orden, ascendente, template_name='ServidoresIndex.html', extra_content=None):
    try:
        name = request.GET['p']
    except:
        name = ''
    ordenar = ''
    if int(ascendente) == 0:
        ordenar = '-'
    if int(orden) == 1:
        ordenar += 'Nombre'
    else:
        if int(orden) == 2:
            ordenar += 'Tipo_servidor_id'
        else:
            if int(orden) == 3:
                ordenar += 'Fecha_alta'
            else:
                if int(orden) == 4:
                    ordenar += 'Estado_servidor_id'

    if name == '':
        servidores = Servidor.objects.all().order_by(ordenar)
        e = 'no'
    else:
        servidores = Servidor.objects.filter(Nombre__icontains=name)
        e = 'si'

    paginator = Paginator(servidores, 10)
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
@staff_member_required(login_url='/')
def desplieguesFiltroCatalogo(request, filtro, template_name='DesplieguesIndex.html', extra_context=None):
    try:
        name = request.GET['p']
    except:
        name = ''
    if name == '':
        catalogo = Catalogo.objects.get(id=filtro)
        despliegues = Despliegue.objects.filter(Catalogo_id_id=catalogo.id).order_by('-Fecha_alta')
        e = 'no'
    else:
        despliegues = Despliegue.objects.filter(Nombre__icontains=name)
        e = 'si'

    paginator = Paginator(despliegues, 10)
    try:
        number = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        number = paginator.page(1)
    except EmptyPage:
        number = paginator.page(paginator.num_pages)
    c = paginator.page(number)
    context = {'p': c, 'e': e, 'filtro': True}
    return TemplateResponse(request, template_name, context)


@login_required
@staff_member_required(login_url='/')
def desplieguesFiltroEstado(request, filtro, template_name='DesplieguesIndex.html', extra_context=None):
    try:
        name = request.GET['p']
    except:
        name = ''
    if name == '':
        estado = Estado_despliegue.objects.get(id=filtro)
        despliegues = Despliegue.objects.filter(Estado_despliegue_id_id=estado.id).order_by('-Fecha_alta')
        e = 'no'
    else:
        despliegues = Despliegue.objects.filter(Nombre__icontains=name)
        e = 'si'

    paginator = Paginator(despliegues, 10)
    try:
        number = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        number = paginator.page(1)
    except EmptyPage:
        number = paginator.page(paginator.num_pages)
    c = paginator.page(number)
    context = {'p': c, 'e': e, 'filtro': True}
    return TemplateResponse(request, template_name, context)


@login_required
@staff_member_required(login_url='/')
def centrosFiltroProvincia(request, filtro, template_name='CentroIndex.html', extra_context=None):
    try:
        name = request.GET['p']
    except:
        name = ''
    if name == '':
        provincia = Provincia.objects.get(id=filtro)
        centros = Centro.objects.filter(Provincia_id_id=provincia.id).order_by('Nombre')
        e = 'no'
    else:
        centros = Centro.objects.filter(Nombre__icontains=name)
        e = 'si'
    paginator = Paginator(centros, 10)
    try:
        number = int(request.GET.get('page', '1'))
    except PageNotAnInteger:
        number = paginator.page(1)
    except EmptyPage:
        number = paginator.page(paginator.num_pages)
    c = paginator.page(number)
    context = {'p': c, 'e': e, 'filtro': True}
    return TemplateResponse(request, template_name, context)


@login_required
@staff_member_required(login_url='/')
def vistadespliegue(request, id, template_name='Despliegue.html'):
    try:
        despliegue = Despliegue.objects.get(id=id)
    except:
        print "no existe"
    return render(request, template_name, {'despliegue': despliegue})
'''