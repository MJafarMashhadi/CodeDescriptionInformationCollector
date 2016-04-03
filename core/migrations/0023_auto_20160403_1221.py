# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20160331_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='xp',
            name='amount',
            field=models.IntegerField(default=1),
        ),
    ]
