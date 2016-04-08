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

    academic_degree = models.CharField(max_length=1, choices=(('G', 'Graduate'), ('U', 'Undergraduate')))
    experience = models.SmallIntegerField(default=0)
    industry_experience = models.PositiveIntegerField(default=0)

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_(
                                        'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    programming_languages = models.ManyToManyField('ProgrammingLanguage', through='UserKnowsPL')

    score = models.IntegerField(default=0)

    student_number = models.CharField(max_length=8, null=True, blank=True, validators=[validators.RegexValidator(r'(8[5-9]|9[0-4])[1-3][0-2][0-9]{4}')])

    badges = models.ManyToManyField('Badge', through='EarnBadge')

    mystery_box_points = models.CharField(max_length=11, blank=True, null=True)
    got_mystery_boxes = models.CharField(max_length=50, blank=True, null=True)

    test_comment = models.BooleanField(default=False)

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
        return CodeSnippet.objects.select_related('language').filter(
            language__in=self.get_knwon_programming_languages(), approved=True)

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
        (float('-inf'), 20),
        (20, 60),
        (60, 100),
        (100, 150),
        (150, 200),
        (200, 260),
        (260, 320),
        (320, float('inf')),
    )

    LEVELS = [
        'Starting to see the light',
        'Taking your first steps',
        'Good job! Keep on',
        'Middle of the way',
        'Code squasher',
        'Point worm',
        'Proficient code summarizer',
        'Monster slayer'
    ]

    def current_level_range(self):
        return self.LEVEL_RANGES[self.level_int]

    @property
    def level_int(self):
        for i in range(len(self.LEVEL_RANGES)):
            if self.LEVEL_RANGES[i][0] <= self.score < self.LEVEL_RANGES[i][1]:
                return i

        return len(self.LEVEL_RANGES)

    def can_submit_code(self):
        return self.level_int >= 4 or self.is_staff or self.is_superuser

    @property
    def level(self):
        return self.LEVELS[self.level_int]

    @property
    def previous_level(self):
        i = self.level_int
        if i == 0:
            return ''
        else:
            return self.LEVELS[i - 1]

    @property
    def next_level(self):
        i = self.level_int
        if i >= len(self.LEVELS) - 1:
            return ''
        else:
            return self.LEVELS[i + 1]

    def get_first_comment_date(self):
        comments = Comment.objects.filter(user=self).order_by('date_time').values('date_time')[:1].all()
        if len(comments) == 0:
            return None
        return comments[0]['date_time']

    def get_last_comment_date(self):
        comments = Comment.objects.filter(user=self).order_by('-date_time').values('date_time')[:1].all()
        if len(comments) == 0:
            return None
        return comments[0]['date_time']

    def should_see_home(self):
        return not Comment.objects.filter(user=self).exists()

    def save(self, *args, **kwargs):
        if not self.pk or (not self.mystery_box_points and not self.got_mystery_boxes):
            self.set_mystery_boxes()

        super(Member, self).save(*args, **kwargs)

    def set_mystery_boxes(self):
        import random
        self.got_mystery_boxes = ''
        self.mystery_box_points = ','.join(list(map(str,
                                                    [
                                                        random.randrange(self.LEVEL_RANGES[1][0],
                                                                         self.LEVEL_RANGES[1][1]),
                                                        random.randrange(self.LEVEL_RANGES[4][0],
                                                                         self.LEVEL_RANGES[4][1]),
                                                        random.randrange(self.LEVEL_RANGES[6][0],
                                                                         self.LEVEL_RANGES[6][1])
                                                    ]
                                                    )))

    def has_mystery_box(self):
        if not self.mystery_box_points:
            return False
        points = list(map(int, self.mystery_box_points.split(',')))
        for p in points:
            if self.score >= p:
                return True

        return False

    def remove_mystery_box(self):
        if not self.mystery_box_points or len(self.mystery_box_points) == 0:
            return
        points = list(map(int, self.mystery_box_points.split(',')))
        for p in points:
            if self.score >= p:
                points.remove(p)
        self.mystery_box_points = ','.join(list(map(str, points)))
        self.save()

    def got_mystery_box_before(self, name):
        if not self.got_mystery_boxes:
            return False
        return ',' not in name and name in self.got_mystery_boxes

    def add_mystery_box_to_history(self, name):
        if self.got_mystery_boxes and len(self.got_mystery_boxes) > 0:
            self.got_mystery_boxes += ',' + name
        else:
            self.got_mystery_boxes = name

        self.save()

    def earn_badge(self, badge_name):
        try:
            badge = Badge.objects.get(slug=badge_name)
        except Badge.DoesNotExist:
            return None

        return EarnBadge.objects.get_or_create(
            user=self,
            badge=badge
        )


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
    self_assessment = models.PositiveIntegerField(default=5, validators=[
        validators.MinValueValidator(1), validators.MaxValueValidator(5)
    ])

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
    approved = models.BooleanField(default=True)
    submitter = models.ForeignKey(Member, null=False, blank=False)

    usersViewed = models.ManyToManyField(Member, through='Comment', related_name='comments')

    class Meta:
        unique_together = ('name', 'language')

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
    test = models.BooleanField(default=False)


    def __str__(self):
        return '{} comment on {}'.format(self.user.get_full_name(), self.snippet.name)

    class Meta:
        unique_together = ('user', 'snippet')

    @property
    def agree_count(self):
        return Evaluate.objects.filter(comment=self, agree=True).count()

    @property
    def disagree_count(self):
        return Evaluate.objects.filter(comment=self, agree=False).count()

    def save(self, *args, **kwargs):
        if 'commit' not in kwargs or kwargs['commit']:
            if not self.skip:
                if self.snippet.is_starred and self.user.comments.filter(comment__skip=False, comment__snippet__is_starred=True).count() == 2-1:
                    self.user.earn_badge('multiple_of_star_methods')
                elif self.snippet.score == 10 and self.user.comments.filter(comment__skip=False, comment__snippet__score=10).count() == 3-1:
                    self.user.earn_badge('multiple_of_10')
        super(Comment, self).save(*args, **kwargs)


class Evaluate(models.Model):
    user = models.ForeignKey(Member)
    comment = models.ForeignKey(Comment)
    agree = models.BooleanField(default=True)
    xp = models.ForeignKey('XP', null=True, blank=True)

    def __str__(self):
        return 'evaluate on comment {}'.format(self.comment)

    class Meta:
        unique_together = ('user', 'comment')


class XP(models.Model):
    user = models.ForeignKey(Member, related_name='experiences')
    amount = models.IntegerField(default=1)
    date_time = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        changed_level = False
        if not self.pk:
            user = self.user
            before = user.level_int
            user.score += self.amount
            user.save()
            after = user.level_int
            if after > before:
                changed_level = True
        if changed_level:
            level = self.user.level_int + 1
            if level == 2:
                self.user.earn_badge('one_star')
            elif level == 4:
                self.user.earn_badge('two_star')
                self.user.earn_badge('middle_of_the_way')
            elif level == 6:
                self.user.earn_badge('three_star')
            elif level == 8:
                self.user.earn_badge('four_star')
                self.user.earn_badge('finishing_the_game')

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
