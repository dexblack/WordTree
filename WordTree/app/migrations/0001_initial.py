# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-21 12:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('tag', models.CharField(db_index=True, max_length=25)),
                ('data', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Submenu',
            fields=[
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, related_name='children', serialize=False, to='app.Menu')),
                ('ordinal', models.IntegerField(db_index=True, default=0)),
                ('parent', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.Menu')),
            ],
        ),
    ]
