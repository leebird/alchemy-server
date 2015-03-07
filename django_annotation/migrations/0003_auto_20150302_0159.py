# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_annotation', '0002_auto_20150302_0140'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entity',
            name='version',
        ),
        migrations.RemoveField(
            model_name='relation',
            name='version',
        ),
    ]
