# Generated by Django 2.2.5 on 2019-09-14 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20190914_2122'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='slug',
        ),
        migrations.AddField(
            model_name='teacher',
            name='slug',
            field=models.SlugField(default='test'),
            preserve_default=False,
        ),
    ]
