# coding=utf-8

from __future__ import unicode_literals

from django import forms
from django.contrib.auth import (authenticate, get_user_model, password_validation)
from django.contrib.auth.hashers import (UNUSABLE_PASSWORD_PREFIX, identify_hasher, )
from django.contrib.auth.models import User
from django.forms.utils import flatatt
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext, ugettext_lazy as _

#from portal.models import AfUsuario

class ReadOnlyPasswordHashWidget(forms.Widget):
    def render(self, name, value, attrs):
        encoded = value
        final_attrs = self.build_attrs(attrs)
        if not encoded or encoded.startswith(UNUSABLE_PASSWORD_PREFIX):
            summary = mark_safe("<strong>%s</strong>" % ugettext("No password set."))
        else:
            try:
                hasher = identify_hasher(encoded)
            except ValueError:
                summary = mark_safe("<strong>%s</strong>" % ugettext(
                    "Contraseña no validada."))
            else:
                summary = format_html_join('', "<strong>{}</strong>: {} ",
                                           ((ugettext(key), value)
                                            for key, value in hasher.safe_summary(encoded).items()))
        return format_html("<div{}>{}</div>", flatatt(final_attrs), summary)


class ReadOnlyPasswordHashField(forms.Field):
    widget = ReadOnlyPasswordHashWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        super(ReadOnlyPasswordHashField, self).__init__(*args, **kwargs)

    def bound_data(self, data, initial):
        # Always return initial because the widget doesn't
        # render an input field.
        return initial

    def has_changed(self, initial, data):
        return False


                               
class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput(attrs={'autofocus': ''}))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    error_messages = {
        'invalid_login': _("Por favor introduzca un usuario correcto %(username)s y su contraseña. "
                           "Tenga en cuenta que ambos campos son sensibles a las mayusculas."),
        'inactive': _("Esta cuenta se encuentra inactiva."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        # Set the label for the "username" field.
        UserModel = get_user_model()
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        self.fields['username'].label = "Usuario"
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            self.user_cache = authenticate(username=username, password=password)
        if self.user_cache is None:
            raise forms.ValidationError(self.error_messages['invalid_login'],
                                        code='invalid_login',
                                        params={'username': self.username_field.verbose_name}, )
        else:
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.
        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.
        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(self.error_messages['inactive'], code='inactive', )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache






class AdminPasswordChangeForm(forms.Form):
    """
    A form used to change the password of a user in the admin interface.
    """
    error_messages = {'password_mismatch': _("Las contraseñas no son las mismas."),}
    required_css_class = 'required'
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput(attrs={'autofocus': ''}),
                                help_text=password_validation.password_validators_help_text_html(), )
    password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput,
                                help_text=_("Introduca la misma contraseña."), )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AdminPasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(self.error_messages['password_mismatch'],
                                            code='password_mismatch', )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        """
        Saves the new password.
        """
        password = self.cleaned_data["password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
            return self.user

    def _get_changed_data(self):
        data = super(AdminPasswordChangeForm, self).changed_data
        for name in self.fields.keys():
            if name not in data:
                return []
        return ['password']

    changed_data = property(_get_changed_data)


class changePass(forms.Form):
    new_password1 = forms.CharField(label=_("Nueva contraseña"),
                                    widget=forms.PasswordInput,)
    new_password2 = forms.CharField(label=_("Repetir Nueva contraseña "),
                                    widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):

        self.user = user
        super(changePass, self).__init__()
        # super(SetPasswordForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
