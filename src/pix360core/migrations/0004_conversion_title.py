# Generated by Django 4.2.6 on 2023-10-23 12:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pix360core", "0003_file_mime_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversion",
            name="title",
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
