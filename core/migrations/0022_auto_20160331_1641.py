# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_set_submitter_2'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='codesnippet',
            unique_together=set([('name', 'language')]),
        ),
    ]
