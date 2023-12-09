# Generated by Django 4.2.7 on 2023-12-08 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0018_alter_santagroup_group_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pick',
            old_name='group_id',
            new_name='group_name',
        ),
        migrations.RenameField(
            model_name='userprofile',
            old_name='group_id',
            new_name='group_name',
        ),
        migrations.AlterUniqueTogether(
            name='pick',
            unique_together={('full_name', 'group_name')},
        ),
    ]