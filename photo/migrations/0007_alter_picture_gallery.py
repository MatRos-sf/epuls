# Generated by Django 5.0.1 on 2024-02-17 10:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("photo", "0006_gallery_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="picture",
            name="gallery",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pictures",
                to="photo.gallery",
            ),
        ),
    ]
