# Generated by Django 4.2.6 on 2024-01-19 12:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_out', models.BooleanField(default=False)),
                ('project_task_name', models.CharField(blank=True, max_length=100, null=True)),
                ('project_id', models.CharField(blank=True, max_length=100, null=True)),
                ('task_status', models.CharField(choices=[('open', 'open'), ('in progress', 'in progress'), ('complete', 'complete'), ('checked', 'checked'), ('correcting', 'correcting'), ('waiting', 'waiting')], default='open', max_length=20)),
                ('task_type', models.CharField(choices=[('with', 'with'), ('without', 'without'), ('gltf', 'gltf'), ('assemble', 'assemble'), ('upload', 'upload')], max_length=20)),
                ('unique_bedroom', models.CharField(blank=True, max_length=100, null=True)),
                ('copy_bedroom', models.CharField(blank=True, max_length=100, null=True)),
                ('in_progress_time', models.DateTimeField(blank=True, null=True)),
                ('in_stock_active', models.DateTimeField(blank=True, null=True)),
                ('checked_time', models.DateTimeField(blank=True, null=True)),
                ('complete_time', models.DateTimeField(blank=True, null=True)),
                ('point', models.FloatField(blank=True, null=True)),
                ('time_point', models.CharField(blank=True, max_length=100, null=True)),
                ('correcting_point', models.FloatField(blank=True, null=True)),
                ('time_correcting_point', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('stock_active', models.BooleanField(default=False)),
                ('check_out_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_check_out_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь Check Out')),
                ('task_correcting_employee_user', models.ForeignKey(blank=True, limit_choices_to={'role': 'Employee'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_correcting_employee_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь Correcting')),
                ('task_employee_user', models.ForeignKey(blank=True, limit_choices_to={'role': 'Employee'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_employee_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
        migrations.CreateModel(
            name='StorageStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('before_status', models.CharField(choices=[('open', 'open'), ('in progress', 'in progress'), ('complete', 'complete'), ('checked', 'checked'), ('correcting', 'correcting'), ('waiting', 'waiting')], max_length=20)),
                ('after_status', models.CharField(choices=[('open', 'open'), ('in progress', 'in progress'), ('complete', 'complete'), ('checked', 'checked'), ('correcting', 'correcting'), ('waiting', 'waiting')], max_length=20)),
                ('create_data', models.DateTimeField(auto_now_add=True)),
                ('storage_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='StorageStatus', to='project.task')),
                ('update_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='StorageStatus', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_type', models.CharField(choices=[('Tower', 'Tower'), ('Villa', 'Villa')], default='Tower', max_length=20)),
                ('project_name', models.CharField(max_length=255)),
                ('built', models.CharField(choices=[('finished', 'finished'), ('off plan', 'off plan')], default='finished', max_length=20)),
                ('project_status', models.CharField(choices=[('open', 'open'), ('in progress', 'in progress'), ('complete', 'complete'), ('checked', 'checked'), ('correcting', 'correcting'), ('waiting', 'waiting')], default='open', max_length=20)),
                ('link_clickup', models.TextField()),
                ('link_cet3', models.TextField()),
                ('project_teg', models.CharField(choices=[('None', 'None'), ('Priority', 'Priority'), ('High priority', 'High priority')], default='None', max_length=20)),
                ('exterior_status', models.CharField(choices=[('open', 'open'), ('in progress', 'in progress'), ('checked', 'checked')], default='open', max_length=20)),
                ('description', models.TextField(blank=True, null=True)),
                ('project_teamlead_user', models.ForeignKey(blank=True, limit_choices_to={'role': 'Teamlead'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_teamlead_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='region', to='project.region')),
                ('task_assemble', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_assemble', to='project.task')),
                ('task_gltf', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_gltf', to='project.task')),
                ('task_upload', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_upload', to='project.task')),
                ('task_with', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_with', to='project.task')),
                ('task_without', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_without', to='project.task')),
            ],
        ),
    ]
