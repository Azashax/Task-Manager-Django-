# Generated by Django 4.2.6 on 2024-07-23 07:39

from django.db import migrations, models
import render.upload_utils


class Migration(migrations.Migration):

    dependencies = [
        ('render', '0020_projectlisting_render_check'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagerendertask',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=render.upload_utils.message_correcting_image),
        ),
    ]
