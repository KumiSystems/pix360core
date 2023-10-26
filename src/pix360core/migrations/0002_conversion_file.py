# Generated by Django 4.2.6 on 2023-10-23 08:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import pix360core.models.content
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("pix360core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Conversion",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("url", models.URLField()),
                ("downloader", models.CharField(blank=True, max_length=256, null=True)),
                ("properties", models.JSONField(blank=True, null=True)),
                (
                    "status",
                    models.IntegerField(
                        choices=[
                            (0, "Pending"),
                            (1, "Processing"),
                            (2, "Done"),
                            (-1, "Failed"),
                        ],
                        default=0,
                    ),
                ),
                ("log", models.TextField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="File",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to=pix360core.models.content.file_upload_path
                    ),
                ),
                ("is_result", models.BooleanField(default=False)),
                (
                    "conversion",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="pix360core.conversion",
                    ),
                ),
            ],
        ),
    ]
