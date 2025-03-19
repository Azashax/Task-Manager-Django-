# Generated by Django 4.2.6 on 2024-03-07 10:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='task_render2d',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_render2d', to='project.task'),
        ),
        migrations.AddField(
            model_name='project',
            name='task_render3d',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_render3d', to='project.task'),
        ),
        migrations.AlterField(
            model_name='task',
            name='task_type',
            field=models.CharField(choices=[('with', 'with'), ('without', 'without'), ('gltf', 'gltf'), ('assemble', 'assemble'), ('upload', 'upload'), ('render2d', 'render2d'), ('render3d', 'render3d')], max_length=20),
        ),
    ]
