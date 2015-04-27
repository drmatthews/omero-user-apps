# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccountRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('omename', models.CharField(max_length=30)),
                ('first_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=75)),
                ('password', models.CharField(max_length=200)),
                ('institution', models.CharField(max_length=100)),
                ('default_group', models.CharField(max_length=100)),
                ('other_groups', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Microscope',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='MicroscopeBooking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField()),
                ('booking_date', models.DateTimeField(verbose_name=b'booking date')),
                ('microscopes', models.ManyToManyField(to='omero_bookings.Microscope')),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TrainingRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('markers', models.CharField(max_length=200)),
                ('instruments', models.ManyToManyField(to='omero_bookings.Microscope')),
                ('samples', models.ManyToManyField(to='omero_bookings.Sample')),
            ],
        ),
    ]
