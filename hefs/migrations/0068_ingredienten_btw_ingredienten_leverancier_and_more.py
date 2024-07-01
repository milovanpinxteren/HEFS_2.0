# Generated by Django 4.1.5 on 2024-07-01 11:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0067_halfproducten_bruikbare_hoeveelheid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredienten',
            name='btw',
            field=models.CharField(blank=True, choices=[('H', 'Hoog (21%)'), ('L', 'Laag (9%)'), ('0', 'Geen/0')], max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='ingredienten',
            name='leverancier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hefs.leveranciers'),
        ),
        migrations.AddField(
            model_name='ingredienten',
            name='verpakkingsoort',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hefs.verpakkingssoort'),
        ),
    ]
