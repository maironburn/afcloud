
from django import forms
from portal.models import AfProyecto, AfEntorno,AfRelEntPro
from django.forms.models import ModelForm
from django.utils.translation import ugettext as _
from portal.Kubernetes.Kuber import Kuber

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
        fields='__all__'
    
    
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
                self.fields['entornos'].initial=kwargs['initial']['entornos']
            #self.fields['entornos'].queryset=AfEntorno.objects.all()


    def saveProyect(self, accion, proyecto=None):
        #proyecto=AfProyecto(pro_nombre=self.nombre, pro_descripcion=self.descripcion)
        if accion=='new':
            proyecto= AfProyecto.objects.create(pro_nombre=self.pro_nombre, pro_descripcion=self.pro_descripcion, pro_activo=self.pro_activo)

        vinculados=AfRelEntPro.objects.filter(pro=proyecto)
        '''
        -borrar de la BBDD las relaciones entornos proyectos
        -conexion con KB y borrado del namespace correspondiente
        '''
        for v in vinculados:
            kuber=Kuber (v.ent.ent_config_file.path)
            kuber.deleteNamespace(self.pro_nombre)
            v.delete()
            
        '''
        -Creacion de las nuevas relaciones entorno proyecto
        -conexion con KB y creacion del namespace correspondiente
        '''            
        for ep in self.entornos_associated:
            afep=AfRelEntPro.objects.create(ent=ep, pro=proyecto)        
            kuber=Kuber (ep.ent_config_file.path)
            kuber.createNameSpace(self.pro_nombre)
            
            #kuber.create_namespaced_ingress(proyecto.pro_nombre)
            #afep.save()
        
       
    def saveRelations(self, instance):
        #proyecto=AfProyecto(pro_nombre=self.nombre, pro_descripcion=self.descripcion)
 
        for ep in self.entornos_associated:
            afep=AfRelEntPro.objects.create(ent=ep, pro=instance)
            afep.save()
        
      
              
    def get_entornos(self):
        return self.entornos_associated
    


class editProyectoForm(forms.ModelForm):
    
    pro_nombre = forms.CharField(max_length=100, label='Nombre')
    pro_descripcion= forms.CharField( max_length=250, label='Descripción',widget=forms.Textarea )
    pro_activo=forms.BooleanField(label=_("Proyecto activo"), initial=True,required=False)
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
        #self.fields['entornos'].initial=kwargs['entornos']
        if len(kwargs):
            if 'initial' in kwargs:
                self.fields['entornos'].queryset=AfEntorno.objects.all()
                self.fields['entornos'].initial=kwargs['initial']['entornos']
                self.pro_nombre=kwargs['instance'].pro_nombre
                self.pro_descripcion=kwargs['instance'].pro_descripcion
                self.pro_activo=kwargs['instance'].pro_activo
                
        


    def saveProyect(self, data,instancia):
        #proyecto=AfProyecto(pro_nombre=self.nombre, pro_descripcion=self.descripcion)
        instancia.pro_nombre=data['pro_nombre']
        instancia.pro_descripcion=data['pro_descripcion']
        instancia.pro_activo=data['pro_activo']
        
        vinculados=AfRelEntPro.objects.filter(pro=instancia)
        for v in vinculados:
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
    
    
