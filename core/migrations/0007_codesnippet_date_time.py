# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20160110_0823'),
    ]

    operations = [
        migrations.AddField(
            model_name='codesnippet',
            name='date_time',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 1, 10, 13, 14, 43, 585154, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
