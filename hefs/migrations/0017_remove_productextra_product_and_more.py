# Generated by Django 4.1.5 on 2023-01-10 14:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0016_apiurls_alter_productextra_product_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productextra',
            name='product',
        ),
        migrations.AlterField(
            model_name='productextra',
            name='productnaam',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, related_name='productextra_productnaam', to='hefs.productinfo'),
        ),
    ]
