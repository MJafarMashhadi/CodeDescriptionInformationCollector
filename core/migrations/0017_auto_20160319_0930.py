# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_added_username_and_nickname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badge',
            name='icon',
            field=models.FileField(upload_to=''),
        ),
    ]
