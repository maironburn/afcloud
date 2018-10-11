from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from portal.models import AfProyecto, AfUsuario, AfPerfil


def user_or_admin_is_allowed(function):

    def wrap(request, *args, **kwargs):

        id_usuario=None
        allowed=False
        try:
            af_user= AfUsuario.objects.get(user=request.user)

            if len(kwargs):
                if 'id'in kwargs:
                    id_usuario=kwargs['id']
                     
            allowed= af_user.usu_administrador or id_usuario==str(request.user.id) 

        except Exception as e:
            pass

        if request.user.is_active and allowed:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied


    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__

    return wrap


def group_required(id_proyecto=None, arg_name=None):
    def decorator(view):
        def wrapper(request, *args, **kwargs):

            numeric_profile={'Miembro': 1, 'Operador':2, 'Gestor':3 ,'af_cloud_admin': 4}
            profile= None
            allowed=False

            try:
                af_user= AfUsuario.objects.get(user=request.user)

                if len(kwargs) and 'id_proyecto'in kwargs:
                    id_proyecto=kwargs['id_proyecto']
                else:
                    id_proyecto=request.session.get('id_proyecto_seleccionado', False)

                try:
                    '''
                    evita forbidden si no hay proyecto seleccionado
                    '''
                    proyecto= AfProyecto.objects.get(pk=id_proyecto)
                except:
                    pass
                    
                if af_user.usu_administrador :
                    profile = 'af_cloud_admin'
                else:
                    af_perfil=AfPerfil.objects.get(usu=af_user, pro=proyecto)
                    profile= af_perfil.tpe.tpe_nombre

                if arg_name:
                    allowed=numeric_profile[profile]>= numeric_profile[arg_name]
                else:
                    allowed=numeric_profile[profile]>1

            except Exception as e:
                pass

            if profile and request.user.is_active and allowed:
                return view(request, *args, **kwargs)
            else:
                raise PermissionDenied

        return wrapper

    return decorator


