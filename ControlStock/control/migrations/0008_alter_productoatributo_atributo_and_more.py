# Generated by Django 5.2 on 2025-05-22 12:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0007_alter_productoatributo_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productoatributo',
            name='atributo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='control.atributo'),
        ),
        migrations.AlterField(
            model_name='productoatributo',
            name='opcion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='control.opcionatributo'),
        ),
    ]
