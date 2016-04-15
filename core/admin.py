from django.contrib import admin
from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import escape
from django.core.urlresolvers import reverse
from .models import *

models = [XP, EarnBadge]
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
    list_display = ('user', 'language', 'proficiency', 'self_assessment')


class KnowLanguageInline(admin.TabularInline):
    model = UserKnowsPL
    extra = 1


class EarnedBadgeInline(admin.TabularInline):
    model = EarnBadge
    extra = 1


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'get_full_name', 'nickname', 'academic_degree', 'score')
    fields = (
        ('first_name', 'last_name', 'nickname'),
        ('email', 'username', 'student_number'),
        'score',
        ('academic_degree', 'experience', 'industry_experience'),
        ('is_active', 'is_staff', 'is_superuser', 'filled_survey'),
        ('date_joined', 'last_login')
    )
    inlines = [KnowLanguageInline, EarnedBadgeInline]
    readonly_fields = ['date_joined', 'last_login', 'score', 'email', 'filled_survey']
    ordering = ['is_active', '-score', 'email']


@admin.register(CodeSnippet)
class CodeSnippetAdmin(admin.ModelAdmin):
    list_display = ('language', 'name', 'score', 'approved', 'submitter')
    fields = (
        ('name', 'language'),
        ('score', 'is_starred'),
        ('approved', 'submitter'),
        'code'
    )
    readonly_fields = ('submitter', )

    def save_model(self, request, obj, form, change):
        if obj.submitter is None:
            obj.submitter = request.user

        obj.save()


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


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')


@admin.register(Evaluate)
class EvaluateAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'agree')
    readonly_fields = ('user', 'comment', 'agree')


class LogEntryAdmin(admin.ModelAdmin):

    date_hierarchy = 'action_time'

    readonly_fields = LogEntry._meta.get_all_field_names()

    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    search_fields = [
        'object_repr',
        'change_message'
    ]


    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag',
        'change_message',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = u'<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return link
    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'

    def queryset(self, request):
        return super(LogEntryAdmin, self).queryset(request) \
            .prefetch_related('content_type')


admin.site.register(LogEntry, LogEntryAdmin)
