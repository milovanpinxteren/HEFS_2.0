# Generated by Django 4.1.5 on 2023-08-06 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0039_alter_customers_ordered_2020_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='JSONData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=25)),
                ('value', models.JSONField()),
            ],
        ),
    ]
