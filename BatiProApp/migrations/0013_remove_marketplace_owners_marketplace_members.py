# Generated by Django 5.1.2 on 2024-12-04 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BatiProApp', '0012_marketmember'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='marketplace',
            name='owners',
        ),
        migrations.AddField(
            model_name='marketplace',
            name='members',
            field=models.ManyToManyField(related_name='marketplaces', to='BatiProApp.marketmember'),
        ),
    ]
