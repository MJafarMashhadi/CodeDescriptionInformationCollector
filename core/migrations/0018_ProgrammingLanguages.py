# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20160319_0930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='username',
            field=models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and -/./_ only.', error_messages={'unique': 'A user with that username already exists.'}, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.-]+$', 'Enter a valid username. This value may contain only letters, numbers and -/./_ characters.', 'invalid')], unique=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='userknowspl',
            name='proficiency',
            field=models.PositiveIntegerField(),
        ),
    ]
