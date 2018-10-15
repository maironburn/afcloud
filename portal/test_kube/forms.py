from django import forms
from portal.models import AfEntorno
from django.utils.translation import ugettext as _

#class EntornoForm(forms.Form):

class EntornoTestForm(forms.Form):    

    ent_config_file = forms.FileField(label='Entorno de Kubernates')
    connection=False
    
    error_messages = {
        'kubernates_conx_error': _("Por favor introduzca un usuario correcto %(username)s y su contraseña. "
                           "Tenga en cuenta que ambos campos son sensibles a las mayusculas."),
        'inactive': _("Esta cuenta se encuentra inactiva."),
    }

    def setConOkStatus(self):
        self.connection=True
        
    def is_valid(self):
        valid = super(EntornoTestForm, self).is_valid()
        
        '''validacion adicional
        if valid:
            if self.connection:
                return True
        '''
        return valid and self.connection
        
        