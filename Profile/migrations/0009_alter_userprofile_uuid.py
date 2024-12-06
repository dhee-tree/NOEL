# Generated by Django 4.2.11 on 2024-12-04 22:30

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0008_auto_20241204_2125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]