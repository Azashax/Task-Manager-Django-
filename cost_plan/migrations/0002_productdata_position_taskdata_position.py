# Generated by Django 4.2.6 on 2025-02-14 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cost_plan', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='productdata',
            name='position',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='taskdata',
            name='position',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
