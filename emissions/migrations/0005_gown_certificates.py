# Generated by Django 5.0.3 on 2024-07-01 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("emissions", "0004_gown_cost"),
    ]

    operations = [
        migrations.AddField(
            model_name="gown",
            name="certificates",
            field=models.CharField(
                choices=[
                    ("FAIRT", "Fairtrade Textile Production Standard"),
                    ("FFL", "Fair for life Kleding"),
                    ("FAIRWARE", "Fair wear Foundation"),
                    ("OEKO-TEX", "OEKO-TEX Made in Green"),
                ],
                default=1,
                max_length=250,
            ),
            preserve_default=False,
        ),
    ]
