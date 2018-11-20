from django import forms
from portal.models import AfIncidencia, AfEstadosIncidencia,AfNotasIncidencia
from django.utils.translation import ugettext as _


class IncidenciasForm(forms.ModelForm):
    
    asunto = forms.CharField(max_length=250,label='Asunto')
    cuerpo = forms.CharField(max_length=1000,label='Cuerpo',widget=forms.Textarea (attrs={'rows':5, 'cols':20}))
    
    class Meta:
        model=AfIncidencia
        fields= ('asunto','cuerpo')
    

    
class AfNotasIncidenciaForm(forms.ModelForm):
    
    asunto = forms.CharField(max_length=250,label='Asunto')
    notas = forms.CharField(max_length=1000,label='Nota',widget=forms.Textarea (attrs={'rows':10, 'cols':20}))
    estado = forms.ModelChoiceField(queryset=AfEstadosIncidencia.objects.all())
    
    class Meta:
        model=AfNotasIncidencia
        fields= ('asunto','notas')

    def __init__(self, *args, **kwargs):
        super(AfNotasIncidenciaForm, self).__init__(*args, **kwargs)
        if len(kwargs):
            if 'initial' in kwargs and 'instance' in kwargs['initial']:
                #rel_it_estado=AfRelIncidenciaEstado.objects.get(incidencia=kwargs['initial']['instance'].id)
                self.fields['estado'].initial= kwargs['initial']['instance'].estado
                if kwargs['initial']['status_ro']:
                    self.fields['estado'].widget.attrs['disabled'] = 'disabled'
        