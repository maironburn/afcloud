from django import forms
from portal.models import AfIncidencia, AfEstadosIncidencia, AfRelIncidenciaEstado,AfNotasIncidencia
from django.utils.translation import ugettext as _


class IncidenciasForm(forms.ModelForm):
    
    asunto = forms.CharField(max_length=250,label='Asunto')
    cuerpo = forms.CharField(max_length=1000,label='Cuerpo',widget=forms.Textarea (attrs={'rows':5, 'cols':20}))
    
    class Meta:
        model=AfIncidencia
        fields= ('asunto','cuerpo')
    

class IncidenciasEditForm(forms.ModelForm):
    
    asunto = forms.CharField(max_length=250,label='Asunto')
    cuerpo = forms.CharField(max_length=1000,label='Actuacion',widget=forms.Textarea (attrs={'rows':10, 'cols':20}))
    estado = forms.ModelChoiceField(queryset=AfEstadosIncidencia.objects.all())
    
    class Meta:
        model=AfIncidencia
        fields= ('asunto','cuerpo')
        
 
    def __init__(self, *args, **kwargs):
        super(IncidenciasEditForm, self).__init__(*args, **kwargs)
        if len(kwargs):
            
            if 'instance' in kwargs:
                rel_it_estado=AfRelIncidenciaEstado.objects.get(incidencia=kwargs['instance'].id)
                self.fields['estado'].initial=AfEstadosIncidencia.objects.get(id=rel_it_estado.estado.id)

    
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
                rel_it_estado=AfRelIncidenciaEstado.objects.get(incidencia=kwargs['initial']['instance'].id)
                self.fields['estado'].initial=AfEstadosIncidencia.objects.get(id=rel_it_estado.estado.id)
                if kwargs['initial']['status_ro']:
                    self.fields['estado'].widget.attrs['disabled'] = 'disabled'
        