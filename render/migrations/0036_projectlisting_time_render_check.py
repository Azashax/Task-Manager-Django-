# Generated by Django 4.2.6 on 2024-08-29 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('render', '0035_rendertaskstatuschange'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectlisting',
            name='time_render_check',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
