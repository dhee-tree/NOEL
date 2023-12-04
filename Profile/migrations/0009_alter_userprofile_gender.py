# Generated by Django 4.2.1 on 2023-12-04 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0008_userprofile_gender_userprofile_is_authenticated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Non-binary', 'Non-binary')], max_length=11),
        ),
    ]