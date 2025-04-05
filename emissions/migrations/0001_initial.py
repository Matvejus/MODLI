# Generated by Django 5.0.3 on 2025-03-13 08:58

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Certification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Gown',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('session_key', models.CharField(blank=True, max_length=40, null=True)),
                ('visible', models.BooleanField(blank=True, help_text='Indicates if the gown is visible on the front-end.', null=True)),
                ('type', models.CharField(choices=[('Bio', 'Bio'), ('Recycled', 'Recycled'), ('Regular', 'Regular')], max_length=255)),
                ('reusable', models.BooleanField()),
                ('woven', models.BooleanField(blank=True, null=True)),
                ('cost', models.FloatField(blank=True, null=True, verbose_name='Cost per piece €')),
                ('laundry_cost', models.FloatField(blank=True, null=True, verbose_name='Cost per wash €')),
                ('waste_cost', models.FloatField(blank=True, null=True, verbose_name='Waste cost penalty €')),
                ('residual_value', models.FloatField(blank=True, null=True, verbose_name='Residual value €')),
                ('weight', models.FloatField(blank=True, null=True, verbose_name='Weight in grams')),
                ('fte_local', models.FloatField(blank=True, null=True, verbose_name='Local FTE')),
                ('fte_local_extra', models.FloatField(blank=True, null=True, verbose_name='Local FTE-extra')),
                ('washes', models.IntegerField(blank=True, null=True)),
                ('comfort', models.IntegerField(validators=[django.core.validators.MinValueValidator(0, message='0 - comofort is not included in the optimization.'), django.core.validators.MaxValueValidator(6, message='6 - Not applicable')], verbose_name='Comfort level (likert scale)')),
                ('hygine', models.IntegerField(validators=[django.core.validators.MinValueValidator(0, message='0 - hygine is not included in the optimization.'), django.core.validators.MaxValueValidator(6, message='6 - Not applicable')], verbose_name='Hygine level (likert scale)')),
                ('source', models.CharField(max_length=100)),
                ('certificates', models.ManyToManyField(blank=True, to='emissions.certification', verbose_name='Sustainability certificates')),
            ],
        ),
        migrations.CreateModel(
            name='EmissionsNew',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emission_stage', models.CharField(choices=[('Production', 'Production'), ('Use', 'Use phase'), ('LOST', 'Lost'), ('EOL', 'End Of life')], max_length=255)),
                ('emission_substage', models.CharField(choices=[('Total', 'Total emissions'), ('Raw', 'Raw'), ('Advanced', 'Advanced'), ('Transport', 'Transport')], max_length=255)),
                ('cost', models.FloatField(blank=True, max_length=255, null=True)),
                ('co2', models.FloatField(blank=True, max_length=255, null=True)),
                ('energy', models.FloatField(blank=True, max_length=255, null=True)),
                ('water', models.FloatField(blank=True, max_length=255, null=True)),
                ('recipe', models.FloatField(blank=True, max_length=255, null=True)),
                ('gown', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='emissions.gown')),
            ],
        ),
    ]
