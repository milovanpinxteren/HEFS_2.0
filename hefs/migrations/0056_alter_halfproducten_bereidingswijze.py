# Generated by Django 4.1.5 on 2024-04-22 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0055_alter_halfproducten_bereidingswijze'),
    ]

    operations = [
        migrations.AlterField(
            model_name='halfproducten',
            name='bereidingswijze',
            field=models.TextField(default=''),
        ),
    ]
