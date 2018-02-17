# Generated by Django 2.0.2 on 2018-02-08 08:45

from django.conf import settings
import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import dvr.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dvr', '0024_auto_20180208_0737'),
    ]

    operations = [
        migrations.CreateModel(
            name='SeriesRecurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='created at')),
                ('modified_at', models.DateTimeField(auto_now=True, null=True, verbose_name='modified at')),
                ('recurrence', dvr.fields.RecurrenceField()),
                ('start_date', models.DateField(blank=True, db_index=True, null=True, verbose_name='start date')),
                ('end_date', models.DateField(blank=True, db_index=True, null=True, verbose_name='end date')),
                ('start_time', models.TimeField(db_index=True, verbose_name='start time')),
                ('end_time', models.TimeField(db_index=True, verbose_name='end time')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seriesrecurrence_created', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seriesrecurrence_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by')),
            ],
            options={
                'verbose_name': 'series recurrence',
                'verbose_name_plural': 'series recurrences',
                'ordering': ['series', 'start_date', 'start_time'],
            },
        ),
        migrations.RemoveField(
            model_name='series',
            name='recurrence',
        ),
        migrations.AlterField(
            model_name='conversion',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, default={}, verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='distributionattempt',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, default={}, verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='distributionchannel',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, default={}, verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='distributionprofile',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, default={}, verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='series',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, default={}, verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='stream',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, default={}, verbose_name='metadata'),
        ),
        migrations.AlterField(
            model_name='video',
            name='metadata',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, default={}, verbose_name='metadata'),
        ),
        migrations.AddField(
            model_name='seriesrecurrence',
            name='series',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurrences', to='dvr.Series', verbose_name='series'),
        ),
    ]