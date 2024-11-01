# Generated by Django 3.2.5 on 2022-03-31 18:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Chartview', '0010_rename_slv1pierce_skill_slv1pierce'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='UnitID',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Chartview.unit'),
        ),
        migrations.AddField(
            model_name='status',
            name='UnitID',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Chartview.unit'),
        ),
        migrations.AddField(
            model_name='trait',
            name='UnitID',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Chartview.unit'),
        ),
        migrations.AddField(
            model_name='unit',
            name='PrebanCode',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='unit',
            name='PrebanName',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
