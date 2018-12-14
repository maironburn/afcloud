# coding=utf-8

from __future__ import unicode_literals
from django.utils.translation import ugettext as _
from django import forms
from portal.models import AfEntorno, AfProyecto

   
class DisponibilidadForm(forms.Form):
    
    #proyecto             = forms.CharField(label='Proyecto', max_length=100)
    porcentaje  = forms.IntegerField(min_value = 1, max_value=100, label="Porcentaje de disponibilidad")
    entornos    = forms.ModelChoiceField(queryset= AfEntorno.objects.all())
    #available_widgets    = forms.ChoiceField(choices=widget_list)
    


    
         

   




            
        

             
        

 