# Generated by Django 4.2.6 on 2024-05-16 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0019_remove_task_json_data_task_json_data_calculate'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='additional_time_point',
            field=models.IntegerField(default=0),
        ),
    ]
