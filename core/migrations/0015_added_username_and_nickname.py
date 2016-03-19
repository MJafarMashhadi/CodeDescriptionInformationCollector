# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


def create_usernames(apps, schema_editor):
    Member = apps.get_model('core', 'Member')
    all_members = Member.objects.values('email').all()
    username_set = set()
    for member in all_members:
        email = member['email']
        username = email[:email.index('@')]
        base_username = username
        n = 1
        while username in username_set:
            username = base_username + str(n)
            n += 1
        username_set.add(username)
        Member.objects.filter(email=email).update(username=username)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_added_xp_and_badge'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='nickname',
            field=models.CharField(blank=True, max_length=30, verbose_name='Nickname'),
        ),
        migrations.AddField(
            model_name='member',
            name='username',
            field=models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and -/_ only.', error_messages={'unique': 'A user with that username already exists.'}, verbose_name='username', max_length=30, validators=[django.core.validators.RegexValidator('^[\\w-]+$', 'Enter a valid username. This value may contain only letters, numbers and -/_ characters.', 'invalid')], null=True),
            preserve_default=False,
        ),
        migrations.RunPython(create_usernames)
    ]
