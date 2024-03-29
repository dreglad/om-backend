# Generated by Django 2.0.2 on 2018-02-06 02:31

import django.contrib.postgres.fields.hstore
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dvr', '0022_auto_20180127_0802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversion',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={}, verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='distributionattempt',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={}, verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='distributionchannel',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={}, verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='distributionprofile',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={}, verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='stream',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={}, verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='video',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={}, verbose_name='metadata'),
        ),
    ]
