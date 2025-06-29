# Generated by Django 5.2.1 on 2025-06-15 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academic_setup', '0002_tipounidadacademica_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ciclo',
            unique_together={('nombre_ciclo', 'carrera')},
        ),
        migrations.AlterField(
            model_name='ciclo',
            name='orden',
            field=models.IntegerField(help_text='Orden numérico para los ciclos (ej: 1, 2, 3...)'),
        ),
        migrations.AlterUniqueTogether(
            name='ciclo',
            unique_together={('nombre_ciclo', 'carrera'), ('orden', 'carrera')},
        ),
    ]
