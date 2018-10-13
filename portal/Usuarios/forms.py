# coding=utf-8

from __future__ import unicode_literals
from django.utils.translation import ugettext as _
from django import forms
from portal.models import AfUsuario
from django.contrib.auth.models import User
from django.contrib.admin import widgets
from django.contrib.auth import password_validation
from django.template.defaultfilters import default
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Field


class UserRawForm(forms.ModelForm):

    username   = forms.CharField(max_length=100,label='Usuario',required=True)
    password = forms.CharField(label=_("Contraseña"), widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(label=_("Repetir contraseña"), widget=forms.PasswordInput,required=True)
    usu_administrador= forms.BooleanField(label=_("Admin AFCloud"), initial=False,required=False)
    error_messages = {
        'password_mismatch': _("Las contraseñas no son las mismas."),
    }

    class Meta:
        model=User
        fields= ('username','first_name', 'last_name','email')


    def __init__(self, *args, **kwargs):
        super(UserRawForm, self).__init__(*args, **kwargs)


        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            afusuario=AfUsuario.objects.get(user=instance)
            if afusuario.usu_administrador==True:
                self.fields['usu_administrador'].widget.attrs['checked'] = True
            self.fields['username'].widget.attrs['readonly'] = True

    def clean_password2(self):
        password =  self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2:
            if password != password2:
                raise forms.ValidationError(self.error_messages['password_mismatch'],
                                            code='password_mismatch', )
        #password_validation.validate_password(password2, self.user)
        return password2


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': _("Las contraseñas no son las mismas."),
    }
    new_password1 = forms.CharField(label=_("Nueva contraseña"),
                                    widget=forms.PasswordInput,required=True
                                    )
    # help_text='La contraseña debe tener 8 caracteres')
    # help_text=password_validation.password_validators_help_text_html())
    new_password2 = forms.CharField(label=_("Repetir Nueva contraseña "),
                                    widget=forms.PasswordInput,required=True)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(self.error_messages['password_mismatch'],
                                            code='password_mismatch', )
            # password_validation.validate_password(password2, self.user)
        return password2


    def save(self, commit=True):
        password =self.clean_new_password2()
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class editUserRawForm(forms.ModelForm):

    username   = forms.CharField(max_length=100,label='Usuario',required=True)
    password = forms.CharField(label=_("Contraseña"), widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label=_("Repetir contraseña"), widget=forms.PasswordInput,required=False)
    usu_administrador= forms.BooleanField(label=_("Admin AFCloud"), initial=False,required=False)
    error_messages = {
        'password_mismatch': _("Las contraseñas no son las mismas."),
    }

    class Meta:
        model=User
        fields= ('username','first_name', 'last_name','email')


    def __init__(self, *args, **kwargs):
        super(editUserRawForm, self).__init__(*args, **kwargs)
        self.fields['usu_administrador'].widget = forms.HiddenInput()
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            afusuario=AfUsuario.objects.get(user=instance)
            if afusuario.usu_administrador==True:
                self.fields['usu_administrador'].widget.attrs['checked'] = True
            self.fields['username'].widget.attrs['readonly'] = True

    def clean_password2(self):
        password =  self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2:
            if password != password2:
                raise forms.ValidationError(self.error_messages['password_mismatch'],
                                            code='password_mismatch', )
        #password_validation.validate_password(password2, self.user)
        return password2



class userEditProfileForm(forms.ModelForm):

    username   = forms.CharField(max_length=100,label='Usuario',required=True)
    password = forms.CharField(label=_("Contraseña"), widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label=_("Repetir contraseña"), widget=forms.PasswordInput,required=False)

    error_messages = {
        'password_mismatch': _("Las contraseñas no son las mismas."),
    }

    class Meta:
        model=User
        fields= ('username','first_name', 'last_name','email')


    def __init__(self, *args, **kwargs):
        super(userEditProfileForm, self).__init__(*args, **kwargs)

        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            afusuario=AfUsuario.objects.get(user=instance)
            self.fields['username'].widget.attrs['readonly'] = True

    def clean_password2(self):
        password =  self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2:
            if password != password2:
                raise forms.ValidationError(self.error_messages['password_mismatch'],
                                            code='password_mismatch', )
        #password_validation.validate_password(password2, self.user)
        return password2
