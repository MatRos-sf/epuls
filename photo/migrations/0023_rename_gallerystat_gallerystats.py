# Generated by Django 5.0.1 on 2024-05-02 17:55

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("photo", "0022_gallerystat_picturestats"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="GalleryStat",
            new_name="GalleryStats",
        ),
    ]
