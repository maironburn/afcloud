from os import path
import yaml
from kubernetes import client, config
from portal.Utils.logger import *
from portal.Kubernetes.Kuber import Kuber
from kubernetes.client.rest import ApiException



class Deployment(object):
    
    all_attr        = ['deployment_name','image','name','app','config_file','replicas', 'c_port'] 
    deployment_name = None
    client          = None
    image           = None
    name            = None
    app             = None
    logger          = None
    config_file     = None
    replicas        = None
    c_port          = None
    deployment      = None
    api_instance    = None
    namespace       = None
    
    '''
    name, image.replicas, app
    '''
    def __init__(self,**kwargs):
        
        self.logger=getLogger()
        
        if kwargs:
            
            if 'create_deployer' in kwargs and kwargs['create_deployer']:
                for a in self.all_attr:
                    if a not in kwargs.keys() or kwargs.get(a) is None:
                        self.logger.error("Faltan argumentos: %s" % (a))
                        raise ValueError("Faltan argumentos: %s" % (a))
            
                self._assign_vars(kwargs)
            
        if 'config_file' in kwargs and kwargs['config_file']:       
            self.config_file  = kwargs.get("config_file")
        else:
            self.logger.error("Faltan argumentos: %s" % (a))
            raise ValueError("fichero de configuracion requerido")

        self.logger.error("Iniciando configuracion de kubernates")
        config.load_kube_config(self.config_file) 
        self.logger.error("Iniciacion correcta, cliente ok")
        
        
        

    def _assign_vars(self,kwargs):
        
        self.deployment_name = kwargs.get("deployment_name")
        self.image           = kwargs.get("image")
        self.name            = kwargs.get("name")
        self.app             = kwargs.get("app")
        self.replicas        = kwargs.get("replicas")
        self.c_port          = kwargs.get("c_port")        
    
    def create_deployment_object(self):
        
        # Configureate Pod template container
        container = client.V1Container(
            name  = self.name, #"nginx",
            image = self.image, #"nginx:1.7.9",
            ports = [client.V1ContainerPort(container_port=self.c_port)])
        
        # Create and configurate a spec section
        template  = client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": self.app}),
                    spec=client.V1PodSpec(containers=[container]))
        # Create the specification of deployment
        spec      = client.ExtensionsV1beta1DeploymentSpec(
                    replicas=self.replicas,
                    template=template)
        
        # Instantiate the deployment object
        self.deployment = client.ExtensionsV1beta1Deployment(
            api_version="extensions/v1beta1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=self.deployment_name),
            spec=spec)
    
        return self.deployment
    
    
    def create_deployment(self, namespace="default"):
        # Create deployement
        api_response = self.api_instance.create_namespaced_deployment(
            body=self.deployment,
            namespace=namespace)
        
        self.logger.info ("Deployment created. status='%s'" % str(api_response.status))
    
    
    def update_deployment(self, namespace="default"):
        
        # Update container image
        self.deployment.spec.template.spec.containers[0].image = "nginx:1.9.1"
        # Update the deployment
        api_response = self.api_instance.patch_namespaced_deployment(
            name=self.deployment_name,
            namespace=namespace,
            body=self.deployment)
        
        self.logger.info ("Deployment updated. status='%s'" % str(api_response.status))
    
    
    def delete_deployment(self,namespace="default"):
        # Delete deployment
        api_response =  self.api_instance.delete_namespaced_deployment(
                        name=self.deployment_name,
                        namespace=namespace,
                        body=client.V1DeleteOptions(
                                        propagation_policy='Foreground',
                                        grace_period_seconds=5
                                )
                        )
        
        self.logger.info("Deployment deleted. status='%s'" % str(api_response.status))

    '''
     0 replicas -> replegar
     
    '''
    def modify_replicas_deployment(self,replicas=0):
        
        #self.deployment.spec.template.spec.containers[0].image = "nginx:1.9.1"
        self.replicas= replicas if replicas else self.replicas
        self.deployment.spec.replicas = self.replicas
        
        api_response =self.api_instance.patch_namespaced_deployment(
                      name=self.deployment_name,
                      namespace=self.namespace,
                      body=self.deployment)
        
        self.logger.info ("Deployment updated. status='%s'" % str(api_response.status))

        
        
    def get_api_instance(self,api_instance):
        
        api_dict={
                    'ExtensionsV1beta1Api': client.ExtensionsV1beta1Api(),
                    'ExtensionsV1beta1Deployment': client.ExtensionsV1beta1Deployment(),
                    'AppsV1Api' : client.AppsV1beta1Api()
                  }
        
        if api_instance and api_instance in api_dict:
            self.api_instance=api_dict[api_instance]
            return True
        
        self.logger.info ("Error al crear la instancia del API de Kubernates: %s" % api_instance)
        raise ValueError ("Error al crear la instancia del API de Kubernates")
    
    
    def getNamespacedDeployment(self, deployment_name=None, namespace="default", replicas=0):
        
        try: 
            self.get_api_instance('ExtensionsV1beta1Api')
            
            # Obtenemos el deployment
            self.deployment_name= deployment_name if deployment_name else self.deployment_name
            self.namespace= namespace if namespace else self.namespace
            
            self.deployment = self.api_instance.read_namespaced_deployment(deployment_name, namespace)

            return self.deployment
            
        except ApiException as e:
            self.logger.info ("Error al crear la instancia del API de Kubernates")

if __name__ == '__main__':
    
    config.load_kube_config()
    extensions_v1beta1 = client.ExtensionsV1beta1Api()
    # Create a deployment object with client-python API. The deployment we
    # created is same as the `nginx-deployment.yaml` in the /examples folder.
    '''
    kwargs= { 'config_file': '/var/www/media/mi_config_entorno', 'create_deployer' : True, 
              'name'     : 'nginx' ,  'image':'nginx:1.7.9', 
              'c_port'   : 80      ,  'app':"nginx", 
              'replicas' : 3       ,  'deployment_name': 'nginx-deployment'
            }
    '''
    
    kwargs= { 'config_file': '/var/www/media/mi_config_entorno'        }
    
        
    dpl= Deployment(**kwargs)
    #deployment= dpl.create_deployment_object()
    dpl.get_api_instance('ExtensionsV1beta1Api')
    #dpl.create_deployment('blank')

    '''hay q parametrizar el metodo con los distintos update'''
    #dpl.update_deployment('blank')
    #dpl.delete_deployment('blank')
    dpl.getNamespacedDeployment('nginx-deployment','blank')
    dpl.modify_replicas_deployment(3)
    #dpl.retract_deployment('blank')

    