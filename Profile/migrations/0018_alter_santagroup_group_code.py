# Generated by Django 4.2.7 on 2023-12-08 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0017_alter_userprofile_group_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='santagroup',
            name='group_code',
            field=models.CharField(blank=True, max_length=6, unique=True),
        ),
    ]