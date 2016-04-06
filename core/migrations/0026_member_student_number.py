# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20160406_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='student_number',
            field=models.CharField(null=True, validators=[django.core.validators.RegexValidator('(8[5-9]|9[0-4])[1-3][0-2][0-9]{4}')], max_length=8, blank=True),
        ),
    ]
