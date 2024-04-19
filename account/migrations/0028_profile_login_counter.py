# Generated by Django 5.0.1 on 2024-04-19 08:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0027_rename_description_profile_presentation"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="login_counter",
            field=models.IntegerField(
                default=0, help_text="show how many time user's login"
            ),
        ),
    ]
