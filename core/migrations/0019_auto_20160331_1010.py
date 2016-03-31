# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_ProgrammingLanguages'),
    ]

    operations = [
        migrations.AddField(
            model_name='codesnippet',
            name='approved',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='codesnippet',
            name='submitter',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL),
        )
    ]
