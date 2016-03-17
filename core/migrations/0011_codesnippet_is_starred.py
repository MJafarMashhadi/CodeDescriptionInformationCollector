# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_codesnippet_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='codesnippet',
            name='is_starred',
            field=models.BooleanField(default=False),
        ),
    ]
