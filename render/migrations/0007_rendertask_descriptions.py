# Generated by Django 4.2.6 on 2024-07-01 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('render', '0006_rendertaskimages'),
    ]

    operations = [
        migrations.AddField(
            model_name='rendertask',
            name='descriptions',
            field=models.TextField(blank=True, null=True),
        ),
    ]
