# Generated by Django 4.1.2 on 2022-11-13 13:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0007_rename_replies_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='replies',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='feed.comments'),
        ),
    ]