# Generated by Django 4.0.4 on 2022-07-09 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_profile_first_name_profile_last_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='about',
            field=models.TextField(blank=True, default='', max_length=1000),
        ),
    ]