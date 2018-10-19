from django import forms
from portal.models import AfEntorno
from django.utils.translation import ugettext as _

#class EntornoForm(forms.Form):

class GlobalConfForm(forms.Form):    

    global_config_crt_file = forms.FileField(label='Fichero del certificado ')
    global_config_key_file = forms.FileField(label='Fichero del key')
    connection=False
    
    error_messages = {
        'kubernates_conx_error': _("Por favor introduzca un usuario correcto %(username)s y su contraseña. "
                           "Tenga en cuenta que ambos campos son sensibles a las mayusculas."),
        'inactive': _("Esta cuenta se encuentra inactiva."),
    }


    def is_valid(self):
        valid = super(GlobalConfForm, self).is_valid()
        
        '''validacion adicional
        if valid:
            if self.connection:
                return True
        '''
        return valid 
        
        