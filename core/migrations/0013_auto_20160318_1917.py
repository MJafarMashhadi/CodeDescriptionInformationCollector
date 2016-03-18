# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20160318_1917'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='have_work_outside_college_projects',
        ),
    ]
