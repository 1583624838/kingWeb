# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-10-04 15:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kingWeb', '0019_auto_20181004_0943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sysloginlog',
            name='clientinfo',
            field=models.TextField(blank=True, db_column='ClientInfo', null=True),
        ),
    ]