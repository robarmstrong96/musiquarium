# Generated by Django 3.1.1 on 2020-11-03 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0009_auto_20201019_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='album_artwork_url',
            field=models.URLField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(default='assets/img/default/default_male.png', upload_to='assets/img/avatars/'),
        ),
        migrations.AlterField(
            model_name='song',
            name='album',
            field=models.CharField(blank=True, default='Unknown Album', max_length=64, verbose_name='Album'),
        ),
        migrations.AlterField(
            model_name='song',
            name='genre',
            field=models.CharField(blank=True, default='Unknown Genre', max_length=32, verbose_name='Genre'),
        ),
    ]
