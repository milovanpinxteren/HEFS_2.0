# Generated by Django 4.1.5 on 2023-07-17 14:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0033_rename_aantalhoofdgerechten_algemeneinformatie_waarde_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerzendOpties',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verzendoptie', models.CharField(max_length=250)),
                ('verzendkosten', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=6, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='neworders',
            name='verzendoptie',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.CASCADE, to='hefs.verzendopties'),
        ),
    ]
