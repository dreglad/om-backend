# Generated by Django 2.0rc1 on 2017-12-04 09:00

import django.contrib.postgres.fields.hstore
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dvr', '0006_auto_20171203_2348'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stream',
            name='api_url',
        ),
        migrations.RemoveField(
            model_name='stream',
            name='dvr_url',
        ),
        migrations.RemoveField(
            model_name='stream',
            name='live_url',
        ),
        migrations.AddField(
            model_name='stream',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True, verbose_name='metadata'),
        ),
        migrations.AddField(
            model_name='stream',
            name='provider',
            field=models.CharField(choices=[('WowzaStreamingEngine', 'Wowza Streaming Engine')], default=1, max_length=64, verbose_name='provider'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='conversion',
            name='progress',
            field=models.FloatField(blank=True, editable=False, null=True, verbose_name='progress'),
        ),
        migrations.AlterField(
            model_name='distributionattempt',
            name='progress',
            field=models.FloatField(blank=True, editable=False, null=True, verbose_name='progress'),
        ),
        migrations.AlterField(
            model_name='distributionchannel',
            name='type',
            field=models.CharField(choices=[('multimedia', 'Captura-Multimedia'), ('ftp', 'FTP'), ('youtube', 'YouTube')], max_length=128, verbose_name='type'),
        ),
        migrations.AlterField(
            model_name='video',
            name='progress',
            field=models.FloatField(blank=True, editable=False, null=True, verbose_name='progress'),
        ),
    ]
