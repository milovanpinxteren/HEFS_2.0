# Generated by Django 4.2.10 on 2024-11-27 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0078_route_google_maps_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='google_maps_link',
            field=models.URLField(blank=True, max_length=1000, null=True),
        ),
    ]