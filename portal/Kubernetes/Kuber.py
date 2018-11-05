from kubernetes import client, config, watch
import yaml, base64
import sys
from os import path
from portal.Utils.logger import *

sys.path.insert(0, '../')

import time, datetime
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint



class Kuber(object):

    v1=None
    config_file=None
    logger= None
    rollback_stack_methods= None


    namespace            = None
    unique_instance_name = None
    persistent_volume    = None
    fqdn                 = None
    nfs_server           = None
    env_name             = None
    operation_result     = False

    def __init__(self,fichero=None):
        self.logger=getLogger()
        if fichero:
            self.config_file=fichero
            self.checkConfigFile(self.config_file)
            if  self.v1 is None or not self.checkConnection():
                raise ValueError("Error en la conexion con Kubernates")

            self.rollback_stack_methods=[] # borrado de cambios en el cluster si ocurre algun error durante su creacion

            self.create_kind_dict        = {
                            'PersistentVolume'          : self.create_persistent_volume,
                            'PersistentVolumeClaim'     : self.create_namespaced_persistent_volume_claim,
                            'Deployment'                : self.create_namespaced_deployment,
                            'create_namespaced_service' : self.create_namespaced_service,
                            'HorizontalPodAutoscaler'   : self.create_namespaced_horizontal_pod_autoscaler,
                            'Service'                   : self.create_namespaced_service
                            }


            self.delete_kind_dict        = {
                            'PersistentVolume'          : self.delete_persistent_volume,
                            'PersistentVolumeClaim'     : self.delete_namespaced_persistent_volume_claim,
                            'Deployment'                : self.delete_namespaced_deployment,
                            'delete_namespaced_service' : self.delete_namespaced_service,
                            'HorizontalPodAutoscaler'   : self.delete_namespaced_horizontal_pod_autoscaler,
                            'Service'                   : self.delete_namespaced_service
                            }


    def checkFileExist(self,name):
        return path.exists(name)

    '''
    Comprueba el fichero de config del master de kubernetes
    y instancia un cliente
    '''
    def checkConfigFile(self,file):

        try:

            if self.checkFileExist(file):

                self.logger.debug('el Fichero de configuracion existe !')
                config.load_kube_config(file)
                #config.load_kube_config()
                self.config_file=file
                self.v1 = client.CoreV1Api()
                self.logger.debug('el Fichero de configuracion es valido !')

            return True

        except Exception as e:
            self.logger.error("Error en la config del fichero de Kb: %s" % format('%s' % e))

        return False

    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#read_namespaced_service
    '''
    def get_rook_nfs_ip(self, ns="rook-nfs", svc='rook-nfs'):

        rook_ip = None

        try:

            api_instance = kubernetes.client.CoreV1Api()
            api_response = api_instance.read_namespaced_service(svc, ns)
            self.logger.info('api_response: %s, ROOK_NFS_IP: %s' %(api_response,api_response.spec.cluster_ip))
            rook_ip=api_response.spec.cluster_ip
            pprint(api_response)

        except ApiException as e:
            print("Exception when calling CoreV1Api->read_namespaced_service: %s\n" % e)

        return rook_ip

    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#list_namespace
    '''
    def getNamespaces(self):

        ns={}
        ret = self.v1.list_namespace()
        for i in ret.items:
            ns.update({i.metadata.name : i.status.phase})
            self.logger.info ("ns: %s, status: %s" % (i.metadata.name,i.metadata.status ))

        return ns


    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#delete_namespace
    '''
    def delete_namespace(self, ns):

        try:
            api_instance = kubernetes.client.CoreV1Api()
            body = kubernetes.client.V1DeleteOptions()
            api_response = api_instance.delete_namespace(ns, body)
            pprint(api_response)

        except ApiException as e:
            print("Exception when calling CoreV1Api->delete_namespace: %s\n" % e)


    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#create_namespace
    '''
    def createNameSpace(self,name,entorno_config_file=None):

        try:

            if entorno_config_file:
                self.checkConfigFile(entorno_config_file)

            body = kubernetes.client.V1Namespace()
            body.kind='Namespace'
            body.api_version='v1'
            metadata={'name': name, 'labels' : {'name': name}}
            body.metadata=metadata
            self.v1.create_namespace(body)
            self.logger.debug('Creado namespace: %s' % name)

        except Exception as e:
            print("Exception when calling CoreV1Api->create_namespace: %s\n" % e.body)


    def deleteNamespace(self,name,entorno_config_file=None):

        try:
            self.operation_result=True
            if entorno_config_file:
                self.checkConfigFile(entorno_config_file)

            body = kubernetes.client.V1DeleteOptions()
            self.v1.delete_namespace(name,body)
            self.logger.debug('Borrado  namespace: %s' % name)

        except Exception as e:
            self.operation_result=False
            pass


    def getClient(self):
        return self.v1


    def getConfigFile(self):
        return self.config_file

    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#list_pod_for_all_namespaces
    '''
    def checkConnection(self):

        try:
            self.logger.debug("Listing pods with their IPs:")
            ret = self.v1.list_pod_for_all_namespaces(watch=False)
            for i in ret.items:
                self.logger.debug("%s\t%s\t%s" %
                  (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

            return True

        except Exception as e:
            pass

        return False

    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/ExtensionsV1beta1Api.md#list_namespaced_deployment
    '''
    def list_namespaced_deployment(self, ins_unique_name, ns, include_uninitialized=True):

        include_uninitialized = True # bool | If true, partially initialized resources are included in the response
        response= {}
        try:
            api_instance = kubernetes.client.ExtensionsV1beta1Api()
            api_response = api_instance.list_namespaced_deployment(ns, include_uninitialized=include_uninitialized)

            for i in api_response.items:
                if ins_unique_name== i.metadata.name:
                    response={'replicas': i.status.replicas, 'creation_timestamp': i.metadata.creation_timestamp}
                    pprint('list_namespaced_deployment: %s'  % (i))

            pprint('list_namespaced_deployment: %s'  % (api_response))

        except ApiException as e:
            print("Exception when calling AppsV1Api->list_namespaced_deployment: %s\n" % e)

        return response
    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AutoscalingV1Api.md#list_namespaced_horizontal_pod_autoscaler
    '''
    def list_namespaced_horizontal_pod_autoscaler(self, ins_unique_name, ns, include_uninitialized=True):

        include_uninitialized = True
        response= {}
        try:
            target_name= '%s%s' % (ins_unique_name,'-hpa')
            api_instance = kubernetes.client.AutoscalingV1Api()
            api_response = api_instance.list_namespaced_horizontal_pod_autoscaler(ns, include_uninitialized=include_uninitialized)

            for i in api_response.items:
                if target_name== i.metadata.name:
                    response={'replicas': i.status.current_replicas, 'creation_timestamp': i.metadata.creation_timestamp}
                    pprint('list_namespaced_deployment: %s'  % (i))

            pprint('list_namespaced_deployment: %s'  % (api_response))

        except ApiException as e:
            print("Exception when calling AppsV1Api->list_namespaced_deployment: %s\n" % e)

        return response

    def list_namespaced_ingress(self, ns, include_uninitialized=True):

        include_uninitialized = True # bool | If true, partially initialized resources are included in the response

        try:

            api_instance = kubernetes.client.ExtensionsV1beta1Api()
            api_response = api_instance.list_namespaced_ingress(ns, include_uninitialized=include_uninitialized)
            pprint(api_response)

        except ApiException as e:
            print("Exception when calling AppsV1Api->list_namespaced_deployment: %s\n" % e)


    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/ExtensionsV1beta1Api.md#create_namespaced_ingress
    '''
    def create_namespaced_ingress(self,ns):

        try:
            api_instance = kubernetes.client.ExtensionsV1beta1Api()
            body = kubernetes.client.V1beta1Ingress(
                    api_version="extensions/v1beta1",
                    kind="Ingress",
                    metadata=client.V1ObjectMeta(name=( '%s-ingress' % ns))
                    )

            api_response = api_instance.create_namespaced_ingress(ns, body)
            pprint('create_namespaced_ingress: %s'  % (api_response))

        except ApiException as e:
            print("Exception when calling ExtensionsV1beta1Api->create_namespaced_ingress: %s\n" % e)


    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#create_persistent_volume
    '''
    def create_persistent_volume(self, kwargs, custom):

        self.persistent_volume=('%s%s' % (custom['unique_instance_name'],'-pv'))
        self.operation_result=True
        kwargs['metadata']['namespace'] = self.namespace
        kwargs['metadata']['name']      = self.persistent_volume
        kwargs['spec']['nfs']['server'] = self.nfs_server

        try:

            api_instance = kubernetes.client.CoreV1Api()
            api_response = api_instance.create_persistent_volume(kwargs)
            pprint('create_persistent_volume: %s'  % (api_response))
            self.rollback_stack_methods.append('PersistentVolume')

        except ApiException as e:
            print("Exception when calling CoreV1Api->create_persistent_volume: %s\n" % e)
            self.operation_result=False



    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#create_namespaced_persistent_volume_claim
    '''
    def create_namespaced_persistent_volume_claim(self, kwargs, custom):

        kwargs['metadata']['name'] = ('%s%s' % (self.unique_instance_name, '-pvc') )
        kwargs['metadata']['namespace'] = self.namespace
        self.operation_result=True
        try:
            api_instance = kubernetes.client.CoreV1Api()
            api_response = api_instance.create_namespaced_persistent_volume_claim (self.namespace, kwargs)
            pprint('create_namespaced_persistent_volume_claim: %s'  % (api_response))
            self.rollback_stack_methods.insert(0,'PersistentVolumeClaim')

        except ApiException as e:
            self.operation_result=False
            print("Exception when calling CoreV1Api->create_namespaced_persistent_volume_claim: %s\n" % e)


    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#create_namespaced_service
    '''
    def create_namespaced_service(self, kwargs, custom):

        self.operation_result=True
        kwargs['metadata']['name']           = ('%s%s' % (self.unique_instance_name,'-svc'))
        kwargs['metadata']['namespace']      = self.namespace
        kwargs['spec']['selector']['app']    = self.unique_instance_name

        try:
            api_instance = kubernetes.client.CoreV1Api()
            api_response = api_instance.create_namespaced_service(self.namespace, kwargs)
            self.rollback_stack_methods.append('Service')
            pprint('create_namespaced_service: %s'  % (api_response))

        except ApiException as e:
            self.operation_result= False
            print("Exception when calling CoreV1Api->create_namespaced_service: %s\n" % e)



    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1Api.md#create_namespaced_deployment
    '''
    def create_namespaced_deployment(self, kwargs, custom):

        self.operation_result = True
        kwargs['metadata']['name']                                = self.unique_instance_name
        kwargs['metadata']['namespace']                           = self.namespace
        kwargs['spec']['replicas']                                = int(custom['replicas_min'])
        kwargs['spec']['template']['metadata']['name']            = self.unique_instance_name
        kwargs['spec']['template']['metadata']['namespace']       = self.namespace
        kwargs['spec']['template']['metadata']['labels']['app']   = self.unique_instance_name
        kwargs['spec']['template']['spec']['containers'][0]['name']  = self.unique_instance_name
        kwargs['spec']['template']['spec']['containers'][0]['image'] = 'registry.%s:32337/nginx-cica:latest' % (self.fqdn,) #'registry.FQDN:32337/nginx-cica:latest'
        kwargs['spec']['template']['spec']['containers'][0]['volumeMounts'][0]['subPath'] =  self.unique_instance_name
        kwargs['spec']['template']['spec']['volumes'][0]['persistentVolumeClaim']['claimName'] = ('%s%s' % (self.unique_instance_name , '-pvc'))
        kwargs['spec']['template']['spec']['imagePullSecrets'][0]['name'] = ('%s%s' % ('registry-', self.env_name))

        try:

            api_instance = kubernetes.client.ExtensionsV1beta1Api()
            api_response = api_instance.create_namespaced_deployment (self.namespace, kwargs)
            pprint('create_namespaced_deployment: %s'  % (api_response))
            self.rollback_stack_methods.append('Deployment')

        except ApiException as e:
            self.operation_result = False
            print("Exception when calling ExtensionsV1beta1Api->create_namespaced_deployment: %s\n" % e)



    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AutoscalingV1Api.md#create_namespaced_horizontal_pod_autoscaler
    '''
    def create_namespaced_horizontal_pod_autoscaler(self,kwargs, custom):

        self.operation_result = True
        kwargs['metadata']['name']      = '%s%s' % (self.unique_instance_name, '-hpa')
        kwargs['metadata']['namespace'] = self.namespace
        kwargs['spec']['maxReplicas']   = int(custom['replicas_max'])
        kwargs['spec']['minReplicas']   = int(custom['replicas_min'])
        kwargs['spec']['scaleTargetRef']['name']= self.unique_instance_name
        try:

            api_instance = kubernetes.client.AutoscalingV1Api()
            api_response = api_instance.create_namespaced_horizontal_pod_autoscaler (self.namespace, kwargs)
            pprint('create_namespaced_horizontal_pod_autoscaler: %s'  % (api_response))
            self.rollback_stack_methods.append('HorizontalPodAutoscaler')

        except ApiException as e:
            self.operation_result = False
            print("Exception when calling AutoscalingV1Api->create_namespaced_horizontal_pod_autoscaler: %s\n" % e)



    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#delete_persistent_volume
    '''
    def delete_persistent_volume(self, kwargs):

        name=('%s%s' % (kwargs['unique_instance_name'],'-pv'))

        try:

            api_instance = kubernetes.client.CoreV1Api()
            body = kubernetes.client.V1DeleteOptions()
            api_response = api_instance.delete_persistent_volume(name, body)
            pprint(api_response)

        except ApiException as e:
            print("Exception when calling CoreV1Api->delete_persistent_volume: %s\n" % e)


    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#delete_namespaced_persistent_volume_claim
    '''
    def delete_namespaced_persistent_volume_claim(self, kwargs):

        name        = ('%s%s' % (kwargs['unique_instance_name'],'-pvc'))
        namespace   = kwargs['namespace']

        try:

            api_instance = kubernetes.client.CoreV1Api()
            body = kubernetes.client.V1DeleteOptions()
            api_response = api_instance.delete_namespaced_persistent_volume_claim(name, namespace, body)
            self.logger.info("delete_namespaced_persistent_volume_claim:->  %s" % (api_response,))
            pprint(api_response)

        except ApiException as e:
            print("Exception when calling CoreV1Api->delete_namespaced_persistent_volume_claim: %s\n" % e)

    def delete_namespaced_deployment(self, kwargs):


        name        = kwargs['unique_instance_name']
        namespace   = kwargs['namespace']

        try:

            api_instance = kubernetes.client.AppsV1Api()
            body = kubernetes.client.V1DeleteOptions()
            api_response = api_instance.delete_namespaced_deployment( name, namespace, body)
            self.logger.info("delete_namespaced_deployment:->  %s" % (api_response,))
            pprint(api_response)

        except ApiException as e:
            print("Exception when calling AppsV1Api->delete_namespaced_deployment: %s\n" % e)


    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AutoscalingV1Api.md#delete_namespaced_horizontal_pod_autoscaler
    '''
    def delete_namespaced_horizontal_pod_autoscaler(self, kwargs):

        name         = '%s%s' % (kwargs['unique_instance_name'], '-hpa')
        namespace    = kwargs['namespace']

        try:

            api_instance = kubernetes.client.AutoscalingV1Api()
            body = kubernetes.client.V1DeleteOptions()
            api_response = api_instance.delete_namespaced_horizontal_pod_autoscaler( name, namespace, body)
            self.logger.info("delete_namespaced_horizontal_pod_autoscaler:->  %s" % (api_response,))
            pprint(api_response)

        except ApiException as e:
            print("Exception when calling AutoscalingV1Api->delete_namespaced_horizontal_pod_autoscaler: %s\n" % e)


    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#delete_namespaced_service
    '''
    def delete_namespaced_service(self, kwargs):

        name         = '%s%s' % (kwargs['unique_instance_name'], '-svc')
        namespace    = kwargs['namespace']

        try:

            api_instance = kubernetes.client.CoreV1Api()
            body = kubernetes.client.V1DeleteOptions()
            api_response = api_instance.delete_namespaced_service(name, namespace, body)
            self.logger.info("delete_namespaced_service:->  %s" % (api_response,))
            pprint(api_response)

        except ApiException as e:
            print("Exception when calling CoreV1Api->delete_namespaced_service: %s\n" % e)


    def rollBackOperations(self, kwargs):

        for op in self.rollback_stack_methods:
            self.logger.info("rollBackOperations: %s" % (op,))
            self.delete_kind_dict[op](kwargs)


    def delete_Instacia(self,**kwargs):

        self.rollback_stack_methods=[
                                     'PersistentVolumeClaim',
                                     'Deployment',
                                     'HorizontalPodAutoscaler',
                                     'Service',
                                     'PersistentVolume'
                                     ]

        try:
            self.namespace                  = kwargs.get('namespace')
            self.unique_instance_name       = kwargs.get('unique_instance_name')
            self.rollBackOperations(kwargs)
            self.logger.info("delete_Instacia: %s" % (self.unique_instance_name ,))

        except ApiException as e:
            print("Exception delete_Instacia->delete_namespaced_service: %s\n" % format(e))


    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1Api.md#read_namespaced_deployment
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1Api.md#patch_namespaced_deployment
    '''
    def modifyDeploymentReplicas(self, deployment_name, ns, replicas):

        try:

            api_instance = kubernetes.client.AppsV1Api()
            body= api_instance.read_namespaced_deployment(deployment_name, ns)
            body.spec.replicas=replicas
            api_response = api_instance.patch_namespaced_deployment(deployment_name, ns, body)
            self.logger.info("modifyDeploymentReplicas:->  Modificando %s a %s" % (deployment_name,replicas))
            pprint(api_response)

        except ApiException as e:
            print("Exception when calling CoreV1Api->delete_namespaced_service: %s\n" % e)


    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1Api.md#list_namespaced_deployment
    '''
    def list_namespaced_deployment_info(self, namespace):

        try:

            api_instance = kubernetes.client.AppsV1Api()
            api_response = api_instance.list_namespaced_deployment(namespace)
            deployments=[]

            for d in api_response.items:
                deployed={ 'name': d.metadata.name      ,   'creation_timestamp':d.metadata.creation_timestamp ,
                            'status': d.spec.replicas    ,   'imagen': d.spec.template.spec.containers[0].image}
                deployments.append(deployed)

            pprint(api_response)

            self.logger.info("list_namespaced_deployment_info:->  %s" % (api_response,))
            '''
            Actualizamos Ingress

            '''
            return deployments


        except ApiException as e:
            print("Exception when calling AppsV1Api->list_namespaced_deployment_info: %s\n" % e)


    def updateIngressPostDeploy(self, kwargs):

        self.namespace            = kwargs.get('namespace')
        self.unique_instance_name = kwargs.get('unique_instance_name')
        self.fqdn                 = kwargs.get('fqdn')
        self.env_name             = kwargs.get('env_name')

        self.logger.info("updateIngressPostDeploy:-> ns: %s\nnombre instancia:%s\nfqdn: %s\nentorno: %s\n" % (self.namespace,
                                                                           self.unique_instance_name,
                                                                           self.fqdn,
                                                                           self.env_name
                                                                           ))


        ingress=self.actualiza_namespaced_ingress(
                                                    self.namespace,
                                                    self.unique_instance_name,
                                                    self.env_name,
                                                    self.fqdn
                                                  )
        pprint(ingress)

        print()


    def getIngressPath(self, service):

        i_backend= kubernetes.client.V1beta1IngressBackend(
                    service_name = '%s-svc' % (service,) ,
                    service_port = 80
                )

        i_path= kubernetes.client.V1beta1HTTPIngressPath (
                    backend=i_backend,
                    path='/%s' % (service,)
                )

        return i_path




    def getIngressRule(self, instancia, host, i_path= None):

        if i_path is None:
            i_path= [self.getIngressPath(instancia)]

        i_rule_value= kubernetes.client.V1beta1HTTPIngressRuleValue(
                    paths=i_path
                )

        i_irule=kubernetes.client.V1beta1IngressRule(
                    host=host,
                    http=i_rule_value
                )


        return i_irule

    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/ExtensionsV1beta1Api.md#read_namespaced_ingress
    '''
    def actualiza_namespaced_ingress(self,ns=None, instancia=None, env= None,fqdn=None ):

        try:

            instancia       = self.unique_instance_name if instancia is None else instancia
            ns              = self.namespace if ns is None else ns
            target_ingress  = '%s-ingress' % (ns,)
            fqdn            = self.fqdn if fqdn is None else fqdn
            env             = self.env_name if env is None else env

            host = '%s.%s.%s' % (ns, env, fqdn)

            api_response=None
            api_instance = kubernetes.client.ExtensionsV1beta1Api()
            api_response = api_instance.read_namespaced_ingress(target_ingress, ns)

            i_irule= self.getIngressRule(instancia,host)

            api_response.spec.rules.append(i_irule)
            api_instance.patch_namespaced_ingress(target_ingress,ns,api_response)
            self.logger.info("actualiza_namespaced_ingress:->  %s" % (api_response,))

        except ApiException as e:
            print("Exception when calling ExtensionsV1beta1Api->read_namespaced_ingress: %s\n" % e)

        return api_response

    def unpublishFromIngress(self,kwargs):

        try:

            self.namespace  = kwargs.get('namespace')
            target_ingress  = '%s-ingress' % (self.namespace,)
            target_svc      = '%s-svc' % kwargs.get('unique_instance_name')
            services        = kwargs.get('services') #list de nombres de instancias q deben permanecer en el Ingress
            lst_svc         = []
            api_response    = None
            api_instance    = kubernetes.client.ExtensionsV1beta1Api()
            api_response    = api_instance.read_namespaced_ingress(target_ingress, self.namespace)

            self.fqdn                 = kwargs.get('fqdn')
            self.env_name             = kwargs.get('env_name')


            host = '%s.%s.%s' % (self.namespace, self.env_name , self.fqdn)

            self.logger.info("unpublishFromIngress:->  %s" % (api_response,))
            self.logger.info("target_ingress: %s , target_svc: % s " % (target_ingress,target_svc))

            for s in services:
                lst_svc.append(self.getIngressPath(s.ins_unique_name))
            i_r= self.getIngressRule(None, host, lst_svc)

            api_response.spec.rules=[i_r]
            self.logger.info("api_response parcheada: %s  " % (api_response))
            api_instance.patch_namespaced_ingress(target_ingress,self.namespace ,api_response)

        except ApiException as e:
            self.logger.error("unpublishFromIngress parcheada: %s  " % (format(e)))
            print("Exception when calling unpublishFromIngress-> %s\n" % (format(e),))


    def createIngressFromTemplate(self,kwargs):

        fichero_yaml                    = kwargs.get('fichero_yaml')
        self.namespace                  = kwargs.get('namespace')
        self.fqdn                       = kwargs.get('fqdn')
        self.env_name                   = kwargs.get('env_name')

        with open(fichero_yaml, 'r') as f:
            data=f.read()
            parsed = yaml.load(data)

        try:

            parsed['metadata']['name']      = '%s%s' % (self.namespace,'-ingress')
            parsed['metadata']['namespace'] = '%s'   % (self.namespace,)
            parsed['spec']['tls'][0]['hosts'][0]   = '%s.%s.%s' % (self.namespace, self.env_name, self.fqdn)
            parsed['spec']['tls'][0]['secretName'] = '%s%s' % (self.namespace, '-secret')
            parsed['spec']['rules'][0]['host']     = '%s.%s.%s' % (self.namespace, self.env_name, self.fqdn)
            api_instance = kubernetes.client.ExtensionsV1beta1Api()
            api_response = api_instance.create_namespaced_ingress(self.namespace, parsed)
            self.logger.info("createIngressFromTemplate:->  %s" % (api_response,))
            self.logger.info("creado el ingress del servicio a partir del fichero:->  %s" % (fichero_yaml,))
            pprint(api_response)

        except ApiException as e:
            print("Exception when calling ExtensionsV1beta1Api->create_namespaced_ingress: %s\n" % e)

        #@todo@ Rollback meths

        return True

        
    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/ExtensionsV1beta1Api.md#delete_namespaced_ingress
    '''
    def delete_namespaced_ingress(self,kwargs):

        self.namespace  = kwargs.get('namespace')
        target_ingress  = '%s-ingress' % (self.namespace,)
        self.namespace                  = kwargs.get('namespace')

        try:

            api_instance = kubernetes.client.ExtensionsV1beta1Api()
            body = kubernetes.client.V1DeleteOptions()
            api_response = api_instance.delete_namespaced_ingress(target_ingress, self.namespace, body)
            self.logger.info("delete_namespaced_ingress:->  %s" % (api_response,))

        except ApiException as e:
            print("Exception when calling delete_namespaced_ingress-> %s\n" % format(e))

        #@todo@ Rollback meths

        return True

    def create_namespaced_secretRegistry(self,kwargs):

        try:

            self.namespace                  = kwargs.get('namespace')
            fichero_yaml                    = kwargs.get('fichero_yaml')
            self.env_name                   = kwargs.get('env_name')

            with open(fichero_yaml, 'r') as f:
                data=f.read()
                parsed = yaml.load(data)

            parsed['data']['.dockerconfigjson'] = kwargs.get('registry_hash')
            parsed['metadata']['name']      = '%s%s' % ('registry-', self.env_name )
            parsed['metadata']['namespace'] = self.namespace

            api_instance = kubernetes.client.CoreV1Api()
            api_response = api_instance.create_namespaced_secret(self.namespace, parsed)
            self.logger.info("create_namespaced_secretRegistry:->  %s" % (api_response,))
            self.logger.info("creado el del registry (kubernetes.io/dockerconfigjson):->  %s" % (fichero_yaml,))
            pprint(api_response)

        except ApiException as e:

            self.logger.info("create_namespaced_secretRegistry:->  %s" % (api_response,))
            self.logger.info("Exception when calling CoreV1Api->create_namespaced_secret: %s\n" % e)
            print("Exception when calling CoreV1Api->create_namespaced_secret: %s\n" % e)



    def create_namespaced_secretIngress(self,kwargs):

        try:

            self.namespace                  = kwargs.get('namespace')
            fichero_yaml                    = kwargs.get('ingress-secret-template')
            crt                             = kwargs.get('crt')
            key                             = kwargs.get('key')

            with open(fichero_yaml, 'r') as f:
                data=f.read()
                parsed = yaml.load(data)

            parsed['metadata']['name']      = 'ingress-secret'
            parsed['metadata']['namespace'] = self.namespace
            parsed['data']['tls.crt']       = crt
            parsed['data']['tls.key']       = key

            api_instance = kubernetes.client.CoreV1Api()
            api_response = api_instance.create_namespaced_secret(self.namespace, parsed)
            self.logger.info("create_namespaced_secretIngress:->  %s" % (api_response,))
            self.logger.info("creado el secret (kubernetes.io/tls):->  %s" % (fichero_yaml,))
            pprint(api_response)
            self.logger.info(api_response)
        except ApiException as e:
            print ('')
            print("Exception when calling CoreV1Api->create_namespaced_secret: %s\n" % e)




    def createServiceStack(self, **kwargs):

        fichero_yaml                    = kwargs.get('fichero_yaml')
        self.namespace                  = kwargs.get('namespace')
        self.unique_instance_name       = kwargs.get('unique_instance_name')
        self.fqdn                       = kwargs.get('fqdn')
        self.nfs_server                 = '192.168.129.22' #kwargs.get('nfs_server')
        self.env_name                   = kwargs.get('env_name')
        replicas_min                    = kwargs.get('replicas_min')
        replicas_max                    = kwargs.get('replicas_max')

        with open(fichero_yaml, 'r') as f:
            data=f.read()
            parsed = list(yaml.load_all(data))

            if parsed:
                for i in parsed:
                    kind = i.get('kind')
                    pprint ("llamando al meth asociado al kind: %s" % (kind))
                    self.logger.info("llamando al meth asociado al kind: %s" % (kind))
                    self.create_kind_dict[kind](i, kwargs)
                    if not self.operation_result and len(self.rollback_stack_methods):
                        self.logger.info("Ocurrio un error durante el despliegue, se lanza el Rollback")
                        self.rollBackOperations(kwargs)
                        return False

                self.updateIngressPostDeploy(kwargs)

        #@todo@ Rollback meths

        return True
