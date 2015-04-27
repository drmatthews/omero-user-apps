# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('omero_signup', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='password',
            field=models.CharField(default='password', max_length=200),
            preserve_default=False,
        ),
    ]
