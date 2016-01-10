# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_codesnippet_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codesnippet',
            name='usersViewed',
            field=models.ManyToManyField(related_name='comments', to=settings.AUTH_USER_MODEL, through='core.Comment'),
        ),
    ]
