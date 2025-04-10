# Generated by Django 4.2.10 on 2025-01-19 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0089_syncinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='syncinfo',
            name='geb_price',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Price in euros (€)', max_digits=10),
        ),
        migrations.AddField(
            model_name='syncinfo',
            name='hob_price',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Price in euros (€)', max_digits=10),
        ),
    ]
