# Generated by Django 4.2.11 on 2024-12-05 00:31

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0009_alter_userprofile_uuid'),
    ]

    operations = [
        migrations.CreateModel(
            name='WishList',
            fields=[
                ('wishlist_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('link', models.CharField(max_length=255)),
                ('date_created', models.DateField(default=datetime.date.today)),
                ('date_updated', models.DateField(default=datetime.date.today)),
                ('is_archived', models.BooleanField(default=False)),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Profile.userprofile')),
            ],
        ),
    ]