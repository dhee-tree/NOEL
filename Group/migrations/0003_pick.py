# Generated by Django 4.2.7 on 2023-12-09 22:02

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Group', '0002_groupmember'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pick',
            fields=[
                ('pick_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=50)),
                ('picked_by', models.CharField(max_length=255, unique=True)),
                ('date_picked', models.DateField(default=datetime.date.today)),
                ('group_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Group.santagroup')),
            ],
            options={
                'unique_together': {('full_name', 'group_id')},
            },
        ),
    ]