# Generated by Django 4.2.6 on 2024-07-22 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('render', '0019_rendertaskimages_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectlisting',
            name='render_check',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
