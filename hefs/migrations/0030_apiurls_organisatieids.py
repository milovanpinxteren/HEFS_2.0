# Generated by Django 4.1.5 on 2023-01-30 10:47

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0029_orders_routenr'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiurls',
            name='organisatieIDs',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(default=0), blank=True, default=[], size=None),
        ),
    ]
