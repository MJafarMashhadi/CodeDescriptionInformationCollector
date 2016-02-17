from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from .models import Member, UserKnowsPL, Comment
from django.forms import inlineformset_factory


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        username_widget = self.fields['username'].widget
        username_widget.input_type = 'email'


class RegistrationForm(UserCreationForm):

    class Meta:
        model = Member
        fields = (
            'email',
            'first_name', 'last_name',
            'academic_degree', 'experience',
            'have_work_outside_college_projects'
        )
        help_texts = {
            'experience': 'in months'
        }

ProgrammingLanguagesFormset = inlineformset_factory(Member, UserKnowsPL, fields=('language', 'proficiency'), extra=2, can_delete=False)

ChangeProgrammingLanguagesFormset = inlineformset_factory(Member, UserKnowsPL, fields=('language', 'proficiency'), extra=1, can_delete=True)


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = Member
        fields = (
            'first_name', 'last_name',
            'academic_degree', 'experience',
            'have_work_outside_college_projects'
        )
        help_texts = {
            'experience': 'in months'
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        exclude = ('date_time', 'user', 'snippet', 'skip')
        widgets = {
            'comment': forms.Textarea({
                'rows': 2,
            })
        }
