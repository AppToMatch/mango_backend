# Generated by Django 4.0.4 on 2022-07-09 20:36

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0003_profile_about'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='likes',
        ),
        migrations.AddField(
            model_name='profile',
            name='i_like',
            field=models.ManyToManyField(blank=True, related_name='i_like', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='profile',
            name='likes_me',
            field=models.ManyToManyField(blank=True, related_name='likes_me', to=settings.AUTH_USER_MODEL),
        ),
    ]
