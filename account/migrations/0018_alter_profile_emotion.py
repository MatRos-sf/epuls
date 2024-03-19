# Generated by Django 5.0.1 on 2024-03-19 12:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0017_profile_emotion"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="emotion",
            field=models.TextField(
                choices=[
                    ("1F601", "Happiness"),
                    ("1F602", "Joy"),
                    ("1F603", "Delight"),
                    ("1F604", "Smile"),
                    ("1F605", "Contentment"),
                    ("1F606", "Amusement"),
                    ("1F607", "Bliss"),
                    ("1F608", "Playfulness"),
                    ("1F609", "Wink"),
                    ("1F60A", "Pleasure"),
                    ("1F60B", "Satisfaction"),
                    ("1F60C", "Relief"),
                    ("1F60D", "Adoration"),
                    ("1F60E", "Coolness"),
                    ("1F60F", "Smirk"),
                    ("1F610", "Neutrality"),
                    ("1F611", "Indifference"),
                    ("1F612", "Displeasure"),
                    ("1F613", "Annoyance"),
                    ("1F614", "Pensiveness"),
                    ("1F615", "Confusion"),
                    ("1F616", "Disconcert"),
                    ("1F617", "Affection"),
                    ("1F618", "Kissing"),
                    ("1F619", "Tenderness"),
                    ("1F61A", "Romance"),
                    ("1F61B", "Playful Tease"),
                    ("1F61C", "Cheeky"),
                    ("1F61D", "Saucy"),
                    ("1F61E", "Disappointment"),
                    ("1F61F", "Worry"),
                    ("1F620", "Anger"),
                    ("1F621", "Frustration"),
                    ("1F622", "Sadness"),
                    ("1F623", "Determination"),
                    ("1F624", "Triumph"),
                    ("1F625", "Mixed Feelings"),
                    ("1F626", "Frustrated Frown"),
                    ("1F627", "Distress"),
                    ("1F628", "Fear"),
                    ("1F629", "Weariness"),
                    ("1F62A", "Sleepiness"),
                    ("1F62B", "Tiredness"),
                    ("1F62C", "Grimace"),
                    ("1F62D", "Sobbing"),
                    ("1F632", "Surprise"),
                    ("1F633", "Embarrassment"),
                    ("1F922", "Nausea"),
                    ("1F921", "Anger with Swearing"),
                    ("1F64F", "Gratitude"),
                    ("1F64C", "Optimism"),
                    ("1F499", "Compassion"),
                    ("1F4AA", "Pride"),
                    ("1F48B", "Affection"),
                    ("1F4AC", "Hope"),
                    ("1F604", "Gratification"),
                    ("1F606", "Ecstasy"),
                    ("1F60C", "Serenity"),
                    ("1F60D", "Empathy"),
                    ("1F64B", "Acceptance"),
                ],
                default="1F601",
            ),
        ),
    ]