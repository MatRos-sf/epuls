# Generated by Django 5.0.1 on 2024-02-16 12:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0003_alter_profile_profile_picture"),
        (
            "photo",
            "0004_rename_date_accepted_profilepicturerequest_examination_date_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="profilepicturerequest",
            name="profile",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to="account.profile",
            ),
            preserve_default=False,
        ),
    ]
