# Generated by Django 4.2.6 on 2024-04-25 09:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('exterior_calculate', '0019_projectexterior_calculated'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExteriorTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_out', models.BooleanField(default=False)),
                ('task_status', models.CharField(choices=[('open', 'open'), ('in progress', 'in progress'), ('complete', 'complete'), ('checked', 'checked'), ('correcting', 'correcting'), ('waiting', 'waiting')], default='open', max_length=20)),
                ('task_type', models.CharField(choices=[('Low Poly', 'Low Poly'), ('Midl Poly', 'Midl Poly'), ('High Poly', 'High Poly'), ('Arrangement', 'Arrangement')], default='Low Poly', max_length=20)),
                ('project_teg', models.CharField(choices=[('None', 'None'), ('Priority', 'Priority'), ('High priority', 'High priority')], default='None', max_length=20)),
                ('in_progress_time', models.DateTimeField(blank=True, null=True)),
                ('in_stock_active', models.DateTimeField(blank=True, null=True)),
                ('checked_time', models.DateTimeField(blank=True, null=True)),
                ('complete_time', models.DateTimeField(blank=True, null=True)),
                ('point', models.FloatField(blank=True, null=True)),
                ('time_point', models.CharField(blank=True, max_length=100, null=True)),
                ('total_correcting', models.IntegerField(default=0)),
                ('stock_active', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('check_out_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Ex_task_qa_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь Qa')),
                ('project_exterior_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ExteriorTask', to='exterior_calculate.projectexterior')),
                ('task_employee_user', models.ForeignKey(blank=True, limit_choices_to={'role': 'ExEmployee'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Ex_task_employee_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь Employee')),
            ],
        ),
        migrations.CreateModel(
            name='ExteriorStorageStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('before_status', models.CharField(choices=[('open', 'open'), ('in progress', 'in progress'), ('complete', 'complete'), ('checked', 'checked'), ('correcting', 'correcting'), ('waiting', 'waiting')], max_length=20)),
                ('after_status', models.CharField(choices=[('open', 'open'), ('in progress', 'in progress'), ('complete', 'complete'), ('checked', 'checked'), ('correcting', 'correcting'), ('waiting', 'waiting')], max_length=20)),
                ('create_data', models.DateTimeField(auto_now_add=True)),
                ('storage_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ExteriorStorageStatus', to='exterior_calculate.exteriortask')),
                ('update_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ExteriorStorageStatus', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
    ]
