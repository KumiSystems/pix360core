# Generated by Django 5.0.6 on 2024-11-15 10:06

import pix360core.fields
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pix360core", "0004_conversion_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversion",
            name="id",
            field=pix360core.fields.Char32UUIDField(
                default=uuid.uuid4, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="conversion",
            name="status",
            field=models.IntegerField(
                choices=[
                    (0, "Pending"),
                    (1, "Processing"),
                    (2, "Done"),
                    (-1, "Failed"),
                    (-2, "Dismissed"),
                    (10, "Downloading"),
                    (11, "Stitching"),
                ],
                default=0,
            ),
        ),
        migrations.AlterField(
            model_name="file",
            name="id",
            field=pix360core.fields.Char32UUIDField(
                default=uuid.uuid4, primary_key=True, serialize=False
            ),
        ),
    ]
