# Generated by Django 4.1.5 on 2024-10-23 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0072_leverancieruserlink'),
    ]

    operations = [
        migrations.AddField(
            model_name='customers',
            name='ordered_2024',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]