# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_added_username_and_nickname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='username',
            field=models.CharField(default='', help_text='Required. 30 characters or fewer. Letters, digits and -/_ only.', error_messages={'unique': 'A user with that username already exists.'}, verbose_name='username', max_length=30, validators=[django.core.validators.RegexValidator('^[\\w-]+$', 'Enter a valid username. This value may contain only letters, numbers and -/_ characters.', 'invalid')], unique=True, null=False),
            preserve_default=False,
        ),
    ]
