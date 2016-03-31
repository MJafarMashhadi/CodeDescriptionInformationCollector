# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


def set_submitter(apps, schema_editor):
    CodeSnippet = apps.get_model('core', 'CodeSnippet')
    Member = apps.get_model('core', 'Member')
    member1 = Member.objects.filter(is_staff=True)[:1][0]
    CodeSnippet.objects.update(submitter=member1)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20160331_1010'),
    ]

    operations = [
        migrations.RunPython(set_submitter),
        migrations.AlterField(
            model_name='codesnippet',
            name='submitter',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
