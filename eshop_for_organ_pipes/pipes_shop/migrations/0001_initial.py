# Generated by Django 2.2.4 on 2021-08-29 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Registry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('shortcut', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Manual',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('shortcut', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Pipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('slug', models.SlugField(unique=True)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
                ('buyer', models.CharField(blank=True, max_length=120)),
                ('time_bought', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
                ('buyable', models.BooleanField(default=True)),
                ('registry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pipes_shop.Registry')),
                ('manual', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pipes_shop.Manual')),
                ('note', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pipes_shop.Note')),
            ],
        ),
    ]
