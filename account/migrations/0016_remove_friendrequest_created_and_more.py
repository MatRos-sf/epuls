# Generated by Django 5.0.1 on 2024-03-14 10:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0015_friendrequest"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="friendrequest",
            name="created",
        ),
        migrations.RemoveField(
            model_name="friendrequest",
            name="is_accepted",
        ),
    ]