# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20160404_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='got_mystery_boxes',
            field=models.CharField(null=True, max_length=50, blank=True),
        ),
        migrations.AddField(
            model_name='member',
            name='mystery_box_points',
            field=models.CharField(null=True, max_length=11, blank=True),
        ),
    ]
