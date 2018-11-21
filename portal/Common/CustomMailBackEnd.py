from django.core.mail import get_connection, send_mail
from django.core.mail.message import EmailMessage
from portal.models import AfMailServer
# TODO: Insert clever settings mechanism



class CustomMailBackEnd(object):
    
    email_server = None
    port         = None
    usuario      = None
    passwd       = None
    use_tls      = None
    
    
    def __init__(self):
        
        mail_config=AfMailServer.objects.first()
        
        if mail_config:
            
            self.email_server = mail_config.email_server
            self.port         = mail_config.port
            self.usuario      = mail_config.usuario
            self.passwd       = mail_config.passwd
            self.use_tls      = mail_config.tls

    
    def get_connection(self):
        
        connection = get_connection(host       = self.email_server, 
                                    port       = self.port, 
                                    username   = self.usuario, 
                                    password   = self.passwd, 
                                    use_tls    = self.use_tls) 

        return connection

if __name__ == '__main__':
    
    cbe=CustomMailBackEnd()
    con= cbe.get_connection()
    EmailMessage('ola ?', 'test msg', 'from_email', ['to'], connection=con).send(fail_silently=False)
    
    