# Generated by Django 3.2.5 on 2022-04-10 19:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Chartview', '0016_auto_20220401_1810'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='skill',
            name='Category',
        ),
        migrations.RemoveField(
            model_name='skill',
            name='PartsName',
        ),
        migrations.RemoveField(
            model_name='skill',
            name='Unit',
        ),
        migrations.RemoveField(
            model_name='trait',
            name='Category',
        ),
        migrations.RemoveField(
            model_name='trait',
            name='PartsName',
        ),
        migrations.RemoveField(
            model_name='trait',
            name='Unit',
        ),
        migrations.AddField(
            model_name='skill',
            name='Status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Chartview.status'),
        ),
        migrations.AddField(
            model_name='trait',
            name='Status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Chartview.status'),
        ),
    ]
