# Generated by Django 4.1.5 on 2023-01-07 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0007_rename_name_productinfo_verpakkingscombinatie'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productinfo',
            old_name='verpakkingscombinatie',
            new_name='combinatie_0',
        ),
        migrations.AddField(
            model_name='productinfo',
            name='combinatie_25',
            field=models.CharField(default='', max_length=10485759),
        ),
    ]
