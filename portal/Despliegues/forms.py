# coding=utf-8

from __future__ import unicode_literals
from django.utils.translation import ugettext as _
from django import forms
from portal.models import AfUsuario,AfTipoPerfil, AfServicio, AfEntorno,AfInstancia,\
    AfRelEntPro
from django.contrib.auth.models import User
from django.contrib.admin import widgets
from softwareproperties.ppa import CurlCallback


class MyModelChoiceFieldService(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.ent.ent_nombre
    


class MyModelChoiceFieldEntorno(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.ent_nombre
    
  

class createMyModelChoiceFieldService(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.ser_nombre
    


class createMyModelChoiceFieldEntorno(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        if isinstance(obj, AfEntorno):
            return obj.ent_nombre
        
        return obj.ent.ent_nombre
    
            
class InstanciaForm(forms.Form):
    
    exclude=None
    service          = createMyModelChoiceFieldService(label="Servicio",queryset=(AfServicio.objects.filter(ser_deleted=False)) ,empty_label="(Seleccione servicio)",required=True)
    entorno          = createMyModelChoiceFieldEntorno(queryset=(AfEntorno.objects.filter(ent_activo=True)), empty_label="(Seleccione entorno)",required=True)
    ins_unique_name  = forms.CharField(max_length=100,label='Nombre del Despliegue',required=True) 
    ser_min_replicas = forms.IntegerField(min_value=0,max_value=5 , label='Mínimo de réplicas: ')
    ser_max_replicas = forms.IntegerField(min_value=0,max_value=10, label='Máximo de réplicas: ')
    
    
    '''
    error_messages = {
        'password_mismatch': _("Las contraseñas no son las mismas."),
    }
    '''

    
 
    def __init__(self, *args, **kwargs):
        super(InstanciaForm, self).__init__(*args, **kwargs)
        
        if len(args):
            if 'entorno_queryset' in args[0] :
                self.fields['entorno'].queryset = args[0]['entorno_queryset']
            if 'service_queryset' in args[0] :
                self.fields['service'].queryset = args[0]['service_queryset']
        if len(kwargs):
            
            if 'initial' in kwargs and 'instance' in kwargs['initial']:
                self.service=kwargs['initial']['service']
                self.entorno=kwargs['initial']['entorno']
                
                            
                
    def is_valid(self):
        return  isinstance(self.user, AfUsuario) and  isinstance(self.perfil, AfTipoPerfil)

                
            
        
   
        
class creaInstanciaForm(forms.Form):
    
    exclude=None
    service          = MyModelChoiceFieldService(label="Servicio",queryset=(AfServicio.objects.filter(ser_deleted=False)) ,empty_label="(Seleccione servicio)")
    entorno          = MyModelChoiceFieldEntorno(queryset=(AfEntorno.objects.all()),empty_label="(Seleccione entorno)")
    ins_unique_name  = forms.CharField(max_length=100,label='Nombre del Despliegue',required=True) 
    ser_min_replicas = forms.IntegerField(min_value=0,max_value=5 , label='Mínimo de réplicas: ')
    ser_max_replicas = forms.IntegerField(min_value=0,max_value=10, label='Máximo de réplicas: ')
    
    catalogo=None
    '''
    error_messages = {
        'password_mismatch': _("Las contraseñas no son las mismas."),
    }
    '''

    
 
    def __init__(self, *args, **kwargs):
        super(creaInstanciaForm, self).__init__(*args, **kwargs)
        
        if len(args):
            if 'service' in args[0] and  args[0]['service']:
                self.service = AfServicio.objects.get(id=args[0]['service'])
                self.entorno = AfRelEntPro.objects.get(id=args[0]['entorno'])
        if len(kwargs):
            
            if 'instance' in kwargs:
                self.service=kwargs['instance'].service
                self.entorno= kwargs['instance'].ent
                            
    def setServicio(self,servicio):
        self.service=servicio

    def getServicio(self):
        return self.service
    
    def setEntorno(self,entorno):
        self.entorno=entorno
        
    def getEntorno(self):
        return self.entorno
    
    def setLineaCatalogo(self,lca):
        self.catalogo=lca
        
    def is_valid(self):
        return  isinstance(self.service, AfServicio) and  isinstance(self.entorno, AfRelEntPro)

                
            
        

         

 
