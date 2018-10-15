from kubernetes import client, config, watch
import yaml
import sys
from os import path
import yaml
from portal.Utils.logger import *
sys.path.insert(0, '../')

import time
import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint


class KuberConnectionFail(Exception):
    pass


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
                raise KuberConnectionFail("Error en la conexion con Kubernates")
            


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
        
        ns=[]
        ret = self.v1.list_namespace()
        for i in ret.items:
            ns.append(i.metadata.name)
            print ("%s" % i.metadata.name)
        
        return ns

    def createNameSpace(self,name,entorno_config_file=None):

        
        try: 
            
            if entorno_config_file:
                self.checkConfigFile(entorno_config_file)
            #api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(self.config_file))
            #configuration = kubernetes.client.Configuration()
            #api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(configuration))
            body = kubernetes.client.V1Namespace() 
            body.kind='Namespace'
            body.api_version='v1'
            metadata={'name': name, 'labels' : {'name': name}}
            body.metadata=metadata
            self.v1.create_namespace(body)
            self.logger.debug('Creado namespace: %s' % name)
        except Exception as e:
            print("Exception when calling CoreV1Api->create_namespace: %s\n" % e.body)        
            
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
            
            self.logger.debug("Tes de conexion ok ")
            return True

        except Exception as e:
            pass

        return False


    def createDeployment(self,fichero_yaml, target_namespace):

        with open(path.join(path.dirname(__file__), fichero_yaml)) as f:
            dep = yaml.load(fichero_yaml)
            k8s_beta = client.ExtensionsV1beta1Api()
            resp = k8s_beta.create_namespaced_deployment(
                body=dep, namespace=target_namespace)
            print("Deployment created. status='%s'" % str(resp.status))
