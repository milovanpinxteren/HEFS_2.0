# Generated by Django 4.1.5 on 2023-01-23 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0026_alter_orderextra_productnaam'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pickorders',
            name='afleverdatum',
        ),
        migrations.AlterField(
            model_name='neworders',
            name='afleverdatum',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='neworders',
            name='conversieID',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='orders',
            name='conversieID',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='productinfo',
            name='productID',
            field=models.CharField(blank=True, db_index=True, default='', help_text='Alleen invullen als je geen automatisch gegenereerd nummer wil', max_length=5, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='productinfo',
            name='productcode',
            field=models.CharField(blank=True, db_index=True, default='', help_text='Alleen invullen als je geen automatisch gegenereerd nummer wil', max_length=3),
        ),
    ]