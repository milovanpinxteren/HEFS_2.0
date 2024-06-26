# Generated by Django 4.1.5 on 2024-04-22 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0057_alter_ingredienten_halfproduct'),
    ]

    operations = [
        migrations.RenameField(
            model_name='halfproducten',
            old_name='bereidingskosten',
            new_name='bereidingskosten_per_eenheid',
        ),
        migrations.RenameField(
            model_name='ingredienten',
            old_name='kostenpereenheid',
            new_name='kosten_per_eenheid',
        ),
        migrations.AddField(
            model_name='halfproducten',
            name='nodig_per_portie',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='ingredienten',
            name='nodig_per_portie',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
    ]
