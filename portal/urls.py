
from django.contrib.staticfiles import views
from django.contrib.auth import views as auth_views
from django.conf.urls import url, include
from django.contrib import admin
from portal.Usuarios import views as user_views
from portal.Proyectos import views as project_views
from portal.Entornos import views as entornos_views
from portal.Servicios import views as servicios_views
from portal.Integrantes import views as integrantes_views
from portal.Catalogo import views as catalogo_views
from portal.Despliegues import views as despliegues_views
from portal.GlobalConf import views as globalconf_views
from portal.Incidencias import views as incidencias_views
from portal.MailServer import views as confmail_views
from portal.Notificaciones import views as notificaciones_views
from portal.Monitoring import views as monitoring_views
from portal.Facturacion import views as facturacion_views
from portal.Disponibilidad import views as ans_views

urlpatterns = [
     # USUARIOS
     url(r'^startpage/$', user_views.index, name='startpage'),
     url(r'^index/$', user_views.index, name='index'),
     url(r'^index/proyecto/(?P<id_proyecto>\d+)/$', user_views.selected_proyect, name='index'),
     url(r'^administrar/usuarios/$', user_views.admin_users, name='admin_usuarios'),
     url(r'^administrar/usuarios/(?P<orden>\d+)/(?P<ascendente>\d+)/$', user_views.administrarUsuariosOrdered, name='usuarios ordenados'),
     url(r'^administrar/usuarios/nuevoUsuario/', user_views.nuevoUsuario, name='nuevoUsuario'),
     url(r'^administrar/usuarios/editarUsuario/(?P<id>\d+)/$', user_views.editAFUser, name='editUser'),
     url(r'^administrar/usuarios/eliminarUsuario/(?P<id>\d+)/$', user_views.deleteAFUser, name='delete'),
     url(r'^administrar/modificarPerfil/(?P<id>\d+)/$', user_views.modificarPerfil, name='OwnUserEdit'),
     ##################################################

     # PROYECTOS
     url(r'^administrar/proyectos/$', project_views.administrarProyectos, name='admin_projects'),
     url(r'^administrar/proyecto/nuevoProyecto/$', project_views.nuevoProyecto, name='index'),
     url(r'^administrar/proyecto/editarProyecto/(?P<id>\d+)/$', project_views.editarProyecto, name='editarProyecto'),
     url(r'^administrar/proyecto/eliminarProyecto/(?P<id>\d+)/$', project_views.borrarProyecto, name='borrarrProyecto'),
     url(r'^administrar/proyectos/(?P<orden>\d+)/(?P<ascendente>\d+)/$', project_views.administrarProyectosOrdered, name='Administrar proyectos'),
     url(r'^detalles/proyectos/(?P<id>\d+)/$', project_views.detallesProyecto, name='detalles_projects'),
     ##################################################

     # SERVICIOS
     url(r'^administrar/servicios/$', servicios_views.administrarServicios, name='admin_services'),
     url(r'^administrar/servicios/(?P<orden>\d+)/(?P<ascendente>\d+)/$', servicios_views.administrarServiciosOrdered, name='Administrar servicios'),
     url(r'^administrar/servicio/nuevoServicio/$', servicios_views.nuevoServicio, name='index'),
     url(r'^administrar/servicio/editarServicio/(?P<id>\d+)/$', servicios_views.editarServicio, name='editarProyecto'),
     url(r'^administrar/servicio/eliminarServicio/(?P<id>\d+)/$', servicios_views.borrarServicio, name='borrarrProyecto'),
     ##################################################


    # ENTORNOS
     url(r'^administrar/entornos/$', entornos_views.administrarEntornos, name='admin_env'),
     url(r'^administrar/entornos/(?P<orden>\d+)/(?P<ascendente>\d+)/$', entornos_views.administrarEntornosOrdered, name='Administrar entornos'),
     url(r'^administrar/entornos/nuevoEntorno/$', entornos_views.nuevoEntorno, name='nuevoEntorno'),
     url(r'^administrar/entornos/editarEntorno/(?P<id>\d+)/$', entornos_views.editarEntorno, name='editarEntorno'),
     url(r'^administrar/entornos/eliminarEntorno/(?P<id>\d+)/$', entornos_views.borrarEntorno, name='borrarrEntorno'),

     ##################################################
    # INTEGRANTES

     url(r'^integrantes/$', integrantes_views.index, name='Administrar Integrante'),
     url(r'^integrantes/proyecto/(?P<id_proyecto>\d+)/$', integrantes_views.integrantesIndex, name='vista integrantes'),
     url(r'^integrantes/proyecto/(?P<id_proyecto>\d+)/(?P<orden>\d+)/(?P<ascendente>\d+)/$', integrantes_views.integrantesIndexOrdered, name='integrantes_ordered'),
     url(r'^integrantes/proyecto/(?P<id_proyecto>\d+)/nuevoIntegrante/$', integrantes_views.nuevoIntegrante, name='nuevoIntegrante'),
     url(r'^integrantes/proyecto/(?P<id_proyecto>\d+)/editarIntegrante/(?P<id_integrante>\d+)/$', integrantes_views.editarIntegrante, name='editarIntegrante'),
     url(r'^integrantes/proyecto/(?P<id_proyecto>\d+)/eliminarIntegrante/(?P<id_integrante>\d+)/$', integrantes_views.eliminarIntegrante, name='borrarIntegrante'),


    ##################################################
    # CATALOGO
     url(r'^catalogo/$', catalogo_views.index, name='catalogo index'),
     url(r'^catalogo/proyecto/(?P<id_proyecto>\d+)/$', catalogo_views.catalogosIndex, name='Administrar catalogos'),
     url(r'^catalogo/proyecto/(?P<id_proyecto>\d+)/nuevoEntrada/$', catalogo_views.nuevoCatalogo, name='nuevoCatalogo'),
     url(r'^catalogo/proyecto/(?P<id_proyecto>\d+)/editarEntrada/(?P<id_servicio>\d+)/$', catalogo_views.editarCatalogo, name='editarCatalogo'),
     url(r'^catalogo/proyecto/(?P<id_proyecto>\d+)/eliminarEntrada/(?P<id_servicio>\d+)/$', catalogo_views.eliminarCatalogo, name='borrarrCatalogo'),

    ##################################################
    # DESPLIEGUES
    url(r'^despliegues/$', despliegues_views.index, name='catalosgo index'),
    url(r'^despliegue/proyecto/(?P<id_proyecto>\d+)/$', despliegues_views.desplieguesIndex, name='Administrar instancias'),
    #url(r'^integrantes/proyecto/(?P<proyecto>\d+)/(?P<orden>\d+)/(?P<ascendente>\d+)/$', integrantes_views.integrantesIndexOrdered, name='Administrar entornos'),
    url(r'^despliegue/proyecto/(?P<id_proyecto>\d+)/crearInstancia/$', despliegues_views.nuevoDespliegue, name='nuevaInstancia'),
    #url(r'^despliegue/proyecto/(?P<id_proyecto>\d+)/editarInstancia/(?P<id_instancia>\d+)/$', despliegues_views.editarDespliegue, name='editarInstancia'),
    url(r'^despliegue/proyecto/(?P<id_proyecto>\d+)/eliminarInstancia/(?P<id_instancia>\d+)/$', despliegues_views.eliminarDespliegue, name='borrarrInstancia'),
    url(r'^despliegue/modifyDeploymentReplicas/(?P<id_instancia>\d+)/(?P<replicas>\d+)/$', despliegues_views.modifyDeploymentReplicas, name='modifyDeploymentReplicas'),
    url(r'^refesh_replicas/proyecto/(?P<id_proyecto>\d+)/$', despliegues_views.refreshReplicas, name='refreshDeploymentReplicas'),
    url(r'^despliegue/manualmodifyDeploymentReplicas/(?P<id_instancia>\d+)/(?P<replicas>\d+)/$', despliegues_views.manualmodifyDeploymentReplicas, name='manualmodifyDeploymentReplicas'),

    ##################################################
    # CONFIGURACION GLOBAL
    url(r'^administrar/globalconf/$', globalconf_views.creaGlogalConf, name='globalconf'),
    url(r'^administrar/conf_mail/$', confmail_views.config_Mail, name='conf_mail_server'),
    # INCIDENCIAS
    url(r'^administrar/incidencias/$', incidencias_views.administrarIncidencias, name='admin_incidencias'),
    url(r'^incidencias/crear/$', incidencias_views.crearIncidencia, name='crear_incidencia'),
    url(r'^detalles/incidencia/(?P<id>\d+)/$', incidencias_views.getItDetails, name='detalles_incidencia'),
    url(r'^detalles/incidencia/(?P<id>\d+)/(?P<notify_id>\d+)$', incidencias_views.getItDetails, name='detalles_incidencia'),
    url(r'^administrar/incidencias/editarIncidencia/(?P<id>\d+)/$', incidencias_views.addNotaIncidencia, name='editarIncidencia'),
    url(r'^eliminarIncidencia/(?P<id>\d+)/$', incidencias_views.eliminarIncidencia, name='eliminar_incidencia'),
    # Notificaciones
    url(r'^consultarNotificaciones/$', notificaciones_views.notificacionesIndex, name='consultar_notificaciones'),
    url(r'^consultarNotificaciones/(?P<id>\d+)/$', notificaciones_views.getNotifyDetails, name='getNotify_details'),
    url(r'^eliminarNotificacion/(?P<id>\d+)/$', notificaciones_views.eliminarNotificacion, name='eliminar_notify'),
    # MONITORIZACION
    url(r'^monitoring/$', monitoring_views.monitoringIndex, name='monitoring'),
    url(r'^admin_monitoring/$', monitoring_views.adminMonitoring, name='adminMonitoring'),
    url(r'^monitoringRequest/$', monitoring_views.monitoringRequest, name='monitoring_request'),
    # FACTURACION
    url(r'^facturacion/$', facturacion_views.facturacionIndex, name='facturacion_index'),
    url(r'^detalles_facturacion/$', facturacion_views.detalles_facturacion, name='detalles_factuacion'),
    url(r'^detalles_facturacion/(?P<id>\d+)/$', facturacion_views.detalles_instancia_facturacion, name='detalles_instance_facturacion'),

    # DISPONIBILIDAD (ANS)
    url(r'^ans/$', ans_views.ansIndex, name='ans_index'),
    url(r'^detalles_ans/$', ans_views.detalles_ans, name='detalles_ans'),
    url(r'^detalles_ans/(?P<id>\d+)/$', ans_views.detalles_instancia_ans, name='detalles_instance_ans'),

]
