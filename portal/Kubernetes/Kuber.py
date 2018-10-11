from kubernetes import client, config, watch
import yaml
import sys
from os import path
import yaml
from portal.Utils.logger import *
sys.path.insert(0, '../')



class KuberConnectionFail(Exception):
    pass


class Kuber(object):

    v1=None
    config_file=None
    logger= None
    
    def __init__(self,fichero):
        self.logger=getLogger()
        if fichero:
            self.config_file=fichero
            self.checkConfigFile(self.config_file)
            if not self.v1 or self.checkConnection():
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
                config.load_kube_config(file)
                self.config_file=file
                self.v1 = client.CoreV1Api()
            return True

        except Exception as e:
            self.logger.error("Error en la config del fichero de Kb: %s" % format('%s' % e))

        return False


    def getClient(self):
        return self.v1

    def checkConnection(self):

        try:
            print("Listing pods with their IPs:")
            ret = self.v1.list_pod_for_all_namespaces(watch=False)
            for i in ret.items:
                print("%s\t%s\t%s" %
                  (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
            return True

        except Exception:
            pass

        return False


    def createDeployment(self,fichero_yaml, target_namespace):

        with open(path.join(path.dirname(__file__), fichero_yaml)) as f:
            dep = yaml.load(fichero_yaml)
            k8s_beta = client.ExtensionsV1beta1Api()
            resp = k8s_beta.create_namespaced_deployment(
                body=dep, namespace=target_namespace)
            print("Deployment created. status='%s'" % str(resp.status))
