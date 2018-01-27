# Generated by Django 2.0.1 on 2018-01-27 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dvr', '0021_auto_20180127_0649'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='height',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='height'),
        ),
        migrations.AddField(
            model_name='video',
            name='width',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='width'),
        ),
    ]
