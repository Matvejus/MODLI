# Generated by Django 5.0.3 on 2024-07-02 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("emissions", "0011_remove_gown_blue_water_remove_gown_co2_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="gown",
            name="weight",
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]
