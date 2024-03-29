# Generated by Django 2.0 on 2017-12-11 10:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dvr', '0009_auto_20171211_0822'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversion',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='conversion_created', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='conversion',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='conversion_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AddField(
            model_name='distributionattempt',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='distributionattempt_created', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='distributionattempt',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='distributionattempt_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AddField(
            model_name='distributionchannel',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='distributionchannel_created', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='distributionchannel',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='distributionchannel_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AddField(
            model_name='stream',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stream_created', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='stream',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stream_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AddField(
            model_name='video',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='video_created', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='video',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='video_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AlterField(
            model_name='conversion',
            name='progress',
            field=models.FloatField(blank=True, null=True, verbose_name='progress'),
        ),
        migrations.AlterField(
            model_name='conversion',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('QUEUED', 'Queued'), ('STARTED', 'Started'), ('SUCCESS', 'Success'), ('FAILURE', 'Failure')], db_index=True, default='PENDING', max_length=32, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='distributionattempt',
            name='progress',
            field=models.FloatField(blank=True, null=True, verbose_name='progress'),
        ),
        migrations.AlterField(
            model_name='distributionattempt',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('QUEUED', 'Queued'), ('STARTED', 'Started'), ('SUCCESS', 'Success'), ('FAILURE', 'Failure')], db_index=True, default='PENDING', max_length=32, verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='video',
            name='progress',
            field=models.FloatField(blank=True, null=True, verbose_name='progress'),
        ),
        migrations.AlterField(
            model_name='video',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('QUEUED', 'Queued'), ('STARTED', 'Started'), ('SUCCESS', 'Success'), ('FAILURE', 'Failure')], db_index=True, default='PENDING', max_length=32, verbose_name='status'),
        ),
    ]
