# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_annotation', '0004_auto_20150305_2100'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entityasargument',
            old_name='category',
            new_name='role',
        ),
        migrations.RenameField(
            model_name='relationasargument',
            old_name='category',
            new_name='role',
        ),
        migrations.RemoveField(
            model_name='argumentrole',
            name='entity_category',
        ),
    ]
