# Generated by Django 2.0 on 2017-12-14 04:22

from django.conf import settings
import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dvr', '0010_auto_20171211_1042'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='conversion',
            options={'ordering': ('-pk',), 'verbose_name': 'conversion', 'verbose_name_plural': 'conversions'},
        ),
        migrations.AddField(
            model_name='distributionchannel',
            name='configuration',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True, verbose_name='configuration'),
        ),
        migrations.AlterField(
            model_name='conversion',
            name='created_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='conversion_created', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AlterField(
            model_name='conversion',
            name='modified_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='conversion_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AlterField(
            model_name='distributionattempt',
            name='created_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='distributionattempt_created', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AlterField(
            model_name='distributionattempt',
            name='modified_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='distributionattempt_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AlterField(
            model_name='distributionchannel',
            name='created_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='distributionchannel_created', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AlterField(
            model_name='distributionchannel',
            name='modified_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='distributionchannel_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AlterField(
            model_name='stream',
            name='created_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stream_created', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AlterField(
            model_name='stream',
            name='modified_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stream_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AlterField(
            model_name='video',
            name='created_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='video_created', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AlterField(
            model_name='video',
            name='modified_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='video_modified', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
    ]
