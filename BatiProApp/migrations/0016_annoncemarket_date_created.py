# Generated by Django 5.1.2 on 2024-12-04 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BatiProApp', '0015_remove_marketplace_note_avismarket'),
    ]

    operations = [
        migrations.AddField(
            model_name='annoncemarket',
            name='date_created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
