# Generated by Django 5.1.2 on 2024-12-04 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BatiProApp', '0013_remove_marketplace_owners_marketplace_members'),
    ]

    operations = [
        migrations.AddField(
            model_name='marketplace',
            name='map',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='marketplace',
            name='note',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=2),
        ),
    ]
