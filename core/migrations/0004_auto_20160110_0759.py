# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_member_have_work_outside_college_projects'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodeSnippet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('code', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('comment', models.TextField()),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('snippet', models.ForeignKey(to='core.CodeSnippet')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='programminglanguage',
            name='id',
        ),
        migrations.AlterField(
            model_name='programminglanguage',
            name='name',
            field=models.CharField(serialize=False, primary_key=True, max_length=40),
        ),
        migrations.AlterField(
            model_name='userknowspl',
            name='proficiency',
            field=models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)]),
        ),
        migrations.AlterUniqueTogether(
            name='userknowspl',
            unique_together=set([('user', 'language')]),
        ),
        migrations.AddField(
            model_name='codesnippet',
            name='language',
            field=models.ForeignKey(to='core.ProgrammingLanguage'),
        ),
        migrations.AddField(
            model_name='codesnippet',
            name='usersViewed',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='core.Comment'),
        ),
        migrations.AlterUniqueTogether(
            name='comment',
            unique_together=set([('user', 'snippet')]),
        ),
    ]
