# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_lowercase_usernames'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='test',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='member',
            name='test_comment',
            field=models.BooleanField(default=False),
        ),
    ]
