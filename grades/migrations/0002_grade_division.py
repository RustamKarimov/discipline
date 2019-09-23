# Generated by Django 2.2.5 on 2019-09-22 20:43

from django.db import migrations, models
import grades.models


class Migration(migrations.Migration):

    dependencies = [
        ('grades', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='division',
            field=models.CharField(default=grades.models.get_division_name, max_length=25),
        ),
    ]