# Generated by Django 5.0.1 on 2024-03-17 22:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("account", "0016_remove_friendrequest_created_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Clipboard",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateField(auto_now_add=True)),
                ("expiry", models.DateField(blank=True, null=True)),
                (
                    "best_friends",
                    models.ManyToManyField(
                        related_name="clipboard_best_friends",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "friends",
                    models.ManyToManyField(
                        related_name="clipboard_friends", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="account.profile",
                    ),
                ),
            ],
        ),
    ]