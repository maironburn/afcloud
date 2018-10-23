from portal.models import AfProyecto, AfUsuario, AfPerfil, AfTipoPerfil
from afcloud.settings import MEDIA_ROOT
from portal.Kubernetes.Kuber import Kuber
from portal.Utils.logger import *
import datetime,os
import yaml 

def get_extra_content(request):

    id_proyecto_seleccionado=False
    proyecto_seleccionado=request.session.get('proyecto_seleccionado', False)
    perfil=request.session.get('perfil', False)
    numeric_profile=request.session.get('numeric_profile', False)
    proyectos=request.session.get('proyectos',False)

    afcloud_admin=request.session.get('afcloud_admin', False)

    context={'proyecto_seleccionado':proyecto_seleccionado,
             'perfil': perfil , 'numeric_profile': numeric_profile,
             'proyectos': proyectos, 'afcloud_admin': afcloud_admin,
             'id_proyecto_seleccionado': id_proyecto_seleccionado
             }

    return context


def getPerfilProyecto(id_proyecto, usuario):

    af_usuario=AfUsuario.objects.get(user=usuario)
    if af_usuario.usu_administrador:
        return 'Gestor'
    proyecto= AfProyecto.objects.get(id=id_proyecto)
    perfil=AfPerfil.objects.get(usu=af_usuario,pro=proyecto)
    tpe=AfTipoPerfil.objects.get(id=perfil.tpe_id)

    return tpe.tpe_nombre


def getProyectos(usuario, solo_activos=True):

    col=[]
    af_usuario=AfUsuario.objects.get(user=usuario)
    if af_usuario.usu_administrador:
        proyectos=AfProyecto.objects.filter(pro_activo=solo_activos)
        col=[ { p.pro_nombre: p.id } for p in proyectos ]
    else:
        perfiles=AfPerfil.objects.filter(usu=af_usuario,pro__pro_activo=solo_activos)
        col=[ { p.pro.pro_nombre: p.pro.id } for p in perfiles ]

    return {'proyectos': col, 'afcloud_admin' : af_usuario.usu_administrador}

def setSessionVars(request, id_proyecto):

    usuario= request.user
    tipo_perfil=getPerfilProyecto(id_proyecto,usuario)
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


    return context
'''
def seccionActivaRedirect(request,id):

    region_activa=request.session.get('seccion_activa',False)
    method_redirect={'despliegues': desplieguesIndex}
    if region_activa:
        return method_redirect[region_activa](request,id)
'''


'''
Recibe un fichero de configuracion del entorno, Master de Kubernates
'''

def handle_uploaded_file(f, dest=MEDIA_ROOT):

    filename=f.name
    if os.path.exists(dest + f.name):
        now = datetime.datetime.now()
        filename+=now.isoformat()
    with open(dest + filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return filename


def getKubernetesEnv(config_file):

    try:
        fichero_config=handle_uploaded_file(config_file)
        kuber=Kuber( (MEDIA_ROOT+ '%s') %(fichero_config))

        return kuber

    except Exception as e:
        print ()

    return False
