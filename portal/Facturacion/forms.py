# coding=utf-8

from __future__ import unicode_literals
from django.utils.translation import ugettext as _
from django import forms
from portal.models import AfEntorno, AfProyecto

   
class FacturacionForm(forms.Form):
    
    #proyecto             = forms.CharField(label='Proyecto', max_length=100)
    entornos             = forms.ModelChoiceField(queryset= AfEntorno.objects.all())
    #available_widgets    = forms.ChoiceField(choices=widget_list)
    


    
         

   




            
        

             
        

 