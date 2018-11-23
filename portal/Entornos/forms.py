from django import forms
from portal.models import AfEntorno
from django.utils.translation import ugettext as _

class EntornoForm(forms.ModelForm):

    ent_nombre      = forms.CharField(max_length=100,label='Nombre',required=True)
    ent_descripcion = forms.CharField( max_length=250, label='Descripción',widget=forms.Textarea(attrs={'rows':2, 'cols':15}) ,required=False)
    ent_activo      = forms.BooleanField(label=_("Entorno activo"), initial=True,required=False)
    ent_config_file = forms.FileField(label='Configuración cluster')
    ent_json_file   = forms.FileField(label='Configuración registry (json)')
    registry_hash   = forms.CharField(max_length=1000,label='Registry Hash',disabled=True,required=False)
    nfs_server      = forms.GenericIPAddressField(max_length=1000,label='Nfs server',disabled=True,required=False)
    connection=False
    
    error_messages = {
        'kubernates_conx_error': _("Por favor introduzca un usuario correcto %(username)s y su contraseña. "
                           "Tenga en cuenta que ambos campos son sensibles a las mayusculas."),
        'inactive': _("Esta cuenta se encuentra inactiva."),
    }
    class Meta:
        model = AfEntorno
        fields = ('ent_nombre', 'ent_descripcion', 'ent_activo',
                  'ent_config_file', 'ent_json_file',
                  'registry_hash', 'nfs_server')

    def __init__(self, *args, **kwargs):
        super(EntornoForm, self).__init__(*args, **kwargs)


    def setClusterIP (self,ip):
        self.cluster_ip=ip
        
    def setConOkStatus(self):
        self.connection=True

    def is_valid(self):

        valid = super(EntornoForm, self).is_valid()
        if not 'ent_config_file' in self.data:
            return valid
        return valid and self.connection 

    def setConfigfile(self,fichero):

        if fichero:
            self.ent_config_file=fichero
