# Generated by Django 4.2.11 on 2024-12-03 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0004_alter_userprofile_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='verification_code',
            field=models.CharField(blank=True, default='', max_length=8),
        ),
    ]
