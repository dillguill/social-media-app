# Generated by Django 4.2.17 on 2025-01-13 23:26

from django.db import migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_alter_profile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='image',
            field=sorl.thumbnail.fields.ImageField(default=1, upload_to='profiles'),
            preserve_default=False,
        ),
    ]
