# Generated by Django 5.0.1 on 2024-02-23 14:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0006_alter_profile_voivodeship"),
        ("puls", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="puls",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="puls.puls",
            ),
        ),
    ]
