# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-13 00:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='submenu',
            name='ordinal',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='submenu',
            name='child',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='children', serialize=False, to='app.Menu'),
        ),
        migrations.AlterField(
            model_name='submenu',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Menu'),
        ),
    ]