# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20160318_1917'),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('slug', models.SlugField(serialize=False, primary_key=True)),
                ('icon', models.FileField(upload_to='badges')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='EarnBadge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('badge', models.ForeignKey(to='core.Badge')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='XP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('amount', models.PositiveIntegerField(default=1)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=200)),
                ('user', models.ForeignKey(related_name='experiences', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='member',
            name='badges',
            field=models.ManyToManyField(through='core.EarnBadge', to='core.Badge'),
        ),
    ]
