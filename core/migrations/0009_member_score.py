# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20160217_0853'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='score',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
