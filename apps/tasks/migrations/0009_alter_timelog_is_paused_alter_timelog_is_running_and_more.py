# Generated by Django 4.0.3 on 2022-03-16 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_alter_timelog_is_paused_alter_timelog_is_running_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timelog',
            name='is_paused',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='timelog',
            name='is_running',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='timelog',
            name='is_stopped',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
