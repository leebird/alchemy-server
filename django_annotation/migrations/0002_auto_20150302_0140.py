# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_annotation', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='argumentrole',
            table='tm_argument_role',
        ),
        migrations.AlterModelTable(
            name='document',
            table='tm_document',
        ),
        migrations.AlterModelTable(
            name='documentproperty',
            table='tm_document_property',
        ),
        migrations.AlterModelTable(
            name='entity',
            table='tm_entity',
        ),
        migrations.AlterModelTable(
            name='entityasargument',
            table='tm_entity_as_argument',
        ),
        migrations.AlterModelTable(
            name='entitycategory',
            table='tm_entity_category',
        ),
        migrations.AlterModelTable(
            name='entityproperty',
            table='tm_entity_property',
        ),
        migrations.AlterModelTable(
            name='relation',
            table='tm_relation',
        ),
        migrations.AlterModelTable(
            name='relationasargument',
            table='tm_relation_as_argument',
        ),
        migrations.AlterModelTable(
            name='relationcategory',
            table='tm_relation_category',
        ),
        migrations.AlterModelTable(
            name='relationproperty',
            table='tm_relation_property',
        ),
        migrations.AlterModelTable(
            name='user',
            table='tm_user',
        ),
        migrations.AlterModelTable(
            name='version',
            table='tm_version',
        ),
    ]
