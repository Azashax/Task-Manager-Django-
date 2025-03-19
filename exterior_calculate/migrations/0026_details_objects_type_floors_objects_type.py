# Generated by Django 4.2.6 on 2024-08-20 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exterior_calculate', '0025_rename_building_object_details_floors'),
    ]

    operations = [
        migrations.AddField(
            model_name='details',
            name='objects_type',
            field=models.CharField(blank=True, choices=[('BuildDetails', 'BuildDetails'), ('Floor', 'Floor'), ('Objects', 'Objects'), ('StaticObject', 'StaticObject')], max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='floors',
            name='objects_type',
            field=models.CharField(blank=True, choices=[('BuildDetails', 'BuildDetails'), ('Floor', 'Floor'), ('Objects', 'Objects'), ('StaticObject', 'StaticObject')], max_length=30, null=True),
        ),
    ]
