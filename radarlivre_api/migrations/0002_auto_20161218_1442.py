# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-12-18 17:42
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('radarlivre_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collector',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
