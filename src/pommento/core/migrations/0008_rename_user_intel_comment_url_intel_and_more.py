# Generated by Django 4.1.4 on 2023-11-15 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "pommento_core",
            "0007_remove_comment_url_intel_comment_url_intel_breach_and_more",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="comment",
            old_name="user_intel",
            new_name="url_intel",
        ),
        migrations.RenameField(
            model_name="comment",
            old_name="url_intel_breach",
            new_name="user_intel_breach",
        ),
        migrations.AlterField(
            model_name="comment",
            name="ip_intel",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]