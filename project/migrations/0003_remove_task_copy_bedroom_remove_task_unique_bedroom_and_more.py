# Generated by Django 4.2.6 on 2024-03-31 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_project_task_render2d_project_task_render3d_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='copy_bedroom',
        ),
        migrations.RemoveField(
            model_name='task',
            name='unique_bedroom',
        ),
        migrations.AddField(
            model_name='task',
            name='total_correcting',
            field=models.IntegerField(default=0),
        ),
    ]
