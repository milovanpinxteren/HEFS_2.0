# Generated by Django 4.2.10 on 2025-04-04 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0095_hoborders_syncinfo_deposit_money_syncinfo_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='hoborders',
            name='sales_channel',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
