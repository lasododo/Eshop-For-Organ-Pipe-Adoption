# Generated by Django 2.2.4 on 2021-12-12 23:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_payment_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='shipping_total',
        ),
    ]
