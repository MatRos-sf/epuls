# Generated by Django 5.0.1 on 2024-03-12 11:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0012_profile_expire_of_tier"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="female_visitor",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="profile",
            name="male_visitor",
            field=models.IntegerField(default=0),
        ),
    ]