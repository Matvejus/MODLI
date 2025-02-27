# Generated by Django 5.0.3 on 2025-02-27 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emissions', '0036_alter_gown_visible'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emissionsnew',
            name='co2',
            field=models.FloatField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='emissionsnew',
            name='cost',
            field=models.FloatField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='emissionsnew',
            name='emission_stage',
            field=models.FloatField(choices=[('Production', 'Production'), ('Use', 'Use phase'), ('LOST', 'Lost'), ('EOL', 'End Of life')], max_length=255),
        ),
        migrations.AlterField(
            model_name='emissionsnew',
            name='emission_substage',
            field=models.FloatField(choices=[('Total', 'Total emissions'), ('Raw', 'Raw'), ('Advanced', 'Advanced'), ('Transport', 'Transport')], max_length=255),
        ),
        migrations.AlterField(
            model_name='emissionsnew',
            name='energy',
            field=models.FloatField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='emissionsnew',
            name='recipe',
            field=models.FloatField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='emissionsnew',
            name='water',
            field=models.FloatField(blank=True, max_length=255, null=True),
        ),
        migrations.DeleteModel(
            name='Emissions',
        ),
    ]
