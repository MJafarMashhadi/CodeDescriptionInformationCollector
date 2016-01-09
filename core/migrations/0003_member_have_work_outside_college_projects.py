# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20160107_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='have_work_outside_college_projects',
            field=models.BooleanField(default=False),
        ),
    ]
