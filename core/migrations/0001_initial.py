# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import core.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login', null=True, blank=True)),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('academic_degree', models.CharField(max_length=1, choices=[('G', 'Graduate'), ('U', 'Undergraduate')])),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status', help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(default=True, verbose_name='active', help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(verbose_name='groups', related_name='user_set', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_query_name='user', to='auth.Group', blank=True)),
            ],
            options={
                'verbose_name': 'عضو',
                'verbose_name_plural': 'اعضاء',
            },
            managers=[
                ('objects', core.models.MemberManager()),
            ],
        ),
        migrations.CreateModel(
            name='ProgrammingLanguage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=40)),
                ('object_oriented', models.BooleanField()),
                ('functional', models.BooleanField()),
                ('compiled', models.BooleanField()),
                ('interpreted', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='UserKnowsPL',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('proficiency', models.SmallIntegerField()),
                ('language', models.ForeignKey(to='core.ProgrammingLanguage')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='member',
            name='programming_languages',
            field=models.ManyToManyField(through='core.UserKnowsPL', to='core.ProgrammingLanguage'),
        ),
        migrations.AddField(
            model_name='member',
            name='user_permissions',
            field=models.ManyToManyField(verbose_name='user permissions', related_name='user_set', help_text='Specific permissions for this user.', related_query_name='user', to='auth.Permission', blank=True),
        ),
    ]
