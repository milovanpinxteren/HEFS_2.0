# Generated by Django 4.1.5 on 2023-02-01 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0030_apiurls_organisatieids'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlgemeneInformatie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prognosegetal', models.IntegerField(default=0, help_text='Hoeveel personen voorspellen we?')),
            ],
        ),
    ]