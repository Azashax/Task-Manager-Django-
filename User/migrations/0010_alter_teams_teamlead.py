# Generated by Django 4.2.6 on 2024-11-13 12:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0009_myuser_telegram_id_alter_myuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teams',
            name='teamlead',
            field=models.OneToOneField(limit_choices_to={'role__in': ['Teamlead', 'interiorTeamLead']}, on_delete=django.db.models.deletion.CASCADE, related_name='teamlead', to=settings.AUTH_USER_MODEL),
        ),
    ]
