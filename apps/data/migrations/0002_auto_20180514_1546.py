# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-05-14 15:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hasagdahtooluur',
            name='group',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='hasagdahtooluur',
            name='search_tooluur',
            field=models.CharField(max_length=50, null=True),
        ),
    ]