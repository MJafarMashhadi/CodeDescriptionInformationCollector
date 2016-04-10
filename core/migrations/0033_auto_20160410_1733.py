# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_member_filled_survey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='email',
            field=models.EmailField(verbose_name='email address', max_length=254, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='member',
            name='first_name',
            field=models.CharField(verbose_name='first name', max_length=30),
        ),
        migrations.AlterField(
            model_name='member',
            name='last_name',
            field=models.CharField(verbose_name='last name', max_length=30),
        ),
    ]
