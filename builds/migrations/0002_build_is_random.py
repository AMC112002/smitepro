# Generated by Django 5.1.5 on 2025-03-19 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('builds', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='is_random',
            field=models.BooleanField(default=False),
        ),
    ]
