# Generated by Django 2.0rc1 on 2017-12-04 05:48

import django.contrib.postgres.fields.hstore
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dvr', '0005_auto_20171203_2335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversion',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True, verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='distributionattempt',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True, verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='distributionchannel',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True, verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='distributionchannel',
            name='slug',
            field=models.SlugField(blank=True, default='', max_length=255, unique=True, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='stream',
            name='slug',
            field=models.SlugField(blank=True, default='', max_length=255, unique=True, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='video',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True, verbose_name='metadata'),
        ),
    ]
