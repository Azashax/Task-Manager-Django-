# Generated by Django 4.2.6 on 2024-01-19 12:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(max_length=255, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=255, verbose_name='Last Name')),
                ('username', models.CharField(max_length=255, unique=True, verbose_name='Username')),
                ('role', models.CharField(choices=[('Admin', 'Admin'), ('Teamlead', 'Teamlead'), ('Manager', 'Manager'), ('QA', 'QA'), ('Employee', 'Employee'), ('ExQA', 'ExQA'), ('ExTeamlead', 'ExTeamlead'), ('ExEmployee', 'ExEmployee')], default='Employee', max_length=20)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('link_telegram', models.CharField(blank=True, max_length=1000, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Teams',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('employees', models.ManyToManyField(blank=True, limit_choices_to={'role': 'Employee'}, related_name='employee', to=settings.AUTH_USER_MODEL)),
                ('teamlead', models.OneToOneField(limit_choices_to={'role': 'Teamlead'}, on_delete=django.db.models.deletion.CASCADE, related_name='teamlead', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
