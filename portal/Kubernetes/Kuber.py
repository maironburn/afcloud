from kubernetes import client, config, watch
import yaml
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

    def __init__(self,fichero=None):
        self.logger=getLogger()
        if fichero:
            self.config_file=fichero
            self.checkConfigFile(self.config_file)
            if  self.v1 is None or not self.checkConnection():
                raise ValueError("Error en la conexion con Kubernates")



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


    def getNamespaces(self):

        ns={}
        ret = self.v1.list_namespace()
        for i in ret.items:
            ns.update({i.metadata.name : i.status.phase})
            self.logger.info ("ns: %s, status: %s" % (i.metadata.name,i.metadata.status ))

        return ns

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

            if entorno_config_file:
                self.checkConfigFile(entorno_config_file)

            body = kubernetes.client.V1DeleteOptions()
            self.v1.delete_namespace(name,body)
            self.logger.debug('Borrado  namespace: %s' % name)

        except Exception as e:
            pass



    def getClient(self):
        return self.v1


    def getConfigFile(self):
        return self.config_file


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


    def list_namespaced_deployment(self, ns, include_uninitialized=True):
        
        api_instance = kubernetes.client.ExtensionsV1beta1Api()
        include_uninitialized = True # bool | If true, partially initialized resources are included in the response
        try:
            api_response = api_instance.list_namespaced_deployment(ns, include_uninitialized=include_uninitialized)
            pprint('list_namespaced_deployment: %s'  % (api_response))
        except ApiException as e:
            print("Exception when calling AppsV1Api->list_namespaced_deployment: %s\n" % e)


    def list_namespaced_ingress(self, ns, include_uninitialized=True):
        
        api_instance = kubernetes.client.ExtensionsV1beta1Api()
        include_uninitialized = True # bool | If true, partially initialized resources are included in the response
        try:
            api_response = api_instance.list_namespaced_ingress(ns, include_uninitialized=include_uninitialized)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling AppsV1Api->list_namespaced_deployment: %s\n" % e)



    def create_namespaced_ingress(self,ns):
        
        api_instance = kubernetes.client.ExtensionsV1beta1Api()
        body = kubernetes.client.V1beta1Ingress(
                    api_version="extensions/v1beta1",
                    kind="Ingress",
                    metadata=client.V1ObjectMeta(name=( '%s-ingress' % ns))
                    )
        try: 
            api_response = api_instance.create_namespaced_ingress(ns, body)
            pprint('create_namespaced_ingress: %s'  % (api_response))
        except ApiException as e:
            print("Exception when calling ExtensionsV1beta1Api->create_namespaced_ingress: %s\n" % e)
    
    
    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#create_persistent_volume
    '''
    def create_persistent_volume(self, kwargs, custom):
        
        api_instance = kubernetes.client.CoreV1Api()
       
        try:
            #kargs[]
            kwargs['metadata']['namespace'] = custom['namespace']
            kwargs['metadata']['name']      = ('%s%s' % (custom['unique_instance_name'],'-pv'))
            kwargs['spec']['nfs']['server'] = custom['nfs-server']
            
            api_response = api_instance.create_persistent_volume(kwargs)
            pprint('create_persistent_volume: %s'  % (api_response))
        except ApiException as e:
            print("Exception when calling CoreV1Api->create_persistent_volume: %s\n" % e)
    
    '''
    https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#create_namespaced_persistent_volume_claim
    '''
    def create_namespaced_persistent_volume_claim(self, kwargs, custom):
        
        api_instance = kubernetes.client.CoreV1Api()
        
        kwargs['metadata']['name'] = ('%s%s' % (custom['unique_instance_name'], '-pvc') )
        kwargs['metadata']['namespace'] = custom['namespace']
        
        try: 
            api_response = api_instance.create_namespaced_persistent_volume_claim (custom['namespace'], kwargs)
            pprint('create_namespaced_persistent_volume_claim: %s'  % (api_response))
        
        except ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_persistent_volume_claim: %s\n" % e)
    
        
    '''
        https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/CoreV1Api.md#create_namespaced_service
    '''        

    def create_namespaced_service(self, kwargs, custom):
        
        api_instance = kubernetes.client.CoreV1Api()
        kwargs['metadata']['name']      = ('%s%s' % (custom['unique_instance_name'],'-svc'))
        kwargs['metadata']['namespace']     = custom['namespace']
        kwargs['spec']['selector']['app']   = custom['unique_instance_name']
        
        try: 
            api_response = api_instance.create_namespaced_service(custom['namespace'], kwargs)
            pprint('create_namespaced_service: %s'  % (api_response))
        except ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_service: %s\n" % e)
    
        

    def create_namespaced_deployment(self, kwargs, custom):
        
        api_instance = kubernetes.client.ExtensionsV1beta1Api()
       
        kwargs['metadata']['name']                                = custom['unique_instance_name']
        kwargs['metadata']['namespace']                           = custom['namespace']
        kwargs['spec']['replicas']                                = int(custom['replicas_min'])
        kwargs['spec']['template']['metadata']['name']            = custom['unique_instance_name']
        kwargs['spec']['template']['metadata']['namespace']       = custom['namespace']
        kwargs['spec']['template']['metadata']['labels']['app']   = custom['unique_instance_name']
        kwargs['spec']['template']['spec']['containers'][0]['name']  = custom['unique_instance_name']
        kwargs['spec']['template']['spec']['containers'][0]['image'] = 'registry.FQDN:32337/nginx-cica:latest'
        kwargs['spec']['template']['spec']['containers'][0]['volumeMounts'][0]['subPath'] = custom['unique_instance_name']
        kwargs['spec']['template']['spec']['volumes'][0]['persistentVolumeClaim']['claimName'] = ('%s%s' % (custom['unique_instance_name'] , '-pvc'))
        kwargs['spec']['template']['spec']['imagePullSecrets'][0]['name'] = ('%s%s' % ('registry-', custom['env-name']))
        
        try: 
            
            api_response = api_instance.create_namespaced_deployment (custom['namespace'], kwargs)
            pprint('create_namespaced_deployment: %s'  % (api_response))
            pass
        except ApiException as e:
            print("Exception when calling ExtensionsV1beta1Api->create_namespaced_deployment: %s\n" % e)
    
              
    def create_namespaced_horizontal_pod_autoscaler(self,kwargs, custom):
        
        api_instance = kubernetes.client.AutoscalingV1Api()
        kwargs['metadata']['name']      = custom['unique_instance_name']
        kwargs['metadata']['namespace'] = custom['namespace']
        kwargs['spec']['maxReplicas']   = int(custom['replicas_max'])
        kwargs['spec']['minReplicas']   = int(custom['replicas_min'])
        kwargs['spec']['scaleTargetRef']['name']= custom['unique_instance_name']
        try: 
            api_response = api_instance.create_namespaced_horizontal_pod_autoscaler (custom['namespace'], kwargs)
            pprint('create_namespaced_horizontal_pod_autoscaler: %s'  % (api_response))
            
        except ApiException as e:
            print("Exception when calling AutoscalingV1Api->create_namespaced_horizontal_pod_autoscaler: %s\n" % e)
    
             
    def createServiceStack(self, **kwargs):
        
        fichero_yaml     = kwargs.get('fichero_yaml')
        target_namespace = kwargs.get('namespace')
        replicas_min     = kwargs.get('replicas_min')
        replicas_max     = kwargs.get('replicas_max')
        instance_name    = kwargs.get('unique_instance_name')

        kind_dict        = {
                            'PersistentVolume'          : self.create_persistent_volume,
                            'PersistentVolumeClaim'     : self.create_namespaced_persistent_volume_claim,
                            'Deployment'                : self.create_namespaced_deployment,
                            'create_namespaced_service' : self.create_namespaced_service,
                            'HorizontalPodAutoscaler'   : self.create_namespaced_horizontal_pod_autoscaler,
                            'Service'                   : self.create_namespaced_service
                            } 
        
        #filename=f.name
        with open('/var/www/afcloud/yaml_all_services_HsXeaZf.yaml', 'r') as f:
            data=f.read()
            parsed = list(yaml.load_all(data))
            
            if parsed:
                for i in parsed:
                    kind = i.get('kind')
                    pprint ("llamando al meth asociado al kind: %s" % (kind))
                    kind_dict[kind](i, kwargs)

        return parsed
        

            
            
            
        