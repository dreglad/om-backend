# Generated by Django 2.0 on 2018-01-02 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dvr', '0016_auto_20171230_0927'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sceneanalysis',
            options={'ordering': ['-created_at', '-end', '-start'], 'verbose_name': 'scene analysis', 'verbose_name_plural': 'scene analysis'},
        ),
        migrations.AlterModelOptions(
            name='scenechange',
            options={'ordering': ['-time', 'created_at'], 'verbose_name': 'scene change', 'verbose_name_plural': 'scene changes'},
        ),
        migrations.AlterField(
            model_name='sceneanalysis',
            name='end',
            field=models.DateTimeField(db_index=True, verbose_name='end'),
        ),
        migrations.AlterField(
            model_name='sceneanalysis',
            name='start',
            field=models.DateTimeField(db_index=True, verbose_name='start'),
        ),
        migrations.AlterField(
            model_name='scenechange',
            name='value',
            field=models.FloatField(blank=True, db_index=True, null=True, verbose_name='value'),
        ),
    ]
