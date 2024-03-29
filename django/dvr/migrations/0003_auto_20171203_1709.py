# Generated by Django 2.0rc1 on 2017-12-03 23:09

import django.contrib.postgres.fields.hstore
from django.contrib.postgres.operations import HStoreExtension
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dvr', '0002_auto_20171126_0044'),
    ]

    operations = [
        HStoreExtension(),
        migrations.CreateModel(
            name='Distribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Waiting'), (1, 'Queued'), (2, 'Running'), (3, 'Success'), (4, 'Failure')], db_index=True, default=0, verbose_name='status')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('modified_at', models.DateTimeField(auto_now=True, null=True, verbose_name='modified at')),
                ('metadata', django.contrib.postgres.fields.hstore.HStoreField(null=True, verbose_name='metadata')),
                ('target', models.CharField(max_length=255, verbose_name='target')),
                ('progress', models.FloatField(null=True, verbose_name='progress')),
                ('result', models.CharField(blank=True, editable=False, max_length=255, verbose_name='result')),
            ],
            options={
                'verbose_name': 'Distribution',
                'verbose_name_plural': 'Distributions',
            },
        ),
        migrations.AddField(
            model_name='conversion',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(null=True, verbose_name='metadata'),
        ),
        migrations.AddField(
            model_name='conversion',
            name='result',
            field=models.CharField(blank=True, editable=False, max_length=64, verbose_name='result'),
        ),
        migrations.AlterField(
            model_name='conversion',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Waiting'), (1, 'Queued'), (2, 'Running'), (3, 'Success'), (4, 'Failure')], db_index=True, default=0, verbose_name='status'),
        ),
        migrations.AddField(
            model_name='distribution',
            name='conversion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='distributions', to='dvr.Conversion', verbose_name='conversion'),
        ),
    ]
