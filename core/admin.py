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


class KnowLangaugeInline(admin.TabularInline):
    model = UserKnowsPL
    extra = 1


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'academic_degree', 'experience', 'is_active')
    fields = (
        ('first_name', 'last_name'),
        ('email', 'password'),
        ('academic_degree', 'experience', 'have_work_outside_college_projects'),
        ('is_active', 'is_staff', 'is_superuser'),
        ('date_joined', 'last_login')
    )
    inlines = [KnowLangaugeInline]
