
from django.contrib import admin

#from afcloud.models import User, UserManager
#from afcloud.models import User, UserManager
from .models import AfServicio, AfEntorno, AfProyecto, AfRelEntPro, \
AfLineaCatalogo, AfInstancia, AfCiclo, AfTipoPerfil, AfPerfil, AfUsuario,AfAuditoria, \
AfGlobalconf ,AfIncidencia, AfEstadosIncidencia, \
AfNotasIncidencia,AfMailServer,AfUserNotify, AfTipoNotify, AfNotify_Tipo_instancia


admin.site.register(AfUsuario)
admin.site.register(AfServicio)
admin.site.register(AfEntorno)
admin.site.register(AfProyecto)
admin.site.register(AfRelEntPro)
admin.site.register(AfLineaCatalogo)
admin.site.register(AfInstancia)
admin.site.register(AfCiclo)
admin.site.register(AfTipoPerfil)
admin.site.register(AfPerfil)
admin.site.register(AfAuditoria)
admin.site.register(AfGlobalconf)
admin.site.register(AfIncidencia)
admin.site.register(AfEstadosIncidencia)
#admin.site.register(AfRelIncidenciaEstado)
admin.site.register(AfNotasIncidencia)
admin.site.register(AfMailServer)
admin.site.register(AfUserNotify)
admin.site.register(AfTipoNotify)
admin.site.register(AfNotify_Tipo_instancia)
