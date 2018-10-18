# coding=utf-8

from __future__ import unicode_literals
from django.utils.translation import ugettext as _
from django import forms
from portal.models import AfUsuario,AfTipoPerfil, AfServicio, AfLineaCatalogo,AfProyecto
from django.contrib.auth.models import User
from django.contrib.admin import widgets


class MyModelChoiceCatalogo(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.ser_nombre
    


        
class CatalogRawForm(forms.ModelForm):
    
    exclude=None
    proyecto=None
    yaml_service=None
    
    ser   = MyModelChoiceCatalogo(label="Servicio",queryset=(AfLineaCatalogo.objects.all()) ,empty_label="(Seleccione servicio)")
    
    lca_tarifa = forms.DecimalField(max_digits=10, label="Tarifa", decimal_places=2,required=True)
    lca_activo=forms.BooleanField(label=_("Activo"), initial=True,required=False)
    '''
    error_messages = {
        'password_mismatch': _("Las contraseñas no son las mismas."),
    }
    '''
    class Meta:
        model=AfLineaCatalogo
        fields= ('ser','lca_tarifa','lca_activo')
    

    def __init__(self, *args, **kwargs):
        super(CatalogRawForm, self).__init__(*args, **kwargs)
        if len(kwargs):
            if 'initial' in kwargs and 'service_queryset' in  kwargs['initial']:
                self.fields['ser'].queryset = kwargs['initial']['service_queryset']
            if 'instance' in kwargs:
                self.ser=kwargs['instance'].ser
                self.lca_tarifa= kwargs['instance'].lca_tarifa
                self.lca_activo= kwargs['instance'].lca_activo
                
        if len(args) and args[0]:
            self.ser=AfServicio.objects.get(id=args[0]['ser'])
            self.yaml_service=self.ser.ser_yaml_file
            self.lca_tarifa=args[0]['lca_tarifa']
            self.lca_activo= True if args[0]['lca_activo']=='on' else False
           
       
    
    def setProyect(self,id_proyecto):
        self.proyecto=AfProyecto.objects.get(id=id_proyecto)
     
        
    def getNamespace(self):
        if self.proyecto:
            return self.proyecto.pro_nombre
        
        return None
    
    def is_valid(self):
        return  isinstance(self.ser, AfServicio) and  self.lca_tarifa
    
    def getYaml(self):
        return self.yaml_service

    def save(self):
        instance =AfLineaCatalogo.objects.create(pro=self.proyecto, ser=self.ser, lca_tarifa=self.lca_tarifa, lca_activo=self.lca_activo)
        return instance  
      
        

class MyModelEditChoiceCatalogo(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.ser_nombre
    


        
class editCatalogRawForm(forms.ModelForm):
    
    exclude=None
    proyecto=None
    ser   = MyModelEditChoiceCatalogo(label="Servicio",queryset=(AfServicio.objects.all()) ,empty_label="(Seleccione servicio)")
    
    lca_tarifa = forms.DecimalField(max_digits=10, label="Tarifa", decimal_places=2,required=True)
    lca_activo=forms.BooleanField(label=_("Activo"), initial=True,required=False)
    '''
    error_messages = {
        'password_mismatch': _("Las contraseñas no son las mismas."),
    }
    '''
    class Meta:
        model=AfLineaCatalogo
        fields= ('ser','lca_tarifa','lca_activo')
    

    def __init__(self, *args, **kwargs):
        super(editCatalogRawForm, self).__init__(*args, **kwargs)
        if len(kwargs):
            if 'instance' in kwargs:
                self.ser=kwargs['instance'].ser
                self.lca_tarifa= kwargs['instance'].lca_tarifa
                self.lca_activo= kwargs['instance'].lca_activo
                
       
           
    def setProyect(self,id_proyecto):
        self.proyecto=AfProyecto.objects.get(id=id_proyecto)
         
    def is_valid(self):
        return  isinstance(self.ser, AfServicio) and  self.lca_tarifa
    

      
        

         

 