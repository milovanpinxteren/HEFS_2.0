# Generated by Django 4.1.5 on 2024-06-07 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0061_productenhalfproducts'),
    ]

    operations = [
        migrations.AddField(
            model_name='productenhalfproducts',
            name='productcode',
            field=models.CharField(default=0, max_length=3),
        ),
    ]
