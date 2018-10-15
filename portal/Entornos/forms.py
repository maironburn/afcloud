from django import forms
from portal.models import AfEntorno
from django.utils.translation import ugettext as _

#class EntornoForm(forms.Form):

class EntornoForm(forms.ModelForm):    
    #usuario   = forms.CharField(max_length=100,label='Nombre de Usuario')
    ent_nombre    = forms.CharField(max_length=100,label='Nombre',required=True)
    ent_descripcion= forms.CharField( max_length=250, label='Descripción',widget=forms.Textarea ,required=False)
    ent_uri = forms.URLField(initial="http://",label='URI',required = False)
    #ent_username   = forms.CharField(max_length=50,label='Username',widget = forms.TextInput,required = False)
    #ent_password = forms.CharField(label=_("Contraseña"), widget=forms.PasswordInput, required=False)
    ent_activo= forms.BooleanField(label=_("Entorno activo"), initial=True,required=False)
    ent_config_file = forms.FileField(label='Entorno de Kubernates')
    connection=False
    
    error_messages = {
        'kubernates_conx_error': _("Por favor introduzca un usuario correcto %(username)s y su contraseña. "
                           "Tenga en cuenta que ambos campos son sensibles a las mayusculas."),
        'inactive': _("Esta cuenta se encuentra inactiva."),
    }
    class Meta:
        model = AfEntorno
        fields = '__all__'
        
    def setConOkStatus(self):
        self.connection=True
        
    def is_valid(self):
        valid = super(EntornoForm, self).is_valid()
        
        '''validacion adicional
        if valid:
            if self.connection:
                return True
        '''
        return valid and self.connection
        
    def setConfigfile(self,fichero):
        self.ent_config_file=fichero        
        