# Generated by Django 4.1.5 on 2023-12-05 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0047_alter_productinfo_btw_percentage'),
    ]

    operations = [
        migrations.CreateModel(
            name='ErrorLogDataGerijptebieren',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('error_message', models.CharField(default='', max_length=300, null=True)),
                ('timestamp', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
