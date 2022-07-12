# Generated by Django 4.0.4 on 2022-07-11 22:34

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0007_picture_is_profile_picture'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='picture',
            unique_together={('user', 'is_profile_picture')},
        ),
    ]
