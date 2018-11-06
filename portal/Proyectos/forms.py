
from django import forms
from portal.models import AfProyecto, AfEntorno,AfRelEntPro,AfGlobalconf
from django.forms.models import ModelForm
from django.utils.translation import ugettext as _
from portal.Kubernetes.Kuber import Kuber
from portal.Utils.aux_meth import *
from afcloud.settings import BASE_DIR, KUBER_TEMPLATES
from portal.Utils import *

#class ProyectoForm(forms.Form):
class ProyectoForm(forms.ModelForm):

    pro_nombre = forms.CharField(max_length=100, label='Nombre')
    pro_descripcion= forms.CharField( max_length=250, label='Descripción',widget=forms.Textarea (attrs={'rows':4, 'cols':15}))
    pro_activo=forms.BooleanField(label=_("Proyecto activo"), initial=True,required=False)

    entornos =forms.MultipleChoiceField(required=False,widget=forms.CheckboxSelectMultiple,
                                             choices=[ (choice.pk, choice.ent_nombre) for choice in AfEntorno.objects.all()])

    entornos_associated=[]


    class Meta:
        model=AfProyecto
        fields=('pro_nombre','pro_descripcion', 'pro_activo')


    def __init__(self, *args,**kwargs):
        self.entornos_associated=[]
        
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
        super(ProyectoForm, self).__init__(*args, **kwargs)
        '''
        if len(kwargs):
            if 'initial' in kwargs:
                self.fields['entornos'].queryset=AfEntorno.objects.all()
                self.fields['entornos'].initial=kwargs['initial']['entornos']
        '''
    
    def is_valid(self):
        
        
        valid = super(ProyectoForm, self).is_valid() 
        
        return valid and len(self.entornos_associated)
    
                        
    def saveProyect(self, accion, proyecto=None):
        
        if accion=='new':    
            proyecto= AfProyecto.objects.create(pro_nombre=self.pro_nombre,pro_nombre_k8s=self.pro_nombre, pro_descripcion=self.pro_descripcion, pro_activo=self.pro_activo)

        '''
        - Creacion de las nuevas relaciones entorno proyecto
        - conexion con Kb8 
        - creacion del namespace correspondiente
        - secret de Ingress
        - secret de Registry
        - ingress del svc
        '''
        for ep in self.entornos_associated:
            
            kwargs={
                    'env_file_path' : ep.ent_config_file.path,
                    'namespace'     : self.pro_nombre,
                    'env_name'      : ep.ent_nombre,
                    'registry_hash' : ep.registry_hash
                    }
            
            if createNameSpaceStack(**kwargs):
                afep=AfRelEntPro.objects.create(ent=ep, pro=proyecto)
                afep.save()


    def saveRelations(self, instance):
        
        for ep in self.entornos_associated:
            afep=AfRelEntPro.objects.create(ent=ep, pro=instance)
            afep.save()



    def get_entornos(self):
        return self.entornos_associated



class editProyectoForm(forms.ModelForm):

    pro_nombre      = forms.CharField(max_length=100, label='Nombre')
    pro_nombre_k8s  = forms.CharField(max_length=100, label='Nombre K8s', required=False)
    pro_descripcion = forms.CharField( max_length=250, label='Descripción',widget=forms.Textarea (attrs={'rows':4, 'cols':15}))
    pro_activo      = forms.BooleanField(label=_("Proyecto activo"), initial=True,required=False)
    entornos= forms.ModelMultipleChoiceField(required=False,widget=forms.CheckboxSelectMultiple, queryset=AfEntorno.objects.all())
    entornos_associated=[]


    class Meta:
        model=AfProyecto
        fields='__all__'


    def __init__(self, *args,**kwargs):

        self.entornos_associated=[]
        super(editProyectoForm, self).__init__(*args, **kwargs)
        self.fields['pro_nombre_k8s'].widget.attrs['readonly'] = True
        
        if len(kwargs):
            if 'initial' in kwargs:
                self.fields['entornos'].queryset=AfEntorno.objects.all()
                self.fields['entornos'].initial=kwargs['initial']['entornos']
                self.pro_nombre=kwargs['instance'].pro_nombre
                self.pro_descripcion=kwargs['instance'].pro_descripcion
                self.pro_activo=kwargs['instance'].pro_activo


        if len(args) and args[0] is not None:
            if 'entornos' in args[0] :
                self.entornos=args[0].getlist('entornos')


    def is_valid(self):
        
        valid = super(editProyectoForm, self).is_valid() 
        
        return valid and (len(self.entornos_associated) or len(self.entornos))
    
    
    def saveProyect(self, data,instancia):
        
        instancia.pro_nombre=data['pro_nombre']
        instancia.pro_descripcion=data['pro_descripcion']
        instancia.pro_activo=data['pro_activo']

        vinculados=AfRelEntPro.objects.filter(pro=instancia).values_list('ent', flat=True)
        to_delete = [x for x in list(vinculados) if str(x) not in data['entornos']]
        to_add    = [x for x in data['entornos'] if int(x) not in list(vinculados)]
        
        for v in to_delete:
            entorno=AfEntorno.objects.get(id=v)
            kuber=Kuber (entorno.ent_config_file.path)
            kuber.delete_namespace(self.pro_nombre)
            
            ent_pro= AfRelEntPro.objects.filter(ent=entorno, pro=instancia)
            for ep in list(ent_pro):
                instancias=AfInstancia.objects.filter(rep=ep)
                for i in list(instancias):
                    print('trying to delete pv: %s-pv' % (i.ins_unique_name,))
                    kuber.delete_persistent_volume({'unique_instance_name': i.ins_unique_name})
                ep.delete()
            
                    
        for v in to_add:
            
            entorno=AfEntorno.objects.get(id=v)
            kwargs={
                    'env_file_path' : entorno.ent_config_file.path,
                    'namespace'     : instancia.pro_nombre,
                    'env_name'      : entorno.ent_nombre,
                    'registry_hash' : entorno.registry_hash
                    }
                        
            if createNameSpaceStack(**kwargs):
                afep=AfRelEntPro.objects.create(ent=entorno, pro=instancia)
                afep.save()
            
        instancia.save()


    def saveRelations(self, instance):
        
        for ep in self.entornos_associated:
            afep=AfRelEntPro.objects.create(ent=ep, pro=instance)
            afep.save()


    def get_entornos(self):
        return self.entornos_associated
