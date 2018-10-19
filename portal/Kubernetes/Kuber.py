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


    def patch_Namespace(self,name,entorno_config_file=None):

        try:

            if entorno_config_file:
                self.checkConfigFile(entorno_config_file)

            body = kubernetes.client.V1NamespaceSpec()
            ns_stats=self.v1.read_namespace_status(name)



            #body.finalizers=[]
            #body.deletion_grace_period_seconds=1
            #ssbody.deletion_timestamp=datetime.datetime.now()
            #body.finalizers=[]
            #metadata=kubernetes.client.V1ObjectMeta(deletion_timestamp=datetime.datetime.now())
            #body.metadata=metadata
            self.v1.patch_namespace_status(name, ns_stats)
            self.logger.debug('patch_Namespace : %s' % name)


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
            pprint(api_response)
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
                    metadata=client.V1ObjectMeta(name=( '%s_ingress' % ns))
                    )
        try: 
            api_response = api_instance.create_namespaced_ingress(ns, body)
            
        except ApiException as e:
            print("Exception when calling ExtensionsV1beta1Api->create_namespaced_ingress: %s\n" % e)
    
    
    
    '''
    caracteristicas personalizadas de la instancia
    '''
    def particularizeYaml(self,fjson, dict_yaml):

        fjson['metadata']['name'] = dict_yaml['deployment_name']
        fjson['spec']['replicas'] = int(dict_yaml['replicas'])

        return fjson

    def createDeployment(self,**kwargs):

        fichero_yaml     = kwargs.get('fichero_yaml')
        target_namespace = kwargs.get('namespace')

        with open(fichero_yaml) as f:
            dep = self.particularizeYaml(yaml.load(f),kwargs)
            k8s_beta = client.ExtensionsV1beta1Api()
            resp = k8s_beta.create_namespaced_deployment(
                body=dep, namespace=target_namespace)
            print("Deployment created. status='%s'" % str(resp.status))
