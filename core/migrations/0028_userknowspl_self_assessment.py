# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_evaluate_xp'),
    ]

    operations = [
        migrations.AddField(
            model_name='userknowspl',
            name='self_assessment',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], default=5),
        ),
    ]
