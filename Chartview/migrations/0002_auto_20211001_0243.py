# Generated by Django 3.2.5 on 2021-09-30 17:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Chartview', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Skills',
            new_name='Skill',
        ),
        migrations.RenameModel(
            old_name='Traits',
            new_name='Trait',
        ),
    ]
