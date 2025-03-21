# Generated by Django 4.2.6 on 2024-09-12 12:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0021_alter_project_project_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectsFilterTeg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teg', models.CharField(max_length=256)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='filter_teg',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.projectsfilterteg'),
        ),
    ]
