# Generated by Django 5.1 on 2024-10-14 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camiones', '0004_camion_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camion',
            name='latitud',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='camion',
            name='longitud',
            field=models.FloatField(default=0.0),
        ),
    ]
