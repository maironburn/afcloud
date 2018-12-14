# coding=utf-8

from __future__ import unicode_literals
from django.utils.translation import ugettext as _
from django import forms
from portal.models import AfUsuario,AfTipoPerfil, AfPerfil
from django.contrib.auth.models import User
from django.contrib.admin import widgets


class MyModelChoiceFieldUser(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.user.username
    


class MyModelChoiceFieldPerfil(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.tpe_nombre
    
        
class IntegrantesRawForm(forms.ModelForm):
    
    exclude=None
    user   = MyModelChoiceFieldUser(label="Usuario",queryset=(AfUsuario.objects.all()) ,empty_label="(Seleccione usuario)")
    
    perfil = MyModelChoiceFieldPerfil(queryset=(AfTipoPerfil.objects.all()),empty_label="(Seleccione perfil)")
    '''
    error_messages = {
        'password_mismatch': _("Las contraseñas no son las mismas."),
    }
    '''
    class Meta:
        model=AfUsuario
        fields= ('user',)
    
 
    def __init__(self, *args, **kwargs):
        super(IntegrantesRawForm, self).__init__(*args, **kwargs)
        if len(kwargs):
            if 'initial' in kwargs and 'user_queryset' in  kwargs['initial']:
                self.fields['user'].queryset = kwargs['initial']['user_queryset']
            if 'initial' in kwargs  and 'user' in kwargs['initial'] and 'tperfil' in kwargs['initial']:
                self.user=kwargs['initial']['user']
                self.perfil=kwargs['initial']['tperfil']
                self.fields['perfil'].initial=kwargs['initial']['tperfil']
                
    def is_valid(self):
        return  isinstance(self.user, AfUsuario) and  isinstance(self.perfil, AfTipoPerfil)


    def save(self,user,tperfil,proyecto):
        
        af_perfil=AfPerfil.objects.create(usu=user, pro=proyecto,tpe=tperfil,per_activo=True)
        return af_perfil
            
        

 