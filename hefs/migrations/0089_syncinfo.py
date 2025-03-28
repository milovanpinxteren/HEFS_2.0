# Generated by Django 4.2.10 on 2025-01-19 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0088_alter_terminallinks_shop_domain_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyncInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hob_product_title', models.CharField(max_length=255)),
                ('hob_product_handle', models.CharField(max_length=255)),
                ('hob_id', models.CharField(max_length=255)),
                ('hob_variant_id', models.CharField(max_length=255)),
                ('geb_id', models.CharField(max_length=255)),
                ('geb_variant_id', models.CharField(max_length=255)),
                ('geb_product_title', models.CharField(max_length=255)),
                ('geb_product_handle', models.CharField(max_length=255)),
                ('quantity', models.IntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
