# Generated by Django 3.1.1 on 2020-11-04 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0011_auto_20201104_0102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='title',
            field=models.CharField(max_length=256, verbose_name='Title'),
        ),
    ]
