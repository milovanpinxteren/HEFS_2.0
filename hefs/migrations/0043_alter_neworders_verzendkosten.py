# Generated by Django 4.1.5 on 2023-10-30 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0042_alter_orders_verzendkosten'),
    ]

    operations = [
        migrations.AlterField(
            model_name='neworders',
            name='verzendkosten',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=6, null=True),
        ),
    ]
