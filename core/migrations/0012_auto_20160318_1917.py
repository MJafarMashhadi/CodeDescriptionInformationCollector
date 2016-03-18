# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def convert_experience(apps, schema_editor):
    Member = apps.get_model('core', 'Member')
    Member.objects.filter(have_work_outside_college_projects=True).update(industry_experience=1)
    Member.objects.filter(have_work_outside_college_projects=False).update(industry_experience=0)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_codesnippet_is_starred'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='industry_experience',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(convert_experience),
    ]
