# Generated by Django 4.2.6 on 2024-03-11 11:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeamsExterior',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('employees', models.ManyToManyField(blank=True, limit_choices_to={'role': 'ExEmployee'}, related_name='employee_ex', to=settings.AUTH_USER_MODEL)),
                ('team_lead', models.OneToOneField(limit_choices_to={'role': 'ExTeamlead'}, on_delete=django.db.models.deletion.CASCADE, related_name='team_lead_ex', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
