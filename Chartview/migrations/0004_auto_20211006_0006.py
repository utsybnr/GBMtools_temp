# Generated by Django 3.2.5 on 2021-10-05 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Chartview', '0003_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='AItype',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='status',
            name='CombinedCategory',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='status',
            name='Joblisence',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
