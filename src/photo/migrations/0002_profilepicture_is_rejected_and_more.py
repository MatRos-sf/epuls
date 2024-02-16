# Generated by Django 5.0.1 on 2024-02-16 11:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("photo", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profilepicture",
            name="is_rejected",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="profilepicture",
            name="picture",
            field=models.ImageField(
                default="default_photo_picture.jpg", upload_to="profile_picture"
            ),
        ),
    ]
