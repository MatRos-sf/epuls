# Generated by Django 5.0.1 on 2024-02-16 11:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AboutUser",
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
                ("height", models.CharField(blank=True, max_length=50, null=True)),
                ("weight", models.CharField(blank=True, max_length=50, null=True)),
                ("politics", models.CharField(blank=True, max_length=50, null=True)),
                ("dish", models.CharField(blank=True, max_length=50, null=True)),
                ("film", models.CharField(blank=True, max_length=50, null=True)),
                ("song", models.CharField(blank=True, max_length=50, null=True)),
                ("idol", models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Visitor",
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
                ("date_of_visit", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Diary",
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
                ("title", models.CharField(max_length=150)),
                ("content", models.TextField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("is_hide", models.BooleanField(default=False, verbose_name="hide")),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Guestbook",
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
                ("entry", models.TextField(help_text="Say hello!")),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "receiver",
                    models.ForeignKey(
                        help_text="The person who receive message.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="received_gb_entry",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        help_text="The person who types something.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_gb_entry",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created"],
            },
        ),
        migrations.CreateModel(
            name="Profile",
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
                ("date_of_birth", models.DateField(blank=True, null=True)),
                (
                    "short_description",
                    models.TextField(blank=True, max_length=100, null=True),
                ),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "type_of_profile",
                    models.TextField(
                        choices=[
                            ("B", "Basic"),
                            ("P", "Pro"),
                            ("X", "Xtreme"),
                            ("D", "Divine"),
                        ],
                        default="B",
                        max_length=1,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("is_confirm", models.BooleanField(default=False)),
                (
                    "about_me",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="account.aboutuser",
                    ),
                ),
                (
                    "friends",
                    models.ManyToManyField(
                        blank=True, related_name="friends", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
    ]