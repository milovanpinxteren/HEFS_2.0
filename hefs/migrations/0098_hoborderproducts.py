# Generated by Django 4.2.10 on 2025-04-06 08:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0097_alter_hoborders_shopifyid'),
    ]

    operations = [
        migrations.CreateModel(
            name='HobOrderProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productname', models.CharField(blank=True, max_length=250, null=True)),
                ('productid', models.CharField(blank=True, max_length=250, null=True)),
                ('aantal', models.IntegerField(blank=True, default=0, null=True)),
                ('hoborder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hefs.hoborders')),
            ],
        ),
    ]
