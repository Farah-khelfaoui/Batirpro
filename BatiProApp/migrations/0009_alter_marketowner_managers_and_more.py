# Generated by Django 5.1.2 on 2024-12-04 17:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BatiProApp', '0008_client_image_url'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='marketowner',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='marketowner',
            name='telephone',
        ),
        migrations.RemoveField(
            model_name='marketowner',
            name='user_ptr',
        ),
        migrations.AddField(
            model_name='marketowner',
            name='client',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Marketowner', to='BatiProApp.client'),
        ),
        migrations.AddField(
            model_name='marketowner',
            name='status',
            field=models.CharField(default='pending ...', max_length=255),
        ),
        migrations.AddField(
            model_name='marketplace',
            name='status',
            field=models.CharField(default='pending ...', max_length=255),
        ),
    ]
