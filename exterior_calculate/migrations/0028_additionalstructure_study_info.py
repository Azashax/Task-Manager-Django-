# Generated by Django 4.2.6 on 2024-11-22 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exterior_calculate', '0027_rename_arb_logo_additionalstructure_arabian_logo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='additionalstructure',
            name='study_info',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
