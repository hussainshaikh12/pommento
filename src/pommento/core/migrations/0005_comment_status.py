# Generated by Django 4.1.4 on 2023-11-11 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pommento_core", "0004_alter_site_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="status",
            field=models.BooleanField(default=False),
        ),
    ]
