
from django import forms
from portal.models import AfProyecto, AfEntorno,AfRelEntPro,AfGlobalconf
from django.forms.models import ModelForm
from django.utils.translation import ugettext as _
from portal.Kubernetes.Kuber import Kuber
from portal.Utils.aux_meth import *

#class ProyectoForm(forms.Form):
class ProyectoForm(forms.ModelForm):

    pro_nombre = forms.CharField(max_length=100, label='Nombre')
    pro_descripcion= forms.CharField( max_length=250, label='Descripción',widget=forms.Textarea )
    pro_activo=forms.BooleanField(label=_("Proyecto activo"), initial=True,required=False)

    entornos =forms.MultipleChoiceField(required=False,widget=forms.CheckboxSelectMultiple,
                                             choices=[ (choice.pk, choice.ent_nombre) for choice in AfEntorno.objects.all()])

    entornos_associated=[]


    class Meta:
        model=AfProyecto
        fields=('pro_nombre','pro_descripcion', 'pro_activo')


    def __init__(self, *args,**kwargs):
        self.entornos_associated=[]
        super(ProyectoForm, self).__init__(*args, **kwargs)
        #self.fields['entornos'].initial=kwargs['entornos']
        if len(args):

            if args[0] :
                self.pro_nombre=args[0].get('pro_nombre', None)
                self.pro_descripcion=args[0].get('pro_descripcion', None)
                self.pro_activo=True if args[0].get('pro_activo', None)=='on' else False

            if 'entornos' in args[0]:
                self.entornos=args[0].getlist('entornos')
                for e in self.entornos:
                    instance=AfEntorno.objects.get(id=e)
                    self.entornos_associated.append(instance)

        if len(kwargs):
            if 'initial' in kwargs:
                self.fields['entornos'].queryset=AfEntorno.objects.all()
                #self.fields['entornos'].initial=kwargs['initial']['entornos']
            #self.fields['entornos'].queryset=AfEntorno.objects.all()

        
    
    def is_valid(self):
        
        
        valid = super(ProyectoForm, self).is_valid() 
        
        return valid and len(self.entornos_associated)
    
                        
    def saveProyect(self, accion, proyecto=None):
        #proyecto=AfProyecto(pro_nombre=self.nombre, pro_descripcion=self.descripcion)
        if accion=='new':
            
            proyecto= AfProyecto.objects.create(pro_nombre=self.pro_nombre,pro_nombre_k8s=self.pro_nombre, pro_descripcion=self.pro_descripcion, pro_activo=self.pro_activo)

        vinculados=AfRelEntPro.objects.filter(pro=proyecto)
        '''
        -borrar de la BBDD las relaciones entornos proyectos
        -conexion con KB y borrado del namespace correspondiente
        '''
        for v in vinculados:
            '''
            kuber=Kuber (v.ent.ent_config_file.path)
            kuber.deleteNamespace(self.pro_nombre)
            '''
            #v.delete()
            pass

        '''
        -Creacion de las nuevas relaciones entorno proyecto
        -conexion con KB y creacion del namespace correspondiente
        '''
        for ep in self.entornos_associated:
            afep=AfRelEntPro.objects.create(ent=ep, pro=proyecto)
            
            kuber=Kuber (ep.ent_config_file.path)
            kuber.createNameSpace(self.pro_nombre)
            
            global_conf=AfGlobalconf.objects.first()
            crt = getFileEncodedB64(global_conf.crt_file.path)
            key = getFileEncodedB64(global_conf.key_file.path)
            
            dict_ingress={'fichero_yaml' : '/home/mdiaz-isotrol/eclipse-workspace/afcloud/afcloud/portal/Kuber_stuff/ingress_template.yaml', 
                          'namespace'    : self.pro_nombre, 
                          'fqdn'         : global_conf.fqdn,
                          'env_name'     : ep.ent_nombre,
                          'registry_hash': ep.registry_hash,
                          'crt'          : crt.decode("utf-8"),
                          'key'          : key.decode("utf-8") 
                          }
            kuber.loadIngressTemplate(dict_ingress)
            dict_ingress['fichero_yaml']='/home/mdiaz-isotrol/eclipse-workspace/afcloud/afcloud/portal/Kuber_stuff/secret_registry.yaml'
            kuber.create_namespaced_secretRegistry(dict_ingress)

            dict_ingress.update({
                                 'ingress-secret-template': '/home/mdiaz-isotrol/eclipse-workspace/afcloud/afcloud/portal/Kuber_stuff/ingress-secret-template.yaml'
                                 })
            
            kuber.create_namespaced_secretIngress(dict_ingress)
            #kuber.create_namespaced_ingress(proyecto.pro_nombre)
            afep.save()


    def saveRelations(self, instance):
        #proyecto=AfProyecto(pro_nombre=self.nombre, pro_descripcion=self.descripcion)
        for ep in self.entornos_associated:
            afep=AfRelEntPro.objects.create(ent=ep, pro=instance)
            afep.save()



    def get_entornos(self):
        return self.entornos_associated



class editProyectoForm(forms.ModelForm):

    pro_nombre      = forms.CharField(max_length=100, label='Nombre')
    pro_nombre_k8s  = forms.CharField(max_length=100, label='Nombre K8s', required=False)
    pro_descripcion = forms.CharField( max_length=250, label='Descripción',widget=forms.Textarea )
    pro_activo      = forms.BooleanField(label=_("Proyecto activo"), initial=True,required=False)
    '''
    entornos =forms.MultipleChoiceField(required=False,widget=forms.CheckboxSelectMultiple)#,
                                             #choices=[ (choice.pk, choice.ent_nombre) for choice in AfEntorno.objects.all()])
    '''
    entornos= forms.ModelMultipleChoiceField(required=False,widget=forms.CheckboxSelectMultiple, queryset=AfEntorno.objects.all())
    entornos_associated=[]


    class Meta:
        model=AfProyecto
        fields='__all__'


    def __init__(self, *args,**kwargs):

        self.entornos_associated=[]
        super(editProyectoForm, self).__init__(*args, **kwargs)
        self.fields['pro_nombre_k8s'].widget.attrs['readonly'] = True
        #self.fields['entornos'].initial=kwargs['entornos']
        if len(kwargs):
            if 'initial' in kwargs:
                self.fields['entornos'].queryset=AfEntorno.objects.all()
                self.fields['entornos'].initial=kwargs['initial']['entornos']
                self.pro_nombre=kwargs['instance'].pro_nombre
                self.pro_descripcion=kwargs['instance'].pro_descripcion
                self.pro_activo=kwargs['instance'].pro_activo



    def is_valid(self):
        
        valid = super(editProyectoForm, self).is_valid() 
        
        return valid #and len(self.entornos_associated)
    
    
    def saveProyect(self, data,instancia):
        #proyecto=AfProyecto(pro_nombre=self.nombre, pro_descripcion=self.descripcion)
        instancia.pro_nombre=data['pro_nombre']
        instancia.pro_descripcion=data['pro_descripcion']
        instancia.pro_activo=data['pro_activo']

        vinculados=AfRelEntPro.objects.filter(pro=instancia).values_list('ent', flat=True)
        to_delete=[x for x in list(vinculados) if str(x) not in data['entornos']]
        
        
        for v in to_delete:
            kuber=Kuber (v.ent.ent_config_file.path)
            #kuber.deleteNamespace(self.pro_nombre)
            kuber.patch_Namespace(self.pro_nombre)
            v.delete()
        
        for ep in data['entornos']:
            entorno=AfEntorno.objects.get(id=ep)
            afep=AfRelEntPro.objects.create(ent=entorno, pro=instancia)
            kuber=Kuber (entorno.ent_config_file.path)
            kuber.createNameSpace(self.pro_nombre)

        instancia.save()


    def saveRelations(self, instance):
        #proyecto=AfProyecto(pro_nombre=self.nombre, pro_descripcion=self.descripcion)

        for ep in self.entornos_associated:
            afep=AfRelEntPro.objects.create(ent=ep, pro=instance)
            afep.save()



    def get_entornos(self):
        return self.entornos_associated
