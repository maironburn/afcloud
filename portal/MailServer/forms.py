from django import forms
from portal.models import AfMailServer 
from django.utils.translation import ugettext as _

#class EntornoForm(forms.Form):

class ConfigMailForm(forms.ModelForm):

    email_server = forms.EmailField()
    port         = forms.IntegerField( label='Puerto del servidor')
    usuario      = forms.CharField(max_length=100,label='Usuario')
    passwd       = forms.CharField(label=_("Contraseña"), widget=forms.PasswordInput, required=True)
    tls          = forms.BooleanField(label=_("Usa TLS"), initial=True,required=False)
    
    '''
    openssl x509 -noout -subject -in CA.crt |tr -d ' ' | cut -d ',' -f4| cut -d'=' -f2
    '''

    class Meta:
        model=AfMailServer
        fields= ('email_server','port','usuario', 'passwd', 'tls')
    
    
    def __init__(self, *args, **kwargs):
        super(ConfigMailForm, self).__init__(*args, **kwargs)
        if len(kwargs)  and 'global_conf' in kwargs['initial']:
            pass

        
                
    def is_valid(self):
        valid = super(ConfigMailForm, self).is_valid()

        return valid


    