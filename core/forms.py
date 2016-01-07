from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from .models import Member, UserKnowsPL, ProgrammingLanguage


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        username_widget = self.fields['username'].widget
        username_widget.input_type = 'email'


class RegistrationForm(UserCreationForm):

    class Meta:
        model = Member
        exclude = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login', 'user_permissions', 'groups')
