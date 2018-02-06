# Generated by Django 2.0rc1 on 2017-11-26 06:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Conversion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Pending'), (2, 'Running'), (3, 'Success'), (4, 'Failure')], db_index=True, default=0, verbose_name='status')),
                ('start', models.DateTimeField(verbose_name='start')),
                ('duration', models.DurationField(verbose_name='duration')),
                ('priority', models.PositiveSmallIntegerField(choices=[(0, 'Normal'), (0, 'High'), (0, 'Low')], default=0, verbose_name='priority')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('modified_at', models.DateTimeField(auto_now=True, null=True, verbose_name='modified at')),
            ],
            options={
                'verbose_name': 'Conversion',
                'verbose_name_plural': 'Conversions',
            },
        ),
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('live_url', models.URLField(blank=True, verbose_name='live URL')),
                ('dvr_url', models.URLField(blank=True, verbose_name='DVR URL')),
                ('api_url', models.URLField(blank=True, verbose_name='API URL')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('modified_at', models.DateTimeField(auto_now=True, null=True, verbose_name='modified at')),
            ],
            options={
                'verbose_name': 'stream',
                'verbose_name_plural': 'streams',
            },
        ),
        migrations.AddField(
            model_name='conversion',
            name='stream',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversions', to='dvr.Stream', verbose_name='stream'),
        ),
    ]