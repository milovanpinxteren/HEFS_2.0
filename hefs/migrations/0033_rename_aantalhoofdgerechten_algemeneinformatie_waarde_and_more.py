# Generated by Django 4.1.5 on 2023-02-01 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0032_algemeneinformatie_aantalhoofdgerechten_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='algemeneinformatie',
            old_name='aantalHoofdgerechten',
            new_name='waarde',
        ),
        migrations.RemoveField(
            model_name='algemeneinformatie',
            name='aantalOrders',
        ),
        migrations.RemoveField(
            model_name='algemeneinformatie',
            name='prognosegetal',
        ),
        migrations.AddField(
            model_name='algemeneinformatie',
            name='naam',
            field=models.CharField(default='', max_length=300),
        ),
    ]