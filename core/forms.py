from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import formset_factory

from .models import Member, Comment, UserKnowsPL, CodeSnippet


class RegistrationForm(UserCreationForm):

    class Meta:
        model = Member
        fields = (
            'username', 'email',
            'first_name', 'last_name', 'nickname',
            'academic_degree', 'experience',
            'industry_experience'
        )
        help_texts = {
            'experience': 'in months',
            'industry_experience': 'in months',
            'nickname': 'will be shown on your profile and in leader boards',
        }


class ProgrammingLanguagesForm(forms.ModelForm):
    class Meta:
        model = UserKnowsPL
        fields = ('language', 'proficiency')
        widgets = {
            'language': forms.HiddenInput()
        }
        labels = {
            'proficiency': 'Experience'
        }

ProgrammingLanguagesFormset = formset_factory(ProgrammingLanguagesForm, can_delete=False, extra=0)


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = Member
        fields = (
            'first_name', 'last_name', 'nickname',
            'academic_degree', 'experience',
            'industry_experience'
        )
        help_texts = {
            'experience': 'in months',
            'industry_experience': 'in months',
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

class CodeSnippetSubmitForm(forms.ModelForm):

    class Meta:
        model = CodeSnippet
        exclude = ('date_time', 'approved', 'submitter', 'usersViewed')