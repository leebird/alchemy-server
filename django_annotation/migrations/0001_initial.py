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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('role', models.CharField(max_length=128)),
                ('mandatory', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('doc_id', models.CharField(max_length=32)),
                ('text', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DocumentProperty',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('label', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=128)),
                ('doc', models.ForeignKey(to='django_annotation.Document')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('start', models.IntegerField()),
                ('end', models.IntegerField()),
                ('text', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityAsArgument',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('argument', models.ForeignKey(to='django_annotation.Entity')),
                ('category', models.ForeignKey(to='django_annotation.ArgumentRole')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityCategory',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('category', models.CharField(max_length=32)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityProperty',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('label', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=128)),
                ('entity', models.ForeignKey(to='django_annotation.Entity')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelationAsArgument',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('argument', models.ForeignKey(to='django_annotation.Relation')),
                ('category', models.ForeignKey(to='django_annotation.ArgumentRole')),
                ('relation', models.ForeignKey(to='django_annotation.Relation', related_name='relation_arguments')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelationCategory',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('category', models.CharField(max_length=32)),
                ('argument_num', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RelationProperty',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('label', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=128)),
                ('relation', models.ForeignKey(to='django_annotation.Relation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('username', models.CharField(max_length=32)),
                ('password', models.CharField(max_length=32)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('version', models.CharField(max_length=64)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to='django_annotation.User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='relationcategory',
            name='version',
            field=models.ForeignKey(to='django_annotation.Version'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='relation',
            name='category',
            field=models.ForeignKey(to='django_annotation.RelationCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='relation',
            name='doc',
            field=models.ForeignKey(to='django_annotation.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='relation',
            name='version',
            field=models.ForeignKey(to='django_annotation.Version'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entitycategory',
            name='version',
            field=models.ForeignKey(to='django_annotation.Version'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entityasargument',
            name='relation',
            field=models.ForeignKey(to='django_annotation.Relation', related_name='entity_arguments'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='category',
            field=models.ForeignKey(to='django_annotation.EntityCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='doc',
            field=models.ForeignKey(to='django_annotation.Document'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='version',
            field=models.ForeignKey(to='django_annotation.Version'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='argumentrole',
            name='entity_category',
            field=models.ForeignKey(to='django_annotation.EntityCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='argumentrole',
            name='relation_category',
            field=models.ForeignKey(to='django_annotation.RelationCategory'),
            preserve_default=True,
        ),
    ]
