# Generated by Django 4.2.6 on 2024-10-24 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0006_alter_myuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='role',
            field=models.CharField(choices=[('Admin', 'Admin'), ('Teamlead', 'Teamlead'), ('Manager', 'Manager'), ('QA', 'QA'), ('Employee', 'Employee'), ('InteriorAdmin', 'AInteriorAdmin'), ('InteriorTeamLead', 'InteriorTeamLead'), ('InteriorManager', 'InteriorManager'), ('InteriorQA', 'InteriorQA'), ('InteriorEmployee', 'InteriorEmployee'), ('ExQA', 'ExQA'), ('ExTeamlead', 'ExTeamlead'), ('ExEmployee', 'ExEmployee'), ('ExAdmin', 'ExAdmin'), ('ExManager', 'ExManager'), ('RenderUploader', 'RenderUploader'), ('RenderQA', 'RenderQA'), ('RenderEnhancer', 'RenderEnhancer'), ('RenderGeometry', 'RenderGeometry'), ('RenderAssetDesigner', 'RenderAssetDesigner'), ('Render3dDesigner', 'Render3dDesigner')], default='Employee', max_length=20),
        ),
    ]
