# Generated by Django 4.2.6 on 2024-03-27 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exterior_calculate', '0013_building_finished_point_building_finished_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='additionalstructure',
            name='arb_logo',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='additionalstructure',
            name='furniture',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='additionalstructure',
            name='logo',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='additionalstructure',
            name='railing',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='additionalstructure',
            name='staircase_curves',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='additionalstructure',
            name='staircase_straight',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='buildingobjects',
            name='arb_logo',
            field=models.CharField(blank=True, default='0', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='buildingobjects',
            name='logo',
            field=models.CharField(blank=True, default='0', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='buildingobjects',
            name='railing',
            field=models.CharField(blank=True, default='0', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='buildingobjects',
            name='staircase_curves',
            field=models.CharField(blank=True, default='0', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='buildingobjects',
            name='staircase_straight',
            field=models.CharField(blank=True, default='0', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='objectsdetails',
            name='arb_logo',
            field=models.CharField(blank=True, default='0', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='objectsdetails',
            name='logo',
            field=models.CharField(blank=True, default='0', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='objectsdetails',
            name='railing',
            field=models.CharField(blank=True, default='0', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='objectsdetails',
            name='staircase_curves',
            field=models.CharField(blank=True, default='0', max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='objectsdetails',
            name='staircase_straight',
            field=models.CharField(blank=True, default='0', max_length=30, null=True),
        ),
    ]
