from django.core import validators
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin, _
from django.utils import timezone


class MemberManager(UserManager):
    """
    Manager class for customized Member class
    """
    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class Member(AbstractBaseUser, PermissionsMixin):
    """
    Site user

    """
    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and '
                    '-/./_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.-]+$',
                                      _('Enter a valid username. '
                                        'This value may contain only letters, numbers '
                                        'and -/./_ characters.'), 'invalid'),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        })
    email = models.EmailField(_('email address'), blank=True, primary_key=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    nickname = models.CharField('Nickname', max_length=30, blank=True)

    academic_degree = models.CharField(max_length=1, choices=(('G', 'Graduate'),('U', 'Undergraduate')))
    experience = models.SmallIntegerField(default=0)
    industry_experience = models.PositiveIntegerField(default=0)

    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    programming_languages = models.ManyToManyField('ProgrammingLanguage', through='UserKnowsPL')

    score = models.PositiveSmallIntegerField(default=0)

    badges = models.ManyToManyField('Badge', through='EarnBadge')

    objects = MemberManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'academic_degree', 'experience']

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return ('%s %s' % (self.first_name, self.last_name)).strip()

    def get_knwon_programming_languages(self):
        return self.programming_languages.filter(userknowspl__proficiency__gt=0)

    def get_understandable_snippets_query_set(self):
        return CodeSnippet.objects.select_related('language').filter(language__in=self.get_knwon_programming_languages())

    def get_commentable_snippets_query_set(self):
        return self.get_understandable_snippets_query_set().exclude(usersViewed__exact=self)

    def get_commentable_snippets(self):
        return self.get_commentable_snippets_query_set().all()

    def earn_xp(self, points, description=''):
        return XP.objects.create(
            user=self,
            amount=points,
            description=description
        )

    LEVEL_RANGES = (
        (0, 20),
        (20,60),
        (60, 100),
        (00, 150),
        (50, 200),
        (00, 260),
        (60, 320),
        (320, 400),
    )

    def current_level_range(self):
        return self.LEVEL_RANGES[self.level_int]

    @property
    def level_int(self):
        for i in range(len(self.LEVEL_RANGES)):
            if self.LEVEL_RANGES[i][0] <= self.score < self.LEVEL_RANGES[i][1]:
                return i

        return len(self.LEVEL_RANGES)

    @property
    def level(self):
        levels = [
            'Starting to see the light',
            'Taking your first steps',
            'Good job! Keep on',
            'Middle of the way',
            'Code squasher',
            'Point warm',
            'Proficient code summarized',
            'Monster slayer'
        ]
        return levels[self.level_int]

    def get_first_comment_date(self):
        comments = Comment.objects.filter(user=self).order_by('date_time')[:1].all()
        if len(comments) == 0:
            return None
        return comments[0].date_time

    def get_last_comment_date(self):
        comments = Comment.objects.filter(user=self).order_by('-date_time')[:1].all()
        if len(comments) == 0:
            return None
        return comments[0].date_time


class ProgrammingLanguage(models.Model):
    name = models.CharField(max_length=40, primary_key=True)
    object_oriented = models.BooleanField()
    functional = models.BooleanField()
    compiled = models.BooleanField()
    interpreted = models.BooleanField()

    def __str__(self):
        return self.name


class UserKnowsPL(models.Model):
    user = models.ForeignKey(Member)
    language = models.ForeignKey(ProgrammingLanguage)
    proficiency = models.PositiveIntegerField()

    def __str__(self):
        return self.language.name

    class Meta:
        verbose_name = 'User knows Programming Language'
        unique_together = ('user', 'language')


class CodeSnippet(models.Model):
    code = models.TextField(null=False, blank=False)
    language = models.ForeignKey(ProgrammingLanguage)
    name = models.CharField(max_length=200, null=True, blank=False)
    date_time = models.DateTimeField(auto_now_add=True)
    score = models.PositiveIntegerField(default=5)
    is_starred = models.BooleanField(default=False)

    usersViewed = models.ManyToManyField(Member, through='Comment', related_name='comments')

    @property
    def n_comments(self):
        return self.usersViewed.exclude(comment__skip=True).count()

    @property
    def virgin(self):
        return not Comment.objects.filter(snippet=self, skip=False).exists()

    def __str__(self):
        return '{} ({})'.format(self.name, self.language.name)


class Comment(models.Model):
    user = models.ForeignKey(Member)
    snippet = models.ForeignKey(CodeSnippet)
    comment = models.TextField(null=True, blank=True)
    date_time = models.DateTimeField(auto_now_add=True)
    skip = models.BooleanField(default=False)

    def __str__(self):
        return '{} comment on {}'.format(self.user.get_full_name(), self.snippet.name)

    class Meta:
        unique_together = ('user', 'snippet')


class XP(models.Model):
    user = models.ForeignKey(Member, related_name='experiences')
    amount = models.PositiveIntegerField(default=1)
    date_time = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.pk:
            user = self.user
            user.score += self.amount
            user.save()
        super(XP, self).save(*args, **kwargs)


class Badge(models.Model):
    slug = models.SlugField(primary_key=True)
    icon = models.FileField()
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class EarnBadge(models.Model):
    user = models.ForeignKey(Member)
    badge = models.ForeignKey(Badge)
    date_time = models.DateTimeField(auto_now_add=True)
