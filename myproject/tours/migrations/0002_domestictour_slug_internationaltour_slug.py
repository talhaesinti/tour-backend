# Generated by Django 5.1.1 on 2024-12-12 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='domestictour',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AddField(
            model_name='internationaltour',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
