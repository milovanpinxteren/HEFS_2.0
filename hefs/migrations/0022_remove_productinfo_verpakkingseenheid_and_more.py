# Generated by Django 4.1.5 on 2023-01-19 10:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0021_rename_url_apiurls_api'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productinfo',
            name='verpakkingseenheid',
        ),
        migrations.AddField(
            model_name='productinfo',
            name='verpakkingscombinatie',
            field=models.ForeignKey(blank=True, default='', on_delete=django.db.models.deletion.PROTECT, related_name='VerpakkingsMogelijkheden', to='hefs.verpakkingsmogelijkheden'),
        ),
    ]
