from portal.models import AfProyecto, AfUsuario, AfPerfil, AfTipoPerfil,AfRelEntPro,AfInstancia,AfGlobalconf,AfUserNotify
from afcloud.settings import MEDIA_ROOT,KUBER_TEMPLATES
from portal.Kubernetes.Kuber import Kuber
from portal.Utils.logger import *
import datetime,os
import yaml , base64
import requests
import json
import urllib.request
from urllib.parse import unquote
import requests


def getPrometheusAvailability(**kwargs):

    try:
        ip_env        = kwargs.get ('ip_env')
        app_name      = kwargs.get ('app_name')
        r_from        = kwargs.get ('r_from')
        r_to          = kwargs.get ('r_to')
        namespace     = kwargs.get ('namespace')
        # prometheus tiene un limite de 11000 puntos arrojados en una consulta
        timedelta_interval= r_to- r_from
        timedelta_interval_d=timedelta_interval/86400
        step=20
        
        if timedelta_interval_d>2:
            timedelta_interval=int(timedelta_interval/10500)
        

        url= ('http://' + ip_env + ':30090/api/v1/query_range?query=avg(kube_pod_container_status_running%7Bnamespace%3D~%22' + 
              namespace + '%22%2C%20%7D)&start=' + str(int(r_from)) + '&end=' + str(int(r_to)) + 
              '&step=' + str(timedelta_interval))
        
        dict_availavility={}
        print(url)
        response = requests.get(url)
        if response.ok:
            jData = json.loads(response.content.decode('utf-8'))
            if len(jData['data']['result']):
                for key in jData['data']['result'][0]['values']:
                    #print (key + " : " + jData[key])
                    dict_availavility.update({ key[0] : key[1]})
            
        print(response)
        
    except Exception as e:
        pass
    
    return dict_availavility
 

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


def getDetallesProyecto(proyecto_instance):

    rel_ent_pro= AfRelEntPro.objects.filter(pro=proyecto_instance)
    instancias_info=[]
    iterado=[]
    for e in rel_ent_pro:
        if e.ent.ent_nombre not in iterado:

            kuber    = Kuber(e.ent.ent_config_file.path)
            response = kuber.list_namespaced_deployment_info(proyecto_instance.pro_nombre)
            for r in response:
                instancia_id= AfInstancia.objects.filter(ins_unique_name=r['name']).values_list('id',flat=True).first()
                r.update({'entorno': e.ent.ent_nombre, 'id': instancia_id})
            instancias_info.extend(response)
            iterado.append(e.ent.ent_nombre)

    return   instancias_info


def getKubernetesEnv(config_file):

    try:
        fichero_config=handle_uploaded_file(config_file)
        kuber=Kuber( (MEDIA_ROOT+ '%s') %(fichero_config))

        return kuber

    except Exception as e:
        print ()

    return False


def getFileEncodedB64(fichero):

    with open(fichero, 'rb') as f:
        content=f.read()
    f.close()

    return base64.b64encode(content)

def hasNotificationPending(request):
    
    af_user= AfUsuario.objects.get(user=request.user)
    notificaciones_no_leidas= AfUserNotify.objects.filter(to_user=af_user, readed=False)
    request.session['notificaciones_no_leidas'] = True if notificaciones_no_leidas.count() else False
    
    return notificaciones_no_leidas
          
def createNameSpaceStack(**kwargs):

    env_file_path = kwargs.get ('env_file_path')
    namespace     = kwargs.get ('namespace')
    env_name      = kwargs.get ('env_name')
    registry_hash = kwargs.get ('registry_hash')

    try:
        kuber=Kuber (env_file_path)
        kuber.createNameSpace(namespace)
        global_conf=AfGlobalconf.objects.first()
        crt = getFileEncodedB64(global_conf.crt_file.path)
        key = getFileEncodedB64(global_conf.key_file.path)

        dict_ingress={
                        'fichero_yaml' : '%s/ingress_template_base.yaml' % (KUBER_TEMPLATES,), # ingress del servicio q debe ser periodicamente actualizado con los despliegues
                        'namespace'    : namespace,
                        'fqdn'         : global_conf.fqdn,
                        'env_name'     : env_name,
                        'registry_hash': registry_hash,
                        'crt'          : crt.decode("utf-8"),
                        'key'          : key.decode("utf-8")
                    }

        # creacion del tipo Ingress (kind: Ingress)
        kuber.createIngressFromTemplate(dict_ingress)
        dict_ingress['fichero_yaml']='%s/secret_registry.yaml' % (KUBER_TEMPLATES,)
        # creacion del tipo secret (kind: Secret)
        kuber.create_namespaced_secretRegistry(dict_ingress)
        dict_ingress.update({
                             'ingress-secret-template': '%s/ingress-secret-template.yaml' % (KUBER_TEMPLATES,)
                                     })
                # creacion del ingress secret (kind: Secret/ type: kubernetes.io/tls)
        kuber.create_namespaced_secretIngress(dict_ingress)

        return True

    except Exception as e:
        pass

    return False
