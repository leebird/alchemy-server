# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ArgumentRole',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('role', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'tm_argument_role',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('collection', models.CharField(max_length=64, db_index=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'tm_collection',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('doc_id', models.CharField(max_length=32, db_index=True)),
                ('text', models.TextField()),
            ],
            options={
                'db_table': 'tm_document',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocumentProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('label', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=128)),
                ('doc', models.ForeignKey(to='alchemy_server.Document')),
            ],
            options={
                'db_table': 'tm_document_property',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('start', models.IntegerField()),
                ('end', models.IntegerField()),
                ('text', models.TextField()),
                ('uid', models.CharField(max_length=32)),
            ],
            options={
                'db_table': 'tm_entity',
                'verbose_name': 'Entity',
                'verbose_name_plural': 'Entities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityAsArgument',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('argument', models.ForeignKey(to='alchemy_server.Entity')),
            ],
            options={
                'db_table': 'tm_entity_as_argument',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('category', models.CharField(max_length=32)),
                ('collection', models.ForeignKey(to='alchemy_server.Collection')),
            ],
            options={
                'db_table': 'tm_entity_category',
                'verbose_name': 'Entity Category',
                'verbose_name_plural': 'Entity Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('label', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=128)),
                ('entity', models.ForeignKey(to='alchemy_server.Entity')),
            ],
            options={
                'db_table': 'tm_entity_property',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('uid', models.CharField(max_length=32)),
            ],
            options={
                'db_table': 'tm_relation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelationAsArgument',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('argument', models.ForeignKey(to='alchemy_server.Relation')),
                ('relation', models.ForeignKey(related_name='relation_arguments', to='alchemy_server.Relation')),
                ('role', models.ForeignKey(to='alchemy_server.ArgumentRole')),
            ],
            options={
                'db_table': 'tm_relation_as_argument',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelationCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('category', models.CharField(max_length=32)),
                ('collection', models.ForeignKey(to='alchemy_server.Collection')),
            ],
            options={
                'db_table': 'tm_relation_category',
                'verbose_name': 'Relation Category',
                'verbose_name_plural': 'Relation Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelationProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('label', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=128)),
                ('relation', models.ForeignKey(to='alchemy_server.Relation')),
            ],
            options={
                'db_table': 'tm_relation_property',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('username', models.CharField(max_length=32, db_index=True)),
                ('password', models.CharField(max_length=32, db_index=True)),
            ],
            options={
                'db_table': 'tm_user',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='relation',
            name='category',
            field=models.ForeignKey(to='alchemy_server.RelationCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='relation',
            name='doc',
            field=models.ForeignKey(to='alchemy_server.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entityasargument',
            name='relation',
            field=models.ForeignKey(related_name='entity_arguments', to='alchemy_server.Relation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entityasargument',
            name='role',
            field=models.ForeignKey(to='alchemy_server.ArgumentRole'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='category',
            field=models.ForeignKey(to='alchemy_server.EntityCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='doc',
            field=models.ForeignKey(to='alchemy_server.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='collection',
            name='user',
            field=models.ForeignKey(to='alchemy_server.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='argumentrole',
            name='relation_category',
            field=models.ForeignKey(to='alchemy_server.RelationCategory'),
            preserve_default=True,
        ),
    ]
