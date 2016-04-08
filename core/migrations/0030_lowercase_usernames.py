# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_usernames(apps, schema_editor):
    Member = apps.get_model('core', 'Member')

    for member in Member.objects.all():
        member.username = member.username.lower()
        member.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20160408_0011'),
    ]

    operations = [
        migrations.RunPython(set_usernames),
    ]
