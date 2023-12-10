# Generated by Django 4.2.7 on 2023-12-09 14:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Group', '0001_initial'),
        ('Profile', '0020_rename_group_name_pick_group_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pick',
            name='group_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Group.santagroup'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='group_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Group.santagroup'),
        ),
        migrations.DeleteModel(
            name='SantaGroup',
        ),
    ]