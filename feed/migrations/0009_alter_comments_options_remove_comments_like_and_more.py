# Generated by Django 4.1.2 on 2022-11-13 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_alter_profile_avatar_alter_profile_cover_image'),
        ('feed', '0008_comments_replies'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comments',
            options={},
        ),
        migrations.RemoveField(
            model_name='comments',
            name='like',
        ),
        migrations.AddField(
            model_name='comments',
            name='liking',
            field=models.ManyToManyField(blank=True, related_name='like_reply', to='users.profile'),
        ),
    ]
