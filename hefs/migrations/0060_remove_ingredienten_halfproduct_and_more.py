# Generated by Django 4.1.5 on 2024-05-27 17:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hefs', '0059_ingredienten_productinfo_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredienten',
            name='halfproduct',
        ),
        migrations.RemoveField(
            model_name='ingredienten',
            name='productinfo',
        ),
        migrations.CreateModel(
            name='HalfproductenIngredienten',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('halfproduct', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hefs.halfproducten')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hefs.ingredienten')),
            ],
            options={
                'unique_together': {('halfproduct', 'ingredient')},
            },
        ),
    ]