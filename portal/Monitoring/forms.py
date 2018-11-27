# coding=utf-8

from __future__ import unicode_literals
from django.utils.translation import ugettext as _
from django import forms
from portal.models import AfEntorno, AfProyecto

from django.contrib.admin import widgets

        
class MonitoringForm(forms.Form):
    
    #proyecto             = forms.CharField(label='Proyecto', max_length=100)
    entornos             = forms.ModelChoiceField(queryset= AfEntorno.objects.all())
    #widget_list          = ['Uso de CPU','Uso de Memoria', 'Uso de Disco']
    widget_list = (
    ('4', 'Cluster Pod Usage'),
    ('5', 'Cluster CPU Usage'),
    ('6', 'Cluster Memory Usage'),
    ('7', 'Cluster Disk Usage'),
    ('9', 'Cluster Pod Capacity'),
    ('10', 'Cluster CPU Usage'),
    ('11', 'Cluster Mem Usage'),
    ('12', 'Cluster Disk Usage'),
    ('16', 'Deployment Replicas'),
    
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
                

class adminMonitoringChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.pro_nombre
    
         
class adminMonitoringForm(forms.Form):
    
    proyecto = adminMonitoringChoiceField(label="Servicio",queryset=(AfProyecto.objects.all()) ,empty_label="(Seleccione proyecto)")
    #proyecto             = forms.ModelChoiceField(queryset= AfProyecto.objects.all())
    entornos             = forms.ModelChoiceField(queryset= AfEntorno.objects.all())
    #widget_list          = ['Uso de CPU','Uso de Memoria', 'Uso de Disco']
    widget_list = (
    ('4', 'Cluster Pod Usage'),
    ('5', 'Cluster CPU Usage'),
    ('6', 'Cluster Memory Usage'),
    ('7', 'Cluster Disk Usage'),
    ('9', 'Cluster Pod Capacity'),
    ('10', 'Cluster CPU Usage'),
    ('11', 'Cluster Mem Usage'),
    ('12', 'Cluster Disk Usage'),
    ('16', 'Deployment Replicas'),
    
)
    
    #available_widgets    = forms.ChoiceField(choices=widget_list)
    
    available_widgets = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=widget_list,
    )
   
    error_messages = {
        'password_mismatch': _("Las contraseñas no son las mismas."),
    }
    
    
 
    def __init__(self, *args, **kwargs):
        super(adminMonitoringForm, self).__init__(*args, **kwargs)
        if len(kwargs):
            if 'initial' in kwargs and 'user_queryset' in  kwargs['initial']:
                self.fields['user'].queryset = kwargs['initial']['user_queryset']
            if 'initial' in kwargs  and 'user' in kwargs['initial'] and 'tperfil' in kwargs['initial']:
                self.user=kwargs['initial']['user']
                self.perfil=kwargs['initial']['tperfil']
                




            
        

             
        

 