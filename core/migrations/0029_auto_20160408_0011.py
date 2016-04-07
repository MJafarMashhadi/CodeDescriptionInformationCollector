# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_userknowspl_self_assessment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
