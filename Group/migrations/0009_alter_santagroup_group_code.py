# Generated by Django 4.2.7 on 2023-12-11 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Group', '0008_alter_santagroup_group_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='santagroup',
            name='group_code',
            field=models.CharField(default='CM9IY2', max_length=6, unique=True),
        ),
    ]