# Generated by Django 4.1.5 on 2024-03-03 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0049_orders_verzendoptie'),
    ]

    operations = [
        migrations.AddField(
            model_name='neworders',
            name='shopifyID',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='orders',
            name='shopifyID',
            field=models.IntegerField(default=0),
        ),
    ]
