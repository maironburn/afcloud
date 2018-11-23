# coding=utf-8

from __future__ import unicode_literals
from django.utils.translation import ugettext as _
from django import forms
from portal.models import AfEntorno
from django.contrib.auth.models import User
from django.contrib.admin import widgets

        
class MonitoringForm(forms.Form):
    
    #proyecto             = forms.CharField(label='Proyecto', max_length=100)
    entornos             = forms.ModelChoiceField(queryset= AfEntorno.objects.all())
    #widget_list          = ['Uso de CPU','Uso de Memoria', 'Uso de Disco']
    widget_list = (
    ('1', 'Uso de CPU_1'),
    ('2', 'Uso de Memoria'),
    ('3', 'Uso de Disco'),
    ('4', 'Widget4'),
    ('5', 'Widget5'),
    ('6', 'Widget6'),
    ('7', 'Widget7'),
    ('8', 'Widget8'),
    
)
    
    available_widgets    = forms.ChoiceField(choices=widget_list)
    
    available_widgets = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=widget_list,
    )
    '''
    error_messages = {
        'password_mismatch': _("Las contraseñas no son las mismas."),
    }
    '''
    
 
    def __init__(self, *args, **kwargs):
        super(MonitoringForm, self).__init__(*args, **kwargs)
        if len(kwargs):
            if 'initial' in kwargs and 'user_queryset' in  kwargs['initial']:
                self.fields['user'].queryset = kwargs['initial']['user_queryset']
            if 'initial' in kwargs  and 'user' in kwargs['initial'] and 'tperfil' in kwargs['initial']:
                self.user=kwargs['initial']['user']
                self.perfil=kwargs['initial']['tperfil']
                
    def is_valid(self):
        return  isinstance(self.user, AfUsuario) and  isinstance(self.perfil, AfTipoPerfil)



            
        

 