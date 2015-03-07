# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_annotation', '0005_auto_20150306_0139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='relationcategory',
            name='argument_num',
        ),
    ]
