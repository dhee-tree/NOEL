# Generated by Django 4.2.7 on 2023-12-08 13:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0016_santagroup_group_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='group_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Profile.santagroup'),
        ),
    ]
