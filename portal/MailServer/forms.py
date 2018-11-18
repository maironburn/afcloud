from django import forms
from portal.models import AfMailServer 
from django.utils.translation import ugettext as _

#class EntornoForm(forms.Form):

class ConfigMailForm(forms.ModelForm):

    email_server = forms.CharField(max_length=100,label='Servidor de correo')
    port         = forms.IntegerField( label='Puerto del servidor')
    usuario      = forms.CharField(max_length=100,label='Usuario')
    passwd       = forms.CharField(label=_("Contraseña"), widget=forms.PasswordInput, required=True)
    tls          = forms.BooleanField(label=_("Usa TLS"), initial=True,required=False)
    


    class Meta:
        model=AfMailServer
        fields= ('email_server','port','usuario', 'passwd', 'tls')
    
    
    def __init__(self, *args, **kwargs):
        
        super(ConfigMailForm, self).__init__(*args, **kwargs)
        
        if len(kwargs)  and 'mail_conf' in kwargs['initial']:
            
            self.fields['email_server'].initial= kwargs['initial']['mail_conf'].email_server
            self.fields['port'].initial= kwargs['initial']['mail_conf'].port
            self.fields['usuario'].initial= kwargs['initial']['mail_conf'].usuario
            self.fields['passwd'].initial= kwargs['initial']['mail_conf'].passwd
            self.fields['tls'].initial= kwargs['initial']['mail_conf'].tls

        
                
    def is_valid(self):
        valid = super(ConfigMailForm, self).is_valid()

        return valid


    