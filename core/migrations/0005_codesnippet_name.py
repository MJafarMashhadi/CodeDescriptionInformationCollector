# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20160110_0759'),
    ]

    operations = [
        migrations.AddField(
            model_name='codesnippet',
            name='name',
            field=models.CharField(null=True, max_length=200),
        ),
    ]
