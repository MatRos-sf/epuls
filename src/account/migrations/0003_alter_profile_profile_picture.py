# Generated by Django 5.0.1 on 2024-02-16 11:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="profile_picture",
            field=models.ImageField(
                default="default_photo_picture.jpg", upload_to="profile_picture"
            ),
        ),
    ]
