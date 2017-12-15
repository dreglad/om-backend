# Generated by Django 2.0 on 2017-12-14 05:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dvr', '0013_distributionprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='distributionattempt',
            name='channel',
        ),
        migrations.AddField(
            model_name='distributionattempt',
            name='profile',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='dvr.DistributionProfile', verbose_name='channel'),
            preserve_default=False,
        ),
    ]
