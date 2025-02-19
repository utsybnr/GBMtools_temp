# Generated by Django 3.2.5 on 2022-04-01 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Chartview', '0011_auto_20220401_0304'),
    ]

    operations = [
        migrations.RenameField(
            model_name='skill',
            old_name='UnitID',
            new_name='Unit',
        ),
        migrations.RenameField(
            model_name='status',
            old_name='UnitID',
            new_name='Unit',
        ),
        migrations.RenameField(
            model_name='trait',
            old_name='UnitID',
            new_name='Unit',
        ),
        migrations.AddField(
            model_name='unit',
            name='GundamwikiIntro',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='unit',
            name='GundamwikiName',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
