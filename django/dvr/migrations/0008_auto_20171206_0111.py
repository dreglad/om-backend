# Generated by Django 2.0rc1 on 2017-12-06 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dvr', '0007_auto_20171204_0300'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conversion',
            name='source_url',
        ),
        migrations.AddField(
            model_name='conversion',
            name='dvr_store',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='DVR Store'),
        ),
    ]
