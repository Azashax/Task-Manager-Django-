# Generated by Django 4.2.6 on 2024-02-10 08:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exterior_calculate', '0006_rename_backing_lod_additionalstructure_high_poly_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buildingobjects',
            name='building_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='building_objects', to='exterior_calculate.building'),
        ),
    ]
