from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import formset_factory

from .models import Member, Comment, UserKnowsPL, CodeSnippet
from django.contrib.auth.forms import AuthenticationForm


class CleanUsernameMixin:
    def clean_username(self):
        if self.cleaned_data.get("username") is None:
            return None
        else:
            return self.cleaned_data.get("username").lower()


class CleanNicknameMixin:
    def clean_nickname(self):
        if self.cleaned_data.get("nickname") is None:
            return None
        else:
            return self.cleaned_data.get("nickname").strip()


class RegistrationForm(UserCreationForm, CleanUsernameMixin, CleanNicknameMixin):

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for f in iter(self.fields):
            print(f)
            f = self.fields[f]
            if f.required:
                f.widget.attrs.update({'class':'required'})

    class Meta:
        model = Member
        fields = (
            'username', 'email',
            'first_name', 'last_name', 'nickname',
            'student_number',
            'academic_degree', 'experience',
            'industry_experience'
        )
        help_texts = {
            'experience': 'in months',
            'industry_experience': 'in months',
            'nickname': 'will be shown on your profile and in leader boards',
        }
        labels = {
            'experience': 'General programming experience',
            'student_number': 'Student ID',
        }


class ProgrammingLanguagesForm(forms.ModelForm):
    class Meta:
        model = UserKnowsPL
        fields = ('language', 'proficiency', 'self_assessment')
        widgets = {
            'language': forms.HiddenInput()
        }
        labels = {
            'proficiency': 'Experience',
            'self_assessment': 'In range of <strong>1-5</strong> specify your proficiency in programming in this language',
        }

ProgrammingLanguagesFormset = formset_factory(ProgrammingLanguagesForm, can_delete=False, extra=0)


class UserProfileForm(forms.ModelForm, CleanUsernameMixin, CleanNicknameMixin):

    class Meta:
        model = Member
        fields = (
            'first_name', 'last_name', 'nickname',
            'student_number',
            'academic_degree', 'experience',
            'industry_experience'
        )
        help_texts = {
            'experience': 'in months',
            'industry_experience': 'in months',
            'nickname': 'will be shown on your profile and in leader boards',

        }
        labels = {
            'experience': 'General programming experience',
            'student_number': 'Student ID',
        }


class CommentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['comment'].required = True

    class Meta:
        model = Comment
        exclude = ('date_time', 'user', 'snippet', 'skip', 'test')
        widgets = {
            'comment': forms.Textarea({
                'rows': 2,
            })
        }


class CodeSnippetSubmitForm(forms.ModelForm):

    class Meta:
        model = CodeSnippet
        exclude = ('date_time', 'approved', 'submitter', 'usersViewed', 'score', 'is_starred')


class ICAuthenticationForm(AuthenticationForm, CleanUsernameMixin):
    pass
