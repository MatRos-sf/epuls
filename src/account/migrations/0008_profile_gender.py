# Generated by Django 5.0.1 on 2024-02-24 09:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0007_profile_puls"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="gender",
            field=models.TextField(
                choices=[("M", "Male"), ("F", "Female")], default="M"
            ),
        ),
    ]
