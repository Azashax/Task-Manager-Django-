# Generated by Django 4.2.6 on 2024-07-09 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('render', '0011_alter_rendertask_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='rendertaskimages',
            name='checked_is',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rendertaskimages',
            name='desc',
            field=models.TextField(blank=True, null=True),
        ),
    ]
