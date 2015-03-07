# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_annotation', '0003_auto_20150302_0159'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='uid',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='relation',
            name='uid',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
    ]
