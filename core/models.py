from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin, _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


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
    email = models.EmailField(_('email address'), blank=True, primary_key=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)

    academic_degree = models.CharField(max_length=1, choices=(('G', 'Graduate'),('U', 'Undergraduate')))
    experience = models.SmallIntegerField(default=0)
    have_work_outside_college_projects = models.BooleanField(default=False)

    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    programming_languages = models.ManyToManyField('ProgrammingLanguage', through='UserKnowsPL')

    objects = MemberManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'academic_degree', 'experience']

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return ('%s %s' % (self.first_name, self.last_name)).strip()


class ProgrammingLanguage(models.Model):
    name = models.CharField(max_length=40)
    object_oriented = models.BooleanField()
    functional = models.BooleanField()
    compiled = models.BooleanField()
    interpreted = models.BooleanField()

    def __str__(self):
        return self.name


class UserKnowsPL(models.Model):
    user = models.ForeignKey(Member)
    language = models.ForeignKey(ProgrammingLanguage)
    proficiency = models.SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

    def __str__(self):
        return self.language.name

    class Meta:
        verbose_name = 'User knows Programming Language'


