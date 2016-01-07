# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='member',
            options={},
        ),
        migrations.AlterModelOptions(
            name='userknowspl',
            options={'verbose_name': 'User knows Programming Language'},
        ),
        migrations.AddField(
            model_name='member',
            name='experience',
            field=models.SmallIntegerField(default=0),
        ),
    ]
