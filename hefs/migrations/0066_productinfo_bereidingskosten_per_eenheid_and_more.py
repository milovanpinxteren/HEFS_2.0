# Generated by Django 4.1.5 on 2024-07-01 11:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0065_leveranciers_verpakkingssoort_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productinfo',
            name='bereidingskosten_per_eenheid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='productinfo',
            name='etiket',
            field=models.BinaryField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='productinfo',
            name='gang',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='gang', to='hefs.gang'),
        ),
        migrations.AddField(
            model_name='productinfo',
            name='leverancier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hefs.leveranciers'),
        ),
        migrations.AddField(
            model_name='productinfo',
            name='verpakkingscombinatie',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='VerpakkingsMogelijkheden', to='hefs.verpakkingsmogelijkheden'),
        ),
        migrations.AddField(
            model_name='productinfo',
            name='verpakkingsoort',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hefs.verpakkingssoort'),
        ),
    ]
