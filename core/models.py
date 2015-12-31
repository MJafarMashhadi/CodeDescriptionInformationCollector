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
    email = models.EmailField(_('email address'), blank=True, primary_key=True)
    name = models.CharField(_('name'), max_length=30, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = MemberManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_short_name(self):
        return self.name

    def get_full_name(self):
        return self.name

    class Meta:
        verbose_name = 'عضو'
        verbose_name_plural = 'اعضاء'

