# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def migrate_data(app, schema_editor):
    print('Migrating data')
    Comment = app.get_model('core', 'Comment')
    db_alias = schema_editor.connection.alias
    rows = Comment.objects.using(db_alias)\
        .filter(comment='[SKIPPED]')\
        .update(comment=None, skip=True)

    print(rows,'rows affected')


def migrate_data_rev(app, schema_editor):
    print('Migrating data')
    Comment = app.get_model('core', 'Comment')
    db_alias = schema_editor.connection.alias
    rows = Comment.objects.using(db_alias)\
        .filter(skip=True)\
        .update(comment='[SKIPPED]')

    print(rows,'rows affected')

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_codesnippet_date_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='skip',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='comment',
            name='comment',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.RunPython(migrate_data, migrate_data_rev)
    ]
