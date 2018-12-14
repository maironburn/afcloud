# coding=utf-8

from __future__ import unicode_literals
from django.utils.translation import ugettext as _
from django import forms
from portal.models import AfEntorno, AfProyecto

from django.contrib.admin import widgets

widget_list = (
    ('4', 'Cluster Pod Usage'),
    ('5', 'Uptime'),
    ('6', 'Cluster Memory Usage'),
    ('7', 'Cluster Disk Usage'),
    ('9', 'Cluster Pod Capacity'),
    #('10', 'Cluster CPU Usage'),
    ('11', 'Cluster Mem Capacity'),
    ('12', 'Cluster Disk Capacity'),
    ('16', 'Deployment Replicas'),
    )        
class MonitoringForm(forms.Form):
    
    #proyecto             = forms.CharField(label='Proyecto', max_length=100)
    entornos             = forms.ModelChoiceField(queryset= AfEntorno.objects.all())
    available_widgets    = forms.ChoiceField(choices=widget_list)
    
    available_widgets = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=widget_list,
    )


                

class adminMonitoringChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.pro_nombre
    
         
class adminMonitoringForm(forms.Form):
    
    proyecto = adminMonitoringChoiceField(label="Proyecto / estado del cluster",queryset=(AfProyecto.objects.all()) ,empty_label="(Seleccione opción)")
    #proyecto             = forms.ModelChoiceField(queryset= AfProyecto.objects.all())
    entornos             = forms.ModelChoiceField(queryset= (AfEntorno.objects.all()))


    #available_widgets    = forms.ChoiceField(choices=widget_list)
    
    available_widgets = forms.MultipleChoiceField(label='Widgets disponibles',
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=widget_list,
    )
   
   



            
        

             
        

 