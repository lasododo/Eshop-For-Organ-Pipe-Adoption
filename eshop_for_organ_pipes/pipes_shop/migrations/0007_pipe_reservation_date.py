# Generated by Django 2.2.4 on 2021-11-21 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pipes_shop', '0006_auto_20211121_1810'),
    ]

    operations = [
        migrations.AddField(
            model_name='pipe',
            name='reservation_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
