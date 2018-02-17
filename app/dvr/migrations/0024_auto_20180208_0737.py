# Generated by Django 2.0.2 on 2018-02-08 07:37

from django.conf import settings
import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import recurrence.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dvr', '0023_auto_20180206_0231'),
    ]

    operations = [
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='created at')),
                ('modified_at', models.DateTimeField(auto_now=True, null=True, verbose_name='modified at')),
                ('metadata', django.contrib.postgres.fields.hstore.HStoreField(default={}, verbose_name='metadata')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('slug', models.SlugField(blank=True, default='', max_length=255, unique=True, verbose_name='slug')),
                ('recurrence', recurrence.fields.RecurrenceField(blank=True, null=True)),
                ('closing_sequence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='closing_sequence_series', to='dvr.Video', verbose_name='closing sequence')),
                ('comeback_sequence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cmeback_sequence_series', to='dvr.Video', verbose_name='comeback sequence')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='series_created', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='series_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by')),
                ('opening_sequence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='opening_sequence_series', to='dvr.Video', verbose_name='opening sequence')),
                ('pause_sequence', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pause_sequence_series', to='dvr.Video', verbose_name='pause sequence')),
                ('stream', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='series', to='dvr.Stream', verbose_name='stream')),
            ],
            options={
                'verbose_name_plural': 'series',
                'ordering': ['name'],
                'verbose_name': 'series',
            },
        ),
        migrations.AddField(
            model_name='video',
            name='series',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='videos', to='dvr.Series', verbose_name='series'),
        ),
    ]