# Generated by Django 4.2.6 on 2024-04-08 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0014_project_task_render2d_upload_alter_task_task_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jsoncalculatedata',
            name='asset',
            field=models.BooleanField(default=False),
        ),
    ]
