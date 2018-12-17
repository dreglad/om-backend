# Generated by Django 2.0.1 on 2018-01-26 06:56

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dvr', '0018_auto_20180126_0629'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='duration',
            field=models.DurationField(blank=True, null=True, verbose_name='duration'),
        ),
        migrations.AddField(
            model_name='video',
            name='file',
            field=models.FileField(blank=True, upload_to='videos/', verbose_name='video file'),
        ),
        migrations.AddField(
            model_name='video',
            name='images',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.FileField(upload_to='images'), default=[], size=None, verbose_name='thumbnails'),
        ),
        migrations.AddField(
            model_name='video',
            name='timestamp_end',
            field=models.DateTimeField(blank=True, null=True, verbose_name='timestamp end'),
        ),
        migrations.AddField(
            model_name='video',
            name='timestamp_start',
            field=models.DateTimeField(blank=True, null=True, verbose_name='timestamp start'),
        ),
    ]