# Generated by Django 4.1.5 on 2023-12-06 15:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0048_errorlogdatagerijptebieren'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='verzendoptie',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, to='hefs.verzendopties'),
        ),
    ]
