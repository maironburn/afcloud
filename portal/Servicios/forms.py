from portal.models import AfServicio
from django.utils.translation import ugettext as _
from django import forms


class ServicioForm(forms.ModelForm):

    ser_descripcion= forms.CharField( max_length=250, label='Descripción',widget=forms.Textarea )
    
    class Meta:
        model = AfServicio
        fields=('ser_nombre','ser_descripcion','ser_tarifa', 'ser_activo')
        #exclude = ('user','usu_username',)

