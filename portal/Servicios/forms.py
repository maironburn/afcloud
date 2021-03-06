from portal.models import AfServicio
from django.utils.translation import ugettext as _
from django import forms




class ServicioForm(forms.ModelForm):

    ser_descripcion  = forms.CharField( max_length=250, label='Descripción',widget=forms.Textarea (attrs={'rows':2, 'cols':15}))
    ser_yaml_file    = forms.FileField(label='Deployment yaml')
    ser_min_replicas = forms.IntegerField(min_value=1,max_value=5, label='Mínimo de réplicas: ')
    ser_max_replicas = forms.IntegerField(min_value=1,max_value=5, label='Máximo de réplicas: ')

    class Meta:
        model = AfServicio
        fields=('ser_nombre','ser_descripcion','ser_tarifa', 'ser_activo','ser_yaml_file', 'ser_min_replicas', 'ser_max_replicas')

    def is_valid(self):
        
        valid = super(ServicioForm, self).is_valid() 
        
        return valid and self.data['ser_min_replicas']<=self.data['ser_max_replicas']

    def setConfigfile(self,fichero):
        try:
            self.ser_yaml_file=fichero
        except Exception as e:
            pass
