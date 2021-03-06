from django import forms
from portal.models import AfGlobalconf 
from django.utils.translation import ugettext as _

#class EntornoForm(forms.Form):

class GlobalConfForm(forms.ModelForm):

    crt_file = forms.FileField(label='Fichero .crt ')
    key_file = forms.FileField(label='Fichero .key', required=False)
    fqdn     = forms.CharField(max_length=100,label='FQDN', help_text="Se creaa partir del .crt", initial="Autogenerado", disabled=True)
    email    = forms.EmailField()

    error_messages = {
        'kubernates_conx_error': _("Por favor introduzca un usuario correcto %(username)s y su contraseña. "
                           "Tenga en cuenta que ambos campos son sensibles a las mayusculas."),
        'inactive': _("Esta cuenta se encuentra inactiva."),
    }

    '''
    openssl x509 -noout -subject -in CA.crt |tr -d ' ' | cut -d ',' -f4| cut -d'=' -f2
    '''

    class Meta:
        model=AfGlobalconf
        fields= ('crt_file','key_file','fqdn', 'email')
    
    
    def __init__(self, *args, **kwargs):
        super(GlobalConfForm, self).__init__(*args, **kwargs)
        if len(kwargs)  and 'global_conf' in kwargs['initial']:
            #self.fields['fqdn'].initial = kwargs['initial']['global_conf'].fqdn
            self.set_fqdn(kwargs['initial']['global_conf'])
            self.set_mail(kwargs['initial']['global_conf'])
            #self.
    def set_fqdn(self,instance):
        self.fields['fqdn'].initial= instance.fqdn
        
    def set_mail(self,instance):
        self.fields['email'].initial= instance.email
        
        
                
    def is_valid(self):
        valid = super(GlobalConfForm, self).is_valid()
        
        '''
        FQDN= openssl x509 -noout -subject -in FICHERO.crt | awk -F \/ '{printf$7}' | cut -c 6-
        
        validacion adicional
        if valid:
            if self.connection:
                return True
        '''
        return valid


    