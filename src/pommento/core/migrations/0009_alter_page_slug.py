# Generated by Django 4.1.4 on 2023-11-15 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pommento_core", "0008_rename_user_intel_comment_url_intel_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="page",
            name="slug",
            field=models.CharField(max_length=255),
        ),
    ]
