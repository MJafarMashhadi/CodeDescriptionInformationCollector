# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_member_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='codesnippet',
            name='score',
            field=models.PositiveIntegerField(default=5),
        ),
    ]
