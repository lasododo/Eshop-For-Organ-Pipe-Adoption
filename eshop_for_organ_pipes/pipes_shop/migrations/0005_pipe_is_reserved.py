# Generated by Django 2.2.4 on 2021-11-21 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pipes_shop', '0004_auto_20210929_2341'),
    ]

    operations = [
        migrations.AddField(
            model_name='pipe',
            name='is_reserved',
            field=models.BooleanField(default=True),
        ),
    ]