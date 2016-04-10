# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_auto_20160408_1615'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='filled_survey',
            field=models.BooleanField(default=False),
        ),
    ]
