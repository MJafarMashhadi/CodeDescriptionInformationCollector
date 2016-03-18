from django.contrib import admin
from .models import *

models = []
registration = map(admin.site.register, models)
list(registration)  # apply, python 3 hack


@admin.register(ProgrammingLanguage)
class PLAdmin(admin.ModelAdmin):
    list_display = ('name', 'object_oriented', 'functional', 'compiled', 'interpreted')
    fields = (
        'name',
        ('object_oriented', 'functional'),
        ('compiled', 'interpreted')
    )


@admin.register(UserKnowsPL)
class UserKnowsPLAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'proficiency')


class KnowLanguageInline(admin.TabularInline):
    model = UserKnowsPL
    extra = 1


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'academic_degree', 'score', 'is_active')
    fields = (
        ('first_name', 'last_name'),
        'email', 'score',
        ('academic_degree', 'experience', 'industry_experience'),
        ('is_active', 'is_staff', 'is_superuser'),
        ('date_joined', 'last_login')
    )
    inlines = [KnowLanguageInline]
    readonly_fields = ['date_joined', 'last_login', 'score', 'email']
    ordering = ['is_active', 'score', 'email']


@admin.register(CodeSnippet)
class CodeSnippetAdmin(admin.ModelAdmin):
    list_display = ('language', 'name', 'score', 'is_starred')
    fields = (
        ('name', 'language'),
        ('score', 'is_starred'),
        'code'
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_time')
    fields = (
        ('user', 'snippet'),
        'comment'
    )

    def get_queryset(self, request):
        qs = super(CommentAdmin, self).get_queryset(request)
        return qs.filter(skip=False)