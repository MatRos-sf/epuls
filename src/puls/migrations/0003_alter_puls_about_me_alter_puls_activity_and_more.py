# Generated by Django 5.0.1 on 2024-02-24 19:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("puls", "0002_puls_messages"),
    ]

    operations = [
        migrations.AlterField(
            model_name="puls",
            name="about_me",
            field=models.IntegerField(
                default=0, help_text="PLUS for fill the section 'about me' in."
            ),
        ),
        migrations.AlterField(
            model_name="puls",
            name="activity",
            field=models.IntegerField(
                default=0, help_text="PLUS for other different activities."
            ),
        ),
        migrations.AlterField(
            model_name="puls",
            name="diaries",
            field=models.IntegerField(
                default=0, help_text="PLUS for entres to diaries."
            ),
        ),
        migrations.AlterField(
            model_name="puls",
            name="logins",
            field=models.IntegerField(
                default=0, help_text="PLUS for log in to the server."
            ),
        ),
        migrations.AlterField(
            model_name="puls",
            name="presentation",
            field=models.IntegerField(
                default=0, help_text="PLUS for fill own presentation in."
            ),
        ),
        migrations.AlterField(
            model_name="puls",
            name="profile_photo",
            field=models.IntegerField(
                default=0, help_text="PLUS for accepted profile photo."
            ),
        ),
        migrations.AlterField(
            model_name="puls",
            name="schools",
            field=models.IntegerField(default=0, help_text="PLUS for fill schools in."),
        ),
        migrations.AlterField(
            model_name="puls",
            name="surfing",
            field=models.IntegerField(
                default=0, help_text="PLUS for surfint the Epuls."
            ),
        ),
        migrations.AlterField(
            model_name="puls",
            name="type",
            field=models.IntegerField(
                default=0,
                help_text="PLUS for type of account: Pro/Extrime/Divine. Once a month.",
            ),
        ),
    ]
