# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20160403_1221'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evaluate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('agree', models.BooleanField(default=True)),
                ('comment', models.ForeignKey(to='core.Comment')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='evaluate',
            unique_together=set([('user', 'comment')]),
        ),
    ]
