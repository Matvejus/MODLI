# Generated by Django 5.0.1 on 2024-02-06 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_rename_gown_name_gown_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gown',
            name='times_reused',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
